from __future__ import annotations
from dataclasses import dataclass, field

from app.core.context import RequestContext
from app.domain.generation.models import AnswerCitation
from app.domain.reranking.models import RerankedChunk
from app.domain.retrieval.models import RetrievedChunk
from app.pipelines.common import PipelineStrategyConfig


@dataclass(frozen=True)
class RetrievalPipelineInput:
    release_id: str
    query: str
    rewrite_config: PipelineStrategyConfig
    retrieval_config: PipelineStrategyConfig
    rerank_config: PipelineStrategyConfig
    generation_config: PipelineStrategyConfig


@dataclass
class RetrievalRuntime:
    retrieval_log_id: str | None = None
    rewrite_query: str | None = None
    retrieval_chunks: list[RetrievedChunk] = field(default_factory=list)
    rerank_chunks: list[RerankedChunk] = field(default_factory=list)
    selected_chunks: list[RerankedChunk] = field(default_factory=list)


@dataclass(frozen=True)
class RetrievalPipelineOutput:
    answer: str
    citations: list[AnswerCitation]
    release_id: str
    retrieval_log_id: str


@dataclass
class RetrievalState:
    ctx: RequestContext
    input: RetrievalPipelineInput
    runtime: RetrievalRuntime = field(default_factory=RetrievalRuntime)
    output: RetrievalPipelineOutput | None = None

