import logging
import random
from typing import List

import httpx
from dateutil import parser

from app.config import settings
from app.schemas import VideoCreate

logger = logging.getLogger("app.youtube_client")

YOUTUBE_API_URL = settings.youtube_api_url


async def fetch_videos(channel_id: str, max_results: int = 10) -> List[VideoCreate]:
    params = {
        "key": settings.youtube_api_key,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": max_results,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(str(YOUTUBE_API_URL), params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
    except httpx.RequestError as e:
        logger.exception("Network error when fetching YouTube videos")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(
            "YouTube API returned error",
            extra={
                "status_code": e.response.status_code,
                "response_text": e.response.text[:200],
            },
        )
        raise

    items = data.get("items", [])
    videos: List[VideoCreate] = []

    for item in items:
        video_id = item.get("id", {}).get("videoId")
        snippet = item.get("snippet", {})
        raw_published = snippet.get("publishedAt")
        if not video_id or not raw_published:
            continue

        try:
            dt_aware = parser.isoparse(raw_published)
            published_naive = dt_aware.replace(tzinfo=None)
        except Exception:
            logger.warning(
                "Failed to parse or strip timezone from publishedAt",
                extra={"value": raw_published},
            )
            continue

        videos.append(
            VideoCreate(
                video_id=video_id,
                title=snippet.get("title", "")[:255],
                description=snippet.get("description", ""),
                published_at=published_naive,
                view_count=random.randint(100, 10_000),
                like_count=random.randint(0, 1_000),
            )
        )

    return videos
