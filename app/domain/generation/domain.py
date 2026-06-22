from __future__ import annotations
from typing import Protocol

from app.core.errors import InvalidStateError
from app.domain.generation.models import AnswerCitation, GenerateAnswerInput, GenerateAnswerOutput
from app.infra.llm import LLMClient


class GenerationStrategy(Protocol):
    async def generate(self, input_data: GenerateAnswerInput) -> GenerateAnswerOutput:
        ...


class LLMGenerationStrategy:
    model = "gpt-4o"

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def generate(self, input_data: GenerateAnswerInput) -> GenerateAnswerOutput:
        context = "\n\n".join(
            f"[{index + 1}] {chunk.content}"
            for index, chunk in enumerate(input_data.selected_chunks)
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a question-answering assistant. "
                    "Answer only using the provided context. "
                    "If the context is insufficient, say you do not know."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Context:\n{input_data.query}\n\n"
                    f"{context}\n\n"
                    "Generate a concise answer based on the context."
                ),
            },
        ]

        answer = await self.llm_client.generate(
            message=messages,
            model=self.model,
        )

        citations = [
            AnswerCitation(
                release_id=input_data.release_id,
                chunk_id=chunk.chunk_id,
                citation_order=index + 1,
                content=chunk.content,
            )
            for index, chunk in enumerate(input_data.selected_chunks)
        ]

        return GenerateAnswerOutput(
            answer=answer,
            citations=citations,
        )


class GenerationStrategyFactory:
    def __init__(self, llm_client: LLMClient) -> None:
        self._strategies: dict[str, GenerationStrategy] = {
            "llm_gen": LLMGenerationStrategy(llm_client),
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

