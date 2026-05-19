from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.core.enums import EvaluationRunStatus, ReleaseStatus


def now_utc() -> datetime:
    return datetime.utcnow()


@dataclass
class ReleaseRecord:
    id: str
    name: str
    description: str
    status: ReleaseStatus
    config_snapshot: dict[str, Any]
    created_at: datetime = field(default_factory=now_utc)


@dataclass(frozen=True)
class DocumentCreate:
    title: str
    content_raw: str
    content_cleaned: str | None


@dataclass
class DocumentRecord:
    id: str
    release_id: str
    title: str
    content_raw: str
    content_cleaned: str | None
    created_at: datetime = field(default_factory=now_utc)


@dataclass(frozen=True)
class ChunkCreate:
    document_id: str
    chunk_index: int
    content: str


@dataclass
class ChunkRecord:
    id: str
    release_id: str
    document_id: str
    chunk_index: int
    content: str
    char_count: int
    created_at: datetime = field(default_factory=now_utc)


@dataclass(frozen=True)
class EmbeddingCreate:
    chunk_id: str
    embedding_model: str
    embedding_dim: int
    vector: list[float]


@dataclass
class ChunkEmbeddingRecord:
    id: str
    release_id: str
    chunk_id: str
    embedding_model: str
    embedding_dim: int
    vector: list[float]
    created_at: datetime = field(default_factory=now_utc)


@dataclass
class VectorSearchRedord:
    chunk_id: str
    content: str
    distance: float
    score: float



@dataclass
class RetrievalLogRecord:
    id: str
    release_id: str
    query_raw: str
    query_rewritten: str | None
    rewrite_used: str | None
    answer_text: str | None
    config_snapshot: dict[str, Any]
    created_at: datetime = field(default_factory=now_utc)


@dataclass(frozen=True)
class RetrievalItemCreate:
    chunk_id: str
    source_type: str
    raw_score: float
    rerank_score: float | None
    rank_before_rerank: int | None
    rank_after_rerank: int | None
    selected_for_context: bool


@dataclass
class RetrievalItemRecord:
    id: str
    retrieval_log_id: str
    release_id: str
    chunk_id: str
    source_type: str
    raw_score: float
    rerank_score: float | None
    rank_before_rerank: int | None
    rank_after_rerank: int | None
    selected_for_context: bool
    created_at: datetime = field(default_factory=now_utc)


@dataclass(frozen=True)
class AnswerCitationCreate:
    chunk_id: str
    citation_order: int
    content: str | None = None


@dataclass
class AnswerCitationRecord:
    id: str
    retrieval_log_id: str
    release_id: str
    chunk_id: str
    citation_order: int
    content: str | None
    created_at: datetime = field(default_factory=now_utc)


@dataclass
class EvaluationDatasetRecord:
    id: str
    name: str
    description: str
    created_at: datetime = field(default_factory=now_utc)


@dataclass(frozen=True)
class EvaluationQuestionCreate:
    question_text: str
    reference_answer: str | None


@dataclass
class EvaluationQuestionRecord:
    id: str
    dataset_id: str
    question_text: str
    reference_answer: str | None
    created_at: datetime = field(default_factory=now_utc)


@dataclass
class EvaluationRunRecord:
    id: str
    release_id: str
    dataset_id: str
    config_snapshot: dict[str, Any]
    run_status: EvaluationRunStatus
    total_count: int = 0
    success_count: int = 0
    failed_count: int = 0
    created_at: datetime = field(default_factory=now_utc)


@dataclass(frozen=True)
class EvaluationItemCreate:
    question_id: str
    retrieval_log_id: str | None
    answer_text: str | None
    citations_snapshot: list[dict[str, Any]]
    judge_result: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationItemRecord:
    id: str
    evaluation_run_id: str
    question_id: str
    release_id: str
    retrieval_log_id: str | None
    answer_text: str | None
    citations_snapshot: list[dict[str, Any]]
    judge_result: dict[str, Any]
    created_at: datetime = field(default_factory=now_utc)


@dataclass
class EvaluationMetricRecord:
    id: str
    evaluation_run_id: str
    metric_snapshot: dict[str, Any]
    created_at: datetime = field(default_factory=now_utc)

