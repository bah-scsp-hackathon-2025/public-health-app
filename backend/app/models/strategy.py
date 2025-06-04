import uuid
from typing import Optional
from sqlalchemy import Column, String
from pydantic import BaseModel
from app.database import Base


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


class StrategyUpdate(BaseModel):
    short_description:  Optional[str]
    full_description:  Optional[str]
    alert_id: Optional[str]


class StrategyResponse(StrategyCreate):
    id: str
