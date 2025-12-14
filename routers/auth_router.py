from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import user_model
from services import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login", response_model=user_model.Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_service.get_user(db, username=form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=user_model.UserInDB, status_code=status.HTTP_201_CREATED)
def create_user(
    user: user_model.UserCreate, 
    db: Session = Depends(get_db),
    # Hanya Admin yang boleh membuat user baru
    current_admin: user_model.User = Depends(auth_service.get_current_admin_user)
):
    db_user = auth_service.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth_service.get_password_hash(user.password)
    db_user = user_model.User(
        username=user.username, 
        hashed_password=hashed_password, 
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me", response_model=user_model.UserInDB)
async def read_users_me(current_user: user_model.User = Depends(auth_service.get_current_user)):
    return current_user