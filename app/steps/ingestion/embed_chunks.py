from __future__ import annotations
from app.repository.chunk_dao import ChunkDao
from app.repository.embedding_dao import EmbeddingDao
from app.repository.records import EmbeddingCreate
from app.domain.embedding import EmbedChunkInput, EmbedChunksInput, EmbedDomain
from app.pipelines.ingestion.models import IngestState


class EmbedChunksStep:
    def __init__(
        self,
        embed_domain: EmbedDomain,
        chunk_dao: ChunkDao,
        embedding_dao: EmbeddingDao,
    ):
        self.embed_domain = embed_domain
        self.chunk_dao = chunk_dao
        self.embedding_dao = embedding_dao

    async def run(self, state: IngestState) -> None:
        chunks = await self.chunk_dao.list_by_ids(
            release_id=state.input.release_id,
            chunk_ids=state.runtime.chunk_ids,
        )
        domain_input = EmbedChunksInput(
            chunks=[EmbedChunkInput(chunk_id=chunk.id, content=chunk.content) for chunk in chunks],
            config=state.input.embedding_config.to_domain_config(),
        )
        domain_output = await self.embed_domain.embed(domain_input)

        state.runtime.chunk_embedding_ids = await self.embedding_dao.batch_insert_embeddings(
            release_id=state.input.release_id,
            embeddings=[
                EmbeddingCreate(
                    chunk_id=embedding.chunk_id,
                    embedding_model=embedding.embedding_model,
                    embedding_dim=embedding.embedding_dim,
                    vector=embedding.vector,
                )
                for embedding in domain_output.embeddings
            ],
        )

