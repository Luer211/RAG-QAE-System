from __future__ import annotations
from dataclasses import dataclass, field

from app.core.context import RequestContext
from app.core.enums import ReleaseStatus
from app.pipelines.common import PipelineStrategyConfig


@dataclass(frozen=True)
class IngestDocumentInput:
    title: str
    content_raw: str


@dataclass(frozen=True)
class IngestPipelineInput:
    release_id: str
    documents: list[IngestDocumentInput]
    cleaner_config: PipelineStrategyConfig
    chunker_config: PipelineStrategyConfig
    embedding_config: PipelineStrategyConfig


@dataclass
class IngestRuntime:
    documents_cleaned_ids: list[str] = field(default_factory=list)
    chunk_ids: list[str] = field(default_factory=list)
    chunk_embedding_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class IngestPipelineOutput:
    release_status: ReleaseStatus


@dataclass
class IngestState:
    ctx: RequestContext
    input: IngestPipelineInput
    runtime: IngestRuntime = field(default_factory=IngestRuntime)
    output: IngestPipelineOutput | None = None

