"""Global test configuration to ensure critical environment variables are set
BEFORE any test module (including backend/test_*.py) imports app.main.

Keeps security enforcement in production code while allowing tests outside
backend/tests/ to import the FastAPI app without early RuntimeError.
"""
import os
from pathlib import Path

# Provide strong SECRET_KEY if not already defined (must be >=32 chars)
if 'SECRET_KEY' not in os.environ or len(os.environ.get('SECRET_KEY','')) < 32:
    os.environ['SECRET_KEY'] = 'test-suite-secret-key-2025-global-abcdef123456'

# Ensure a test database URL (SQLite) if none provided
os.environ.setdefault('DATABASE_URL', 'sqlite:///./test_api.db')

# Mark we are in testing mode so code paths can optionally reduce cost factors
os.environ.setdefault('TESTING', '1')

# Avoid duplicate collection/import mismatch: ignore backend/test_ml_system.py (duplicate of root test)
# Updated signature per pytest deprecation (use Path)
def pytest_ignore_collect(collection_path: Path, config):  # noqa: D401
    try:
        return str(collection_path).replace('\\', '/').endswith('backend/test_ml_system.py')
    except Exception:
        return False
