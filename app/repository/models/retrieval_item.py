from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKeyConstraint, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.repository.models.base import Base


class RetrievalItemOrm(Base):
    __tablename__ = "retrieval_items"
    __table_args__ = (
        ForeignKeyConstraint(
            ["retrieval_log_id", "release_id"],
            ["retrieval_logs.id", "retrieval_logs.release_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["release_id", "chunk_id"],
            ["chunks.release_id", "chunks.id"],
            ondelete="CASCADE",
        ),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    retrieval_log_id: Mapped[str] = mapped_column(String(64), nullable=False)
    release_id: Mapped[str] = mapped_column(String(64), nullable=False)
    chunk_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_score: Mapped[float] = mapped_column(Float, nullable=False)
    rerank_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rank_before_rerank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rank_after_rerank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    selected_for_context: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
