from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.strategy import (
    Strategy,
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
)
from app.routers.alerts import get_alert_by_id

router = APIRouter(prefix="/strategies", tags=["strategies"])


@router.get("/generate/{alert_id}", response_model=List[StrategyResponse])
async def generate_strategies(alert_id: str, db: Session = Depends(get_db)):
    alert = get_alert_by_id(alert_id, db)
    # logic to generate strategy
    #

    # dummy data
    strategies = [
        StrategyCreate(
            short_description=alert.name + " Strategy 1",
            full_description=alert.description,
            alert_id=alert_id,
        ),
        StrategyCreate(
            short_description=alert.name + " Strategy 2",
            full_description=alert.description,
            alert_id=alert_id,
        ),
        StrategyCreate(
            short_description=alert.name + " Strategy 3",
            full_description=alert.description,
            alert_id=alert_id,
        ),
    ]

    db_strategies = [add_strategy_to_db(strategy, alert_id, db) for strategy in strategies]
    return db_strategies


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: str, db: Session = Depends(get_db)):
    return get_strategy_by_id(strategy_id, db)


def get_strategy_by_id(strategy_id: str, db: Session = Depends(get_db)):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.get("/alert/{alert_id}", response_model=List[StrategyResponse])
async def get_strategies_by_alert(alert_id: str, db: Session = Depends(get_db)):
    strategies = db.query(Strategy).filter(Strategy.alert_id == alert_id).all()
    if strategies is None:
        strategies = []
    return strategies


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    return add_strategy_to_db(strategy, strategy.alert_id, db)


def add_strategy_to_db(strategy: StrategyCreate, alert_id: str, db: Session = Depends(get_db)):
    db_strategy = Strategy(
        short_description=strategy.short_description,
        full_description=strategy.full_description,
        alert_id=alert_id,
    )
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(strategy_id: str, strategy_update: StrategyUpdate, db: Session = Depends(get_db)):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")

    if strategy_update.short_description:
        strategy.short_description = strategy_update.short_description
    if strategy_update.full_description:
        strategy.full_description = strategy_update.full_description

    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return strategy


@router.delete("/{strategy_id}", response_model=StrategyResponse)
async def delete_strategy(strategy_id: str, db: Session = Depends(get_db)):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")

    db.delete(strategy)
    db.commit()
    return strategy
