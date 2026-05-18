from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.errors import ConflictError, NotFoundError
from app.core.ids import new_id
from app.repository.models.answer_citation import AnswerCitationOrm
from app.repository.models.retrieval_item import RetrievalItemOrm
from app.repository.models.retrieval_log import RetrievalLogOrm
from app.repository.records import (
    AnswerCitationCreate,
    AnswerCitationRecord,
    RetrievalItemCreate,
    RetrievalItemRecord,
    RetrievalLogRecord,
)


class RetrievalLogDao:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def create_log(
        self,
        release_id: str,
        query_raw: str,
        config_snapshot: dict,
    ) -> RetrievalLogRecord:
        record = RetrievalLogOrm(
            id=new_id("retlog"),
            release_id=release_id,
            query_raw=query_raw,
            query_rewritten=None,
            rewrite_used=None,
            answer_text=None,
            config_snapshot=config_snapshot,
        )
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    session.add(record)
                    await session.flush()
                    await session.refresh(record)
            return self._log_record(record)
        except IntegrityError as exc:
            raise ConflictError("Failed to create retrieval log") from exc

    async def update_rewrite(
        self,
        retrieval_log_id: str,
        query_rewritten: str,
        rewrite_used: str,
    ) -> RetrievalLogRecord:
        async with self.session_factory() as session:
            async with session.begin():
                record = await self._get_log_orm(session, retrieval_log_id)
                record.query_rewritten = query_rewritten
                record.rewrite_used = rewrite_used
                await session.flush()
                await session.refresh(record)
            return self._log_record(record)

    async def update_answer(self, retrieval_log_id: str, answer_text: str) -> RetrievalLogRecord:
        async with self.session_factory() as session:
            async with session.begin():
                record = await self._get_log_orm(session, retrieval_log_id)
                record.answer_text = answer_text
                await session.flush()
                await session.refresh(record)
            return self._log_record(record)

    async def batch_insert_items(
        self,
        retrieval_log_id: str,
        release_id: str,
        items: list[RetrievalItemCreate],
    ) -> list[RetrievalItemRecord]:
        records = [
            RetrievalItemOrm(
                id=new_id("retitem"),
                retrieval_log_id=retrieval_log_id,
                release_id=release_id,
                chunk_id=item.chunk_id,
                source_type=item.source_type,
                raw_score=item.raw_score,
                rerank_score=item.rerank_score,
                rank_before_rerank=item.rank_before_rerank,
                rank_after_rerank=item.rank_after_rerank,
                selected_for_context=item.selected_for_context,
            )
            for item in items
        ]
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    session.add_all(records)
                    await session.flush()
                    for record in records:
                        await session.refresh(record)
            return [self._item_record(record) for record in records]
        except IntegrityError as exc:
            raise ConflictError("Failed to insert retrieval items") from exc

    async def batch_insert_citations(
        self,
        retrieval_log_id: str,
        release_id: str,
        citations: list[AnswerCitationCreate],
    ) -> list[AnswerCitationRecord]:
        records = [
            AnswerCitationOrm(
                id=new_id("cite"),
                retrieval_log_id=retrieval_log_id,
                release_id=release_id,
                chunk_id=citation.chunk_id,
                citation_order=citation.citation_order,
            )
            for citation in citations
        ]
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    session.add_all(records)
                    await session.flush()
                    for record in records:
                        await session.refresh(record)
            return [self._citation_record(record) for record in records]
        except IntegrityError as exc:
            raise ConflictError("Failed to insert answer citations") from exc

    async def get(self, retrieval_log_id: str) -> RetrievalLogRecord:
        async with self.session_factory() as session:
            record = await self._get_log_orm(session, retrieval_log_id)
            return self._log_record(record)

    async def list_items(self, retrieval_log_id: str) -> list[RetrievalItemRecord]:
        async with self.session_factory() as session:
            records = await session.scalars(
                select(RetrievalItemOrm)
                .where(RetrievalItemOrm.retrieval_log_id == retrieval_log_id)
                .order_by(RetrievalItemOrm.rank_after_rerank, RetrievalItemOrm.rank_before_rerank)
            )
            return [self._item_record(record) for record in records]

    async def list_citations(self, retrieval_log_id: str) -> list[AnswerCitationRecord]:
        async with self.session_factory() as session:
            records = await session.scalars(
                select(AnswerCitationOrm)
                .where(AnswerCitationOrm.retrieval_log_id == retrieval_log_id)
                .order_by(AnswerCitationOrm.citation_order)
            )
            return [self._citation_record(record) for record in records]

    async def _get_log_orm(self, session, retrieval_log_id: str) -> RetrievalLogOrm:
        record = await session.get(RetrievalLogOrm, retrieval_log_id)
        if record is None:
            raise NotFoundError(f"Retrieval log not found: {retrieval_log_id}")
        return record

    def _log_record(self, orm: RetrievalLogOrm) -> RetrievalLogRecord:
        return RetrievalLogRecord(
            id=orm.id,
            release_id=orm.release_id,
            query_raw=orm.query_raw,
            query_rewritten=orm.query_rewritten,
            rewrite_used=orm.rewrite_used,
            answer_text=orm.answer_text,
            config_snapshot=orm.config_snapshot,
            created_at=orm.created_at,
        )

    def _item_record(self, orm: RetrievalItemOrm) -> RetrievalItemRecord:
        return RetrievalItemRecord(
            id=orm.id,
            retrieval_log_id=orm.retrieval_log_id,
            release_id=orm.release_id,
            chunk_id=orm.chunk_id,
            source_type=orm.source_type,
            raw_score=orm.raw_score,
            rerank_score=orm.rerank_score,
            rank_before_rerank=orm.rank_before_rerank,
            rank_after_rerank=orm.rank_after_rerank,
            selected_for_context=orm.selected_for_context,
            created_at=orm.created_at,
        )

    def _citation_record(self, orm: AnswerCitationOrm) -> AnswerCitationRecord:
        return AnswerCitationRecord(
            id=orm.id,
            retrieval_log_id=orm.retrieval_log_id,
            release_id=orm.release_id,
            chunk_id=orm.chunk_id,
            citation_order=orm.citation_order,
            content=None,
            created_at=orm.created_at,
        )
