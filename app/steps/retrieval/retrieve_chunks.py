from __future__ import annotations
from app.repository.dao.chunk_dao import ChunkDao
from app.domain.retrieval import RetrievalCandidate, RetrievalDomain, RetrieveChunksInput
from app.pipelines.retrieval.models import RetrievalState


class RetrieveChunksStep:
    def __init__(self, retrieval_domain: RetrievalDomain, chunk_dao: ChunkDao):
        self.retrieval_domain = retrieval_domain
        self.chunk_dao = chunk_dao

    async def run(self, state: RetrievalState) -> None:
        chunks = await self.chunk_dao.list_by_release(state.input.release_id)
        domain_output = await self.retrieval_domain.retrieve(
            RetrieveChunksInput(
                query=state.runtime.rewrite_query or state.input.query,
                candidates=[
                    RetrievalCandidate(chunk_id=chunk.id, content=chunk.content)
                    for chunk in chunks
                ],
                config=state.input.retrieval_config.to_domain_config(),
            )
        )
        state.runtime.retrieval_chunks = domain_output.items

