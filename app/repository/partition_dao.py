from __future__ import annotations
from app.repository.memory_store import MemoryStore


class PartitionDao:
    def __init__(self, store: MemoryStore):
        self.store = store

    async def ensure_release_partitions(self, release_id: str) -> None:
        self.store.release_partitions.add(release_id)

