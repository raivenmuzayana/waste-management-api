from database import SessionLocal, engine, Base
from services import seed_service # <--- Import Service Baru

# Pastikan tabel ada
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    try:
        print("Mulai generate data dummy...")
        
        JUMLAH_DATA = 500
        
        # Panggil fungsi yang SAMA dengan yang dipakai di Router
        result = seed_service.execute_seeding(db=db, total_data=JUMLAH_DATA)
        
        print(f"🎉 Selesai! Detail: {result}")

    except Exception as e:
        print(f"❌ Terjadi error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_waste_data()
    seed_wine_data()
    print("=== SELESAI ===")