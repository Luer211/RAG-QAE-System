from __future__ import annotations

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKeyConstraint, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.repository.models.base import Base


class ChunkEmbeddingOrm(Base):
    __tablename__ = "chunk_embeddings"
    __table_args__ = (
        ForeignKeyConstraint(
            ["release_id"],
            ["knowledge_releases.id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["release_id", "chunk_id"],
            ["chunks.release_id", "chunks.id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("release_id", "chunk_id", "embedding_model"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    release_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    chunk_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(255), nullable=False)
    embedding_dim: Mapped[int] = mapped_column(Integer, nullable=False)
    vector: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
