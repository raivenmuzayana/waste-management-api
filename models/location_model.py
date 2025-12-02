from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from database import Base

# --- Model Database (SQLAlchemy) ---
# Nama class ini TETAP 'Location' agar seed.py dan service bisa membacanya
class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    collection_records = relationship("CollectionRecord", back_populates="location")


# --- Skema API (Pydantic) ---

class LocationBase(BaseModel):
    name: str
    latitude: float | None = None
    longitude: float | None = None

class LocationCreate(LocationBase):
    pass

# GANTI NAMA DI SINI (Dulu 'Location' juga, sekarang 'LocationResponse')
class LocationResponse(LocationBase):
    id: int

    class Config:
        from_attributes = True