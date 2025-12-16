from sqlalchemy.orm import Session
from models.collection_model import CollectionRecord, CollectionCreate, CollectionUpdate

def create_collection(db: Session, collection: CollectionCreate):
    # Konversi ke dictionary
    data = collection.model_dump()
    
    # Jika collection_date tidak diisi (None), hapus key-nya 
    # agar SQLAlchemy menggunakan default value (datetime.now) dari model database
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

    # exclude_unset=True penting agar field yang tidak dikirim user tidak menimpa data lama dengan None
    update_data = collection_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_collection, key, value)

    db.commit()
    db.refresh(db_collection)
    return db_collection