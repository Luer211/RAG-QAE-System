from __future__ import annotations
from dataclasses import dataclass

from app.domain.common import DomainStrategyConfig


@dataclass(frozen=True)
class RetrievalCandidate:
    chunk_id: str
    content: str


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    content: str
    source_type: str
    raw_score: float
    rank_before_rerank: int


@dataclass(frozen=True)
class RetrieveChunksInput:
    query: str
    candidates: list[RetrievalCandidate]
    config: DomainStrategyConfig


@dataclass(frozen=True)
class RetrieveChunksOutput:
    items: list[RetrievedChunk]

