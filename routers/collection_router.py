from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from services import collection_service, auth_service
from models import user_model
from models.collection_model import CollectionResponse, CollectionCreate, CollectionUpdate

router = APIRouter(
    prefix="/collections",
    tags=["Collections"],
    # Level Router: Minimal User harus Login (Bisa Admin, Bisa Analyst)
    dependencies=[Depends(auth_service.get_current_user)] 
)

# POST: Tambah Data (Analyst BOLEH input data lapangan)
@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection_item(collection: CollectionCreate, db: Session = Depends(get_db)):
    return collection_service.create_collection(db=db, collection=collection)

# GET: Ambil Semua Data (Analyst BOLEH lihat)
@router.get("/", response_model=List[CollectionResponse])
def read_collections(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return collection_service.get_collections(db, skip=skip, limit=limit)

# GET: Ambil Data by ID (Analyst BOLEH lihat)
@router.get("/{collection_id}", response_model=CollectionResponse)
def read_collection(collection_id: int, db: Session = Depends(get_db)):
    db_collection = collection_service.get_collection_by_id(db, collection_id=collection_id)
    if db_collection is None:
        raise HTTPException(status_code=404, detail="Catatan tidak ditemukan")
    return db_collection

# DELETE: Hapus Data (HANYA ADMIN)
@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_collection(
    collection_id: int, 
    db: Session = Depends(get_db),
    # UBAH DISINI: Kunci khusus Admin
    current_admin: user_model.User = Depends(auth_service.get_current_admin_user)
):
    success = collection_service.delete_collection(db, collection_id=collection_id)
    if not success:
        raise HTTPException(status_code=404, detail="Catatan tidak ditemukan")
    return None

# PUT: Edit Data (HANYA ADMIN)
@router.put("/{collection_id}", response_model=CollectionResponse)
def update_collection_item(
    collection_id: int, 
    collection_data: CollectionUpdate, 
    db: Session = Depends(get_db),
    # UBAH DISINI: Kunci khusus Admin
    current_admin: user_model.User = Depends(auth_service.get_current_admin_user) 
):
    updated_collection = collection_service.update_collection(db, collection_id, collection_data)
    if not updated_collection:
        raise HTTPException(status_code=404, detail="Catatan tidak ditemukan")
    return updated_collection