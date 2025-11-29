# storytrain/backend/schemas.py
from datetime import datetime
from pydantic import BaseModel


class ChildBase(BaseModel):
    name: str
    age: int | None = None


class ChildCreate(ChildBase):
    pass


class ChildOut(ChildBase):
    id: int
    class Config:
        orm_mode = True


class SessionOut(BaseModel):
    id: int
    child_id: int
    video_path: str
    created_at: datetime

    class Config:
        orm_mode = True
from pydantic import BaseModel
from typing import Dict

class StoryBlockCreate(BaseModel):
    text: str
    options: Dict[str, str]

class StoryBlockResponse(BaseModel):
    id: int
    text: str
    options: Dict[str, str]

    class Config:
        orm_mode = True
