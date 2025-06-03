from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.alert import Alert

router = APIRouter(prefix="/alerts", tags=["alerts"])


class AlertModel(BaseModel):
    name: str
    description: str
    risk_score: int
    risk_reason: str
    location: str


class AlertResponse(AlertModel):
    id: int


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_alert(alert: AlertModel, db: Session = Depends(get_db)):
    # Check if alert already exists
    db_alert = db.query(Alert).filter(Alert.name == alert.name).first()
    if db_alert:
        raise HTTPException(status_code=400, detail="Alert already exists")

    db_alert = Alert(
        name=alert.name,
        description=alert.description,
        risk_score=alert.risk_score,
        risk_reason=alert.risk_reason,
        location=alert.location,
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = db.query(Alert).offset(skip).limit(limit).all()
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
