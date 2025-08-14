from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    summary = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
