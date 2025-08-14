from sqlalchemy import Column, Integer, String, Text, DateTime
from .database import Base
from datetime import datetime

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, nullable=False)
    original_filename = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    hash = Column(String(64), nullable=False, index=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
