from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.policy import Policy

router = APIRouter(prefix="/policies", tags=["policies"])


class PolicyCreate(BaseModel):
    title: str
    content: str
    author: str
    approved: bool


class PolicyUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    approved: Optional[bool] = None


class PolicyResponse(PolicyCreate):
    id: int


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
async def update_policy(policy_id: int, policy_update: PolicyUpdate, db: Session = Depends(get_db)):
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
