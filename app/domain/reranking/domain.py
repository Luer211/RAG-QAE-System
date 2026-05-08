from __future__ import annotations
from typing import Protocol

from app.core.errors import InvalidStateError
from app.domain.reranking.models import RerankChunksInput, RerankChunksOutput, RerankedChunk


class RerankStrategy(Protocol):
    async def rerank(self, input_data: RerankChunksInput) -> RerankChunksOutput:
        ...


class MockRerankStrategy:
    async def rerank(self, input_data: RerankChunksInput) -> RerankChunksOutput:
        ranked_source = sorted(
            input_data.items,
            key=lambda item: (item.raw_score, -item.rank_before_rerank),
            reverse=True,
        )
        ranked: list[RerankedChunk] = []
        for index, item in enumerate(ranked_source):
            rank = index + 1
            ranked.append(
                RerankedChunk(
                    chunk_id=item.chunk_id,
                    content=item.content,
                    source_type=item.source_type,
                    raw_score=item.raw_score,
                    rerank_score=item.raw_score,
                    rank_before_rerank=item.rank_before_rerank,
                    rank_after_rerank=rank,
                    selected_for_context=rank <= input_data.top_k,
                )
            )
        return RerankChunksOutput(
            items=ranked,
            selected_chunks=[item for item in ranked if item.selected_for_context],
        )


class RerankStrategyFactory:
    def __init__(self) -> None:
        self._strategies: dict[str, RerankStrategy] = {
            "mock_rerank": MockRerankStrategy(),
        }

    def get(self, strategy_key: str) -> RerankStrategy:
        try:
            return self._strategies[strategy_key]
        except KeyError as exc:
            raise InvalidStateError(f"Unknown rerank strategy: {strategy_key}") from exc


class RerankDomain:
    def __init__(self, strategy_factory: RerankStrategyFactory):
        self.strategy_factory = strategy_factory

    async def rerank(self, input_data: RerankChunksInput) -> RerankChunksOutput:
        strategy = self.strategy_factory.get(input_data.config.strategy_key)
        return await strategy.rerank(input_data)

