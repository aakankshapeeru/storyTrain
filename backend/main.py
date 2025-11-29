# backend/main.py
import os
import uuid
from pathlib import Path
from datetime import datetime  # if you need it here later

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db, create_story_block
from . import models, schemas
from .workers.generator import generate_block

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="StoryTrain Backend 🚂")

# Enable frontend communication (CORS)
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
    db: Session = Depends(get_db),
):
    # Check child exists
    child = db.query(models.Child).filter(models.Child.id == child_id).first()
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

    # Save DB entry (if your model is StorySession or Session, adjust the name)
    session = models.StorySession(
        child_id=child_id,
        video_path=str(filepath),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return session


# ---- Story Block Endpoints ----

@app.post("/block", response_model=schemas.StoryBlockResponse)
def new_block(db: Session = Depends(get_db)):
    text, options = generate_block()
    block = create_story_block(db, text, options)
    return block


@app.post("/session/start", response_model=schemas.SessionStartResponse)
def start_session(db: Session = Depends(get_db)):
    text, options = generate_block()

    block = models.StoryBlock(text=text, options=options)
    db.add(block)
    db.commit()
    db.refresh(block)

    session = models.StorySession(
        current_block_id=block.id,
        history=[f"{block.id}:start"],
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {"session_id": session.id, "block": block}


@app.post("/session/{session_id}/continue", response_model=schemas.StoryBlockResponse)
def continue_session(
    session_id: int,
    req: schemas.SessionContinueRequest,
    db: Session = Depends(get_db),
):
    session = (
        db.query(models.StorySession)
        .filter(models.StorySession.id == session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    prev_block = (
        db.query(models.StoryBlock)
        .filter(models.StoryBlock.id == session.current_block_id)
        .first()
    )
    if not prev_block:
        raise HTTPException(status_code=404, detail="Previous block not found")

    prompt = prev_block.text + f"\nContinue the story following choice {req.choice}: "

    text, options = generate_block(prompt=prompt)

    block = models.StoryBlock(text=text, options=options)
    db.add(block)
    db.commit()
    db.refresh(block)

    session.current_block_id = block.id
    session.history.append(f"{block.id}:{req.choice}")
    db.commit()

    return block
