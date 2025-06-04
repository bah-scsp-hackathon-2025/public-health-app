from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.trend import Trend, TrendCreate, TrendUpdate, TrendResponse

router = APIRouter(prefix="/trends", tags=["trends"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_summmary(trend: TrendCreate, db: Session = Depends(get_db)):
    db_trend = db.query(Trend).filter(Trend.data == trend.data).first()
    if db_trend:
        raise HTTPException(status_code=400, detail="Trend already exists")

    db_trend = Trend(
        data=trend.data,
    )
    db.add(db_trend)
    db.commit()
    db.refresh(db_trend)
    return db_trend


@router.get("/", response_model=List[TrendResponse])
async def get_trends(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    trends = db.query(Trend).offset(skip).limit(limit).all()
    return trends


@router.get("/{trend_id}", response_model=TrendResponse)
async def get_trend(trend_id: str, db: Session = Depends(get_db)):
    trend = db.query(Trend).filter(Trend.id == trend_id).first()
    if trend is None:
        raise HTTPException(status_code=404, detail="Trend not found")
    return trend


@router.put("/{trend_id}", response_model=TrendResponse)
async def update_trend(trend_id: str, trend_update: TrendUpdate, db: Session = Depends(get_db)):
    trend = db.query(Trend).filter(Trend.id == trend_id).first()
    if trend is None:
        raise HTTPException(status_code=404, detail="Trend not found")

    if trend_update.data:
        trend.data = trend_update.data

    db.add(trend)
    db.commit()
    db.refresh(trend)
    return trend


@router.delete("/{trend_id}", response_model=TrendResponse)
async def delete_trend(trend_id: str, db: Session = Depends(get_db)):
    trend = db.query(Trend).filter(Trend.id == trend_id).first()
    if trend is None:
        raise HTTPException(status_code=404, detail="Trend not found")

    db.delete(trend)
    db.commit()
    return trend
