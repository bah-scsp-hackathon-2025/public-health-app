from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.database import get_db
from app.models.alert import Alert, AlertCreate, AlertUpdate, AlertResponse

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    db_alert = db.query(Alert).filter(Alert.name == alert.name).first()
    if db_alert:
        raise HTTPException(status_code=400, detail="Alert already exists")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db_alert = Alert(
        name=alert.name,
        description=alert.description,
        risk_score=alert.risk_score,
        risk_reason=alert.risk_reason,
        location=alert.location,
        latitude=alert.latitude,
        longitude=alert.longitude,
        created=current_time,
        updated=current_time,
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(db: Session = Depends(get_db)):
    return get_all_alerts(db=db)


def get_all_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = db.query(Alert).offset(skip).limit(limit).all()
    return alerts


@router.get("/state/{location}", response_model=List[AlertResponse])
async def get_alerts(location: str, db: Session = Depends(get_db)):
    location = location.replace("_", " ").lower()
    alerts = db.query(Alert).filter(func.lower(Alert.location) == location).all()
    if alerts is None:
        alerts = []
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str, db: Session = Depends(get_db)):
    return get_alert_by_id(alert_id, db)


def get_alert_by_id(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(alert_id: str, alert_update: AlertUpdate, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    if alert_update.name:
        alert.name = alert_update.name
    if alert_update.description:
        alert.description = alert_update.description
    if alert_update.risk_score:
        alert.risk_score = alert_update.risk_score
    if alert_update.risk_reason:
        alert.risk_reason = alert_update.risk_reason
    if alert_update.location:
        alert.location = alert_update.location
    if alert_update.latitude:
        alert.latitude = alert_update.latitude
    if alert_update.longitude:
        alert.longitude = alert_update.longitude
    alert.updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/{alert_id}", response_model=AlertResponse)
async def delete_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.delete(alert)
    db.commit()
    return alert
