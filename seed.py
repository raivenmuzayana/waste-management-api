# file: seed.py
import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import location_model, category_model, collection_model
from datetime import datetime

# Buat tabel jika belum ada
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    try:
        # 1. BACA CSV
        # Pastikan nama file CSV sesuai dengan yang ada di folder Anda
        csv_file = "dataset_sampah_dummy (2).csv" 
        print(f"Membaca file {csv_file}...")
        df = pd.read_csv(csv_file)

        # Hapus spasi di nama kolom jika ada
        df.columns = df.columns.str.strip()

        # 2. ITERASI SETIAP BARIS
        count = 0
        for index, row in df.iterrows():
            # --- Handle Lokasi ---
            loc_name = row['Lokasi']
            # Cek apakah lokasi sudah ada di DB?
            location = db.query(location_model.Location).filter_by(name=loc_name).first()
            if not location:
                # Buat baru jika belum ada
                location = location_model.Location(name=loc_name, latitude=0.0, longitude=0.0)
                db.add(location)
                db.commit()
                db.refresh(location)
            
            # --- Handle Kategori ---
            cat_name = row['Jenis_Sampah']
            category = db.query(category_model.WasteCategory).filter_by(name=cat_name).first()
            if not category:
                category = category_model.WasteCategory(name=cat_name, description="Impor dari CSV")
                db.add(category)
                db.commit()
                db.refresh(category)

            # --- Handle Format Tanggal ---
            # CSV format: DD/MM/YYYY, Database butuh: YYYY-MM-DD
            date_str = row['Tanggal']
            try:
                date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                # Fallback jika format salah
                date_obj = datetime.now()

            # --- Masukkan Data Sampah ---
            vol = float(row['Volume_Sampah_kg'])
            
            record = collection_model.CollectionRecord(
                volume_kg=vol,
                collection_date=date_obj,
                location_id=location.id,
                category_id=category.id
            )
            db.add(record)
            count += 1
        
        db.commit()
        print(f"Berhasil memasukkan {count} data ke database!")

    except Exception as e:
        print(f"Terjadi error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()