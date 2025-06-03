from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.policy import (
    Policy,
    PolicyCreate,
    PolicyUpdate,
    PolicyResponse,
    Strategy,
    StrategyCreate,
    StrategyResponse,
)
from app.routers.alerts import get_alert

router = APIRouter(prefix="/policies", tags=["policies"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_policy(policy: PolicyCreate, db: Session = Depends(get_db)):
    # Check if policy already exists
    db_policy = db.query(Policy).filter(Policy.title == policy.title).first()
    if db_policy:
        raise HTTPException(status_code=400, detail="Policy already exists")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db_policy = Policy(
        title=policy.title,
        content=policy.content,
        author=policy.author,
        approved=policy.approved,
        created=current_time,
        updated=current_time,
    )
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy


@router.get("/", response_model=List[PolicyResponse])
async def get_policies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    policies = db.query(Policy).offset(skip).limit(limit).all()
    return policies


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: int, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: int, policy_update: PolicyUpdate, db: Session = Depends(get_db)
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")

    if policy_update.title:
        policy.title = policy_update.title
    if policy_update.content:
        policy.content = policy_update.content
    if policy_update.author:
        policy.author = policy_update.author
    if policy_update.approved:
        policy.approved = policy_update.approved
    policy.updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.delete("/{policy_id}", response_model=PolicyResponse)
async def delete_policy(policy_id: int, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")

    db.delete(policy)
    db.commit()
    return policy


@router.post("/generate/{alert_id}", response_model=List[StrategyResponse])
async def generate_strategies(alert_id: int, db: Session = Depends(get_db)):
    alert = get_alert(alert_id, db)
    # logic to generate strategy
    #
    strategies = []

    db_strategies = [_create_strategy(strategy, alert_id) for strategy in strategies]
    return db_strategies


@router.get("/strategy/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


def _create_strategy(strategy: StrategyCreate, alert_id: int, db: Session = Depends(get_db)):
    db_strategy = Strategy(
        short_description=strategy.short_description,
        full_description=strategy.full_description,
        alert_id=alert_id,
    )
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy


@router.post("/draft/{strategy_id}", status_code=status.HTTP_201_CREATED)
async def draft_policy(strategy_id: int, db: Session = Depends(get_db)):
    strategy = get_strategy(strategy_id, db)
    # logic to generate policy
    #
    policy = {}

    db_policy = create_policy(policy, db)
    return db_policy


@router.get("/approved/{alert_id}", response_model=PolicyResponse)
async def get_approved_policies(alert_id: int, db: Session = Depends(get_db)):
    db_policies = db.query(Policy).filter((Policy.alert_id == alert_id & Policy.approved == True)).all()
    if db_policies is None:
        raise HTTPException(status_code=404, detail="Policies not found")
    return db_policies
