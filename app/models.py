from datetime import datetime
from typing import Optional

from pydantic import conint, constr
from sqlmodel import Field, SQLModel


class Video(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    video_id: constr(max_length=100) = Field(
        sa_column_kwargs={
            "unique": True,
            "nullable": False,
        }
    )
    title: constr(max_length=255)
    description: Optional[str]
    published_at: datetime
    view_count: conint(ge=0)
    like_count: conint(ge=0)
    processed_at: datetime
