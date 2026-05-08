from __future__ import annotations
from dataclasses import dataclass

from app.services.dto.common import StrategyConfigDTO


@dataclass(frozen=True)
class IngestDocumentServiceInput:
    title: str
    content_raw: str


@dataclass(frozen=True)
class IngestServiceInput:
    release_id: str
    documents: list[IngestDocumentServiceInput]
    cleaner_config: StrategyConfigDTO
    chunker_config: StrategyConfigDTO
    embedding_config: StrategyConfigDTO


@dataclass(frozen=True)
class IngestServiceOutput:
    message: str = "success"

