from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKeyConstraint, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.repository.models.base import Base


class AnswerCitationOrm(Base):
    __tablename__ = "answer_citations"
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
        UniqueConstraint("retrieval_log_id", "citation_order"),
        UniqueConstraint("retrieval_log_id", "chunk_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    retrieval_log_id: Mapped[str] = mapped_column(String(64), nullable=False)
    release_id: Mapped[str] = mapped_column(String(64), nullable=False)
    chunk_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    citation_order: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
