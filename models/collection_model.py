from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from database import Base 

# --- BAGIAN 1: SQLAlchemy Model ---
class CollectionRecord(Base):
    __tablename__ = "collection_records"

    id = Column(Integer, primary_key=True, index=True)
    volume_kg = Column(Float, nullable=False)
    collection_date = Column(DateTime, default=datetime.now)
    
    # PERBAIKAN: Set nullable=False agar wajib diisi
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False) 
    category_id = Column(Integer, ForeignKey("waste_categories.id"), nullable=False)

    # Relasi
    location = relationship("Location", back_populates="collection_records")
    waste_category = relationship("WasteCategory", back_populates="collection_records")

# --- BAGIAN 2: Pydantic Schemas ---
class CollectionCreate(BaseModel):
    volume_kg: float
    location_id: int
    category_id: int
    collection_date: datetime | None = None

    # Konfigurasi Pydantic V2
    model_config = ConfigDict(from_attributes=True)

class CollectionResponse(BaseModel):
    id: int
    volume_kg: float
    collection_date: datetime
    location_id: int
    category_id: int

    # Konfigurasi Pydantic V2
    model_config = ConfigDict(from_attributes=True)