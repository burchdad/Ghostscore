"""
Pytest plugin to ensure test DB is always reset and schema is applied before tests.
"""
import os
import sys
# Ensure backend/ is on sys.path for test imports
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import pytest
from models.database import reset_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    # Use a dedicated SQLite test DB file
    os.environ["DATABASE_URL"] = "sqlite:///./test_ghostscore.db"
    # Remove any previous test DB file
    db_path = os.path.join(os.getcwd(), "test_ghostscore.db")
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass
    # Reset DB schema
    reset_db()
    yield
    # Optionally, clean up after tests
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass
