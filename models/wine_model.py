from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import declarative_base

WineBase = declarative_base()

class Wine(WineBase):
    __tablename__ = "wines"

    id = Column(Integer, primary_key=True, index=True)
    fixed_acidity = Column(Float)
    volatile_acidity = Column(Float)
    citric_acid = Column(Float)
    residual_sugar = Column(Float)
    chlorides = Column(Float)
    free_sulfur_dioxide = Column(Float)
    total_sulfur_dioxide = Column(Float)
    density = Column(Float)
    pH = Column(Float)
    sulphates = Column(Float)
    alcohol = Column(Float)
    quality = Column(Integer)