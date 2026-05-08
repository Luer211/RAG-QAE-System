from __future__ import annotations
from dataclasses import dataclass

from app.domain.common import DomainStrategyConfig
from app.domain.retrieval.models import RetrievedChunk


@dataclass(frozen=True)
class RerankedChunk:
    chunk_id: str
    content: str
    source_type: str
    raw_score: float
    rerank_score: float
    rank_before_rerank: int
    rank_after_rerank: int
    selected_for_context: bool


@dataclass(frozen=True)
class RerankChunksInput:
    items: list[RetrievedChunk]
    config: DomainStrategyConfig
    top_k: int = 3


@dataclass(frozen=True)
class RerankChunksOutput:
    items: list[RerankedChunk]
    selected_chunks: list[RerankedChunk]

