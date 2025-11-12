from sqlalchemy.orm import Session
from models import category_model
from fastapi import HTTPException, status

def get_category(db: Session, category_id: int):
    return db.query(category_model.WasteCategory).filter(category_model.WasteCategory.id == category_id).first()

def get_category_by_name(db: Session, name: str):
    return db.query(category_model.WasteCategory).filter(category_model.WasteCategory.name == name).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(category_model.WasteCategory).offset(skip).limit(limit).all()

def create_category(db: Session, category: category_model.WasteCategoryCreate):
    db_category = get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")
    
    db_category = category_model.WasteCategory(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category