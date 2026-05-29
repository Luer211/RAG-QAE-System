from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.errors import ConflictError
from app.core.ids import new_uuid
from app.repository.models.chunk import ChunkOrm
from app.repository.models.chunk_embedding import ChunkEmbeddingOrm
from app.repository.records import EmbeddingCreate, VectorSearchRecord


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

    async def search_similar_chunks(
            self,
            release_id: str,
            query_vector: list[float],
            embedding_model: str,
            top_k: int,
    ) -> list[VectorSearchRecord]:
        """余弦相似度检索排序"""

        distance = ChunkEmbeddingOrm.vector.cosine_distance(query_vector).label("distance")
        score = (1.0 - ChunkEmbeddingOrm.vector.cosine_distance(query_vector)).label("score")

        stmt = (
            select(
                ChunkEmbeddingOrm.chunk_id,
                ChunkOrm.content,
                distance,
                score,
            )
            .join(
                ChunkOrm,
                (ChunkOrm.release_id == ChunkEmbeddingOrm.release_id)
                & (ChunkOrm.id == ChunkEmbeddingOrm.chunk_id),
            )
            .where(
                ChunkEmbeddingOrm.release_id == release_id,
                ChunkEmbeddingOrm.embedding_model == embedding_model,
            )
            .order_by(distance)
            .limit(top_k)
        )

        async with self.session_factory() as session:
            rows = await session.execute(stmt)

        return [
            VectorSearchRecord(
                chunk_id=str(row.chunk_id),
                content=row.content,
                distance=float(row.distance),
                score=float(row.score),
            )
            for row in rows
        ]
        