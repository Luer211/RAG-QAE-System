from __future__ import annotations
from dataclasses import dataclass

from app.domain.common import DomainStrategyConfig


@dataclass(frozen=True)
class RewriteQueryInput:
    query: str
    config: DomainStrategyConfig


@dataclass(frozen=True)
class RewriteQueryOutput:
    query_rewritten: str
    rewrite_used: str

