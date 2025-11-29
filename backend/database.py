# storytrain/backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./storytrain.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from backend.models import StoryBlock
from sqlalchemy.orm import Session

def create_story_block(db: Session, text: str, options: dict):
    block = StoryBlock(text=text, options=options)
    db.add(block)
    db.commit()
    db.refresh(block)
    return block

