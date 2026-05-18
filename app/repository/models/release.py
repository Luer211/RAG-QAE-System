from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ReleaseStatus
from app.repository.models.base import Base
from app.repository.models.status import release_status


class ReleaseOrm(Base):
    __tablename__ = "knowledge_releases"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    status: Mapped[ReleaseStatus] = mapped_column(
        release_status,
        nullable=False,
        default=ReleaseStatus.DRAFT,
        server_default=ReleaseStatus.DRAFT.value,
    )
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
