from __future__ import annotations
from app.core.enums import EvaluationRunStatus
from app.core.errors import ConflictError, NotFoundError
from app.core.ids import new_id
from app.repository.memory_store import MemoryStore
from app.repository.records import (
    EvaluationDatasetRecord,
    EvaluationItemCreate,
    EvaluationItemRecord,
    EvaluationMetricRecord,
    EvaluationQuestionCreate,
    EvaluationQuestionRecord,
    EvaluationRunRecord,
)


class EvaluationDao:
    def __init__(self, store: MemoryStore):
        self.store = store

    async def create_dataset(self, name: str, description: str) -> EvaluationDatasetRecord:
        if any(dataset.name == name for dataset in self.store.evaluation_datasets.values()):
            raise ConflictError(f"Dataset name already exists: {name}")
        record = EvaluationDatasetRecord(
            id=new_id("dataset"),
            name=name,
            description=description,
        )
        self.store.evaluation_datasets[record.id] = record
        return record

    async def list_datasets(self) -> list[EvaluationDatasetRecord]:
        return sorted(
            self.store.evaluation_datasets.values(),
            key=lambda dataset: dataset.created_at,
            reverse=True,
        )

    async def get_dataset(self, dataset_id: str) -> EvaluationDatasetRecord:
        record = self.store.evaluation_datasets.get(dataset_id)
        if record is None:
            raise NotFoundError(f"Dataset not found: {dataset_id}")
        return record

    async def add_questions(
        self,
        dataset_id: str,
        questions: list[EvaluationQuestionCreate],
    ) -> list[EvaluationQuestionRecord]:
        await self.get_dataset(dataset_id)
        records: list[EvaluationQuestionRecord] = []
        for question in questions:
            record = EvaluationQuestionRecord(
                id=new_id("question"),
                dataset_id=dataset_id,
                question_text=question.question_text,
                reference_answer=question.reference_answer,
            )
            self.store.evaluation_questions[record.id] = record
            records.append(record)
        return records

    async def list_questions(self, dataset_id: str) -> list[EvaluationQuestionRecord]:
        await self.get_dataset(dataset_id)
        return [
            question
            for question in self.store.evaluation_questions.values()
            if question.dataset_id == dataset_id
        ]

    async def create_run(
        self,
        release_id: str,
        dataset_id: str,
        config_snapshot: dict,
    ) -> EvaluationRunRecord:
        await self.get_dataset(dataset_id)
        record = EvaluationRunRecord(
            id=new_id("evalrun"),
            release_id=release_id,
            dataset_id=dataset_id,
            config_snapshot=config_snapshot,
            run_status=EvaluationRunStatus.RUNNING,
        )
        self.store.evaluation_runs[record.id] = record
        return record

    async def get_run(self, evaluation_run_id: str) -> EvaluationRunRecord:
        record = self.store.evaluation_runs.get(evaluation_run_id)
        if record is None:
            raise NotFoundError(f"Evaluation run not found: {evaluation_run_id}")
        return record

    async def update_run_status(
        self,
        evaluation_run_id: str,
        status: EvaluationRunStatus,
        total_count: int,
        success_count: int,
        failed_count: int,
    ) -> EvaluationRunRecord:
        record = await self.get_run(evaluation_run_id)
        record.run_status = status
        record.total_count = total_count
        record.success_count = success_count
        record.failed_count = failed_count
        return record

    async def create_item(
        self,
        evaluation_run_id: str,
        release_id: str,
        item: EvaluationItemCreate,
    ) -> EvaluationItemRecord:
        record = EvaluationItemRecord(
            id=new_id("evalitem"),
            evaluation_run_id=evaluation_run_id,
            question_id=item.question_id,
            release_id=release_id,
            retrieval_log_id=item.retrieval_log_id,
            answer_text=item.answer_text,
            citations_snapshot=item.citations_snapshot,
            judge_result=item.judge_result,
        )
        self.store.evaluation_items[record.id] = record
        return record

    async def list_items(self, evaluation_run_id: str) -> list[EvaluationItemRecord]:
        return [
            item
            for item in self.store.evaluation_items.values()
            if item.evaluation_run_id == evaluation_run_id
        ]

    async def update_item_judge_result(
        self,
        evaluation_item_id: str,
        judge_result: dict,
    ) -> EvaluationItemRecord:
        record = self.store.evaluation_items.get(evaluation_item_id)
        if record is None:
            raise NotFoundError(f"Evaluation item not found: {evaluation_item_id}")
        record.judge_result = judge_result
        return record

    async def create_metric(
        self,
        evaluation_run_id: str,
        metric_snapshot: dict,
    ) -> EvaluationMetricRecord:
        record = EvaluationMetricRecord(
            id=new_id("metric"),
            evaluation_run_id=evaluation_run_id,
            metric_snapshot=metric_snapshot,
        )
        self.store.evaluation_metrics[record.id] = record
        return record

    async def get_metric(self, evaluation_run_id: str) -> EvaluationMetricRecord:
        for metric in self.store.evaluation_metrics.values():
            if metric.evaluation_run_id == evaluation_run_id:
                return metric
        raise NotFoundError(f"Evaluation metric not found: {evaluation_run_id}")

