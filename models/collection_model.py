# file: models/collection_model.py
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from datetime import datetime
from database import Base 

# --- BAGIAN 1: SQLAlchemy Model ---
class CollectionRecord(Base):  # Ganti nama class jadi CollectionRecord
    __tablename__ = "collection_records" # Nama tabel di database

    id = Column(Integer, primary_key=True, index=True)
    volume_kg = Column(Float, nullable=False) # Konsisten menggunakan volume_kg
    collection_date = Column(DateTime, default=datetime.now)
    
    # Foreign Keys
    location_id = Column(Integer, ForeignKey("locations.id")) 
    category_id = Column(Integer, ForeignKey("waste_categories.id")) # Sesuai nama tabel kategori

    # Relasi balik (agar bisa akses detail lokasi/kategori dari data sampah)
    location = relationship("Location", back_populates="collection_records")
    waste_category = relationship("WasteCategory", back_populates="collection_records")

# --- BAGIAN 2: Pydantic Schemas ---
class CollectionCreate(BaseModel):
    volume_kg: float = Field(..., gt=0, description="Volume harus lebih besar dari 0")
    category_id: int
    collection_date: datetime | None = None

class CollectionResponse(BaseModel):
    id: int
    volume_kg: float
    collection_date: datetime
    location_id: int
    category_id: int

    class Config:
        from_attributes = True