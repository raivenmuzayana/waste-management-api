from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine  # Ambil engine dari database.py
import pandas as pd
import io

router = APIRouter(
    prefix="/import",
    tags=["Import Data"]
)

@router.post("/csv-to-table")
async def upload_csv_as_table(
    table_name: str, 
    file: UploadFile = File(...)
):
    """
    Mengunggah CSV dan menyimpannya sebagai tabel baru di database.
    """
    # 1. Validasi tipe file
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File harus berformat CSV")

    try:
        # 2. Baca file CSV menggunakan Pandas
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        # 3. Simpan DataFrame ke Database sebagai Tabel Baru
        # 'if_exists="replace"' akan menimpa tabel jika nama sudah ada
        # 'if_exists="fail"' akan error jika tabel sudah ada
        # 'if_exists="append"' akan menambah data jika tabel sudah ada
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

        return {
            "message": f"File CSV berhasil diimpor ke tabel '{table_name}'",
            "rows_inserted": len(df),
            "columns": list(df.columns)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses CSV: {str(e)}")