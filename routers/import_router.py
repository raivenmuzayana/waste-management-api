from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import collection_model, location_model, category_model
import pandas as pd
import io
from datetime import datetime

router = APIRouter(
    prefix="/import",
    tags=["Import Data"]
)

@router.post("/csv-collection")
async def import_collection_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Import data transaksi sampah dari CSV.
    Melakukan lookup ID untuk Lokasi dan Kategori secara otomatis.
    Mencegah penghapusan tabel (Schema) yang terjadi jika menggunakan to_sql replace.
    """
    # 1. Validasi Ekstensi File
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File harus berformat CSV")

    try:
        # 2. Baca Konten File
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))

        # 3. Cek Kolom Wajib (Sesuaikan nama kolom dengan header di CSV kamu)
        required_cols = ['Tanggal', 'Lokasi', 'Jenis_Sampah', 'Volume_Sampah_kg']
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(status_code=400, detail=f"CSV harus memiliki kolom: {required_cols}")

        # 4. Persiapkan Mapping (Kamus) dari Database
        # Tujuannya mengubah string "Lokasi_13" menjadi ID (misal: 1)
        
        # Ambil semua lokasi
        locations = db.query(location_model.Location).all()
        # Buat dictionary: {'Lokasi_13': 1, 'Lokasi_2': 5, ...}
        loc_map = {loc.name: loc.id for loc in locations}

        # Ambil semua kategori
        categories = db.query(category_model.WasteCategory).all()
        # Buat dictionary: {'Organik': 1, 'B3': 2, ...}
        cat_map = {cat.name: cat.id for cat in categories}

        new_records = []
        errors = []

        # 5. Iterasi setiap baris di CSV
        for index, row in df.iterrows():
            loc_name = row['Lokasi']
            cat_name = row['Jenis_Sampah']
            date_str = row['Tanggal']
            vol = row['Volume_Sampah_kg']

            # A. Validasi ID Lokasi & Kategori
            loc_id = loc_map.get(loc_name)
            cat_id = cat_map.get(cat_name)

            if not loc_id or not cat_id:
                # Catat error tapi jangan stop proses (biar data valid tetap masuk)
                # Berguna jika ada Typo di CSV
                errors.append(f"Baris {index+2}: Lokasi '{loc_name}' atau Kategori '{cat_name}' tidak ditemukan di Database.")
                continue

            # B. Konversi Tanggal (DD/MM/YYYY -> Python Date Object)
            try:
                # CSV kamu pakai DD/MM/YYYY (contoh: 10/05/2022)
                coll_date = datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                errors.append(f"Baris {index+2}: Format tanggal '{date_str}' salah. Gunakan format DD/MM/YYYY.")
                continue

            # C. Buat Object SQLAlchemy
            record = collection_model.CollectionRecord(
                collection_date=coll_date,
                volume_kg=float(vol),
                location_id=loc_id,
                category_id=cat_id
            )
            new_records.append(record)

        # 6. Simpan ke Database (Bulk Insert)
        if new_records:
            db.bulk_save_objects(new_records)
            db.commit()
        
        # 7. Return Hasil Laporan
        return {
            "message": "Proses import selesai",
            "total_baris_csv": len(df),
            "berhasil_disimpan": len(new_records),
            "gagal": len(errors),
            "contoh_error": errors[:5] # Tampilkan max 5 error pertama agar response tidak kepanjangan
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal memproses file: {str(e)}")