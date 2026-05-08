from __future__ import annotations
from dataclasses import dataclass

from app.domain.common import DomainStrategyConfig
from app.domain.reranking.models import RerankedChunk


@dataclass(frozen=True)
class AnswerCitation:
    release_id: str
    chunk_id: str
    citation_order: int
    content: str


@dataclass(frozen=True)
class GenerateAnswerInput:
    release_id: str
    selected_chunks: list[RerankedChunk]
    config: DomainStrategyConfig


@dataclass(frozen=True)
class GenerateAnswerOutput:
    answer: str
    citations: list[AnswerCitation]

