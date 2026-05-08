from __future__ import annotations
from app.core.errors import NotFoundError
from app.core.ids import new_uuid
from app.dao.memory_store import MemoryStore
from app.dao.records import DocumentCreate, DocumentRecord


class DocumentDao:
    def __init__(self, store: MemoryStore):
        self.store = store

    async def batch_insert_cleaned_documents(
        self,
        release_id: str,
        documents: list[DocumentCreate],
    ) -> list[str]:
        ids: list[str] = []
        for document in documents:
            record = DocumentRecord(
                id=new_uuid(),
                release_id=release_id,
                title=document.title,
                content_raw=document.content_raw,
                content_cleaned=document.content_cleaned,
            )
            self.store.documents[record.id] = record
            ids.append(record.id)
        return ids

    async def list_by_release(self, release_id: str) -> list[DocumentRecord]:
        return [
            document
            for document in self.store.documents.values()
            if document.release_id == release_id
        ]

    async def list_by_ids(self, release_id: str, document_ids: list[str]) -> list[DocumentRecord]:
        wanted = set(document_ids)
        return [
            document
            for document in self.store.documents.values()
            if document.release_id == release_id and document.id in wanted
        ]

    async def get(self, release_id: str, document_id: str) -> DocumentRecord:
        record = self.store.documents.get(document_id)
        if record is None or record.release_id != release_id:
            raise NotFoundError(f"Document not found: {document_id}")
        return record

