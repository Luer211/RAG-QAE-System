from __future__ import annotations
from typing import Protocol

from app.core.errors import InvalidStateError
from app.domain.chunking.models import ChunkDocumentsInput, ChunkDocumentsOutput, ChunkedText


class ChunkerStrategy(Protocol):
    async def chunk(self, input_data: ChunkDocumentsInput) -> ChunkDocumentsOutput:
        ...


class MockChunkerStrategy:
    def __init__(self, max_chars: int = 800) -> None:
        self.max_chars = max_chars

    async def chunk(self, input_data: ChunkDocumentsInput) -> ChunkDocumentsOutput:
        chunks: list[ChunkedText] = []
        for document in input_data.documents:
            text = document.content_cleaned.strip()
            if not text:
                continue
            for index, start in enumerate(range(0, len(text), self.max_chars)):
                chunks.append(
                    ChunkedText(
                        document_id=document.document_id,
                        chunk_index=index,
                        content=text[start : start + self.max_chars],
                    )
                )
        return ChunkDocumentsOutput(chunks=chunks)


class ChunkerStrategyFactory:
    def __init__(self) -> None:
        self._strategies: dict[str, ChunkerStrategy] = {
            "mock_chunk": MockChunkerStrategy(),
        }

    def get(self, strategy_key: str) -> ChunkerStrategy:
        try:
            return self._strategies[strategy_key]
        except KeyError as exc:
            raise InvalidStateError(f"Unknown chunker strategy: {strategy_key}") from exc


class ChunkDomain:
    def __init__(self, strategy_factory: ChunkerStrategyFactory):
        self.strategy_factory = strategy_factory

    async def chunk(self, input_data: ChunkDocumentsInput) -> ChunkDocumentsOutput:
        strategy = self.strategy_factory.get(input_data.config.strategy_key)
        return await strategy.chunk(input_data)

