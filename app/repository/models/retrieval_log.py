from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKeyConstraint, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.repository.models.base import Base


class RetrievalLogOrm(Base):
    __tablename__ = "retrieval_logs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["release_id"],
            ["knowledge_releases.id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("id", "release_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    release_id: Mapped[str] = mapped_column(String(64), nullable=False)
    query_raw: Mapped[str] = mapped_column(Text, nullable=False)
    query_rewritten: Mapped[str | None] = mapped_column(Text, nullable=True)
    rewrite_used: Mapped[str | None] = mapped_column(String(255), nullable=True)
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    config_snapshot: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
