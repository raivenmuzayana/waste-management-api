from pydantic import BaseModel
from datetime import date

class AvgVolumePerLocation(BaseModel):
    location_name: str
    average_volume: float

class AvgVolumePerCategory(BaseModel):
    category_name: str
    average_volume: float

class TopLocation(BaseModel):
    location_name: str
    total_volume: float

class CategoryDistribution(BaseModel):
    category_name: str
    total_volume: float
    percentage: float

class DailyTrend(BaseModel):
    collection_date: date
    total_volume: float

    # Tambahkan Config ini agar contoh di Swagger UI lebih masuk akal
    class Config:
        json_schema_extra = {
            "example": {
                "collection_date": "2023-10-27",
                "total_volume": 1337.42
            }
        }