from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Report(Base):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    content = Column(String)
    approved = Column(Boolean)
    created = Column(String)
    updated = Column(String)


class ReportCreate(BaseModel):
    title: str
    content: str
    author: str
    approved: bool


class ReportUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    approved: Optional[bool] = None


class ReportResponse(ReportCreate):
    id: int
