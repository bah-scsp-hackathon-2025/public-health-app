from sqlalchemy import Column, Integer, String
from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    author = Column(String)
    description = Column(String)
