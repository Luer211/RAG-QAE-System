from __future__ import annotations
from typing import Any

from pydantic import BaseModel, Field


class StrategyConfig(BaseModel):
    strategy_key: str
    params: dict[str, Any] = Field(default_factory=dict)


class SuccessResponse(BaseModel):
    message: str = "success"

