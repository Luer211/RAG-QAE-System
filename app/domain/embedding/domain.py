from __future__ import annotations
from hashlib import sha256
from typing import Protocol

from app.core.errors import InvalidStateError
from app.infra.embedding import EmbeddingClient
from app.domain.embedding.models import ChunkEmbedding, EmbedChunksInput, EmbedChunksOutput


class EmbeddingStrategy(Protocol):
    async def embed(self, input_data: EmbedChunksInput) -> EmbedChunksOutput:
        ...


# Todo: 我们这里应该是直接使用，嗯model的话固定下来就好了。
class OpenAIEmbeddingStrategy:
    embedding_dim = 1536

    def __init__(self, client: EmbeddingClient):
        self.client = client
        self.model = "open_embedding_small"
    
    async def embed(self, input_data: EmbedChunksInput) -> EmbedChunksOutput:
        vectors = await self.client.embed(
            texts=[chunk.content for chunk in input_data.chunks],
            model=self.model,
        )

        return EmbedChunksOutput(
            embeddings=[
                ChunkEmbedding(
                    chunk_id=chunk.chunk_id,
                    embedding_model=self.model,
                    embedding_dim=self.embedding_dim,
                    vector=vector
                )
                for chunk, vector in zip(input_data.chunks, vectors)
            ]
        )


class EmbeddingStrategyFactory:
    def __init__(self, embedding_client: EmbeddingClient) -> None:
        self._strategies: dict[str, EmbeddingStrategy] = {
            "open_ai_model": OpenAIEmbeddingStrategy(embedding_client),
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

