from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.enums import ReleaseStatus
from app.core.errors import ConflictError, NotFoundError
from app.core.ids import new_id
from app.repository.models.release import ReleaseOrm
from app.repository.records import ReleaseRecord


class ReleaseDao:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def create(self, name: str, description: str, config_snapshot: dict) -> ReleaseRecord:
        record = ReleaseOrm(
            id=new_id("rel"),
            name=name,
            description=description,
            status=ReleaseStatus.DRAFT,
            config_snapshot=config_snapshot,
        )
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    session.add(record)
                    await session.flush()
                    await session.refresh(record)
            return self._to_record(record)
        except IntegrityError as exc:
            raise ConflictError(f"Release name already exists: {name}") from exc

    async def get(self, release_id: str) -> ReleaseRecord | None:
        async with self.session_factory() as session:
            record = await session.get(ReleaseOrm, release_id)
            return self._to_record(record) if record is not None else None

    async def get_or_raise(self, release_id: str) -> ReleaseRecord:
        record = await self.get(release_id)
        if record is None:
            raise NotFoundError(f"Release not found: {release_id}")
        return record

    async def list(self) -> list[ReleaseRecord]:
        async with self.session_factory() as session:
            records = await session.scalars(
                select(ReleaseOrm).order_by(ReleaseOrm.created_at.desc())
            )
            return [self._to_record(record) for record in records]

    async def update_status(self, release_id: str, status: ReleaseStatus) -> ReleaseRecord:
        async with self.session_factory() as session:
            async with session.begin():
                record = await session.get(ReleaseOrm, release_id)
                if record is None:
                    raise NotFoundError(f"Release not found: {release_id}")
                record.status = status
                await session.flush()
                await session.refresh(record)
            return self._to_record(record)

    def _to_record(self, orm: ReleaseOrm) -> ReleaseRecord:
        return ReleaseRecord(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            status=orm.status,
            config_snapshot=orm.config_snapshot,
            created_at=orm.created_at,
        )
