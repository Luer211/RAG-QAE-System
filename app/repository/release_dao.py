from __future__ import annotations
from app.core.enums import ReleaseStatus
from app.core.errors import ConflictError, NotFoundError
from app.core.ids import new_id
from app.repository.memory_store import MemoryStore
from app.repository.records import ReleaseRecord


class ReleaseDao:
    def __init__(self, store: MemoryStore):
        self.store = store

    async def create(self, name: str, description: str, config_snapshot: dict) -> ReleaseRecord:
        if any(release.name == name for release in self.store.releases.values()):
            raise ConflictError(f"Release name already exists: {name}")

        record = ReleaseRecord(
            id=new_id("rel"),
            name=name,
            description=description,
            status=ReleaseStatus.DRAFT,
            config_snapshot=config_snapshot,
        )
        self.store.releases[record.id] = record
        return record

    async def get(self, release_id: str) -> ReleaseRecord | None:
        return self.store.releases.get(release_id)

    async def get_or_raise(self, release_id: str) -> ReleaseRecord:
        record = await self.get(release_id)
        if record is None:
            raise NotFoundError(f"Release not found: {release_id}")
        return record

    async def list(self) -> list[ReleaseRecord]:
        return sorted(self.store.releases.values(), key=lambda item: item.created_at, reverse=True)

    async def update_status(self, release_id: str, status: ReleaseStatus) -> ReleaseRecord:
        record = await self.get_or_raise(release_id)
        record.status = status
        return record

