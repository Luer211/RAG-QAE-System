from __future__ import annotations
from typing import Protocol

from app.infra.embedding.client import EmbeddingClient
from app.core.errors import InvalidStateError
from app.domain.retrieval.models import RetrieveChunksInput, RetrieveChunksOutput, RetrievedChunk
from app.repository.dao.embedding_dao import EmbeddingDao


class RetrievalStrategy(Protocol):
    async def retrieve(self, input_data: RetrieveChunksInput) -> RetrieveChunksOutput:
        ...


class PgVectorRetrievalStrategy:
    def __init__(
        self,
        embedding_client: EmbeddingClient,
        embedding_dao: EmbeddingDao,
        # Todo: 这里需要我们考虑一件事情，model的选择究竟应该怎么做
        embedding_model: str = "text-embedding-3-small",
    ):
        self.embedding_client = embedding_client
        self.embedding_dao = embedding_dao
        self.embedding_model = embedding_model

    async def retrieve(self, input_data: RetrieveChunksInput) -> RetrieveChunksOutput:
        top_k = int(input_data.config.params.get("top_k", 10))
        self.embedding_model = input_data.config.params.get(
            "embedding_model",
            self.embedding_model,
        )

        query_vectors = await self.embedding_client.embed(
            texts=[input_data.query],
            model=self.embedding_model,
        )
        query_vector = query_vectors[0]

        rows = await self.embedding_dao.search_similar_chunks(
            release_id=input_data.release_id,
            query_vector=query_vector,
            embedding_model=self.embedding_model,
            top_k=top_k
        )

        return RetrieveChunksOutput(
            items=[
                RetrievedChunk(
                    chunk_id=row.chunk_id,
                    content=row.content,
                    source_type="pgvector",
                    raw_score=row.score,
                    rank_before_rerank=index+1,
                )
                for index, row in enumerate(rows)
            ]
        )


class RetrievalStrategyFactory:
    def __init__(self, embedding_client=None, embedding_dao=None) -> None:
        self._strategies: dict[str, RetrievalStrategy] = {
            "pgvector_retrieval": PgVectorRetrievalStrategy(
                embedding_client=embedding_client,
                embedding_dao=embedding_dao,
            )
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

