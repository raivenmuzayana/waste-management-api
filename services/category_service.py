from sqlalchemy.orm import Session
from models import category_model
from fastapi import HTTPException, status

# Read
def get_category(db: Session, category_id: int):
    return db.query(category_model.WasteCategory).filter(category_model.WasteCategory.id == category_id).first()

def get_category_by_name(db: Session, name: str):
    return db.query(category_model.WasteCategory).filter(category_model.WasteCategory.name == name).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(category_model.WasteCategory).offset(skip).limit(limit).all()

# Create (Dikembalikan)
def create_category(db: Session, category: category_model.WasteCategoryCreate):
    db_category = get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")
    
    db_category = category_model.WasteCategory(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# Update (Baru)
def update_category(db: Session, category_id: int, category_data: category_model.WasteCategoryUpdate):
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    
    update_data = category_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)

    db.commit()
    db.refresh(db_category)
    return db_category

# Delete (Baru)
def delete_category(db: Session, category_id: int):
    db_category = get_category(db, category_id)
    if not db_category:
        return False
    
    try:
        db.delete(db_category)
        db.commit()
        return True
    except Exception:
        db.rollback()
        # Error biasanya terjadi karena kategori ini masih dipakai di data transaksi (collections)
        raise Exception("Tidak bisa menghapus kategori ini karena sedang digunakan pada data sampah.")