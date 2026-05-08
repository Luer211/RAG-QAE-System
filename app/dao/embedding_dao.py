from __future__ import annotations
from app.core.ids import new_uuid
from app.dao.memory_store import MemoryStore
from app.dao.records import ChunkEmbeddingRecord, EmbeddingCreate


class EmbeddingDao:
    def __init__(self, store: MemoryStore):
        self.store = store

    async def batch_insert_embeddings(
        self,
        release_id: str,
        embeddings: list[EmbeddingCreate],
    ) -> list[str]:
        ids: list[str] = []
        for embedding in embeddings:
            record = ChunkEmbeddingRecord(
                id=new_uuid(),
                release_id=release_id,
                chunk_id=embedding.chunk_id,
                embedding_model=embedding.embedding_model,
                embedding_dim=embedding.embedding_dim,
                vector=embedding.vector,
            )
            self.store.chunk_embeddings[record.id] = record
            ids.append(record.id)
        return ids

