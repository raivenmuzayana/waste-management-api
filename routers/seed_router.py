from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services import seed_service  # <--- Import Service Baru

router = APIRouter(
    prefix="/seed",
    tags=["Seed Data (Generator)"]
)

@router.post("/generate-dummy-data")
def generate_data(jumlah_data: int = 100, db: Session = Depends(get_db)):
    try:
        # Panggil logika dari satu sumber yang sama
        result = seed_service.execute_seeding(db=db, total_data=jumlah_data)
        
        return {
            "message": "Sukses generate data dummy",
            "detail": result
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal generate data: {str(e)}")