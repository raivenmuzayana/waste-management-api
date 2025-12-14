from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import category_model, user_model
from services import category_service, auth_service

router = APIRouter(
    prefix="/categories",
    tags=["Waste Categories"],
    dependencies=[Depends(auth_service.get_current_user)]
)

@router.get("/", response_model=List[category_model.WasteCategoryResponse])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = category_service.get_categories(db, skip=skip, limit=limit)
    return categories

@router.get("/{category_id}", response_model=category_model.WasteCategoryResponse)
def read_category(category_id: int, db: Session = Depends(get_db)):
    db_category = category_service.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category