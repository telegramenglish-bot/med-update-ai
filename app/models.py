from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .database import Base

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    specialty = Column(String)
    summary = Column(Text)
    translated_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
