from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models import collection_model, location_model, category_model
from typing import List
from datetime import date

# 1. Rata-rata volume per lokasi
def get_avg_volume_per_location(db: Session) -> List:
    result = db.query(
        location_model.Location.name.label("location_name"),
        func.avg(collection_model.CollectionRecord.volume_kg).label("average_volume")
    ).join(collection_model.CollectionRecord, location_model.Location.id == collection_model.CollectionRecord.location_id)\
     .group_by(location_model.Location.name)\
     .all()
    return result

# 2. Rata-rata volume per jenis sampah
def get_avg_volume_per_category(db: Session) -> List:
    result = db.query(
        category_model.WasteCategory.name.label("category_name"),
        func.avg(collection_model.CollectionRecord.volume_kg).label("average_volume")
    ).join(collection_model.CollectionRecord, category_model.WasteCategory.id == collection_model.CollectionRecord.waste_category_id)\
     .group_by(category_model.WasteCategory.name)\
     .all()
    return result

# 3. Lokasi produksi sampah tertinggi (Top 5)
def get_top_locations(db: Session, limit: int = 5) -> List:
    result = db.query(
        location_model.Location.name.label("location_name"),
        func.sum(collection_model.CollectionRecord.volume_kg).label("total_volume")
    ).join(collection_model.CollectionRecord, location_model.Location.id == collection_model.CollectionRecord.location_id)\
     .group_by(location_model.Location.name)\
     .order_by(desc("total_volume"))\
     .limit(limit)\
     .all()
    return result

# 4. Distribusi jenis sampah
def get_category_distribution(db: Session) -> List:
    # Pertama, hitung total volume keseluruhan
    total_waste = db.query(func.sum(collection_model.CollectionRecord.volume_kg)).scalar()
    if not total_waste or total_waste == 0:
        return []

    # Kedua, hitung total per kategori
    result_raw = db.query(
        category_model.WasteCategory.name.label("category_name"),
        func.sum(collection_model.CollectionRecord.volume_kg).label("total_volume")
    ).join(collection_model.CollectionRecord, category_model.WasteCategory.id == collection_model.CollectionRecord.waste_category_id)\
     .group_by(category_model.WasteCategory.name)\
     .all()
    
    # Ketiga, hitung persentase
    distribution = [
        {
            "category_name": r.category_name,
            "total_volume": r.total_volume,
            "percentage": (r.total_volume / total_waste) * 100
        } for r in result_raw
    ]
    return distribution

# 5. Tren volume sampah (harian)
def get_daily_trend(db: Session) -> List:
    result = db.query(
        func.date(collection_model.CollectionRecord.collection_date).label("collection_date"),
        func.sum(collection_model.CollectionRecord.volume_kg).label("total_volume")
    ).group_by(func.date(collection_model.CollectionRecord.collection_date))\
     .order_by("collection_date")\
     .all()
    return result

# 6. Prediksi (Placeholder)
def get_prediction(db: Session):
    # Ini adalah placeholder.
    # [cite: 10] Meminta prediksi, yang membutuhkan model ML (seperti ARIMA atau Prophet).
    # Ini tidak bisa dilakukan dengan SQL sederhana.
    # Untuk proyek nyata, service ini akan memanggil model ML yang sudah di-train.
    return {"message": "Fitur prediksi sedang dalam pengembangan."}