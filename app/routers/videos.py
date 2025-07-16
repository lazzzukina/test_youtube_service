from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio.session import AsyncSession

import app.crud as crud
from app.database import get_session
from app.models import Video

router = APIRouter(tags=["videos"])


@router.get(
    "/videos/",
    response_model=List[Video],
    summary="List videos filtered by views and likes",
)
async def read_videos(
    *,
    min_views: int = Query(0, ge=0, description="Only videos with ≥ this many views"),
    min_likes: int = Query(0, ge=0, description="Only videos with ≥ this many likes"),
    session: AsyncSession = Depends(get_session),
):
    return await crud.get_videos(session, min_views, min_likes)
