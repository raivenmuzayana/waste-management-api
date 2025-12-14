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

<<<<<<< Updated upstream
@router.post("/", response_model=category_model.WasteCategory, status_code=status.HTTP_201_CREATED)
def create_new_category(
    category: category_model.WasteCategoryCreate, 
    db: Session = Depends(get_db),
    current_admin: user_model.User = Depends(auth_service.get_current_admin_user)
):
    return category_service.create_category(db=db, category=category)
=======

>>>>>>> Stashed changes

@router.get("/", response_model=List[category_model.WasteCategory])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = category_service.get_categories(db, skip=skip, limit=limit)
    return categories

@router.get("/{category_id}", response_model=category_model.WasteCategory)
def read_category(category_id: int, db: Session = Depends(get_db)):
    db_category = category_service.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category