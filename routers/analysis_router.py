from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import analysis_model, user_model
from services import analysis_service, auth_service

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
    # Hanya Admin atau Data Analyst yang boleh mengakses
    dependencies=[Depends(auth_service.get_current_admin_or_analyst_user)]
)

@router.get("/avg-volume/by-location", response_model=List[analysis_model.AvgVolumePerLocation])
def get_avg_volume_by_location(db: Session = Depends(get_db)):
    return analysis_service.get_avg_volume_per_location(db)

@router.get("/avg-volume/by-category", response_model=List[analysis_model.AvgVolumePerCategory])
def get_avg_volume_by_category(db: Session = Depends(get_db)):
    return analysis_service.get_avg_volume_per_category(db)

@router.get("/top-locations", response_model=List[analysis_model.TopLocation])
def get_top_producing_locations(db: Session = Depends(get_db)):
    return analysis_service.get_top_locations(db)

@router.get("/distribution", response_model=List[analysis_model.CategoryDistribution])
def get_waste_distribution(db: Session = Depends(get_db)):
    return analysis_service.get_category_distribution(db)

@router.get("/trend/daily", response_model=List[analysis_model.DailyTrend])
def get_daily_collection_trend(db: Session = Depends(get_db)):
    return analysis_service.get_daily_trend(db)

@router.get("/prediction")
def get_volume_prediction(db: Session = Depends(get_db)):
    return analysis_service.get_prediction(db)