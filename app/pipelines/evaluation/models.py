from __future__ import annotations
from dataclasses import dataclass, field

from app.core.context import RequestContext
from app.pipelines.common import PipelineStrategyConfig


@dataclass(frozen=True)
class EvaluationPipelineInput:
    release_id: str
    dataset_id: str
    rewrite_config: PipelineStrategyConfig
    retrieval_config: PipelineStrategyConfig
    rerank_config: PipelineStrategyConfig
    generation_config: PipelineStrategyConfig
    judge_config: PipelineStrategyConfig


@dataclass
class EvaluationRuntime:
    evaluation_run_id: str | None = None


@dataclass(frozen=True)
class EvaluationPipelineOutput:
    evaluation_run_id: str


@dataclass
class EvaluationState:
    ctx: RequestContext
    input: EvaluationPipelineInput
    runtime: EvaluationRuntime = field(default_factory=EvaluationRuntime)
    output: EvaluationPipelineOutput | None = None

