from __future__ import annotations
from dataclasses import asdict

from app.repository.dao.retrieval_log_dao import RetrievalLogDao
from app.pipelines.retrieval.models import RetrievalState


class CreateRetrievalLogStep:
    def __init__(self, retrieval_log_dao: RetrievalLogDao):
        self.retrieval_log_dao = retrieval_log_dao

    async def run(self, state: RetrievalState) -> None:
        config_snapshot = {
            "rewrite_config": asdict(state.input.rewrite_config),
            "retrieval_config": asdict(state.input.retrieval_config),
            "rerank_config": asdict(state.input.rerank_config),
            "generation_config": asdict(state.input.generation_config),
        }
        log = await self.retrieval_log_dao.create_log(
            release_id=state.input.release_id,
            query_raw=state.input.query,
            config_snapshot=config_snapshot,
        )
        state.runtime.retrieval_log_id = log.id

