import httpx
import pytest

from app.schemas import VideoCreate
from app.services.youtube_client import fetch_videos


class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code
        self.text = "" if status_code < 400 else str(json_data)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("Error", request=None, response=self)

    def json(self):
        return self._json


class DummyClient:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def get(self, url, params=None, timeout=None):
        return self._response


@pytest.mark.asyncio
async def test_fetch_videos_success(monkeypatch):
    items = [
        {
            "id": {"videoId": "id1"},
            "snippet": {
                "title": "title1",
                "description": "desc1",
                "publishedAt": "2025-07-16T00:00:00Z",
            },
        }
    ]
    dummy_resp = DummyResponse({"items": items}, status_code=200)
    monkeypatch.setattr(
        "app.services.youtube_client.httpx.AsyncClient", lambda: DummyClient(dummy_resp)
    )

    videos = await fetch_videos("chan", max_results=1)
    assert isinstance(videos, list)
    assert len(videos) == 1

    video = videos[0]
    assert isinstance(video, VideoCreate)
    assert video.video_id == "id1"
    assert video.published_at.tzinfo is None


@pytest.mark.asyncio
async def test_fetch_videos_api_error(monkeypatch):
    dummy_resp = DummyResponse({"error": {}}, status_code=403)
    monkeypatch.setattr(
        "app.services.youtube_client.httpx.AsyncClient", 
        lambda: DummyClient(dummy_resp)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await fetch_videos("chan", max_results=1)
