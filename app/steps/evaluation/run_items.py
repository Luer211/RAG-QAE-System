from __future__ import annotations
from app.repository.dao.evaluation_dao import EvaluationDao
from app.repository.records import EvaluationItemCreate
from app.pipelines.evaluation.models import EvaluationState
from app.pipelines.retrieval import RetrievalPipeline, RetrievalPipelineInput


class RunEvaluationItemsStep:
    def __init__(
        self,
        evaluation_dao: EvaluationDao,
        retrieval_pipeline: RetrievalPipeline,
    ):
        self.evaluation_dao = evaluation_dao
        self.retrieval_pipeline = retrieval_pipeline

    async def run(self, state: EvaluationState) -> None:
        questions = await self.evaluation_dao.list_questions(state.input.dataset_id)
        evaluation_run_id = state.runtime.evaluation_run_id or ""

        for question in questions:
            retrieval_output = await self.retrieval_pipeline.run(
                RetrievalPipelineInput(
                    release_id=state.input.release_id,
                    query=question.question_text,
                    rewrite_config=state.input.rewrite_config,
                    retrieval_config=state.input.retrieval_config,
                    rerank_config=state.input.rerank_config,
                    generation_config=state.input.generation_config,
                ),
                ctx=state.ctx,
            )
            await self.evaluation_dao.create_item(
                evaluation_run_id=evaluation_run_id,
                release_id=state.input.release_id,
                item=EvaluationItemCreate(
                    question_id=question.id,
                    retrieval_log_id=retrieval_output.retrieval_log_id,
                    answer_text=retrieval_output.answer,
                    citations_snapshot=[
                        {
                            "release_id": citation.release_id,
                            "chunk_id": citation.chunk_id,
                            "citation_order": citation.citation_order,
                            "content": citation.content,
                        }
                        for citation in retrieval_output.citations
                    ],
                ),
            )

