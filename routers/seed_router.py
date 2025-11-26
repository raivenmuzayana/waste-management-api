from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import location_model, category_model, collection_model
import random
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/seed",
    tags=["Seed Data (Generator)"]
)

@router.post("/generate-dummy-data")
def generate_data(jumlah_data: int = 100, db: Session = Depends(get_db)):
    """
    Endpoint untuk meng-generate data dummy secara otomatis.
    Parameter 'jumlah_data' menentukan berapa banyak transaksi yang dibuat.
    """
    try:
        # --- 1. MEMBUAT DATA MASTER (Lokasi & Kategori) ---
        
        # Daftar Nama Lokasi Palsu (Sama seperti seed.py Anda)
        location_names = [
            "Pasar Induk Gedebage", "TPS 3R Sukaluyu", "Terminal Cicaheum", 
            "Alun-alun Bandung", "Pasar Kosambi", "Kawasan Dago", 
            "Komplek Setiabudi", "Mall PVJ Area"
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
                # Generate koordinat acak
                lat = -6.9 + random.uniform(-0.05, 0.05)
                lon = 107.6 + random.uniform(-0.05, 0.05)
                loc = location_model.Location(name=name, latitude=lat, longitude=lon)
                db.add(loc)
                db.commit()
                db.refresh(loc)
            db_locations.append(loc)

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

        # --- 2. GENERATE DATA TRANSAKSI ---
        
        for i in range(jumlah_data):
            # A. Pilih Random Lokasi & Kategori
            random_loc = random.choice(db_locations)
            random_cat = random.choice(db_categories)
            
            # B. Random Volume (5.0 kg - 100.0 kg)
            random_vol = round(random.uniform(5.0, 100.0), 2)
            
            # C. Random Tanggal (Dalam 30 hari terakhir)
            days_ago = random.randint(0, 30)
            random_date = datetime.now() - timedelta(days=days_ago)
            
            # Buat Objek Record
            new_record = collection_model.CollectionRecord(
                volume_kg=random_vol,
                collection_date=random_date,
                location_id=random_loc.id,
                category_id=random_cat.id
            )
            db.add(new_record)

        # Commit sekaligus
        db.commit()
        
        return {
            "message": "Sukses generate data dummy",
            "jumlah_lokasi": len(db_locations),
            "jumlah_kategori": len(db_categories),
            "data_transaksi_dibuat": jumlah_data
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal generate data: {str(e)}")