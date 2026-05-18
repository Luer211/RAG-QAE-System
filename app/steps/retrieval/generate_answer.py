from __future__ import annotations
from app.repository.records import AnswerCitationCreate
from app.repository.retrieval_log_dao import RetrievalLogDao
from app.domain.generation import GenerateAnswerInput, GenerationDomain
from app.pipelines.retrieval.models import RetrievalPipelineOutput, RetrievalState


class GenerateAnswerStep:
    def __init__(
        self,
        generation_domain: GenerationDomain,
        retrieval_log_dao: RetrievalLogDao,
    ):
        self.generation_domain = generation_domain
        self.retrieval_log_dao = retrieval_log_dao

    async def run(self, state: RetrievalState) -> None:
        domain_output = await self.generation_domain.generate(
            GenerateAnswerInput(
                release_id=state.input.release_id,
                selected_chunks=state.runtime.selected_chunks,
                config=state.input.generation_config.to_domain_config(),
            )
        )
        retrieval_log_id = state.runtime.retrieval_log_id or ""
        await self.retrieval_log_dao.update_answer(
            retrieval_log_id=retrieval_log_id,
            answer_text=domain_output.answer,
        )
        await self.retrieval_log_dao.batch_insert_citations(
            retrieval_log_id=retrieval_log_id,
            release_id=state.input.release_id,
            citations=[
                AnswerCitationCreate(
                    chunk_id=citation.chunk_id,
                    citation_order=citation.citation_order,
                    content=citation.content,
                )
                for citation in domain_output.citations
            ],
        )
        state.output = RetrievalPipelineOutput(
            answer=domain_output.answer,
            citations=domain_output.citations,
            release_id=state.input.release_id,
            retrieval_log_id=retrieval_log_id,
        )

