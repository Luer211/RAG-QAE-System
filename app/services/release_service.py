from __future__ import annotations
from app.dao.chunk_dao import ChunkDao
from app.dao.document_dao import DocumentDao
from app.dao.partition_dao import PartitionDao
from app.dao.records import ChunkRecord, DocumentRecord, ReleaseRecord
from app.dao.release_dao import ReleaseDao
from app.services.dto.release import (
    ChunkServiceOutput,
    CreateReleaseServiceInput,
    DocumentServiceOutput,
    ReleaseServiceOutput,
)


class ReleaseService:
    def __init__(
        self,
        release_dao: ReleaseDao,
        partition_dao: PartitionDao,
        document_dao: DocumentDao,
        chunk_dao: ChunkDao,
    ):
        self.release_dao = release_dao
        self.partition_dao = partition_dao
        self.document_dao = document_dao
        self.chunk_dao = chunk_dao

    async def create_release(self, input_data: CreateReleaseServiceInput) -> ReleaseServiceOutput:
        release = await self.release_dao.create(
            name=input_data.name,
            description=input_data.description,
            config_snapshot=input_data.config_snapshot,
        )
        await self.partition_dao.ensure_release_partitions(release.id)
        return self._release_output(release)

    async def list_releases(self) -> list[ReleaseServiceOutput]:
        return [self._release_output(release) for release in await self.release_dao.list()]

    async def list_documents(self, release_id: str) -> list[DocumentServiceOutput]:
        await self.release_dao.get_or_raise(release_id)
        documents = await self.document_dao.list_by_release(release_id)
        return [self._document_output(document) for document in documents]

    async def get_document(self, release_id: str, document_id: str) -> DocumentServiceOutput:
        await self.release_dao.get_or_raise(release_id)
        return self._document_output(await self.document_dao.get(release_id, document_id))

    async def list_chunks(self, release_id: str, document_id: str) -> list[ChunkServiceOutput]:
        await self.document_dao.get(release_id, document_id)
        chunks = await self.chunk_dao.list_by_document(release_id, document_id)
        return [self._chunk_output(chunk) for chunk in chunks]

    def _release_output(self, record: ReleaseRecord) -> ReleaseServiceOutput:
        return ReleaseServiceOutput(
            id=record.id,
            name=record.name,
            description=record.description,
            status=record.status,
            config_snapshot=record.config_snapshot,
            created_at=record.created_at,
        )

    def _document_output(self, record: DocumentRecord) -> DocumentServiceOutput:
        return DocumentServiceOutput(
            id=record.id,
            release_id=record.release_id,
            title=record.title,
            content_raw=record.content_raw,
            content_cleaned=record.content_cleaned,
            created_at=record.created_at,
        )

    def _chunk_output(self, record: ChunkRecord) -> ChunkServiceOutput:
        return ChunkServiceOutput(
            id=record.id,
            release_id=record.release_id,
            document_id=record.document_id,
            chunk_index=record.chunk_index,
            content=record.content,
            char_count=record.char_count,
            created_at=record.created_at,
        )

