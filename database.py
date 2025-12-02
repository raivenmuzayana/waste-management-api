from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus  # <-- Tambahan penting untuk password dengan simbol @

# Load konfigurasi dari file .env
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Fix jika password kosong
if not DB_PASSWORD:
    DB_PASSWORD = ""

# AMANKAN PASSWORD: Ubah simbol @ menjadi kode aman (%40) agar tidak error
# Ini langkah krusial karena password Anda mengandung @
SAFE_PASSWORD = quote_plus(DB_PASSWORD)

# URL Koneksi menggunakan pymysql dengan password yang sudah diamankan
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{SAFE_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()