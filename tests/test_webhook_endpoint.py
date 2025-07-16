import hashlib
import hmac
import json
from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app

WEBHOOK_SECRET = "supersecret"
client = TestClient(app)


def test_webhook_success():
    payload = {
        "video_id": "vid123",
        "title": "Title",
        "description": "Desc",
        "published_at": datetime.utcnow().isoformat(),
        "view_count": 10,
        "like_count": 2,
    }
    body = json.dumps(payload).encode("utf-8")
    signature = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    headers = {
        "X-Signature": signature,
        "Content-Type": "application/json",
    }

    response = client.post("/webhook", content=body, headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "ingested"
    assert response_data["video_id"] == payload["video_id"]


def test_webhook_bad_signature():
    payload = {
        "video_id": "vid123",
        "title": "Title",
        "description": "Desc",
        "published_at": datetime.utcnow().isoformat(),
        "view_count": 10,
        "like_count": 2,
    }
    body = json.dumps(payload).encode("utf-8")

    headers = {
        "X-Signature": "bad",
        "Content-Type": "application/json",
    }
    response = client.post("/webhook", content=body, headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid signature"
