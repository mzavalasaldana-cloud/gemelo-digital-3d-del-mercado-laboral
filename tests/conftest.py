"""
tests/conftest.py: Configuración global de pytest para LaborTwin.
Garantiza el aislamiento estricto de base de datos dirigiendo todas las pruebas
a 'labortwin_test' en PostgreSQL y bloqueando cualquier acceso a 'labortwin_db'.
"""

import os

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:1234@localhost:5432/labortwin_test"
)

# Establecer DATABASE_URL en el entorno ANTES de importar módulos del backend
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

import pytest
import backend.database as db

# Reconfigurar explícitamente el motor con NullPool para evitar conflictos de event loops en asyncpg
db.set_database_url(TEST_DATABASE_URL, use_null_pool=True)


@pytest.fixture(scope="session", autouse=True)
def enforce_test_db_isolation():
    """
    Verifica de forma estricta que los tests se ejecuten contra 'labortwin_test'
    y nunca toquen la base de datos operativa 'labortwin_db'.
    """
    current_url = str(db.get_engine().url)
    assert "labortwin_test" in current_url, (
        f"VIOLACIÓN DE AISLAMIENTO: Los tests deben ejecutarse en 'labortwin_test', "
        f"pero db.get_engine() apunta a '{current_url}'."
    )
    assert "labortwin_db" not in current_url, (
        f"VIOLACIÓN DE SEGURIDAD: Se detectó intento de acceso a la base operativa "
        f"'labortwin_db' durante los tests: '{current_url}'."
    )
