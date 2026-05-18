from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.errors import ConflictError, NotFoundError
from app.core.ids import new_uuid
from app.repository.models.document import DocumentOrm
from app.repository.records import DocumentCreate, DocumentRecord


class DocumentDao:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def batch_insert_cleaned_documents(
        self,
        release_id: str,
        documents: list[DocumentCreate],
    ) -> list[str]:
        records = [
            DocumentOrm(
                id=new_uuid(),
                release_id=release_id,
                title=document.title,
                content_raw=document.content_raw,
                content_cleaned=document.content_cleaned,
            )
            for document in documents
        ]
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    session.add_all(records)
                    await session.flush()
            return [record.id for record in records]
        except IntegrityError as exc:
            raise ConflictError("Failed to insert documents") from exc

    async def list_by_release(self, release_id: str) -> list[DocumentRecord]:
        async with self.session_factory() as session:
            records = await session.scalars(
                select(DocumentOrm).where(DocumentOrm.release_id == release_id)
            )
            return [self._to_record(record) for record in records]

    async def list_by_ids(self, release_id: str, document_ids: list[str]) -> list[DocumentRecord]:
        if not document_ids:
            return []
        async with self.session_factory() as session:
            records = await session.scalars(
                select(DocumentOrm).where(
                    DocumentOrm.release_id == release_id,
                    DocumentOrm.id.in_(document_ids),
                )
            )
            return [self._to_record(record) for record in records]

    async def get(self, release_id: str, document_id: str) -> DocumentRecord:
        async with self.session_factory() as session:
            record = await session.scalar(
                select(DocumentOrm).where(
                    DocumentOrm.release_id == release_id,
                    DocumentOrm.id == document_id,
                )
            )
            if record is None:
                raise NotFoundError(f"Document not found: {document_id}")
            return self._to_record(record)

    def _to_record(self, orm: DocumentOrm) -> DocumentRecord:
        return DocumentRecord(
            id=orm.id,
            release_id=orm.release_id,
            title=orm.title,
            content_raw=orm.content_raw,
            content_cleaned=orm.content_cleaned,
            created_at=orm.created_at,
        )
