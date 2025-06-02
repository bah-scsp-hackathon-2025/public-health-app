from sqlalchemy import Column, Integer, String
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)
    risk_score = Column(Integer)
    risk_reason = Column(String)
    location = Column(String)
