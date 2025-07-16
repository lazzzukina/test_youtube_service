from datetime import datetime
from typing import Union

from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Video


async def get_videos(
    session: AsyncSession,
    min_views: int = 0,
    min_likes: int = 0,
) -> list[Video]:
    query = select(Video).where(Video.view_count >= min_views)
    if min_likes:
        query = query.where(Video.like_count >= min_likes)
    result = await session.execute(query)

    return result.scalars().all()


async def create_or_update_video(
    session: AsyncSession,
    video_data: Union[Video, BaseModel],
) -> Video:
    if isinstance(video_data, BaseModel):
        data = video_data.dict()
    else:
        data = {k: v for k, v in video_data.__dict__.items() if not k.startswith("_")}
    data.pop("id", None)

    query = select(Video).where(Video.video_id == data["video_id"])
    result = await session.execute(query)
    obj = result.scalar_one_or_none()

    if obj:
        for key, value in data.items():
            setattr(obj, key, value)
        obj.processed_at = datetime.utcnow()
    else:
        obj = Video(**data)
        obj.processed_at = datetime.utcnow()
        session.add(obj)

    try:
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise

    await session.refresh(obj)

    return obj
