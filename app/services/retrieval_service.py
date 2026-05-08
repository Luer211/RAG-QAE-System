from __future__ import annotations
from app.core.context import new_request_context
from app.dao.records import AnswerCitationRecord, RetrievalItemRecord, RetrievalLogRecord
from app.dao.release_dao import ReleaseDao
from app.dao.retrieval_log_dao import RetrievalLogDao
from app.pipelines.retrieval import RetrievalPipeline, RetrievalPipelineInput
from app.services.dto.retrieval import (
    CitationServiceOutput,
    RetrievalItemServiceOutput,
    RetrievalLogServiceOutput,
    RetrievalServiceInput,
    RetrievalServiceOutput,
)
from app.services.mapping import to_pipeline_config


class RetrievalService:
    def __init__(
        self,
        release_dao: ReleaseDao,
        retrieval_log_dao: RetrievalLogDao,
        retrieval_pipeline: RetrievalPipeline,
    ):
        self.release_dao = release_dao
        self.retrieval_log_dao = retrieval_log_dao
        self.retrieval_pipeline = retrieval_pipeline

    async def query(self, input_data: RetrievalServiceInput) -> RetrievalServiceOutput:
        await self.release_dao.get_or_raise(input_data.release_id)
        output = await self.retrieval_pipeline.run(
            RetrievalPipelineInput(
                release_id=input_data.release_id,
                query=input_data.query,
                rewrite_config=to_pipeline_config(input_data.rewrite_config),
                retrieval_config=to_pipeline_config(input_data.retrieval_config),
                rerank_config=to_pipeline_config(input_data.rerank_config),
                generation_config=to_pipeline_config(input_data.generation_config),
            ),
            ctx=new_request_context(),
        )
        return RetrievalServiceOutput(
            answer=output.answer,
            citations=[
                CitationServiceOutput(
                    release_id=citation.release_id,
                    chunk_id=citation.chunk_id,
                    citation_order=citation.citation_order,
                    content=citation.content,
                )
                for citation in output.citations
            ],
            release_id=output.release_id,
            retrieval_log_id=output.retrieval_log_id,
        )

    async def get_log(self, retrieval_log_id: str) -> RetrievalLogServiceOutput:
        return self._log_output(await self.retrieval_log_dao.get(retrieval_log_id))

    async def list_items(self, retrieval_log_id: str) -> list[RetrievalItemServiceOutput]:
        await self.retrieval_log_dao.get(retrieval_log_id)
        return [
            self._item_output(item)
            for item in await self.retrieval_log_dao.list_items(retrieval_log_id)
        ]

    async def list_citations(self, retrieval_log_id: str) -> list[CitationServiceOutput]:
        await self.retrieval_log_dao.get(retrieval_log_id)
        return [
            self._citation_output(citation)
            for citation in await self.retrieval_log_dao.list_citations(retrieval_log_id)
        ]

    def _log_output(self, record: RetrievalLogRecord) -> RetrievalLogServiceOutput:
        return RetrievalLogServiceOutput(
            id=record.id,
            release_id=record.release_id,
            query_raw=record.query_raw,
            query_rewritten=record.query_rewritten,
            rewrite_used=record.rewrite_used,
            answer_text=record.answer_text,
            config_snapshot=record.config_snapshot,
            created_at=record.created_at,
        )

    def _item_output(self, record: RetrievalItemRecord) -> RetrievalItemServiceOutput:
        return RetrievalItemServiceOutput(
            id=record.id,
            chunk_id=record.chunk_id,
            source_type=record.source_type,
            raw_score=record.raw_score,
            rerank_score=record.rerank_score,
            rank_before_rerank=record.rank_before_rerank,
            rank_after_rerank=record.rank_after_rerank,
            selected_for_context=record.selected_for_context,
        )

    def _citation_output(self, record: AnswerCitationRecord) -> CitationServiceOutput:
        return CitationServiceOutput(
            release_id=record.release_id,
            chunk_id=record.chunk_id,
            citation_order=record.citation_order,
            content=record.content,
        )

