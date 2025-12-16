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
def get_daily_trend(db: Session, start_date: date = None, end_date: date = None) -> Dict[str, Any]: # Ubah type hint return
    """
    Mengambil tren harian & menghitung status NAIK/TURUN.
    """
    # ATURAN: Default 180 hari terakhir
    if not start_date:
        start_date = date.today() - timedelta(days=180)

    # 1. Query Dasar
    query = db.query(
        func.date(collection_model.CollectionRecord.collection_date).label("collection_date"),
        func.sum(collection_model.CollectionRecord.volume_kg).label("total_volume")
    )

    # 2. Filter Tanggal
    query = query.filter(func.date(collection_model.CollectionRecord.collection_date) >= start_date)
    if end_date:
        query = query.filter(func.date(collection_model.CollectionRecord.collection_date) <= end_date)

    # 3. Eksekusi
    results = query.group_by(func.date(collection_model.CollectionRecord.collection_date))\
                   .order_by("collection_date")\
                   .all()
    
    # Handle jika data kosong
    if not results:
        return {
            "trend_status": "STABIL",
            "data": []
        }

    # 4. Analisis Tren dengan Pandas
    data_list = [{"collection_date": r.collection_date, "total_volume": r.total_volume} for r in results]
    df = pd.DataFrame(data_list)
    
    df["collection_date"] = pd.to_datetime(df["collection_date"])
    df = df.sort_values("collection_date")

    # Moving Average
    df["moving_average"] = df["total_volume"].rolling(window=7, min_periods=1).mean()

    # Rounding
    df["total_volume"] = df["total_volume"].round(2)
    df["moving_average"] = df["moving_average"].round(2)

    # --- 5. LOGIKA BARU: Tentukan Status NAIK/TURUN ---
    # Kita gunakan Linear Regression sederhana pada data yang ada untuk melihat 'slope' (kemiringan)
    # Jika slope positif = NAIK, negatif = TURUN
    
    trend_status = "STABIL"
    if len(df) > 1:
        # Buat urutan hari (0, 1, 2, ...) sebagai X
        x = np.arange(len(df))
        y = df["total_volume"].values
        
        # Fit user-friendly polynomial (degree 1 = linear)
        slope, intercept = np.polyfit(x, y, 1)
        
        if slope > 0.05: # Threshold toleransi sedikit
            trend_status = "NAIK"
        elif slope < -0.05:
            trend_status = "TURUN"
        else:
            trend_status = "STABIL"

    # 6. Return Format Baru
    return {
        "trend_status": trend_status,
        "data": df.to_dict(orient="records")
    }

# --- 8. Analisis Top Producing Day (Baru) ---
def get_top_producing_days(db: Session) -> List[Dict[str, Any]]:
    """
    Menganalisis akumulasi volume sampah berdasarkan HARI (Senin - Minggu).
    """
    # 1. Query Data (Hanya tanggal dan volume)
    results = db.query(
        collection_model.CollectionRecord.collection_date,
        collection_model.CollectionRecord.volume_kg
    ).all()

    if not results:
        return []

    # 2. Masukkan ke Pandas DataFrame
    data = [{"date": r.collection_date, "volume": r.volume_kg} for r in results]
    df = pd.DataFrame(data)

    # 3. Preprocessing Date
    df["date"] = pd.to_datetime(df["date"])
    
    # Ekstrak nama hari (Monday, Tuesday, etc.)
    df["day_name"] = df["date"].dt.day_name()

    # 4. Grouping & Sum
    grouped = df.groupby("day_name")["volume"].sum().reset_index()

    # 5. Hitung Persentase
    total_vol = grouped["volume"].sum()
    grouped["percentage"] = (grouped["volume"] / total_vol) * 100

    # 6. Sorting (Terbesar ke Terkecil)
    grouped = grouped.sort_values(by="volume", ascending=False)

    # 7. Formatting output
    # Kita bulatkan angkanya agar rapi
    result_list = []
    for _, row in grouped.iterrows():
        result_list.append({
            "day_name": row["day_name"],
            "total_volume": round(row["volume"], 2),
            "percentage": round(row["percentage"], 1)
        })

    return result_list

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

def get_location_category_pivot(db: Session):
    # 1. Ambil data mentah (Sama seperti query Anda, tapi ambil semua)
    query = db.query(
        location_model.Location.name.label("location"),
        category_model.WasteCategory.name.label("category"),
        collection_model.CollectionRecord.volume_kg
    ).join(collection_model.CollectionRecord, location_model.Location.id == collection_model.CollectionRecord.location_id)\
     .join(category_model.WasteCategory, category_model.WasteCategory.id == collection_model.CollectionRecord.category_id)\
     .all()

    if not query:
        return {"x_axis": [], "y_axis": [], "data": []}

    # 2. Masukkan ke Pandas DataFrame
    df = pd.DataFrame(query, columns=["location", "category", "volume_kg"])

    # 3. Lakukan PIVOT (Magic-nya di sini!)
    # index=Baris (Lokasi), columns=Kolom (Kategori), values=Isi (Volume)
    # fill_value=0 artinya: yang kosong diisi 0
    pivot_df = df.pivot_table(index="location", columns="category", values="volume_kg", aggfunc="sum", fill_value=0)

    # 4. Format Output agar enak dimakan Frontend (ApexCharts / Chart.js friendly)
    result = {
        "y_axis": pivot_df.index.tolist(),      # Daftar Lokasi
        "x_axis": pivot_df.columns.tolist(),    # Daftar Kategori
        "data": pivot_df.values.tolist()        # Matrix Angka [[10, 0, 5], [2, 20, 0], ...]
    }
    
    return result

def get_dashboard_summary(db: Session) -> Dict:
    # 1. Total Sampah (All time)
    total = db.query(func.sum(collection_model.CollectionRecord.volume_kg)).scalar() or 0
    
    # 2. Total Lokasi Aktif
    loc_count = db.query(func.count(location_model.Location.id)).scalar() or 0
    
    # 3. Lokasi Paling Kotor
    top_loc = get_top_locations(db, limit=1)
    top_loc_name = top_loc[0].location_name if top_loc else "-"
    
    # 4. Hari Tersibuk
    top_day = get_top_producing_days(db)
    busiest = top_day[0]['day_name'] if top_day else "-"

    # --- 5. LOGIKA BARU: Trend Status (7 Hari vs 7 Hari Sebelumnya) ---
    today = date.today()
    week_ago = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)

    # Volume Minggu Ini (H-7 sampai Hari Ini)
    current_vol = db.query(func.sum(collection_model.CollectionRecord.volume_kg))\
        .filter(func.date(collection_model.CollectionRecord.collection_date) > week_ago)\
        .scalar() or 0

    # Volume Minggu Lalu (H-14 sampai H-7)
    prev_vol = db.query(func.sum(collection_model.CollectionRecord.volume_kg))\
        .filter(func.date(collection_model.CollectionRecord.collection_date) <= week_ago,
                func.date(collection_model.CollectionRecord.collection_date) > two_weeks_ago)\
        .scalar() or 0

    if current_vol > prev_vol:
        trend = "NAIK"
    elif current_vol < prev_vol:
        trend = "TURUN"
    else:
        trend = "STABIL"

    return {
        "total_waste_kg": round(total, 2),
        "total_locations": loc_count,
        "most_polluted_location": top_loc_name,
        "busiest_day": busiest,
        "trend_status": trend # <--- Masukkan ke return
    }