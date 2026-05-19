from __future__ import annotations
from app.repository.dao.evaluation_dao import EvaluationDao
from app.pipelines.evaluation.models import EvaluationPipelineOutput, EvaluationState


class CreateEvaluationMetricsStep:
    def __init__(self, evaluation_dao: EvaluationDao):
        self.evaluation_dao = evaluation_dao

    async def run(self, state: EvaluationState) -> None:
        evaluation_run_id = state.runtime.evaluation_run_id or ""
        items = await self.evaluation_dao.list_items(evaluation_run_id)
        scores = [
            float(item.judge_result.get("score", 0.0))
            for item in items
            if item.judge_result
        ]
        metric_snapshot = {
            "item_count": len(items),
            "judged_count": len(scores),
            "average_score": sum(scores) / len(scores) if scores else 0.0,
        }
        await self.evaluation_dao.create_metric(
            evaluation_run_id=evaluation_run_id,
            metric_snapshot=metric_snapshot,
        )
        state.output = EvaluationPipelineOutput(evaluation_run_id=evaluation_run_id)

