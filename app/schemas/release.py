from __future__ import annotations
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.core.enums import ReleaseStatus


class CreateReleaseRequest(BaseModel):
    name: str
    description: str = ""
    config_snapshot: dict[str, Any] = Field(default_factory=dict)


class ReleaseResponse(BaseModel):
    id: str
    name: str
    description: str
    status: ReleaseStatus
    config_snapshot: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ReleaseListResponse(BaseModel):
    items: list[ReleaseResponse]
    total: int


class DocumentResponse(BaseModel):
    id: str
    release_id: str
    title: str
    content_raw: str
    content_cleaned: Optional[str] = None
    created_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int


class ChunkResponse(BaseModel):
    id: str
    release_id: str
    document_id: str
    chunk_index: int
    content: str
    char_count: int
    created_at: datetime


class ChunkListResponse(BaseModel):
    items: list[ChunkResponse]
    total: int
