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
)
from app.routers.strategies import get_strategy_by_id

router = APIRouter(prefix="/policies", tags=["policies"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_policy(policy: PolicyCreate, db: Session = Depends(get_db)):
    return add_policy_to_db(policy, db)


def add_policy_to_db(policy: PolicyCreate, db: Session = Depends(get_db)):
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
        alert_id=policy.alert_id,
        strategy_id=policy.strategy_id,
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
async def get_policy(policy_id: str, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: str, policy_update: PolicyUpdate, db: Session = Depends(get_db)
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
    if policy_update.alert_id:
        policy.alert_id = policy_update.alert_id
    if policy_update.strategy_id:
        policy.strategy_id = policy_update.strategy_id
    policy.updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.delete("/{policy_id}", response_model=PolicyResponse)
async def delete_policy(policy_id: str, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")

    db.delete(policy)
    db.commit()
    return policy


@router.get("/generate/{strategy_id}", status_code=status.HTTP_201_CREATED)
async def generate_policy(strategy_id: str, db: Session = Depends(get_db)):
    db_strategy = get_strategy_by_id(strategy_id, db)
    # logic to generate policy
    #

    # dummy data
    policy = PolicyCreate(
        title=db_strategy.short_description,
        content=db_strategy.full_description,
        author="BAH",
        alert_id="1",
        approved=False,
        strategy_id=strategy_id,
    )

    db_policy = add_policy_to_db(policy, db)
    return db_policy


@router.get("/{status_}/alert/{alert_id}", response_model=List[PolicyResponse])
async def get_policies_by_status_by_alert(status_: str, alert_id: str, db: Session = Depends(get_db)):
    approved = True if status_ == "approved" else False
    db_policies = get_policies_by_alert_from_db(alert_id, db)
    if db_policies is None:
        db_policies = []
    return  [db_policy for db_policy in db_policies if db_policy.approved == approved]


@router.get("/alert/{alert_id}", response_model=List[PolicyResponse])
async def get_policies_by_alert(alert_id: str, db: Session = Depends(get_db)):
    return get_policies_by_alert_from_db(alert_id, db)


def get_policies_by_alert_from_db(alert_id: str, db: Session = Depends(get_db)):
    db_policies = db.query(Policy).filter(Policy.alert_id == alert_id).all()
    if db_policies is None:
        db_policies = []
    return db_policies


@router.get("/{status_}/", response_model=List[PolicyResponse])
async def get_policies_by_status(status_: str, db: Session = Depends(get_db)):
    approved = True if status_ == "approved" else False
    db_policies = db.query(Policy).filter(Policy.approved == approved).all()
    if db_policies is None:
        db_policies = []
    return db_policies
