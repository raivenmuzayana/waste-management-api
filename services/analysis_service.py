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
    """
    Mengambil tren harian dengan batasan default 180 hari terakhir.
    Menghitung 7-Day Moving Average untuk melihat garis tren.
    """
    # ATURAN: Data dibuat dalam 180 hari terakhir (jika user tidak kirim filter tanggal)
    if not start_date:
        start_date = date.today() - timedelta(days=180)

    # 1. Query Dasar
    query = db.query(
        func.date(collection_model.CollectionRecord.collection_date).label("collection_date"),
        func.sum(collection_model.CollectionRecord.volume_kg).label("total_volume")
    )

    # 2. Terapkan Filter Tanggal
    query = query.filter(func.date(collection_model.CollectionRecord.collection_date) >= start_date)
    
    if end_date:
        query = query.filter(func.date(collection_model.CollectionRecord.collection_date) <= end_date)

    # 3. Eksekusi Query
    results = query.group_by(func.date(collection_model.CollectionRecord.collection_date))\
                   .order_by("collection_date")\
                   .all()
    
    if not results:
        return []

    # 4. Analisis Tren dengan Pandas (Moving Average)
    # Konversi hasil query (list of tuples) ke DataFrame
    # SQLAlchemy row bisa diakses via index atau attribute, kita pakai list of dicts biar aman
    data_list = [{"collection_date": r.collection_date, "total_volume": r.total_volume} for r in results]
    df = pd.DataFrame(data_list)
    
    # Pastikan kolom date bertipe datetime agar urutan benar
    df["collection_date"] = pd.to_datetime(df["collection_date"])
    df = df.sort_values("collection_date")

    # Hitung Simple Moving Average (SMA) 7 Hari
    # Ini membuat garis tren yang lebih halus ("smooth")
    df["moving_average"] = df["total_volume"].rolling(window=7, min_periods=1).mean()

    # Rounding agar rapi
    df["total_volume"] = df["total_volume"].round(2)
    df["moving_average"] = df["moving_average"].round(2)

    # Kembalikan ke format List of Dict untuk JSON Response
    return df.to_dict(orient="records")

# --- 6. Prediksi (Linear Regression) ---
def get_prediction(db: Session) -> Dict[str, Any]:
    """
    Memprediksi volume sampah untuk 7 hari ke depan menggunakan Linear Regression.
    """
    # 1. Ambil data historis harian
    results = db.query(
        func.date(collection_model.CollectionRecord.collection_date).label("collection_date"),
        func.sum(collection_model.CollectionRecord.volume_kg).label("total_volume")
    ).group_by(func.date(collection_model.CollectionRecord.collection_date))\
     .order_by("collection_date")\
     .all()

    if len(results) < 2:
        return {
            "status": "error",
            "message": "Data tidak cukup untuk melakukan prediksi. Minimal butuh 2 hari data."
        }

    # 2. Konversi ke Pandas
    data = [{"date": r.collection_date, "volume": r.total_volume} for r in results]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    
    # 3. Feature Engineering
    start_date = df["date"].min()
    df["days_since_start"] = (df["date"] - start_date).dt.days

    X = df[["days_since_start"]]
    y = df["volume"]

    # 4. Latih Model
    model = LinearRegression()
    model.fit(X, y)

    # 5. Prediksi 7 Hari ke Depan
    last_day_metric = df["days_since_start"].max()
    future_days = np.array([[last_day_metric + i] for i in range(1, 8)])
    predicted_volumes = model.predict(future_days)

    predictions = []
    last_date = df["date"].max()
    
    for i, vol in enumerate(predicted_volumes):
        next_date = last_date + timedelta(days=i+1)
        predictions.append({
            "date": next_date.strftime("%Y-%m-%d"),
            "predicted_volume_kg": max(0, round(vol, 2)) # Ensure no negative volume
        })

    slope = model.coef_[0]
    trend_status = "NAIK" if slope > 0 else "TURUN"

    return {
        "status": "success",
        "trend_analysis": trend_status,
        "slope": round(slope, 2),
        "predictions": predictions
    }

# --- 7. Optimasi Rute (TSP Nearest Neighbor) ---

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Menghitung jarak lingkaran besar antara dua titik di bumi (dalam km).
    """
    R = 6371.0 

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
    # 1. Ambil semua lokasi yang valid (punya lat/long)
    locations = db.query(location_model.Location).filter(
        location_model.Location.latitude.isnot(None),
        location_model.Location.longitude.isnot(None)
    ).all()

    # Perbaikan Logic: Cek jika data kosong
    if not locations:
        return []

    # Perbaikan Logic: Urutkan dulu berdasarkan ID agar start point konsisten
    locations.sort(key=lambda x: x.id)

    unvisited = locations[:]
    
    # Tentukan Titik Awal (Di sini kita ambil lokasi ID terkecil sebagai depot/start)
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
        
        # Pindah ke lokasi terdekat yang ditemukan
        if nearest_location:
            route.append(nearest_location)
            unvisited.remove(nearest_location)
            current_location = nearest_location
            
    return route