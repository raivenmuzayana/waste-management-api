from sqlalchemy import Column, Integer, String, Enum as SAEnum
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from database import Base
import enum

# --- Model Database (SQLAlchemy) ---

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DATA_ANALYST = "data_analyst"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.DATA_ANALYST)

# --- Skema API (Pydantic) ---

class UserCreate(BaseModel):
    username: str
    password: str
    role: UserRole = UserRole.DATA_ANALYST

class UserInDB(BaseModel):
    id: int
    username: str
    role: UserRole

    class Config:
        from_attributes = True # Dulu orm_mode=True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None