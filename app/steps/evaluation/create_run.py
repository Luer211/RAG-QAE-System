from __future__ import annotations
from dataclasses import asdict

from app.dao.evaluation_dao import EvaluationDao
from app.pipelines.evaluation.models import EvaluationState


class CreateEvaluationRunStep:
    def __init__(self, evaluation_dao: EvaluationDao):
        self.evaluation_dao = evaluation_dao

    async def run(self, state: EvaluationState) -> None:
        config_snapshot = {
            "rewrite_config": asdict(state.input.rewrite_config),
            "retrieval_config": asdict(state.input.retrieval_config),
            "rerank_config": asdict(state.input.rerank_config),
            "generation_config": asdict(state.input.generation_config),
            "judge_config": asdict(state.input.judge_config),
        }
        run = await self.evaluation_dao.create_run(
            release_id=state.input.release_id,
            dataset_id=state.input.dataset_id,
            config_snapshot=config_snapshot,
        )
        state.runtime.evaluation_run_id = run.id

