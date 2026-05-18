from __future__ import annotations
from app.repository.records import RetrievalItemCreate
from app.repository.retrieval_log_dao import RetrievalLogDao
from app.domain.reranking import RerankChunksInput, RerankDomain
from app.pipelines.retrieval.models import RetrievalState


class RerankChunksStep:
    def __init__(
        self,
        rerank_domain: RerankDomain,
        retrieval_log_dao: RetrievalLogDao,
    ):
        self.rerank_domain = rerank_domain
        self.retrieval_log_dao = retrieval_log_dao

    async def run(self, state: RetrievalState) -> None:
        domain_output = await self.rerank_domain.rerank(
            RerankChunksInput(
                items=state.runtime.retrieval_chunks,
                config=state.input.rerank_config.to_domain_config(),
            )
        )
        state.runtime.rerank_chunks = domain_output.items
        state.runtime.selected_chunks = domain_output.selected_chunks
        await self.retrieval_log_dao.batch_insert_items(
            retrieval_log_id=state.runtime.retrieval_log_id or "",
            release_id=state.input.release_id,
            items=[
                RetrievalItemCreate(
                    chunk_id=item.chunk_id,
                    source_type=item.source_type,
                    raw_score=item.raw_score,
                    rerank_score=item.rerank_score,
                    rank_before_rerank=item.rank_before_rerank,
                    rank_after_rerank=item.rank_after_rerank,
                    selected_for_context=item.selected_for_context,
                )
                for item in domain_output.items
            ],
        )

