from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import category_model, user_model
from services import category_service, auth_service

router = APIRouter(
    prefix="/categories",
    tags=["Waste Categories"],
    # Semua user (termasuk Analyst) boleh BACA (GET)
    dependencies=[Depends(auth_service.get_current_user)]
)

# 1. READ ALL
@router.get("/", response_model=List[category_model.WasteCategoryResponse])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return category_service.get_categories(db, skip=skip, limit=limit)

# 2. READ ONE
@router.get("/{category_id}", response_model=category_model.WasteCategoryResponse)
def read_category(category_id: int, db: Session = Depends(get_db)):
    db_category = category_service.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

# 3. CREATE (Hanya Admin)
@router.post("/", response_model=category_model.WasteCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_new_category(
    category: category_model.WasteCategoryCreate, 
    db: Session = Depends(get_db),
    current_admin: user_model.User = Depends(auth_service.get_current_admin_user)
):
    return category_service.create_category(db=db, category=category)

# 4. UPDATE (Hanya Admin)
@router.put("/{category_id}", response_model=category_model.WasteCategoryResponse)
def update_category_data(
    category_id: int,
    category_data: category_model.WasteCategoryUpdate,
    db: Session = Depends(get_db),
    current_admin: user_model.User = Depends(auth_service.get_current_admin_user)
):
    updated_category = category_service.update_category(db, category_id, category_data)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category

# 5. DELETE (Hanya Admin)
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_admin: user_model.User = Depends(auth_service.get_current_admin_user)
):
    try:
        success = category_service.delete_category(db, category_id)
        if not success:
            raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return None