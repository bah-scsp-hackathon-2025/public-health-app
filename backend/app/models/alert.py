from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)
    risk_score = Column(Integer)
    risk_reason = Column(String)
    location = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    created = Column(String)
    updated = Column(String)


class AlertCreate(BaseModel):
    name: str
    description: str
    risk_score: int
    risk_reason: str
    location: str
    latitude: str
    longitude: str


class AlertUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    risk_score: Optional[int] = None
    risk_reason: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None


class AlertResponse(AlertCreate):
    id: int
