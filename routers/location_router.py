from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import location_model, user_model
from services import location_service, auth_service
from models.location_model import LocationResponse, LocationCreate, LocationUpdate

router = APIRouter(
    prefix="/locations",
    tags=["Locations"],
    dependencies=[Depends(auth_service.get_current_user)]
)

# Perhatikan: response_model sekarang pakai LocationResponse
@router.post("/", response_model=location_model.LocationResponse, status_code=status.HTTP_201_CREATED)
def create_new_location(
    location: location_model.LocationCreate, 
    db: Session = Depends(get_db),
    current_admin: user_model.User = Depends(auth_service.get_current_admin_user)
):
    return location_service.create_location(db=db, location=location)

@router.get("/", response_model=List[location_model.LocationResponse])
def read_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    locations = location_service.get_locations(db, skip=skip, limit=limit)
    return locations

@router.get("/{location_id}", response_model=location_model.LocationResponse)
def read_location(location_id: int, db: Session = Depends(get_db)):
    db_location = location_service.get_location(db, location_id=location_id)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return db_location

@router.put("/{location_id}", response_model=LocationResponse)
def update_location_data(
    location_id: int, 
    location_data: LocationUpdate, 
    db: Session = Depends(get_db),
    current_admin: user_model.User = Depends(auth_service.get_current_admin_user) # Hanya Admin boleh edit
):
    updated_location = location_service.update_location(db, location_id, location_data)
    if not updated_location:
        raise HTTPException(status_code=404, detail="Location not found")
    return updated_location

@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_location(
    location_id: int, 
    db: Session = Depends(get_db),
    current_admin: user_model.User = Depends(auth_service.get_current_admin_user) # Hanya Admin boleh hapus
):
    try:
        success = location_service.delete_location(db, location_id)
        if not success:
            raise HTTPException(status_code=404, detail="Location not found")
    except Exception as e:
        # Menangkap error jika lokasi masih dipakai di data sampah
        raise HTTPException(status_code=400, detail=str(e))
    return None