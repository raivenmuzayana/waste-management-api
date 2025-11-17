from fastapi import FastAPI, Depends
from database import engine, Base, get_db
from models import user_model, location_model, category_model, collection_model
from routers import auth_router, location_router, category_router, collection_router, analysis_router
from sqlalchemy.orm import Session
from services import auth_service # untuk initial admin

# Membuat semua tabel di database (jika belum ada)
# Ini akan membuat tabel user, location, waste_category, dan collection_record
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Waste Management Monitoring System API",
    description="API untuk memantau volume dan jenis sampah.",
    version="1.0.0"
)

# --- Include Routers ---
app.include_router(auth_router.router)
app.include_router(location_router.router)
app.include_router(category_router.router)
app.include_router(collection_router.router)
app.include_router(analysis_router.router)

# Endpoint root untuk cek status
@app.get("/")
def read_root():
    return {"message": "Waste Management Monitoring System API"}

# --- Bonus: Buat Admin User Pertama Kali (jika belum ada) ---
@app.on_event("startup")
def create_first_admin():
    db = next(get_db())
    admin = auth_service.get_user(db, "admin")
    if not admin:
        print("Creating first admin user (username: admin, password: admin)...")
        admin_user = user_model.UserCreate(
            username="admin",
            password="admin", # Ganti ini di produksi!
            role=user_model.UserRole.ADMIN
        )
        hashed_password = auth_service.get_password_hash(admin_user.password)
        db_admin = user_model.User(
            username=admin_user.username,
            hashed_password=hashed_password,
            role=admin_user.role
        )
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
        print("First admin user created.")
    db.close()