#seed.py random generator

import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import location_model, category_model, collection_model

# Buat tabel jika belum ada (Safe check)
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    try:
        print("Mulai generate data dummy...")

        # --- 1. MEMBUAT DATA MASTER (Lokasi & Kategori) ---
        
        # Daftar Nama Lokasi Palsu
        location_names = [
            "Pasar Induk Kecamatan A", "TPS RT B", "Terminal C", 
            "Pasar Modern D", "Pasar E", "Kawasan F", 
            "Komplek G", "Mall H"
        ]
        
        # Daftar Kategori Sampah
        category_names = [
            "Organik", "Plastik", "Kertas/Karton", 
            "Logam/Kaleng", "Kaca", "Residu"
        ]

        # Masukkan Lokasi ke DB (Cek dulu biar gak dobel)
        db_locations = []
        for name in location_names:
            loc = db.query(location_model.Location).filter_by(name=name).first()
            if not loc:
                # Generate koordinat acak sekitar Bandung (Latitude -6.9, Longitude 107.6)
                lat = -6.9 + random.uniform(-0.05, 0.05)
                lon = 107.6 + random.uniform(-0.05, 0.05)
                loc = location_model.Location(name=name, latitude=lat, longitude=lon)
                db.add(loc)
                db.commit()
                db.refresh(loc)
            db_locations.append(loc) # Simpan objek lokasi untuk dipakai nanti

        # Masukkan Kategori ke DB
        db_categories = []
        for name in category_names:
            cat = db.query(category_model.WasteCategory).filter_by(name=name).first()
            if not cat:
                cat = category_model.WasteCategory(name=name, description=f"Sampah jenis {name}")
                db.add(cat)
                db.commit()
                db.refresh(cat)
            db_categories.append(cat)

        print(f"✅ Berhasil membuat {len(db_locations)} lokasi dan {len(db_categories)} kategori.")

        # --- 2. GENERATE DATA TRANSAKSI (Collection Records) ---
        
        JUMLAH_DATA = 500  # Mau bikin berapa data? Ganti angka ini sesuka hati
        
        records_buffer = []
        for i in range(JUMLAH_DATA):
            # A. Pilih Random Lokasi & Kategori dari yang sudah dibuat di atas
            random_loc = random.choice(db_locations)
            random_cat = random.choice(db_categories)
            
            # B. Random Volume (Misal antara 5.0 kg sampai 100.0 kg)
            random_vol = round(random.uniform(5.0, 100.0), 2)
            
            # C. Random Tanggal (Dalam 180 hari terakhir)
            days_ago = random.randint(0, 180)
            random_date = datetime.now() - timedelta(days=days_ago)
            
            # Buat Objek Record
            new_record = collection_model.CollectionRecord(
                volume_kg=random_vol,
                collection_date=random_date,
                location_id=random_loc.id,
                category_id=random_cat.id
            )
            db.add(new_record)

        # Commit sekaligus biar cepat
        db.commit()
        print(f"🎉 Selesai! Berhasil meng-generate {JUMLAH_DATA} data sampah secara acak.")

    except Exception as e:
        print(f"❌ Terjadi error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()