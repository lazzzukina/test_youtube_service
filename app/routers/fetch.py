import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import app.crud as crud
import app.services.youtube_client as yc
from app.database import get_session

logger = logging.getLogger("app.fetch_router")
router = APIRouter()


@router.post("/fetch/", response_model=dict)
async def fetch_and_store(
    channel_id: str,
    max_results: int = 10,
    session: AsyncSession = Depends(get_session),
):
    try:
        records = await yc.fetch_videos(channel_id, max_results)
    except httpx.HTTPStatusError as e:
        logger.error("YouTube API returned error", exc_info=e)
        raise HTTPException(status_code=502, detail="YouTube API error")
    except Exception as e:
        raise HTTPException(status_code=502, detail="Internal fetching error")

    ingested_ids = []
    for record in records:
        try:
            obj = await crud.create_or_update_video(session, record)
            ingested_ids.append(obj.video_id)
        except Exception as e:
            logger.error(
                "Error ingesting video",
                extra={"video_id": getattr(record, "video_id", None), "error": str(e)},
            )
            raise HTTPException(status_code=500, detail="Database ingestion error")

    return {"count": len(ingested_ids), "videos": ingested_ids}
