from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKeyConstraint, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.repository.models.base import Base


class ChunkOrm(Base):
    __tablename__ = "chunks"
    __table_args__ = (
        ForeignKeyConstraint(
            ["release_id"],
            ["knowledge_releases.id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["release_id", "document_id"],
            ["documents.release_id", "documents.id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("release_id", "document_id", "chunk_index"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    release_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    document_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    char_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
