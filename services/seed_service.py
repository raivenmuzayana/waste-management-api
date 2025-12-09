import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import location_model, category_model, collection_model

# --- KONFIGURASI DATA (Satu tempat untuk ubah semua) ---
LOCATION_NAMES = [
    "Pasar Induk Kecamatan A", "TPS RT B", "Terminal C", 
    "Pasar Modern D", "Pasar E", "Kawasan F", 
    "Komplek G", "Mall H"
]

CATEGORY_NAMES = [
    "Organik", "Plastik", "Kertas/Karton", 
    "Logam/Kaleng", "Kaca", "Residu"
]

def execute_seeding(db: Session, total_data: int):
    """
    Fungsi inti untuk generate data. 
    Bisa dipanggil oleh API Router maupun CLI Script.
    """
    generated_count = 0
    
    # 1. Pastikan Master Data (Lokasi) Ada
    db_locations = []
    for name in LOCATION_NAMES:
        loc = db.query(location_model.Location).filter_by(name=name).first()
        if not loc:
            # Generate koordinat acak sekitar Bandung
            lat = -6.9 + random.uniform(-0.05, 0.05)
            lon = 107.6 + random.uniform(-0.05, 0.05)
            loc = location_model.Location(name=name, latitude=lat, longitude=lon)
            db.add(loc)
            db.commit()
            db.refresh(loc)
        db_locations.append(loc)

    # 2. Pastikan Master Data (Kategori) Ada
    db_categories = []
    for name in CATEGORY_NAMES:
        cat = db.query(category_model.WasteCategory).filter_by(name=name).first()
        if not cat:
            cat = category_model.WasteCategory(name=name, description=f"Sampah jenis {name}")
            db.add(cat)
            db.commit()
            db.refresh(cat)
        db_categories.append(cat)

    # 3. Generate Transaksi
    new_records = []
    for _ in range(total_data):
        random_loc = random.choice(db_locations)
        random_cat = random.choice(db_categories)
        random_vol = round(random.uniform(5.0, 100.0), 2)
        
        # Random tanggal 180 hari terakhir
        days_ago = random.randint(0, 180)
        random_date = datetime.now() - timedelta(days=days_ago)
        
        record = collection_model.CollectionRecord(
            volume_kg=random_vol,
            collection_date=random_date,
            location_id=random_loc.id,
            category_id=random_cat.id
        )
        new_records.append(record)
    
    # Bulk insert agar lebih cepat (opsional, bisa pakai add biasa)
    if new_records:
        db.bulk_save_objects(new_records)
        db.commit()
        generated_count = len(new_records)

    return {
        "locations_count": len(db_locations),
        "categories_count": len(db_categories),
        "records_created": generated_count
    }