from __future__ import annotations
from app.dao.retrieval_log_dao import RetrievalLogDao
from app.domain.query_rewrite import QueryRewriteDomain, RewriteQueryInput
from app.pipelines.retrieval.models import RetrievalState


class RewriteQueryStep:
    def __init__(
        self,
        query_rewrite_domain: QueryRewriteDomain,
        retrieval_log_dao: RetrievalLogDao,
    ):
        self.query_rewrite_domain = query_rewrite_domain
        self.retrieval_log_dao = retrieval_log_dao

    async def run(self, state: RetrievalState) -> None:
        domain_output = await self.query_rewrite_domain.rewrite(
            RewriteQueryInput(
                query=state.input.query,
                config=state.input.rewrite_config.to_domain_config(),
            )
        )
        state.runtime.rewrite_query = domain_output.query_rewritten
        await self.retrieval_log_dao.update_rewrite(
            retrieval_log_id=state.runtime.retrieval_log_id or "",
            query_rewritten=domain_output.query_rewritten,
            rewrite_used=domain_output.rewrite_used,
        )

