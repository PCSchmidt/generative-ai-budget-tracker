import os
import pytest
import sys
from sqlalchemy import create_engine, text, event  # added event
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from alembic.script import ScriptDirectory  # added
from sqlalchemy.exc import InvalidRequestError  # added
import uuid  # added for unique emails
# Ensure backend directory (parent of this tests folder) is on sys.path so 'app' package is importable
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Force test database URL (SQLite file DB)
os.environ['DATABASE_URL'] = 'sqlite:///./test_api.db'
# Testing flag
os.environ.setdefault('TESTING', '1')

# Ensure a strong SECRET_KEY for tests (main.py enforces >=32 chars)
if 'SECRET_KEY' not in os.environ or len(os.environ.get('SECRET_KEY','')) < 32:
    os.environ['SECRET_KEY'] = 'test-suite-secret-key-2025-abcdef123456'

# Alembic setup BEFORE importing app modules that may reflect metadata
from alembic.config import Config
from alembic import command

# Build alembic config relative to backend root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ALEMBIC_INI_PATH = os.path.join(BASE_DIR, 'alembic.ini')

alembic_cfg = Config(ALEMBIC_INI_PATH)
# Force absolute script_location so running from project root works
ABS_SCRIPT_DIR = os.path.join(BASE_DIR, 'alembic')
alembic_cfg.set_main_option('script_location', ABS_SCRIPT_DIR)
assert os.path.isdir(ABS_SCRIPT_DIR), f"Alembic script dir missing: {ABS_SCRIPT_DIR}"

# Ensure alembic sees the same DATABASE_URL
alembic_cfg.set_main_option('sqlalchemy.url', os.environ['DATABASE_URL'])

# Run migrations once per test session to create schema
@pytest.fixture(scope='session', autouse=True)
def apply_migrations():
    db_url = os.environ['DATABASE_URL']
    if db_url.startswith('sqlite:///'):
        db_path = db_url.replace('sqlite:///', '')
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except OSError:
                pass
    # Fresh upgrade
    command.upgrade(alembic_cfg, 'head')
    yield

script_directory = ScriptDirectory.from_config(alembic_cfg)

from app.database import get_db, DATABASE_URL  # noqa: E402
from app.main import app  # noqa: E402

# Create engine & session factory AFTER migrations
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

# SAVEPOINT pattern enabling rollback even after code under test calls commit()
@event.listens_for(SessionTesting, 'after_transaction_end')
def restart_savepoint(session, transaction):
    # If the outermost nested transaction ended, start a new one so further commits stay isolated
    if transaction.nested and not transaction._parent.nested:
        session.expire_all()
        session.begin_nested()

# Optional: verify current revision matches head (safety net)
@pytest.fixture(scope='session', autouse=True)
def verify_head_revision():
    heads = set(script_directory.get_heads())
    with engine.connect() as conn:
        current = conn.execute(text('SELECT version_num FROM alembic_version')).scalar()
    assert current in heads, f'Current revision {current} not in heads {heads}'
    yield

@pytest.fixture(scope='function')
def db_session():
    connection = engine.connect()
    # Enable FK constraints for sqlite
    try:
        connection.execute(text('PRAGMA foreign_keys=ON'))
    except Exception:
        pass
    # Start a root transaction only if one not already present
    if not connection.in_transaction():
        try:
            transaction = connection.begin()
        except InvalidRequestError:
            transaction = connection.get_transaction()
    else:
        transaction = connection.get_transaction()
    session: Session = SessionTesting(bind=connection)
    session.begin_nested()  # initial SAVEPOINT
    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            try:
                transaction.rollback()
            except Exception:
                pass
        connection.close()

@pytest.fixture(scope='function')
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    # Ensure no leakage of overrides
    app.dependency_overrides.clear()

@pytest.fixture
def create_user(client):
    def _create(email='test@example.com', password='Secretpass1'):
        resp = client.post('/auth/signup', json={'email': email, 'password': password})
        assert resp.status_code == 200
        return resp.json()
    return _create

try:
    from freezegun import freeze_time
    _HAS_FREEZEGUN = True
except ImportError:
    _HAS_FREEZEGUN = False

@pytest.fixture
def frozen_time():
    """Freeze time for deterministic expiry tests.
    Usage: with frozen_time('2025-01-01T00:00:00Z'):
    If freezegun not installed, yields a passthrough context manager.
    """
    if not _HAS_FREEZEGUN:
        from contextlib import contextmanager
        @contextmanager
        def _noop(ts=None):
            yield
        return _noop
    return freeze_time

@pytest.fixture
def user_factory(client):
    counter = {'i': 0}
    def _make(email=None, password='Secretpass1'):
        counter['i'] += 1
        if not email:
            email = f'user{counter["i"]}-{uuid.uuid4().hex[:8]}@example.com'
        resp = client.post('/auth/signup', json={'email': email, 'password': password})
        assert resp.status_code == 200, resp.text
        data = resp.json()
        return data, password
    return _make

@pytest.fixture
def auth_pair(user_factory):
    data, pwd = user_factory()
    return data  # contains access_token, refresh_token, user

@pytest.fixture
def access_token(auth_pair):
    return auth_pair['access_token']

@pytest.fixture
def refresh_token(auth_pair):
    return auth_pair['refresh_token']

@pytest.fixture
def expired_refresh_token(db_session, user_factory, frozen_time):
    # Create a refresh token then advance time beyond expiry
    from app.auth.security import create_refresh_record
    from app.auth.models import User
    data, _ = user_factory()
    user_id = data['user']['id']
    raw, rt = create_refresh_record(db_session, user_id, expires_minutes=0)  # Immediate expiry
    return raw
