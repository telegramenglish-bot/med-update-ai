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


from sqlalchemy import Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    subscription_plan = Column(String, default="free")
    preferred_language = Column(String, default="es")
