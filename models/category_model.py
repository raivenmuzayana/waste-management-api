from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict
from database import Base

# --- Model Database (SQLAlchemy) ---
class WasteCategory(Base):
    __tablename__ = "waste_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)

    collection_records = relationship("CollectionRecord", back_populates="waste_category")


# --- Skema API (Pydantic) ---

class WasteCategoryBase(BaseModel):
    name: str
    description: str | None = None

# 1. CREATE (Dikembalikan)
class WasteCategoryCreate(WasteCategoryBase):
    pass

# 2. UPDATE (Baru - semua field opsional)
class WasteCategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

# 3. RESPONSE
class WasteCategoryResponse(WasteCategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)