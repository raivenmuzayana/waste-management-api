# file: seed.py
import pandas as pd
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from urllib.parse import quote_plus

# --- Import Model ---
# 1. Model Sampah (Pakai Base lama)
from database import Base as WasteBase, engine as waste_engine, SessionLocal as WasteSession
from models import location_model, category_model, collection_model
# 2. Model Wine (Pakai Base baru yang kita buat di langkah 2)
from models.wine_model import Wine, WineBase 

from datetime import datetime

# --- KONFIGURASI KONEKSI KEDUA (WINE DB) ---
load_dotenv()

# Ambil kredensial dari .env
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD") or ""
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
SAFE_PASSWORD = quote_plus(DB_PASSWORD)

# NAMA DATABASE BARU (Hardcode atau ambil dari env jika mau)
WINE_DB_NAME = "wine_db"

# Buat URL Koneksi Khusus Wine
WINE_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{SAFE_PASSWORD}@{DB_HOST}:{DB_PORT}/{WINE_DB_NAME}"

# Setup Engine & Session untuk Wine
wine_engine = create_engine(WINE_DATABASE_URL)
WineSession = sessionmaker(autocommit=False, autoflush=False, bind=wine_engine)

# --- INITIALIZE TABLES ---
# Buat tabel sampah di DB Sampah
WasteBase.metadata.create_all(bind=waste_engine)
# Buat tabel wine di DB Wine (Penting!)
WineBase.metadata.create_all(bind=wine_engine)


def seed_waste_data():
    """Import ke Database Sampah (Default)"""
    db = WasteSession()
    csv_file = "dataset_sampah_dummy (2).csv"
    
    if not os.path.exists(csv_file):
        print(f"[SKIP] File {csv_file} tidak ditemukan.")
        return

    print(f"--- Mengimpor ke DATABASE UTAMA (Sampah): {csv_file} ---")
    try:
        df = pd.read_csv(csv_file)
        df.columns = df.columns.str.strip()
        count = 0
        for index, row in df.iterrows():
            # Logika Import Sampah
            loc_name = row['Lokasi']
            location = db.query(location_model.Location).filter_by(name=loc_name).first()
            if not location:
                location = location_model.Location(name=loc_name, latitude=0.0, longitude=0.0)
                db.add(location)
                db.commit()
                db.refresh(location)
            
            cat_name = row['Jenis_Sampah']
            category = db.query(category_model.WasteCategory).filter_by(name=cat_name).first()
            if not category:
                category = category_model.WasteCategory(name=cat_name, description="Impor CSV")
                db.add(category)
                db.commit()
                db.refresh(category)

            date_str = row['Tanggal']
            try:
                date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                date_obj = datetime.now()

            record = collection_model.CollectionRecord(
                volume_kg=float(row['Volume_Sampah_kg']),
                collection_date=date_obj,
                location_id=location.id,
                category_id=category.id
            )
            db.add(record)
            count += 1
        
        db.commit()
        print(f"-> SUKSES: {count} data sampah tersimpan.\n")
    except Exception as e:
        print(f"-> ERROR Sampah: {e}\n")
        db.rollback()
    finally:
        db.close()

def seed_wine_data():
    """Import ke Database Baru (wine_db)"""
    db = WineSession() # Perhatikan kita pakai session yang berbeda
    csv_file = "WineQT.csv"
    
    if not os.path.exists(csv_file):
        print(f"[SKIP] File {csv_file} tidak ditemukan.")
        return

    print(f"--- Mengimpor ke DATABASE BARU ({WINE_DB_NAME}): {csv_file} ---")
    try:
        df = pd.read_csv(csv_file)
        count = 0
        for index, row in df.iterrows():
            wine = Wine(
                fixed_acidity=row['fixed acidity'],
                volatile_acidity=row['volatile acidity'],
                citric_acid=row['citric acid'],
                residual_sugar=row['residual sugar'],
                chlorides=row['chlorides'],
                free_sulfur_dioxide=row['free sulfur dioxide'],
                total_sulfur_dioxide=row['total sulfur dioxide'],
                density=row['density'],
                pH=row['pH'],
                sulphates=row['sulphates'],
                alcohol=row['alcohol'],
                quality=int(row['quality'])
            )
            db.add(wine)
            count += 1
        
        db.commit()
        print(f"-> SUKSES: {count} data wine tersimpan di database '{WINE_DB_NAME}'.\n")
    except Exception as e:
        print(f"-> ERROR Wine: {e}\n")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_waste_data()
    seed_wine_data()
    print("=== SELESAI ===")