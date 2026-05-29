from __future__ import annotations
from app.domain.retrieval import RetrievalDomain, RetrieveChunksInput
from app.pipelines.retrieval.models import RetrievalState


class RetrieveChunksStep:
    def __init__(self, retrieval_domain: RetrievalDomain):
        self.retrieval_domain = retrieval_domain

    async def run(self, state: RetrievalState) -> None:
        domain_output = await self.retrieval_domain.retrieve(
            RetrieveChunksInput(
                release_id=state.input.release_id,
                query=state.runtime.rewrite_query or state.input.query,
                config=state.input.retrieval_config.to_domain_config(),
            )
        )
        state.runtime.retrieval_chunks = domain_output.items
