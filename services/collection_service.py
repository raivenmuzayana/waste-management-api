from sqlalchemy.orm import Session
from models.collection_model import CollectionRecord, CollectionCreate, CollectionUpdate

def create_collection(db: Session, collection: CollectionCreate):
    # PERBAIKAN: Gunakan model_dump() menggantikan .dict()
    # exclude_unset=True dihapus untuk location_id/category_id agar pasti terkirim
    # Kita handle collection_date manual jika None
    
    data = collection.model_dump()
    
    # Jika collection_date tidak diisi (None), hapus dari dict agar SQLAlchemy pakai default datetime.now()
    if data.get("collection_date") is None:
        del data["collection_date"]

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

def update_collection(db: Session, collection_id: int, collection_data: CollectionUpdate):
    db_collection = db.query(CollectionRecord).filter(CollectionRecord.id == collection_id).first()
    if not db_collection:
        return None

    update_data = collection_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_collection, key, value)

    db.commit()
    db.refresh(db_collection)
    return db_collection