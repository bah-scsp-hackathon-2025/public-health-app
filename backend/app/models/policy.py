from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    content = Column(String)
    approved = Column(Boolean)
    created = Column(String)
    updated = Column(String)


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


class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    short_description = Column(String)
    full_description = Column(String)


class StrategyCreate(BaseModel):
    short_description: str
    full_description: str


class StrategyResponse(StrategyCreate):
    id: int
