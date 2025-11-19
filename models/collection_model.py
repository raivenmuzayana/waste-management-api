from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from database import Base  # Pastikan file database.py sudah dibuat oleh Orang 1

# --- BAGIAN 1: SQLAlchemy Model (Tabel Database) ---
class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    volume = Column(Float, nullable=False) # Berat/Volume sampah
    collection_date = Column(DateTime, default=datetime.now) # Waktu pengambilan
    
    # Foreign Keys (Menghubungkan ke tabel Lokasi dan Kategori)
    location_id = Column(Integer, ForeignKey("locations.id")) 
    category_id = Column(Integer, ForeignKey("categories.id"))

    # Relationship (Opsional, agar bisa memanggil data detail)
    # location = relationship("Location", back_populates="collections")
    # category = relationship("Category", back_populates="collections")

# --- BAGIAN 2: Pydantic Schemas (Validasi Request/Response) ---

# Schema untuk input data (Create)
class CollectionCreate(BaseModel):
    volume: float
    location_id: int
    category_id: int
    # collection_date opsional, jika kosong pakai waktu sekarang

# Schema untuk output data (Response)
class CollectionResponse(BaseModel):
    id: int
    volume: float
    collection_date: datetime
    location_id: int
    category_id: int

    class Config:
        from_attributes = True # Agar kompatibel dengan ORM SQLAlchemy