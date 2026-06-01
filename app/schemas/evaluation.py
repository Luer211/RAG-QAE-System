from __future__ import annotations
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.core.enums import EvaluationRunStatus
from app.schemas.common import StrategyConfig


class CreateDatasetRequest(BaseModel):
    name: str
    description: str = ""


class DatasetResponse(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime


class EvaluationQuestionInput(BaseModel):
    question_text: str
    reference_answer: Optional[str] = None


class AddQuestionsRequest(BaseModel):
    questions: list[EvaluationQuestionInput]


class AddSuccessResponse(BaseModel):
    dataset_id: str
    added_count: int


class QuestionResponse(BaseModel):
    id: str
    dataset_id: str
    question_text: str
    reference_answer: Optional[str] = None
    created_at: datetime


class EvaluationRunRequest(BaseModel):
    release_id: str
    dataset_id: str
    rewrite_config: StrategyConfig
    retrieval_config: StrategyConfig
    rerank_config: StrategyConfig 
    generation_config: StrategyConfig
    judge_config: StrategyConfig


class EvaluationRunSubmitResponse(BaseModel):
    evaluation_run_id: str
    run_status: EvaluationRunStatus


class EvaluationRunResponse(BaseModel):
    id: str
    release_id: str
    dataset_id: str
    run_status: EvaluationRunStatus
    total_count: int
    success_count: int
    failed_count: int
    created_at: datetime


class EvaluationItemResponse(BaseModel):
    id: str
    evaluation_run_id: str
    question_id: str
    retrieval_log_id: Optional[str] = None
    answer_text: Optional[str] = None
    citations_snapshot: list[dict[str, Any]] = Field(default_factory=list)
    judge_result: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class EvaluationMetricResponse(BaseModel):
    evaluation_run_id: str
    metric_snapshot: dict[str, Any] = Field(default_factory=dict)
