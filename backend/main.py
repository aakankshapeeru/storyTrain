# storytrain/backend/main.py
import os
import uuid
from pathlib import Path

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models, schemas

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="StoryTrain Backend 🚂")

# Enable frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Storage setup ----
MEDIA_ROOT = Path("media")
SESSIONS_DIR = MEDIA_ROOT / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


# ---- Child Endpoints ----

@app.post("/children", response_model=schemas.ChildOut)
def create_child(child: schemas.ChildCreate, db: Session = Depends(get_db)):
    db_child = models.Child(name=child.name, age=child.age)
    db.add(db_child)
    db.commit()
    db.refresh(db_child)
    return db_child


@app.get("/children", response_model=list[schemas.ChildOut])
def list_children(db: Session = Depends(get_db)):
    return db.query(models.Child).all()


# ---- Session Upload ----

@app.post("/sessions/upload", response_model=schemas.SessionOut)
async def upload_session(
    child_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Check child exists
    child = db.query(models.Child).filter(models.Child.Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found.")

    # Validate content type
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a video.")

    # Save file
    ext = os.path.splitext(file.filename)[1] or ".mp4"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = SESSIONS_DIR / filename

    with open(filepath, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    # Save DB entry
    session = models.Session(child_id=child_id, video_path=str(filepath))
    db.add(session)
    db.commit()
    db.refresh(session)

    return session

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import StoryBlockResponse
from backend.database import create_story_block
from backend.workers.generator import generate_block

app = FastAPI()

@app.post("/block", response_model=StoryBlockResponse)
def new_block(db: Session = Depends(get_db)):
    text, options = generate_block()
    block = create_story_block(db, text, options)
    return block

