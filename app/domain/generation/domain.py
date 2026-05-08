from __future__ import annotations
from typing import Protocol

from app.core.errors import InvalidStateError
from app.domain.generation.models import AnswerCitation, GenerateAnswerInput, GenerateAnswerOutput


class GenerationStrategy(Protocol):
    async def generate(self, input_data: GenerateAnswerInput) -> GenerateAnswerOutput:
        ...


class MockGenerationStrategy:
    async def generate(self, input_data: GenerateAnswerInput) -> GenerateAnswerOutput:
        if not input_data.selected_chunks:
            return GenerateAnswerOutput(answer="No relevant context found.", citations=[])

        citations = [
            AnswerCitation(
                release_id=input_data.release_id,
                chunk_id=chunk.chunk_id,
                citation_order=index + 1,
                content=chunk.content,
            )
            for index, chunk in enumerate(input_data.selected_chunks)
        ]
        context_preview = " ".join(chunk.content for chunk in input_data.selected_chunks)
        answer = f"Mock answer based on {len(citations)} chunks: {context_preview[:300]}"
        return GenerateAnswerOutput(answer=answer, citations=citations)


class GenerationStrategyFactory:
    def __init__(self) -> None:
        self._strategies: dict[str, GenerationStrategy] = {
            "mock_gen": MockGenerationStrategy(),
        }

    def get(self, strategy_key: str) -> GenerationStrategy:
        try:
            return self._strategies[strategy_key]
        except KeyError as exc:
            raise InvalidStateError(f"Unknown generation strategy: {strategy_key}") from exc


class GenerationDomain:
    def __init__(self, strategy_factory: GenerationStrategyFactory):
        self.strategy_factory = strategy_factory

    async def generate(self, input_data: GenerateAnswerInput) -> GenerateAnswerOutput:
        strategy = self.strategy_factory.get(input_data.config.strategy_key)
        return await strategy.generate(input_data)

