from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from database import Base

# --- Model Database (SQLAlchemy) ---

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Relasi: Satu lokasi punya banyak catatan pengumpulan
    collection_records = relationship("CollectionRecord", back_populates="location")


# --- Skema API (Pydantic) ---

class LocationBase(BaseModel):
    name: str
    latitude: float | None = None
    longitude: float | None = None

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int

    class Config:
        from_attributes = True