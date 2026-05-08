from __future__ import annotations
from dataclasses import dataclass

from app.domain.common import DomainStrategyConfig


@dataclass(frozen=True)
class ChunkDocumentInput:
    document_id: str
    content_cleaned: str


@dataclass(frozen=True)
class ChunkedText:
    document_id: str
    chunk_index: int
    content: str


@dataclass(frozen=True)
class ChunkDocumentsInput:
    documents: list[ChunkDocumentInput]
    config: DomainStrategyConfig


@dataclass(frozen=True)
class ChunkDocumentsOutput:
    chunks: list[ChunkedText]

