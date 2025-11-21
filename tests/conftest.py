import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app  # Impor aplikasi FastAPI utama Anda
from services import auth_service
from models import user_model

# --- Setup Database Testing (SQLite in-memory) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Buat tabel di database in-memory
Base.metadata.create_all(bind=engine)

# --- Override Dependency (Penting!) ---
# Ganti dependency get_db agar menggunakan database tes
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Terapkan override ke aplikasi
app.dependency_overrides[get_db] = override_get_db

# --- Fixtures (Alat bantu tes) ---

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    # Override DB untuk TestClient
    app.dependency_overrides[get_db] = lambda: db_session
    
    with TestClient(app) as c:
        yield c
        
    # Kembalikan override
    app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_admin_user(db_session):
    # Buat user admin di DB tes
    admin_user = user_model.User(
        username="testadmin",
        hashed_password=auth_service.get_password_hash("password123"),
        role=user_model.UserRole.ADMIN
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)
    return admin_user

@pytest.fixture(scope="function")
def admin_auth_headers(test_admin_user):
    # Buat token untuk admin
    token = auth_service.create_access_token(data={"sub": test_admin_user.username})
    return {"Authorization": f"Bearer {token}"}