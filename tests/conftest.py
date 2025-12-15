import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, text

# 1. Setup Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 2. Import ASLI dari aplikasi
from database import SessionLocal, engine
from main import app
from services import auth_service
from models import user_model

# --- FIXTURES DATABASE & CLIENT ---

@pytest.fixture(scope="session")
def db_engine():
    """Menggunakan engine database asli (MySQL)"""
    yield engine

@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    OPSI AMAN (Safe Mode) dengan Nested Transaction.
    Data akan di-rollback setelah setiap tes selesai.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.expire_all()
            session.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    from database import get_db
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

# --- FIXTURES USER & AUTHENTICATION ---

@pytest.fixture(scope="function")
def test_admin_user(db_session):
    """Membuat user ADMIN sementara"""
    # Cek user lama (preventif)
    user = db_session.query(user_model.User).filter_by(username="testadmin").first()
    if not user:
        user = user_model.User(
            username="testadmin",
            hashed_password=auth_service.get_password_hash("password123"),
            role=user_model.UserRole.ADMIN
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_analyst_user(db_session):
    """Membuat user DATA ANALYST sementara (BARU)"""
    user = db_session.query(user_model.User).filter_by(username="testanalyst").first()
    if not user:
        user = user_model.User(
            username="testanalyst",
            hashed_password=auth_service.get_password_hash("password123"),
            role=user_model.UserRole.DATA_ANALYST
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def admin_token(test_admin_user):
    """Mengembalikan STRING token (bukan dict header)"""
    return auth_service.create_access_token(data={"sub": test_admin_user.username})

@pytest.fixture(scope="function")
def analyst_token(test_analyst_user):
    """Mengembalikan STRING token untuk analyst (BARU)"""
    return auth_service.create_access_token(data={"sub": test_analyst_user.username})

# Opsional: Jika ada tes lama yang pakai header langsung
@pytest.fixture(scope="function")
def admin_auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}