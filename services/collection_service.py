# file: services/collection_service.py
from sqlalchemy.orm import Session
from models.collection_model import CollectionRecord, CollectionCreate

def create_collection(db: Session, collection: CollectionCreate):
    # Jika collection_date tidak diisi, biarkan default (now) dari database/model
    data = collection.dict(exclude_unset=True)
    db_collection = CollectionRecord(**data)
    
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return db_collection

def get_collections(db: Session, skip: int = 0, limit: int = 100):
    return db.query(CollectionRecord).offset(skip).limit(limit).all()

def get_collection_by_id(db: Session, collection_id: int):
    return db.query(CollectionRecord).filter(CollectionRecord.id == collection_id).first()

def delete_collection(db: Session, collection_id: int):
    db_collection = db.query(CollectionRecord).filter(CollectionRecord.id == collection_id).first()
    if db_collection:
        db.delete(db_collection)
        db.commit()
        return True
    return False