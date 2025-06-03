import uuid
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel
from app.database import Base


class Policy(Base):
    __tablename__ = "policies"

    id = Column(String, default=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    content = Column(String)
    approved = Column(Boolean)
    created = Column(String)
    updated = Column(String)
    alert_id = Column(String)


class PolicyCreate(BaseModel):
    title: str
    content: str
    author: str
    approved: bool
    alert_id: str


class PolicyUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    approved: Optional[bool] = None
    alert_id: Optional[str] = None


class PolicyResponse(PolicyCreate):
    id: str


class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(String, default=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    short_description = Column(String)
    full_description = Column(String)
    alert_id = Column(String)


class StrategyCreate(BaseModel):
    short_description: str
    full_description: str
    alert_id: str


class StrategyResponse(StrategyCreate):
    id: str
