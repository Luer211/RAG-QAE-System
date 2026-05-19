from __future__ import annotations
from app.repository.dao.evaluation_dao import EvaluationDao
from app.domain.judging import JudgeAnswerInput, JudgeDomain
from app.pipelines.evaluation.models import EvaluationState


class JudgeEvaluationItemsStep:
    def __init__(self, evaluation_dao: EvaluationDao, judge_domain: JudgeDomain):
        self.evaluation_dao = evaluation_dao
        self.judge_domain = judge_domain

    async def run(self, state: EvaluationState) -> None:
        evaluation_run_id = state.runtime.evaluation_run_id or ""
        items = await self.evaluation_dao.list_items(evaluation_run_id)
        questions = await self.evaluation_dao.list_questions(state.input.dataset_id)
        question_map = {question.id: question for question in questions}

        for item in items:
            question = question_map[item.question_id]
            judge_output = await self.judge_domain.judge(
                JudgeAnswerInput(
                    question=question.question_text,
                    answer=item.answer_text,
                    reference_answer=question.reference_answer,
                    config=state.input.judge_config.to_domain_config(),
                )
            )
            await self.evaluation_dao.update_item_judge_result(
                evaluation_item_id=item.id,
                judge_result=judge_output.result,
            )

