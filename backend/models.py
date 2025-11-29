# storytrain/backend/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from .database import Base


class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)

    sessions = relationship("Session", back_populates="child")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    video_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    child = relationship("Child", back_populates="sessions")
from sqlalchemy import Column, Integer, String, JSON
from backend.database import Base

class StoryBlock(Base):
    __tablename__ = "story_blocks"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    options = Column(JSON, nullable=False)

class StorySession(Base):
    __tablename__ = "story_sessions"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    current_block_id = Column(Integer, ForeignKey("story_blocks.id"), nullable=True)

    # track entire history as a JSON list: ["1:A", "2:B", ...]
    history = Column(JSON, default=[])


