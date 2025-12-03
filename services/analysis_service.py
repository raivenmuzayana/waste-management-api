import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date, timedelta
from models import collection_model, location_model, category_model
from typing import List, Dict, Any
import math

# --- 1. Rata-rata volume per lokasi ---
def get_avg_volume_per_location(db: Session) -> List:
    result = db.query(
        location_model.Location.name.label("location_name"),
        func.avg(collection_model.CollectionRecord.volume_kg).label("average_volume")
    ).join(collection_model.CollectionRecord, location_model.Location.id == collection_model.CollectionRecord.location_id)\
     .group_by(location_model.Location.name)\
     .all()
    return result

# --- 2. Rata-rata volume per jenis sampah ---
def get_avg_volume_per_category(db: Session) -> List:
    result = db.query(
        category_model.WasteCategory.name.label("category_name"),
        func.avg(collection_model.CollectionRecord.volume_kg).label("average_volume")
    ).join(collection_model.CollectionRecord, category_model.WasteCategory.id == collection_model.CollectionRecord.category_id)\
     .group_by(category_model.WasteCategory.name)\
     .all()
    return result

# --- 3. Top Locations ---
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

# --- 4. Distribusi ---
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

# --- 5. Tren Harian ---
def get_daily_trend(db: Session, start_date: date = None, end_date: date = None) -> List:
    # 1. Query Dasar: Ambil tanggal dan total volume
    query = db.query(
        func.date(collection_model.CollectionRecord.collection_date).label("collection_date"),
        func.sum(collection_model.CollectionRecord.volume_kg).label("total_volume")
    )

    # 2. Filter: Jika user memasukkan start_date
    if start_date:
        query = query.filter(func.date(collection_model.CollectionRecord.collection_date) >= start_date)
    
    # 3. Filter: Jika user memasukkan end_date
    if end_date:
        query = query.filter(func.date(collection_model.CollectionRecord.collection_date) <= end_date)

    # 4. Eksekusi: Group by tanggal dan urutkan
    result = query.group_by(func.date(collection_model.CollectionRecord.collection_date))\
                  .order_by("collection_date")\
                  .all()
    
    return result

# --- 6. Prediksi ---
def get_prediction(db: Session) -> Dict[str, Any]:
    """
    Memprediksi volume sampah untuk 7 hari ke depan menggunakan Linear Regression.
    """
    # 1. Ambil data historis harian (Total volume per hari)
    # Kita gunakan query yang sama dengan Daily Trend
    results = db.query(
        func.date(collection_model.CollectionRecord.collection_date).label("collection_date"),
        func.sum(collection_model.CollectionRecord.volume_kg).label("total_volume")
    ).group_by(func.date(collection_model.CollectionRecord.collection_date))\
     .order_by("collection_date")\
     .all()

    # Cek jika data terlalu sedikit untuk prediksi
    if len(results) < 2:
        return {
            "status": "error",
            "message": "Data tidak cukup untuk melakukan prediksi. Minimal butuh 2 hari data."
        }

    # 2. Konversi ke Pandas DataFrame untuk kemudahan olah data
    data = [{"date": r.collection_date, "volume": r.total_volume} for r in results]
    df = pd.DataFrame(data)
    
    # Pastikan kolom date bertipe datetime
    df["date"] = pd.to_datetime(df["date"])
    
    # 3. Feature Engineering: Ubah tanggal menjadi "Ordinal" (angka) agar bisa dihitung regresi
    # Kita hitung selisih hari dari tanggal pertama data
    start_date = df["date"].min()
    df["days_since_start"] = (df["date"] - start_date).dt.days

    # Siapkan X (fitur) dan y (target)
    X = df[["days_since_start"]]
    y = df["volume"]

    # 4. Latih Model Linear Regression
    model = LinearRegression()
    model.fit(X, y)

    # 5. Lakukan Prediksi untuk 7 Hari ke Depan
    last_day_metric = df["days_since_start"].max()
    future_days = np.array([[last_day_metric + i] for i in range(1, 8)]) # Hari ke-1 s/d 7 besok
    predicted_volumes = model.predict(future_days)

    # 6. Format Hasil Prediksi
    predictions = []
    last_date = df["date"].max()
    
    for i, vol in enumerate(predicted_volumes):
        next_date = last_date + timedelta(days=i+1)
        predictions.append({
            "date": next_date.strftime("%Y-%m-%d"),
            "predicted_volume_kg": round(vol, 2) # Bulatkan 2 desimal
        })

    # Hitung Tren (Koefisien kemiringan/Slope)
    # Jika positif = tren naik, negatif = tren turun
    slope = model.coef_[0]
    trend_status = "NAIK" if slope > 0 else "TURUN"

    return {
        "status": "success",
        "trend_analysis": trend_status,
        "slope": round(slope, 2), # Rata-rata kenaikan/penurunan per hari
        "predictions": predictions
    }

# --- 7. Optimasi Rute (TSP Nearest Neighbor) ---

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Menghitung jarak lingkaran besar antara dua titik di bumi (dalam km).
    """
    R = 6371.0 # Radius bumi dalam km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def get_optimized_route(db: Session) -> List[location_model.Location]:
    """
    Mengembalikan daftar lokasi yang sudah diurutkan berdasarkan rute terpendek
    menggunakan algoritma Greedy (Nearest Neighbor).
    """
    # 1. Ambil semua lokasi yang memiliki koordinat valid
    locations = db.query(location_model.Location).filter(
        location_model.Location.latitude.isnot(None),
        location_model.Location.longitude.isnot(None)
    ).all()

    if not locations:
        return []

    # 2. Algoritma Nearest Neighbor
    unvisited = locations[:]
    
    # Mulai dari lokasi pertama yang ditemukan (atau bisa custom logic)
    current_location = unvisited.pop(0) 
    route = [current_location]

    while unvisited:
        nearest_location = None
        min_dist = float('inf')

        for loc in unvisited:
            dist = calculate_haversine_distance(
                current_location.latitude, current_location.longitude,
                loc.latitude, loc.longitude
            )
            if dist < min_dist:
                min_dist = dist
                nearest_location = loc
        
        # Pindah ke lokasi terdekat
        if nearest_location:
            route.append(nearest_location)
            unvisited.remove(nearest_location)
            current_location = nearest_location
            
    return route