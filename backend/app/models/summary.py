import uuid
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, String
from app.database import Base


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(String, default=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    description = Column(String)


class SummaryCreate(BaseModel):
    description: str


class SummaryUpdate(BaseModel):
    description: Optional[str] = None


class SummaryResponse(SummaryCreate):
    id: str
