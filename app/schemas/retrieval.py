from __future__ import annotations
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.common import StrategyConfig


class RetrievalRequest(BaseModel):
    release_id: str
    query: str
    rewrite_config: StrategyConfig = Field(
        default_factory=lambda: StrategyConfig(strategy_key="mock_rewrite")
    )
    retrieval_config: StrategyConfig = Field(
        default_factory=lambda: StrategyConfig(strategy_key="mock_retrieval")
    )
    rerank_config: StrategyConfig = Field(
        default_factory=lambda: StrategyConfig(strategy_key="mock_rerank")
    )
    generation_config: StrategyConfig = Field(
        default_factory=lambda: StrategyConfig(strategy_key="mock_gen")
    )


class AnswerCitationResponse(BaseModel):
    release_id: str
    chunk_id: str
    citation_order: int
    content: Optional[str] = None


class RetrievalResult(BaseModel):
    answer: str
    citations: list[AnswerCitationResponse]
    release_id: str
    retrieval_log_id: str


class RetrievalLogResponse(BaseModel):
    id: str
    release_id: str
    query_raw: str
    query_rewritten: Optional[str] = None
    rewrite_used: Optional[str] = None
    answer_text: Optional[str] = None
    config_snapshot: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class RetrievalItemResponse(BaseModel):
    id: str
    chunk_id: str
    source_type: str
    raw_score: float
    rerank_score: Optional[float] = None
    rank_before_rerank: Optional[int] = None
    rank_after_rerank: Optional[int] = None
    selected_for_context: bool
