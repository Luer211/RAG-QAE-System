from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.errors import ConflictError
from app.core.ids import new_uuid
from app.repository.models.chunk import ChunkOrm
from app.repository.records import ChunkCreate, ChunkRecord


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
