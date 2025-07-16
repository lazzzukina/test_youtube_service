from datetime import datetime

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

import app.crud as crud
from app.models import Video

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(name="engine")
def engine_fixture():
    return create_async_engine(DATABASE_URL, echo=False, future=True)


@pytest_asyncio.fixture(name="session")
async def session_fixture(engine):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with AsyncSessionLocal() as session:
        yield session


@pytest.mark.asyncio
async def test_create_or_update_video_new(session):
    now = datetime.utcnow()
    video = Video(
        video_id="vid1",
        title="Test",
        description="Desc",
        published_at=now,
        view_count=1,
        like_count=1,
        processed_at=now,
    )
    obj = await crud.create_or_update_video(session, video)
    assert obj.id is not None
    assert obj.video_id == "vid1"


@pytest.mark.asyncio
async def test_create_or_update_video_update(session):
    now = datetime.utcnow()
    first_video = Video(
        video_id="same",
        title="T1",
        description="D1",
        published_at=now,
        view_count=2,
        like_count=3,
        processed_at=now,
    )
    first_obj = await crud.create_or_update_video(session, first_video)
    secodnd_video = Video(
        video_id="same",
        title="T1",
        description="D1",
        published_at=now,
        view_count=10,
        like_count=5,
        processed_at=now,
    )
    second_obj = await crud.create_or_update_video(session, secodnd_video)
    assert second_obj.id == first_obj.id
    assert second_obj.view_count == 10
    assert second_obj.like_count == 5


@pytest.mark.asyncio
async def test_get_videos_filter(session):
    now = datetime.utcnow()
    first_video = Video(
        video_id="v1",
        title="A",
        description="A",
        published_at=now,
        view_count=1,
        like_count=0,
        processed_at=now,
    )
    second_video = Video(
        video_id="v2",
        title="B",
        description="B",
        published_at=now,
        view_count=100,
        like_count=0,
        processed_at=now,
    )
    await crud.create_or_update_video(session, first_video)
    await crud.create_or_update_video(session, second_video)
    results = await crud.get_videos(session, min_views=50)
    assert len(results) == 1
    assert results[0].video_id == "v2"
