"""create videos table

Revision ID: 0001_create_videos_table
Revises:
Create Date: 2025-07-16 00:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_create_videos_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "video",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("video_id", sa.String(100), unique=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("published_at", sa.DateTime, nullable=False),
        sa.Column("view_count", sa.Integer, nullable=False),
        sa.Column("like_count", sa.Integer, nullable=False),
        sa.Column("processed_at", sa.DateTime, nullable=False),
    )


def downgrade():
    op.drop_table("video")
