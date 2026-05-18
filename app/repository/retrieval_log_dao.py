from __future__ import annotations
from app.core.errors import NotFoundError
from app.core.ids import new_id
from app.repository.memory_store import MemoryStore
from app.repository.records import (
    AnswerCitationCreate,
    AnswerCitationRecord,
    RetrievalItemCreate,
    RetrievalItemRecord,
    RetrievalLogRecord,
)


class RetrievalLogDao:
    def __init__(self, store: MemoryStore):
        self.store = store

    async def create_log(
        self,
        release_id: str,
        query_raw: str,
        config_snapshot: dict,
    ) -> RetrievalLogRecord:
        record = RetrievalLogRecord(
            id=new_id("retlog"),
            release_id=release_id,
            query_raw=query_raw,
            query_rewritten=None,
            rewrite_used=None,
            answer_text=None,
            config_snapshot=config_snapshot,
        )
        self.store.retrieval_logs[record.id] = record
        return record

    async def update_rewrite(
        self,
        retrieval_log_id: str,
        query_rewritten: str,
        rewrite_used: str,
    ) -> RetrievalLogRecord:
        record = await self.get(retrieval_log_id)
        record.query_rewritten = query_rewritten
        record.rewrite_used = rewrite_used
        return record

    async def update_answer(self, retrieval_log_id: str, answer_text: str) -> RetrievalLogRecord:
        record = await self.get(retrieval_log_id)
        record.answer_text = answer_text
        return record

    async def batch_insert_items(
        self,
        retrieval_log_id: str,
        release_id: str,
        items: list[RetrievalItemCreate],
    ) -> list[RetrievalItemRecord]:
        records: list[RetrievalItemRecord] = []
        for item in items:
            record = RetrievalItemRecord(
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
            self.store.retrieval_items[record.id] = record
            records.append(record)
        return records

    async def batch_insert_citations(
        self,
        retrieval_log_id: str,
        release_id: str,
        citations: list[AnswerCitationCreate],
    ) -> list[AnswerCitationRecord]:
        records: list[AnswerCitationRecord] = []
        for citation in citations:
            record = AnswerCitationRecord(
                id=new_id("cite"),
                retrieval_log_id=retrieval_log_id,
                release_id=release_id,
                chunk_id=citation.chunk_id,
                citation_order=citation.citation_order,
                content=citation.content,
            )
            self.store.answer_citations[record.id] = record
            records.append(record)
        return records

    async def get(self, retrieval_log_id: str) -> RetrievalLogRecord:
        record = self.store.retrieval_logs.get(retrieval_log_id)
        if record is None:
            raise NotFoundError(f"Retrieval log not found: {retrieval_log_id}")
        return record

    async def list_items(self, retrieval_log_id: str) -> list[RetrievalItemRecord]:
        return [
            item
            for item in self.store.retrieval_items.values()
            if item.retrieval_log_id == retrieval_log_id
        ]

    async def list_citations(self, retrieval_log_id: str) -> list[AnswerCitationRecord]:
        return sorted(
            [
                citation
                for citation in self.store.answer_citations.values()
                if citation.retrieval_log_id == retrieval_log_id
            ],
            key=lambda citation: citation.citation_order,
        )

