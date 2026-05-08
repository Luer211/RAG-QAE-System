from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.services.dto.common import StrategyConfigDTO


@dataclass(frozen=True)
class RetrievalServiceInput:
    release_id: str
    query: str
    rewrite_config: StrategyConfigDTO
    retrieval_config: StrategyConfigDTO
    rerank_config: StrategyConfigDTO
    generation_config: StrategyConfigDTO


@dataclass(frozen=True)
class CitationServiceOutput:
    release_id: str
    chunk_id: str
    citation_order: int
    content: str | None


@dataclass(frozen=True)
class RetrievalServiceOutput:
    answer: str
    citations: list[CitationServiceOutput]
    release_id: str
    retrieval_log_id: str


@dataclass(frozen=True)
class RetrievalLogServiceOutput:
    id: str
    release_id: str
    query_raw: str
    query_rewritten: str | None
    rewrite_used: str | None
    answer_text: str | None
    config_snapshot: dict[str, Any]
    created_at: datetime


@dataclass(frozen=True)
class RetrievalItemServiceOutput:
    id: str
    chunk_id: str
    source_type: str
    raw_score: float
    rerank_score: float | None
    rank_before_rerank: int | None
    rank_after_rerank: int | None
    selected_for_context: bool

