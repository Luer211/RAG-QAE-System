from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.enums import EvaluationRunStatus
from app.core.errors import ConflictError, NotFoundError
from app.core.ids import new_id
from app.repository.models.evaluation_dataset import EvaluationDatasetOrm
from app.repository.models.evaluation_item import EvaluationItemOrm
from app.repository.models.evaluation_metric import EvaluationMetricOrm
from app.repository.models.evaluation_question import EvaluationQuestionOrm
from app.repository.models.evaluation_run import EvaluationRunOrm
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
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def create_dataset(self, name: str, description: str) -> EvaluationDatasetRecord:
        record = EvaluationDatasetOrm(
            id=new_id("dataset"),
            name=name,
            description=description,
        )
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    session.add(record)
                    await session.flush()
                    await session.refresh(record)
            return self._dataset_record(record)
        except IntegrityError as exc:
            raise ConflictError(f"Dataset name already exists: {name}") from exc

    async def list_datasets(self) -> list[EvaluationDatasetRecord]:
        async with self.session_factory() as session:
            records = await session.scalars(
                select(EvaluationDatasetOrm).order_by(EvaluationDatasetOrm.created_at.desc())
            )
            return [self._dataset_record(record) for record in records]

    async def get_dataset(self, dataset_id: str) -> EvaluationDatasetRecord:
        async with self.session_factory() as session:
            record = await session.get(EvaluationDatasetOrm, dataset_id)
            if record is None:
                raise NotFoundError(f"Dataset not found: {dataset_id}")
            return self._dataset_record(record)

    async def add_questions(
        self,
        dataset_id: str,
        questions: list[EvaluationQuestionCreate],
    ) -> list[EvaluationQuestionRecord]:
        await self.get_dataset(dataset_id)
        records = [
            EvaluationQuestionOrm(
                id=new_id("question"),
                dataset_id=dataset_id,
                question_text=question.question_text,
                reference_answer=question.reference_answer,
            )
            for question in questions
        ]
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    session.add_all(records)
                    await session.flush()
                    for record in records:
                        await session.refresh(record)
            return [self._question_record(record) for record in records]
        except IntegrityError as exc:
            raise ConflictError("Failed to insert evaluation questions") from exc

    async def list_questions(self, dataset_id: str) -> list[EvaluationQuestionRecord]:
        await self.get_dataset(dataset_id)
        async with self.session_factory() as session:
            records = await session.scalars(
                select(EvaluationQuestionOrm)
                .where(EvaluationQuestionOrm.dataset_id == dataset_id)
                .order_by(EvaluationQuestionOrm.created_at)
            )
            return [self._question_record(record) for record in records]

    async def create_run(
        self,
        release_id: str,
        dataset_id: str,
        config_snapshot: dict,
    ) -> EvaluationRunRecord:
        await self.get_dataset(dataset_id)
        record = EvaluationRunOrm(
            id=new_id("evalrun"),
            release_id=release_id,
            dataset_id=dataset_id,
            config_snapshot=config_snapshot,
            run_status=EvaluationRunStatus.RUNNING,
        )
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    session.add(record)
                    await session.flush()
                    await session.refresh(record)
            return self._run_record(record)
        except IntegrityError as exc:
            raise ConflictError("Failed to create evaluation run") from exc

    async def get_run(self, evaluation_run_id: str) -> EvaluationRunRecord:
        async with self.session_factory() as session:
            record = await session.get(EvaluationRunOrm, evaluation_run_id)
            if record is None:
                raise NotFoundError(f"Evaluation run not found: {evaluation_run_id}")
            return self._run_record(record)

    async def update_run_status(
        self,
        evaluation_run_id: str,
        status: EvaluationRunStatus,
        total_count: int,
        success_count: int,
        failed_count: int,
    ) -> EvaluationRunRecord:
        async with self.session_factory() as session:
            async with session.begin():
                record = await session.get(EvaluationRunOrm, evaluation_run_id)
                if record is None:
                    raise NotFoundError(f"Evaluation run not found: {evaluation_run_id}")
                record.run_status = status
                record.total_count = total_count
                record.success_count = success_count
                record.failed_count = failed_count
                await session.flush()
                await session.refresh(record)
            return self._run_record(record)

    async def create_item(
        self,
        evaluation_run_id: str,
        release_id: str,
        item: EvaluationItemCreate,
    ) -> EvaluationItemRecord:
        record = EvaluationItemOrm(
            id=new_id("evalitem"),
            evaluation_run_id=evaluation_run_id,
            question_id=item.question_id,
            release_id=release_id,
            retrieval_log_id=item.retrieval_log_id,
            answer_text=item.answer_text,
            citations_snapshot=item.citations_snapshot,
            judge_result=item.judge_result,
        )
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    session.add(record)
                    await session.flush()
                    await session.refresh(record)
            return self._item_record(record)
        except IntegrityError as exc:
            raise ConflictError("Failed to create evaluation item") from exc

    async def list_items(self, evaluation_run_id: str) -> list[EvaluationItemRecord]:
        async with self.session_factory() as session:
            records = await session.scalars(
                select(EvaluationItemOrm)
                .where(EvaluationItemOrm.evaluation_run_id == evaluation_run_id)
                .order_by(EvaluationItemOrm.created_at)
            )
            return [self._item_record(record) for record in records]

    async def update_item_judge_result(
        self,
        evaluation_item_id: str,
        judge_result: dict,
    ) -> EvaluationItemRecord:
        async with self.session_factory() as session:
            async with session.begin():
                record = await session.get(EvaluationItemOrm, evaluation_item_id)
                if record is None:
                    raise NotFoundError(f"Evaluation item not found: {evaluation_item_id}")
                record.judge_result = judge_result
                await session.flush()
                await session.refresh(record)
            return self._item_record(record)

    async def create_metric(
        self,
        evaluation_run_id: str,
        metric_snapshot: dict,
    ) -> EvaluationMetricRecord:
        record = EvaluationMetricOrm(
            id=new_id("metric"),
            evaluation_run_id=evaluation_run_id,
            metric_snapshot=metric_snapshot,
        )
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    session.add(record)
                    await session.flush()
                    await session.refresh(record)
            return self._metric_record(record)
        except IntegrityError as exc:
            raise ConflictError("Failed to create evaluation metric") from exc

    async def get_metric(self, evaluation_run_id: str) -> EvaluationMetricRecord:
        async with self.session_factory() as session:
            record = await session.scalar(
                select(EvaluationMetricOrm).where(
                    EvaluationMetricOrm.evaluation_run_id == evaluation_run_id
                )
            )
            if record is None:
                raise NotFoundError(f"Evaluation metric not found: {evaluation_run_id}")
            return self._metric_record(record)

    def _dataset_record(self, orm: EvaluationDatasetOrm) -> EvaluationDatasetRecord:
        return EvaluationDatasetRecord(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            created_at=orm.created_at,
        )

    def _question_record(self, orm: EvaluationQuestionOrm) -> EvaluationQuestionRecord:
        return EvaluationQuestionRecord(
            id=orm.id,
            dataset_id=orm.dataset_id,
            question_text=orm.question_text,
            reference_answer=orm.reference_answer,
            created_at=orm.created_at,
        )

    def _run_record(self, orm: EvaluationRunOrm) -> EvaluationRunRecord:
        return EvaluationRunRecord(
            id=orm.id,
            release_id=orm.release_id,
            dataset_id=orm.dataset_id,
            config_snapshot=orm.config_snapshot,
            run_status=orm.run_status,
            total_count=orm.total_count,
            success_count=orm.success_count,
            failed_count=orm.failed_count,
            created_at=orm.created_at,
        )

    def _item_record(self, orm: EvaluationItemOrm) -> EvaluationItemRecord:
        return EvaluationItemRecord(
            id=orm.id,
            evaluation_run_id=orm.evaluation_run_id,
            question_id=orm.question_id,
            release_id=orm.release_id,
            retrieval_log_id=orm.retrieval_log_id,
            answer_text=orm.answer_text,
            citations_snapshot=orm.citations_snapshot,
            judge_result=orm.judge_result,
            created_at=orm.created_at,
        )

    def _metric_record(self, orm: EvaluationMetricOrm) -> EvaluationMetricRecord:
        return EvaluationMetricRecord(
            id=orm.id,
            evaluation_run_id=orm.evaluation_run_id,
            metric_snapshot=orm.metric_snapshot,
            created_at=orm.created_at,
        )
