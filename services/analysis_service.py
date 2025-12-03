<<<<<<< Updated upstream
=======
# file: services/analysis_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models import collection_model, location_model, category_model
from typing import List
from datetime import datetime, timedelta

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
    ).join(collection_model.CollectionRecord, category_model.WasteCategory.id == collection_model.CollectionRecord.category_id)\
     .group_by(category_model.WasteCategory.name)\
     .all()
    return result

# 3. Top Locations
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

# 4. Distribusi
def get_category_distribution(db: Session) -> List:
    total_waste = db.query(func.sum(collection_model.CollectionRecord.volume_kg)).scalar()
    if not total_waste or total_waste == 0:
        return []

    result_raw = db.query(
        category_model.WasteCategory.name.label("category_name"),
        func.sum(collection_model.CollectionRecord.volume_kg).label("total_volume")
    ).join(collection_model.CollectionRecord, category_model.WasteCategory.id == collection_model.CollectionRecord.category_id)\
     .group_by(category_model.WasteCategory.name)\
     .all()
    
    distribution = [
        {
            "category_name": r.category_name,
            "total_volume": r.total_volume,
            "percentage": (r.total_volume / total_waste) * 100
        } for r in result_raw
    ]
    return distribution

# 5. Tren Harian
def get_daily_trend(db: Session) -> List:
    result = db.query(
        func.date(collection_model.CollectionRecord.collection_date).label("collection_date"),
        func.sum(collection_model.CollectionRecord.volume_kg).label("total_volume")
    ).group_by(func.date(collection_model.CollectionRecord.collection_date))\
     .order_by("collection_date")\
     .all()
    return result

# 6. Prediksi Volume (Linear Regression)
def get_prediction(db: Session):
    # --- A. Ambil Data 30 Hari Terakhir ---
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    # Query: Kelompokkan volume berdasarkan tanggal
    daily_data = db.query(
        func.date(collection_model.CollectionRecord.collection_date).label('date'),
        func.sum(collection_model.CollectionRecord.volume_kg).label('total_volume')
    ).filter(
        collection_model.CollectionRecord.collection_date >= thirty_days_ago
    ).group_by(
        func.date(collection_model.CollectionRecord.collection_date)
    ).order_by(
        func.date(collection_model.CollectionRecord.collection_date)
    ).all()

    # --- B. Cek Kecukupan Data ---
    # Jika data kurang dari 2 hari, rumus regresi tidak bisa bekerja
    if len(daily_data) < 2:
        return {
            "status": "Not enough data",
            "message": "Data belum cukup untuk prediksi. Butuh minimal data 2 hari.",
            "predicted_volume_next_day": 0,
            "trend": "UNKNOWN"
        }

    # --- C. Rumus Matematika (Regresi Linear: y = mx + c) ---
    # x = urutan hari (0, 1, 2...)
    # y = volume sampah
    n = len(daily_data)
    sum_x = 0
    sum_y = 0
    sum_xy = 0
    sum_x2 = 0
    
    current_volume = 0 # Menyimpan volume hari terakhir untuk perbandingan

    for i, row in enumerate(daily_data):
        x = i
        y = float(row.total_volume) # Pastikan formatnya angka (float)
        
        sum_x += x
        sum_y += y
        sum_xy += (x * y)
        sum_x2 += (x * x)
        
        current_volume = y

    # Menghitung Slope (Kemiringan Garis / m)
    # Rumus: m = (n*Σxy - Σx*Σy) / (n*Σx² - (Σx)²)
    numerator = (n * sum_xy) - (sum_x * sum_y)
    denominator = (n * sum_x2) - (sum_x ** 2)
    
    if denominator == 0:
        m = 0
    else:
        m = numerator / denominator

    # Menghitung Intercept (Titik Potong / c)
    # Rumus: c = (Σy - m*Σx) / n
    c = (sum_y - (m * sum_x)) / n

    # --- D. Lakukan Prediksi ---
    # Kita ingin memprediksi hari berikutnya (index ke-n)
    next_day_index = n
    predicted_value = (m * next_day_index) + c

    # Mencegah hasil prediksi minus (tidak mungkin sampah minus)
    if predicted_value < 0:
        predicted_value = 0

    # --- E. Tentukan Status Tren ---
    trend_status = "STABIL"
    advice = "Volume sampah stabil."

    if m > 5: # Angka sensitivitas, bisa diubah sesuai kebutuhan
        trend_status = "MENINGKAT"
        advice = "Waspada! Tren sampah meningkat, siapkan armada tambahan."
    elif m < -5:
        trend_status = "MENURUN"
        advice = "Tren sampah menurun, armada bisa dikurangi."

    # --- F. Kembalikan Hasil ---
    return {
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "total_days_analyzed": n,
        "last_recorded_volume": round(current_volume, 2),
        "predicted_volume_next_day": round(predicted_value, 2),
        "trend": trend_status,
        "advice": advice,
        "equation": f"y = {round(m, 2)}x + {round(c, 2)}" # Menampilkan rumus untuk skripsi
    }
>>>>>>> Stashed changes
