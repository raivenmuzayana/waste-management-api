from sqlalchemy.orm import Session
from models.collection_model import Collection, CollectionCreate

# Fungsi Create (Menambah Catatan)
def create_collection(db: Session, collection: CollectionCreate):
    db_collection = Collection(
        volume=collection.volume,
        location_id=collection.location_id,
        category_id=collection.category_id
    )
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return db_collection

# Fungsi Read All (Melihat semua catatan)
def get_collections(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Collection).offset(skip).limit(limit).all()

# Fungsi Read One (Melihat satu catatan berdasarkan ID)
def get_collection_by_id(db: Session, collection_id: int):
    return db.query(Collection).filter(Collection.id == collection_id).first()

# Fungsi Delete (Menghapus catatan)
def delete_collection(db: Session, collection_id: int):
    db_collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if db_collection:
        db.delete(db_collection)
        db.commit()
        return True
    return False