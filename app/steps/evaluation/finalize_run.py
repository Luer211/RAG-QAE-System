from __future__ import annotations
from app.core.enums import EvaluationRunStatus
from app.repository.dao.evaluation_dao import EvaluationDao
from app.pipelines.evaluation.models import EvaluationState


class FinalizeEvaluationRunStep:
    def __init__(self, evaluation_dao: EvaluationDao):
        self.evaluation_dao = evaluation_dao

    async def run(self, state: EvaluationState) -> None:
        evaluation_run_id = state.runtime.evaluation_run_id or ""
        items = await self.evaluation_dao.list_items(evaluation_run_id)
        total_count = len(items)
        success_count = sum(1 for item in items if item.answer_text)
        failed_count = total_count - success_count
        if total_count == 0 or failed_count == total_count:
            status = EvaluationRunStatus.FAILED
        elif failed_count > 0:
            status = EvaluationRunStatus.PARTIAL_SUCCESS
        else:
            status = EvaluationRunStatus.SUCCESS

        await self.evaluation_dao.update_run_status(
            evaluation_run_id=evaluation_run_id,
            status=status,
            total_count=total_count,
            success_count=success_count,
            failed_count=failed_count,
        )

