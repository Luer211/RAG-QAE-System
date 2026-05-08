from __future__ import annotations
from typing import Protocol

from app.core.errors import InvalidStateError
from app.domain.retrieval.models import RetrieveChunksInput, RetrieveChunksOutput, RetrievedChunk


class RetrievalStrategy(Protocol):
    async def retrieve(self, input_data: RetrieveChunksInput) -> RetrieveChunksOutput:
        ...


class MockRetrievalStrategy:
    async def retrieve(self, input_data: RetrieveChunksInput) -> RetrieveChunksOutput:
        query_terms = {term.lower() for term in input_data.query.split() if term}
        scored: list[tuple[float, str, str]] = []
        for candidate in input_data.candidates:
            content_terms = {term.lower() for term in candidate.content.split() if term}
            overlap = len(query_terms & content_terms)
            score = float(overlap) if query_terms else 0.0
            if score > 0 or not query_terms:
                scored.append((score, candidate.chunk_id, candidate.content))

        if not scored:
            scored = [(0.0, candidate.chunk_id, candidate.content) for candidate in input_data.candidates[:5]]

        scored.sort(key=lambda item: item[0], reverse=True)
        items = [
            RetrievedChunk(
                chunk_id=chunk_id,
                content=content,
                source_type="mock_text",
                raw_score=score,
                rank_before_rerank=index + 1,
            )
            for index, (score, chunk_id, content) in enumerate(scored[:10])
        ]
        return RetrieveChunksOutput(items=items)


class RetrievalStrategyFactory:
    def __init__(self) -> None:
        self._strategies: dict[str, RetrievalStrategy] = {
            "mock_retrieval": MockRetrievalStrategy(),
        }

    def get(self, strategy_key: str) -> RetrievalStrategy:
        try:
            return self._strategies[strategy_key]
        except KeyError as exc:
            raise InvalidStateError(f"Unknown retrieval strategy: {strategy_key}") from exc


class RetrievalDomain:
    def __init__(self, strategy_factory: RetrievalStrategyFactory):
        self.strategy_factory = strategy_factory

    async def retrieve(self, input_data: RetrieveChunksInput) -> RetrieveChunksOutput:
        strategy = self.strategy_factory.get(input_data.config.strategy_key)
        return await strategy.retrieve(input_data)

