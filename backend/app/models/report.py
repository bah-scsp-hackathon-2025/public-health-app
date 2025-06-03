from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Report(Base):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)
    author = Column(String, index=True)
    content = Column(String)
    approved = Column(Boolean)
