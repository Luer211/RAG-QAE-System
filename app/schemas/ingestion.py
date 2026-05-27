from __future__ import annotations
from pydantic import BaseModel, Field

from app.schemas.common import StrategyConfig


class IngestDocumentRequest(BaseModel):
    title: str
    content_raw: str


class IngestJobRequest(BaseModel):
    release_id: str
    documents: list[IngestDocumentRequest]
    cleaner_config: StrategyConfig
    chunker_config: StrategyConfig
    embedding_config: StrategyConfig

