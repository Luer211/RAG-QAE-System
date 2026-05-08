from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from app.domain.common import DomainStrategyConfig


@dataclass(frozen=True)
class PipelineStrategyConfig:
    strategy_key: str
    params: dict[str, Any] = field(default_factory=dict)

    def to_domain_config(self) -> DomainStrategyConfig:
        return DomainStrategyConfig(strategy_key=self.strategy_key, params=self.params)

