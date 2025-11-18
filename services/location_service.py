from sqlalchemy.orm import Session
from models import location_model
from fastapi import HTTPException, status

def get_location(db: Session, location_id: int):
    return db.query(location_model.Location).filter(location_model.Location.id == location_id).first()

def get_location_by_name(db: Session, name: str):
    return db.query(location_model.Location).filter(location_model.Location.name == name).first()

def get_locations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(location_model.Location).offset(skip).limit(limit).all()

def create_location(db: Session, location: location_model.LocationCreate):
    db_location = get_location_by_name(db, name=location.name)
    if db_location:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Location name already exists")
    
    db_location = location_model.Location(**location.model_dump())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location