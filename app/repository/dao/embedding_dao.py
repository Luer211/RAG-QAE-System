from __future__ import annotations

from sqlalchemy.exc import IntegrityError

from app.core.errors import ConflictError
from app.core.ids import new_uuid
from app.repository.models.chunk_embedding import ChunkEmbeddingOrm
from app.repository.records import EmbeddingCreate


class EmbeddingDao:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def batch_insert_embeddings(
        self,
        release_id: str,
        embeddings: list[EmbeddingCreate],
    ) -> list[str]:
        records = [
            ChunkEmbeddingOrm(
                id=new_uuid(),
                release_id=release_id,
                chunk_id=embedding.chunk_id,
                embedding_model=embedding.embedding_model,
                embedding_dim=embedding.embedding_dim,
                vector=embedding.vector,
            )
            for embedding in embeddings
        ]
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    session.add_all(records)
                    await session.flush()
            return [record.id for record in records]
        except IntegrityError as exc:
            raise ConflictError("Failed to insert chunk embeddings") from exc
