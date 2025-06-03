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
