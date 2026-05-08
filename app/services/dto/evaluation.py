from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.core.enums import EvaluationRunStatus
from app.services.dto.common import StrategyConfigDTO


@dataclass(frozen=True)
class CreateDatasetServiceInput:
    name: str
    description: str


@dataclass(frozen=True)
class DatasetServiceOutput:
    id: str
    name: str
    description: str
    created_at: datetime


@dataclass(frozen=True)
class AddQuestionServiceInput:
    question_text: str
    reference_answer: str | None


@dataclass(frozen=True)
class QuestionServiceOutput:
    id: str
    dataset_id: str
    question_text: str
    reference_answer: str | None
    created_at: datetime


@dataclass(frozen=True)
class EvaluationRunServiceInput:
    release_id: str
    dataset_id: str
    rewrite_config: StrategyConfigDTO
    retrieval_config: StrategyConfigDTO
    rerank_config: StrategyConfigDTO
    generation_config: StrategyConfigDTO
    judge_config: StrategyConfigDTO


@dataclass(frozen=True)
class EvaluationRunServiceOutput:
    id: str
    release_id: str
    dataset_id: str
    run_status: EvaluationRunStatus
    total_count: int
    success_count: int
    failed_count: int
    created_at: datetime


@dataclass(frozen=True)
class EvaluationItemServiceOutput:
    id: str
    evaluation_run_id: str
    question_id: str
    retrieval_log_id: str | None
    answer_text: str | None
    citations_snapshot: list[dict[str, Any]]
    judge_result: dict[str, Any]
    created_at: datetime


@dataclass(frozen=True)
class EvaluationMetricServiceOutput:
    evaluation_run_id: str
    metric_snapshot: dict[str, Any]

