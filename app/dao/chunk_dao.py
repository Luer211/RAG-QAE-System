from __future__ import annotations
from app.core.ids import new_uuid
from app.dao.memory_store import MemoryStore
from app.dao.records import ChunkCreate, ChunkRecord


class ChunkDao:
    def __init__(self, store: MemoryStore):
        self.store = store

    async def batch_insert_chunks(self, release_id: str, chunks: list[ChunkCreate]) -> list[str]:
        ids: list[str] = []
        for chunk in chunks:
            record = ChunkRecord(
                id=new_uuid(),
                release_id=release_id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                char_count=len(chunk.content),
            )
            self.store.chunks[record.id] = record
            ids.append(record.id)
        return ids

    async def list_by_release(self, release_id: str) -> list[ChunkRecord]:
        return [chunk for chunk in self.store.chunks.values() if chunk.release_id == release_id]

    async def list_by_document(self, release_id: str, document_id: str) -> list[ChunkRecord]:
        return [
            chunk
            for chunk in self.store.chunks.values()
            if chunk.release_id == release_id and chunk.document_id == document_id
        ]

    async def list_by_ids(self, release_id: str, chunk_ids: list[str]) -> list[ChunkRecord]:
        wanted = set(chunk_ids)
        return [
            chunk
            for chunk in self.store.chunks.values()
            if chunk.release_id == release_id and chunk.id in wanted
        ]

