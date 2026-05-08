from __future__ import annotations
from app.core.enums import ReleaseStatus
from app.dao.release_dao import ReleaseDao
from app.pipelines.ingestion.models import IngestPipelineOutput, IngestState


class MarkReleaseReadyStep:
    def __init__(self, release_dao: ReleaseDao):
        self.release_dao = release_dao

    async def run(self, state: IngestState) -> None:
        release = await self.release_dao.update_status(
            release_id=state.input.release_id,
            status=ReleaseStatus.READY,
        )
        state.output = IngestPipelineOutput(release_status=release.status)

