from datetime import datetime
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKeyConstraint, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.core.enums import EvaluationRunStatus, ReleaseStatus

class Base(DeclarativeBase):
    pass

release_status = SAEnum(
    ReleaseStatus,
    name="release_status",
    native_enum=True,
    create_type=False,
    values_callable=lambda x: [e.value for e in x],
)

evaluation_run_status = SAEnum(
    EvaluationRunStatus,
    name="evaluation_run_status",
    native_enum=True,
    create_type=False,
    values_callable=lambda x: [e.value for e in x],
)

# Todo: Model 还不完整

class ReleaseOrm(Base):
    __tablename__ = "knowledge_releases"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[ReleaseStatus] = mapped_column(release_status, default=ReleaseStatus.DRAFT)
    config_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class DocumentOrm(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    release_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(512))
    content_raw: Mapped[str] = mapped_column(Text)
    content_cleaned: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class ChunkOrm(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    release_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    document_id: Mapped[str] = mapped_column(UUID(as_uuid=False))
    chunk_index: Mapped[int]
    content: Mapped[str] = mapped_column(Text)
    char_count: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class ChunkEmbeddingOrm(Base):
    __tablename__ = "chunk_embeddings"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    release_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    chunk_id: Mapped[str] = mapped_column(UUID(as_uuid=False))
    embedding_model: Mapped[str] = mapped_column(String(255))
    embedding_dim: Mapped[int]
    vector: Mapped[list[float]] = mapped_column(Vector(1536))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())