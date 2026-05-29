from __future__ import annotations

from sqlalchemy import text
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.errors import ConflictError
from app.core.ids import new_uuid
from app.repository.models.chunk import ChunkOrm
from app.repository.records import ChunkCreate, ChunkRecord, TextSearchRecord


class ChunkDao:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def batch_insert_chunks(self, release_id: str, chunks: list[ChunkCreate]) -> list[str]:
        records = [
            ChunkOrm(
                id=new_uuid(),
                release_id=release_id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                char_count=len(chunk.content),
            )
            for chunk in chunks
        ]
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    session.add_all(records)
                    await session.flush()
            return [record.id for record in records]
        except IntegrityError as exc:
            raise ConflictError("Failed to insert chunks") from exc

    async def list_by_release(self, release_id: str) -> list[ChunkRecord]:
        async with self.session_factory() as session:
            records = await session.scalars(
                select(ChunkOrm)
                .where(ChunkOrm.release_id == release_id)
                .order_by(ChunkOrm.document_id, ChunkOrm.chunk_index)
            )
            return [self._to_record(record) for record in records]

    async def list_by_document(self, release_id: str, document_id: str) -> list[ChunkRecord]:
        async with self.session_factory() as session:
            records = await session.scalars(
                select(ChunkOrm)
                .where(
                    ChunkOrm.release_id == release_id,
                    ChunkOrm.document_id == document_id,
                )
                .order_by(ChunkOrm.chunk_index)
            )
            return [self._to_record(record) for record in records]

    async def list_by_ids(self, release_id: str, chunk_ids: list[str]) -> list[ChunkRecord]:
        if not chunk_ids:
            return []
        async with self.session_factory() as session:
            records = await session.scalars(
                select(ChunkOrm).where(
                    ChunkOrm.release_id == release_id,
                    ChunkOrm.id.in_(chunk_ids),
                )
            )
            return [self._to_record(record) for record in records]

    async def search_full_text_chunks(
        self,
        release_id: str,
        query: str,
        top_k: int,
    ) -> list[TextSearchRecord]:
        """全文检索方法"""

        if not query.strip():
            return []

        stmt = text(
            """
            SELECT
                id AS chunk_id,
                content,
                ts_rank_cd(
                    search_vector,
                    websearch_to_tsquery('simple', :query)
                ) AS score
            FROM chunks
            WHERE release_id = :release_id
            AND search_vector @@ websearch_to_tsquery('simple', :query)
            ORDER BY score DESC, id
            LIMIT :top_k
            """
        )

        async with self.session_factory() as session:
            rows = await session.execute(
                stmt,
                {
                    "release_id": release_id,
                    "query": query,
                    "top_k": top_k,
                },
            )

        return [
            TextSearchRecord(
                chunk_id=str(row.chunk_id),
                content=row.content,
                score=float(row.score),
            )
            for row in rows
        ]

    def _to_record(self, orm: ChunkOrm) -> ChunkRecord:
        return ChunkRecord(
            id=orm.id,
            release_id=orm.release_id,
            document_id=orm.document_id,
            chunk_index=orm.chunk_index,
            content=orm.content,
            char_count=orm.char_count,
            created_at=orm.created_at,
        )
