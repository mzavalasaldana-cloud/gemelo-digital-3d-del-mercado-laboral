"""
Pruebas de Integración End-to-End: Langflow + PostgreSQL + FastAPI.
Verifica que la orquestación entre la base de datos PostgreSQL, el motor
Langflow Desktop y la persistencia de conversaciones sea sólida y consistente.
"""

import pytest
import psycopg2
from backend.database import DATABASE_URL, AsyncSessionLocal, init_db
from backend.models import CopilotMessageModel
from backend.copilot_service import get_langflow_config, execute_copilot_query
from sqlalchemy import select, delete


@pytest.mark.asyncio
async def test_postgres_connection_and_table_schema():
    """Valida la conectividad a PostgreSQL y la existencia de las tablas principales."""
    await init_db()
    async with AsyncSessionLocal() as session:
        # Consulta para verificar que la tabla copilot_chat_history esté disponible
        stmt = select(CopilotMessageModel).limit(1)
        res = await session.execute(stmt)
        # Debe ejecutarse sin lanzar excepción de tabla inexistente
        assert res is not None


@pytest.mark.asyncio
async def test_postgres_message_lifecycle():
    """Prueba el ciclo de vida de persistencia y limpieza de mensajes en PostgreSQL."""
    test_session = "pytest-integration-session"
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # 1. Limpiar previamente si existe
        await session.execute(delete(CopilotMessageModel).where(CopilotMessageModel.session_id == test_session))
        await session.commit()
        
        # 2. Insertar mensaje
        msg = CopilotMessageModel(
            session_id=test_session,
            country="KENYA",
            scenario="BASELINE",
            month=6,
            user_message="¿Qué impacto tiene el subsidio en el sector informal?",
            assistant_response="El subsidio reduce la tasa de informalidad acelerando la transición.",
            source="langflow",
            flow_id="2d660758-1eee-46f8-969f-c17998844627",
            verified_metrics={"informalityRate": 82.7},
            policy_params={"smeSubsidyUSDMonth": 50.0}
        )
        session.add(msg)
        await session.commit()
        msg_id = msg.id
        assert msg_id is not None
        
        # 3. Leer mensaje
        stmt = select(CopilotMessageModel).where(CopilotMessageModel.session_id == test_session)
        res = await session.execute(stmt)
        records = res.scalars().all()
        assert len(records) == 1
        assert records[0].source == "langflow"
        assert records[0].verified_metrics["informalityRate"] == 82.7
        
        # 4. Limpiar
        await session.execute(delete(CopilotMessageModel).where(CopilotMessageModel.session_id == test_session))
        await session.commit()


def test_langflow_config_validity():
    """Verifica que la configuración de conexión a Langflow apunte a valores válidos."""
    cfg = get_langflow_config()
    assert cfg["base_url"].startswith("http")
    assert cfg["flow_id"] == "2d660758-1eee-46f8-969f-c17998844627"
    assert len(cfg["api_key"]) > 10
    assert cfg["timeout"] >= 30.0
