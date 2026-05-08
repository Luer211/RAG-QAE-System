from __future__ import annotations
from dataclasses import dataclass, field

from app.dao.records import (
    AnswerCitationRecord,
    ChunkEmbeddingRecord,
    ChunkRecord,
    DocumentRecord,
    EvaluationDatasetRecord,
    EvaluationItemRecord,
    EvaluationMetricRecord,
    EvaluationQuestionRecord,
    EvaluationRunRecord,
    ReleaseRecord,
    RetrievalItemRecord,
    RetrievalLogRecord,
)


@dataclass
class MemoryStore:
    releases: dict[str, ReleaseRecord] = field(default_factory=dict)
    release_partitions: set[str] = field(default_factory=set)
    documents: dict[str, DocumentRecord] = field(default_factory=dict)
    chunks: dict[str, ChunkRecord] = field(default_factory=dict)
    chunk_embeddings: dict[str, ChunkEmbeddingRecord] = field(default_factory=dict)
    retrieval_logs: dict[str, RetrievalLogRecord] = field(default_factory=dict)
    retrieval_items: dict[str, RetrievalItemRecord] = field(default_factory=dict)
    answer_citations: dict[str, AnswerCitationRecord] = field(default_factory=dict)
    evaluation_datasets: dict[str, EvaluationDatasetRecord] = field(default_factory=dict)
    evaluation_questions: dict[str, EvaluationQuestionRecord] = field(default_factory=dict)
    evaluation_runs: dict[str, EvaluationRunRecord] = field(default_factory=dict)
    evaluation_items: dict[str, EvaluationItemRecord] = field(default_factory=dict)
    evaluation_metrics: dict[str, EvaluationMetricRecord] = field(default_factory=dict)


store = MemoryStore()

