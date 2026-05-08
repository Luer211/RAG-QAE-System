from __future__ import annotations
from typing import Protocol

from app.core.errors import InvalidStateError
from app.domain.query_rewrite.models import RewriteQueryInput, RewriteQueryOutput


class QueryRewriteStrategy(Protocol):
    async def rewrite(self, input_data: RewriteQueryInput) -> RewriteQueryOutput:
        ...


class MockQueryRewriteStrategy:
    async def rewrite(self, input_data: RewriteQueryInput) -> RewriteQueryOutput:
        return RewriteQueryOutput(
            query_rewritten=" ".join(input_data.query.split()),
            rewrite_used=input_data.config.strategy_key,
        )


class QueryRewriteStrategyFactory:
    def __init__(self) -> None:
        self._strategies: dict[str, QueryRewriteStrategy] = {
            "mock_rewrite": MockQueryRewriteStrategy(),
        }

    def get(self, strategy_key: str) -> QueryRewriteStrategy:
        try:
            return self._strategies[strategy_key]
        except KeyError as exc:
            raise InvalidStateError(f"Unknown rewrite strategy: {strategy_key}") from exc


class QueryRewriteDomain:
    def __init__(self, strategy_factory: QueryRewriteStrategyFactory):
        self.strategy_factory = strategy_factory

    async def rewrite(self, input_data: RewriteQueryInput) -> RewriteQueryOutput:
        strategy = self.strategy_factory.get(input_data.config.strategy_key)
        return await strategy.rewrite(input_data)

