from __future__ import annotations
from pydantic import BaseModel, Field

from app.schemas.common import StrategyConfig


class IngestDocumentRequest(BaseModel):
    title: str
    content_raw: str


# Todo: 这个默认的要改掉
class IngestJobRequest(BaseModel):
    release_id: str
    documents: list[IngestDocumentRequest]
    cleaner_config: StrategyConfig = Field(
        default_factory=lambda: StrategyConfig(strategy_key="mock_clean")
    )
    chunker_config: StrategyConfig = Field(
        default_factory=lambda: StrategyConfig(strategy_key="mock_chunk")
    )
    embedding_config: StrategyConfig = Field(
        default_factory=lambda: StrategyConfig(strategy_key="mock_model")
    )

