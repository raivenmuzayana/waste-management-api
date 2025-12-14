from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from config import settings
from models import user_model
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import get_db

# Konteks untuk hashing password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Skema keamanan OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    return db.query(user_model.User).filter(user_model.User.username == username).first()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = user_model.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# --- Dependencies untuk Cek Role ---

def get_current_admin_user(current_user: user_model.User = Depends(get_current_user)):
    if current_user.role != user_model.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Operation not permitted: requires admin privileges"
        )
    return current_user

def get_current_admin_or_analyst_user(current_user: user_model.User = Depends(get_current_user)):
    if current_user.role not in (user_model.UserRole.ADMIN, user_model.UserRole.DATA_ANALYST):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Operation not permitted: requires admin or analyst privileges"
        )
    return current_user