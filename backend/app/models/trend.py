import uuid
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, String
from app.database import Base


class Trend(Base):
    __tablename__ = "trends"

    id = Column(String, default=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    data = Column(String)


class TrendCreate(BaseModel):
    data: str


class TrendUpdate(BaseModel):
    data: Optional[str] = None


class TrendResponse(TrendCreate):
    id: str
