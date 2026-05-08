from __future__ import annotations
from dataclasses import dataclass

from app.domain.common import DomainStrategyConfig


@dataclass(frozen=True)
class EmbedChunkInput:
    chunk_id: str
    content: str


@dataclass(frozen=True)
class ChunkEmbedding:
    chunk_id: str
    embedding_model: str
    embedding_dim: int
    vector: list[float]


@dataclass(frozen=True)
class EmbedChunksInput:
    chunks: list[EmbedChunkInput]
    config: DomainStrategyConfig


@dataclass(frozen=True)
class EmbedChunksOutput:
    embeddings: list[ChunkEmbedding]

