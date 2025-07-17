# YouTube service

A small backend built with FastAPI and SQLModel (SQLAlchemy) that:

1. **Fetches** video metadata from the YouTube Data API  
2. **Processes** and validates data with Pydantic  
3. **Stores** records in PostgreSQL via migrations (Alembic)  
4. **Exposes** HTTP endpoints to trigger fetch, ingest via webhook, and list stored videos with filters  
5. **Runs asynchronously** (httpx + FastAPI) and is containerized with Docker  

---

## Project structure

```
.
├── .env                       # environment variables
├── Dockerfile
├── docker-compose.yml
├── alembic.ini                # Alembic config
├── alembic/                   # migration scripts
│   ├── env.py
│   └── versions/
├── app/
│   ├── main.py                # FastAPI app & router setup
│   ├── config.py              # Pydantic settings
│   ├── database.py            # DB engine & session
│   ├── models.py              # SQLModel ORM models
│   ├── schemas.py             # Pydantic request/response schemas
│   ├── crud.py                # Create/read/update logic
│   ├── services/
│   │   └── youtube_client.py  # YouTube data API integr
│   └── routers/
│       ├── fetch.py           # `/fetch/` endpoint
│       └── webhook.py         # `/webhook` endpoint
├── requirements.txt
└── tests/                     # pytest test suite
    ├── test_crud.py
    ├── test_youtube_client.py
    └── test_webhook_endpoint.py
```

---

## Prerequisites

- **Docker** (≥ 20.10)  
- **Docker Compose** (v2 syntax)  
---

## Setup & Run

1. **Clone the repo**  
   ```bash
   git clone <repo_url>
   cd prod_youtube_service
   ```

2. **Copy & edit environment file**  
   ```bash
   cp .env.example .env
   ```
   Fill in:
   ```dotenv
   DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/youtubedb
   YOUTUBE_API_KEY=your_google_cloud_api_key
   YOUTUBE_API_URL=https://www.googleapis.com/youtube/v3/search
   WEBHOOK_SECRET=supersecret
   ```

3. **Build & start containers**  
   ```bash
   docker-compose build
   docker-compose up -d
   ```

4. **Apply database migrations**  
   ```bash
   docker-compose exec web alembic upgrade head
   ```

5. **Access the API**  
   Open your browser or send requests to:  
   ```
   http://localhost:8000
   ```

---

## API endpoints

### 1. Fetch & store videos

```
POST /fetch/?channel_id={CHANNEL_ID}&max_results={n}
```

- **Params**:
  - `channel_id` (string) — YouTube channel ID  
  - `max_results` (int, default=10) — number of videos  
- **Success response** `200 OK`:
  ```json
  {
    "count": 5,
    "videos": ["abc123", "def456", ...]
  }
  ```

### 2. Webhook ingestion simulation

```
POST /webhook
Headers:
  X-Signature: <HMAC-SHA256 signature>
Content-Type: application/json
Body: JSON matching `VideoBase` schema (without `processed_at`)
```

- **Signature**  
  ```python
  import hmac, hashlib
  body_bytes = json.dumps(payload).encode()
  sig = hmac.new(WEBHOOK_SECRET.encode(), body_bytes, hashlib.sha256).hexdigest()
  ```  
- **Success** `200 OK`:
  ```json
  { "status":"ingested", "video_id":"PVSFGnuI_UA" }
  ```
- **Invalid signature** `400 Bad Request`:
  ```json
  { "detail":"Invalid signature" }
  ```

### 3. List Stored Videos

```
GET /videos/?min_views={min_views}&min_likes={min_likes}
```

- **Query**:
  - `min_views` (int, default=0)  
  - `min_likes` (int, default=0)  
- **Response** `200 OK`:  
  ```json
  [
    {
      "id": 1,
      "video_id": "...",
      "title": "...",
      "description": "...",
      "published_at": "2025-06-16T03:13:31",
      "view_count": 7269,
      "like_count": 181,
      "processed_at": "2025-07-16T17:03:44.851343"
    },
    ...
  ]
  ```

---

## Code Highlights

- **FastAPI** for high‑performance async HTTP  
- **SQLModel** (SQLAlchemy + Pydantic) for ORM & schema  
- **httpx** async client for external API calls  
- **Alembic** for versioned migrations  
- **Pydantic Settings** for configuration via `.env`  
- **HMAC**‑SHA256 signature validation for webhook security  
- **Docker Compose** spins up `db` (Postgres) + `web` (FastAPI)  
---

## Testing

- **Unit tests** with `pytest` and `pytest-asyncio`  
- **Coverage** of:
  - CRUD logic (insert/update/get)  
  - YouTube client (success & error)  
  - Webhook endpoint (valid/invalid signature)  

Run tests:

```bash
docker-compose exec web pytest --disable-warnings -q
```
