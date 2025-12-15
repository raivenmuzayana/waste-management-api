from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from database import get_db
from models import analysis_model, user_model, location_model, category_model
from services import analysis_service, auth_service
from datetime import date


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
def get_daily_collection_trend(
    # Tambahkan dua parameter ini:
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    #Format tanggal: YYYY-MM-DD 
    return analysis_service.get_daily_trend(db, start_date=start_date, end_date=end_date)


@router.get("/top-days", response_model=List[analysis_model.TopProducingDay])
def get_top_producing_days_analysis(db: Session = Depends(get_db)):
    return analysis_service.get_top_producing_days(db)

@router.get("/prediction", response_model=Dict[str, Any]) 
def get_volume_prediction(db: Session = Depends(get_db)):
    # Linear Regression.
    return analysis_service.get_prediction(db)

@router.get("/route/optimize", response_model=List[location_model.LocationResponse])
def get_optimized_waste_collection_route(db: Session = Depends(get_db)):
    #  Traveling Salesperson Problem Nearest Neighbor
    
    return analysis_service.get_optimized_route(db)

@router.get("/heatmap/location-category", response_model=List[analysis_model.PivotData])
def get_heatmap_data(db: Session = Depends(get_db)):
    return analysis_service.get_location_category_pivot(db)

@router.get("/summary", response_model=analysis_model.DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):

    return analysis_service.get_dashboard_summary(db)

