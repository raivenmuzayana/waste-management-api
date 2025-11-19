from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db # Import dari Orang 1
from services import collection_service
from models.collection_model import CollectionCreate, CollectionResponse

router = APIRouter(
    prefix="/collections",
    tags=["Collections"]
)

# POST: Tambah Data
@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection_item(collection: CollectionCreate, db: Session = Depends(get_db)):
    # Tips: Nanti bisa tambahkan validasi apakah location_id dan category_id valid
    return collection_service.create_collection(db=db, collection=collection)

# GET: Ambil Semua Data
@router.get("/", response_model=List[CollectionResponse])
def read_collections(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return collection_service.get_collections(db, skip=skip, limit=limit)

# GET: Ambil Data by ID
@router.get("/{collection_id}", response_model=CollectionResponse)
def read_collection(collection_id: int, db: Session = Depends(get_db)):
    db_collection = collection_service.get_collection_by_id(db, collection_id=collection_id)
    if db_collection is None:
        raise HTTPException(status_code=404, detail="Catatan tidak ditemukan")
    return db_collection

# DELETE: Hapus Data
@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_collection(collection_id: int, db: Session = Depends(get_db)):
    success = collection_service.delete_collection(db, collection_id=collection_id)
    if not success:
        raise HTTPException(status_code=404, detail="Catatan tidak ditemukan")
    return None