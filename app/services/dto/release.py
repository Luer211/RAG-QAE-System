from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.core.enums import ReleaseStatus


@dataclass(frozen=True)
class CreateReleaseServiceInput:
    name: str
    description: str
    config_snapshot: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReleaseServiceOutput:
    id: str
    name: str
    description: str
    status: ReleaseStatus
    config_snapshot: dict[str, Any]
    created_at: datetime


@dataclass(frozen=True)
class DocumentServiceOutput:
    id: str
    release_id: str
    title: str
    content_raw: str
    content_cleaned: str | None
    created_at: datetime


@dataclass(frozen=True)
class ChunkServiceOutput:
    id: str
    release_id: str
    document_id: str
    chunk_index: int
    content: str
    char_count: int
    created_at: datetime

