import hashlib
import hmac
import logging
import os

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError

from app import crud
from app.database import get_session
from app.models import Video
from app.schemas import VideoCreate

logger = logging.getLogger("app.webhook")
router = APIRouter(tags=["webhook"])


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    payload: VideoCreate,
    x_signature: str = Header(..., alias="X-Signature"),
    session=Depends(get_session),
):
    body = await request.body()
    secret = os.getenv("WEBHOOK_SECRET", "").encode()
    sig = hmac.new(secret, body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, x_signature):
        logger.warning("Invalid signature: %s", x_signature)
        raise HTTPException(400, detail="Invalid signature")

    video_obj = Video(
        video_id=payload.video_id,
        title=payload.title,
        description=payload.description,
        published_at=payload.published_at,
        view_count=payload.view_count,
        like_count=payload.like_count,
    )

    try:
        obj = await crud.create_or_update_video(session, video_obj)
    except SQLAlchemyError:
        logger.exception("DB error on ingest")
        raise HTTPException(500, detail="Database error")

    logger.info("Ingested video_id=%s", obj.video_id)

    return {"status": "ingested", "video_id": obj.video_id}
