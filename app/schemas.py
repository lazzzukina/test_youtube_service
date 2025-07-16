from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, conint, constr
from sqlmodel import SQLModel


class VideoCreate(SQLModel):
    video_id: constr(max_length=100)
    title: constr(max_length=255)
    description: Optional[str] = None
    published_at: datetime
    view_count: conint(ge=0)
    like_count: conint(ge=0)


class VideoBase(BaseModel):
    video_id: str = Field(..., max_length=100, description="YouTube video ID")
    title: str = Field(..., max_length=255, description="Video title")
    description: Optional[str] = Field(None, description="Video description")
    published_at: datetime = Field(..., description="ISO‑format publish timestamp")
    view_count: int = Field(..., ge=0, description="Number of views")
    like_count: int = Field(..., ge=0, description="Number of likes")

    processed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when record was processed",
    )

    class Config:
        from_attributes = True
