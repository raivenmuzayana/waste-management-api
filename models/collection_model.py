from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# ==========================================
# BAGIAN 1: SQLAlchemy Model (Database)
# ==========================================
class CollectionRecord(Base):
    __tablename__ = "collection_records"

    id = Column(Integer, primary_key=True, index=True)
    volume_kg = Column(Float, nullable=False)
    collection_date = Column(DateTime, default=datetime.now)
    
    # Foreign Keys
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False) 
    category_id = Column(Integer, ForeignKey("waste_categories.id"), nullable=False)

    # Relasi (PENTING untuk joinedload)
    location = relationship("Location", back_populates="collection_records")
    waste_category = relationship("WasteCategory", back_populates="collection_records")


# ==========================================
# BAGIAN 2: Pydantic Schemas (API Response)
# ==========================================

# Schema Mini untuk Nested Object
class LocationLite(BaseModel):
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)

class CategoryLite(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

# Schema untuk Input (Create)
class CollectionCreate(BaseModel):
    volume_kg: float
    location_id: int
    category_id: int
    collection_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    # --- Tambahkan Class ini ---
class CollectionUpdate(BaseModel):
    volume_kg: float | None = None
    collection_date: datetime | None = None
    location_id: int | None = None
    category_id: int | None = None

# Schema untuk Output (Response)
class CollectionResponse(BaseModel):
    id: int
    volume_kg: float
    collection_date: datetime
    
    # Nested Object (Bukan cuma ID)
    location: LocationLite
    waste_category: CategoryLite

    model_config = ConfigDict(from_attributes=True)