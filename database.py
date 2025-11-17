from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Membuat engine SQLAlchemy untuk MySQL
engine = create_engine(
    settings.DATABASE_URL
)

# Membuat SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class untuk model ORM kita
Base = declarative_base()

# Dependency untuk mendapatkan DB session di API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()