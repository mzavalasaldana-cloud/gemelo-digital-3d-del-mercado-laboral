"""
tests/conftest.py: Configuración global de pytest para LaborTwin.
Garantiza el aislamiento estricto de base de datos dirigiendo todas las pruebas
que usan la base de datos a 'labortwin_test' en PostgreSQL y bloqueando
cualquier acceso a 'labortwin_db'.
"""

import os
import pytest

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:1234@localhost:5432/labortwin_test"
)

# Establecer DATABASE_URL en el entorno para procesos que lean directamente la variable
os.environ["DATABASE_URL"] = TEST_DATABASE_URL


@pytest.fixture(scope="session")
def enforce_test_db_isolation():
    """
    Configura la base de datos de pruebas 'labortwin_test' con NullPool
    y verifica de forma estricta que los tests nunca toquen la base operativa 'labortwin_db'.
    Solo importa backend.database dinámicamente cuando este fixture es activado por tests que usan la BD.
    """
    import backend.database as db

    # Reconfigurar explícitamente el motor con NullPool para evitar conflictos de event loops en asyncpg
    db.set_database_url(TEST_DATABASE_URL, use_null_pool=True)

    current_url = str(db.get_engine().url)
    assert "labortwin_test" in current_url, (
        f"VIOLACIÓN DE AISLAMIENTO: Los tests deben ejecutarse en 'labortwin_test', "
        f"pero db.get_engine() apunta a '{current_url}'."
    )
    assert "labortwin_db" not in current_url, (
        f"VIOLACIÓN DE SEGURIDAD: Se detectó intento de acceso a la base operativa "
        f"'labortwin_db' durante los tests: '{current_url}'."
    )
    return db


@pytest.fixture(autouse=True)
def _auto_db_isolation_if_needed(request):
    """
    Activa automáticamente enforce_test_db_isolation solo en pruebas que usan la base de datos
    (marcadas con 'db' o ubicadas en módulos de integración PostgreSQL).
    """
    if request.node.get_closest_marker("db") is not None or "postgres" in request.node.nodeid:
        request.getfixturevalue("enforce_test_db_isolation")

