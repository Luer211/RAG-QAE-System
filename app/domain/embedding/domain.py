from __future__ import annotations
from hashlib import sha256
from typing import Protocol

from app.core.errors import InvalidStateError
from app.domain.embedding.models import ChunkEmbedding, EmbedChunksInput, EmbedChunksOutput


class EmbeddingStrategy(Protocol):
    async def embed(self, input_data: EmbedChunksInput) -> EmbedChunksOutput:
        ...


class MockEmbeddingStrategy:
    embedding_model = "mock_model"
    embedding_dim = 1536

    async def embed(self, input_data: EmbedChunksInput) -> EmbedChunksOutput:
        embeddings = [
            ChunkEmbedding(
                chunk_id=chunk.chunk_id,
                embedding_model=self.embedding_model,
                embedding_dim=self.embedding_dim,
                vector=self._vectorize(chunk.content),
            )
            for chunk in input_data.chunks
        ]
        return EmbedChunksOutput(embeddings=embeddings)

    def _vectorize(self, text: str) -> list[float]:
        digest = sha256(text.encode("utf-8")).digest()
        return [round(digest[i] / 255, 6) for i in range(self.embedding_dim)]


class EmbeddingStrategyFactory:
    def __init__(self) -> None:
        self._strategies: dict[str, EmbeddingStrategy] = {
            "mock_model": MockEmbeddingStrategy(),
        }

    def get(self, strategy_key: str) -> EmbeddingStrategy:
        try:
            return self._strategies[strategy_key]
        except KeyError as exc:
            raise InvalidStateError(f"Unknown embedding strategy: {strategy_key}") from exc


class EmbedDomain:
    def __init__(self, strategy_factory: EmbeddingStrategyFactory):
        self.strategy_factory = strategy_factory

    async def embed(self, input_data: EmbedChunksInput) -> EmbedChunksOutput:
        strategy = self.strategy_factory.get(input_data.config.strategy_key)
        return await strategy.embed(input_data)

