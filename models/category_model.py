from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from database import Base

# --- Model Database (SQLAlchemy) ---

class WasteCategory(Base):
    __tablename__ = "waste_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)

    # Relasi: Satu kategori punya banyak catatan pengumpulan
    collection_records = relationship("CollectionRecord", back_populates="waste_category")


# --- Skema API (Pydantic) ---

class WasteCategoryBase(BaseModel):
    name: str
    description: str | None = None

class WasteCategoryCreate(WasteCategoryBase):
    pass

class WasteCategory(WasteCategoryBase):
    id: int

    class Config:
        from_attributes = True