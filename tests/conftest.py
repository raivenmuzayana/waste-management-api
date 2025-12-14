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

# --- FIXTURES ---

@pytest.fixture(scope="session")
def db_engine():
    """Menggunakan engine database asli (MySQL)"""
    yield engine

@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    OPSI AMAN (Safe Mode):
    Menggunakan Nested Transaction.
    Meskipun kodemu memanggil db.commit(), data TIDAK akan tersimpan permanen.
    Setelah tes selesai, semuanya di-rollback.
    """
    connection = db_engine.connect()
    transaction = connection.begin() # Mulai transaksi utama
    
    # Bind session ke koneksi
    session = SessionLocal(bind=connection)

    # MULAI REKAYASA (Magic Trick)
    # Kita mulai 'Nested Transaction' (Savepoint)
    session.begin_nested()

    # Event Listener:
    # Setiap kali kodemu memanggil session.commit(), kita tangkap event-nya.
    # Alih-alih commit ke database, kita hanya restart savepoint-nya.
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.expire_all()
            session.begin_nested()

    yield session

    # BERSIH-BERSIH
    session.close()
    transaction.rollback() # Hapus semua jejak transaksi
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    # Override get_db agar aplikasi menggunakan session palsu kita (yang aman tadi)
    from database import get_db
    app.dependency_overrides[get_db] = lambda: db_session
    
    with TestClient(app) as c:
        yield c
    
    # Hapus override setelah selesai
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_admin_user(db_session):
    """
    Membuat user admin untuk keperluan tes.
    Karena kita pakai Opsi Aman (Rollback), user ini akan hilang sendiri
    setelah tes selesai. Jadi aman, tidak akan menumpuk di database.
    """
    # Cek dulu barangkali di DB asli emang udah ada user 'testadmin'
    existing_user = db_session.query(user_model.User).filter_by(username="testadmin").first()
    if existing_user:
        return existing_user

    admin_user = user_model.User(
        username="testadmin",
        hashed_password=auth_service.get_password_hash("password123"),
        role=user_model.UserRole.ADMIN
    )
    db_session.add(admin_user)
    db_session.commit() # Ini akan ditangkap oleh restart_savepoint di atas
    db_session.refresh(admin_user)
    return admin_user

@pytest.fixture(scope="function")
def admin_auth_headers(test_admin_user):
    token = auth_service.create_access_token(data={"sub": test_admin_user.username})
    return {"Authorization": f"Bearer {token}"}