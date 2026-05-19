from __future__ import annotations
from app.core.context import new_request_context
from app.repository.dao.evaluation_dao import EvaluationDao
from app.repository.records import (
    EvaluationDatasetRecord,
    EvaluationItemRecord,
    EvaluationMetricRecord,
    EvaluationQuestionCreate,
    EvaluationQuestionRecord,
    EvaluationRunRecord,
)
from app.repository.dao.release_dao import ReleaseDao
from app.pipelines.evaluation import EvaluationPipeline, EvaluationPipelineInput
from app.services.dto.evaluation import (
    AddQuestionServiceInput,
    CreateDatasetServiceInput,
    DatasetServiceOutput,
    EvaluationItemServiceOutput,
    EvaluationMetricServiceOutput,
    EvaluationRunServiceInput,
    EvaluationRunServiceOutput,
    QuestionServiceOutput,
)
from app.services.mapping import to_pipeline_config


class EvaluationService:
    def __init__(
        self,
        release_dao: ReleaseDao,
        evaluation_dao: EvaluationDao,
        evaluation_pipeline: EvaluationPipeline,
    ):
        self.release_dao = release_dao
        self.evaluation_dao = evaluation_dao
        self.evaluation_pipeline = evaluation_pipeline

    async def create_dataset(self, input_data: CreateDatasetServiceInput) -> DatasetServiceOutput:
        return self._dataset_output(
            await self.evaluation_dao.create_dataset(
                name=input_data.name,
                description=input_data.description,
            )
        )

    async def list_datasets(self) -> list[DatasetServiceOutput]:
        return [
            self._dataset_output(dataset)
            for dataset in await self.evaluation_dao.list_datasets()
        ]

    async def add_questions(
        self,
        dataset_id: str,
        questions: list[AddQuestionServiceInput],
    ) -> list[QuestionServiceOutput]:
        records = await self.evaluation_dao.add_questions(
            dataset_id=dataset_id,
            questions=[
                EvaluationQuestionCreate(
                    question_text=question.question_text,
                    reference_answer=question.reference_answer,
                )
                for question in questions
            ],
        )
        return [self._question_output(record) for record in records]

    async def list_questions(self, dataset_id: str) -> list[QuestionServiceOutput]:
        return [
            self._question_output(question)
            for question in await self.evaluation_dao.list_questions(dataset_id)
        ]

    async def run_evaluation(
        self,
        input_data: EvaluationRunServiceInput,
    ) -> EvaluationRunServiceOutput:
        await self.release_dao.get_or_raise(input_data.release_id)
        output = await self.evaluation_pipeline.run(
            EvaluationPipelineInput(
                release_id=input_data.release_id,
                dataset_id=input_data.dataset_id,
                rewrite_config=to_pipeline_config(input_data.rewrite_config),
                retrieval_config=to_pipeline_config(input_data.retrieval_config),
                rerank_config=to_pipeline_config(input_data.rerank_config),
                generation_config=to_pipeline_config(input_data.generation_config),
                judge_config=to_pipeline_config(input_data.judge_config),
            ),
            ctx=new_request_context(),
        )
        return self._run_output(await self.evaluation_dao.get_run(output.evaluation_run_id))

    async def get_run(self, evaluation_run_id: str) -> EvaluationRunServiceOutput:
        return self._run_output(await self.evaluation_dao.get_run(evaluation_run_id))

    async def list_run_items(self, evaluation_run_id: str) -> list[EvaluationItemServiceOutput]:
        await self.evaluation_dao.get_run(evaluation_run_id)
        return [
            self._item_output(item)
            for item in await self.evaluation_dao.list_items(evaluation_run_id)
        ]

    async def get_metrics(self, evaluation_run_id: str) -> EvaluationMetricServiceOutput:
        await self.evaluation_dao.get_run(evaluation_run_id)
        return self._metric_output(await self.evaluation_dao.get_metric(evaluation_run_id))

    def _dataset_output(self, record: EvaluationDatasetRecord) -> DatasetServiceOutput:
        return DatasetServiceOutput(
            id=record.id,
            name=record.name,
            description=record.description,
            created_at=record.created_at,
        )

    def _question_output(self, record: EvaluationQuestionRecord) -> QuestionServiceOutput:
        return QuestionServiceOutput(
            id=record.id,
            dataset_id=record.dataset_id,
            question_text=record.question_text,
            reference_answer=record.reference_answer,
            created_at=record.created_at,
        )

    def _run_output(self, record: EvaluationRunRecord) -> EvaluationRunServiceOutput:
        return EvaluationRunServiceOutput(
            id=record.id,
            release_id=record.release_id,
            dataset_id=record.dataset_id,
            run_status=record.run_status,
            total_count=record.total_count,
            success_count=record.success_count,
            failed_count=record.failed_count,
            created_at=record.created_at,
        )

    def _item_output(self, record: EvaluationItemRecord) -> EvaluationItemServiceOutput:
        return EvaluationItemServiceOutput(
            id=record.id,
            evaluation_run_id=record.evaluation_run_id,
            question_id=record.question_id,
            retrieval_log_id=record.retrieval_log_id,
            answer_text=record.answer_text,
            citations_snapshot=record.citations_snapshot,
            judge_result=record.judge_result,
            created_at=record.created_at,
        )

    def _metric_output(self, record: EvaluationMetricRecord) -> EvaluationMetricServiceOutput:
        return EvaluationMetricServiceOutput(
            evaluation_run_id=record.evaluation_run_id,
            metric_snapshot=record.metric_snapshot,
        )

