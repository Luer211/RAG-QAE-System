from __future__ import annotations
from app.core.context import RequestContext
from app.pipelines.retrieval.models import RetrievalPipelineInput, RetrievalPipelineOutput, RetrievalState
from app.steps.retrieval.create_log import CreateRetrievalLogStep
from app.steps.retrieval.generate_answer import GenerateAnswerStep
from app.steps.retrieval.rerank_chunks import RerankChunksStep
from app.steps.retrieval.retrieve_chunks import RetrieveChunksStep
from app.steps.retrieval.rewrite_query import RewriteQueryStep


class RetrievalPipeline:
    def __init__(
        self,
        create_log_step: CreateRetrievalLogStep,
        rewrite_step: RewriteQueryStep,
        retrieve_step: RetrieveChunksStep,
        rerank_step: RerankChunksStep,
        generate_step: GenerateAnswerStep,
    ) -> None:
        self.create_log_step = create_log_step
        self.rewrite_step = rewrite_step
        self.retrieve_step = retrieve_step
        self.rerank_step = rerank_step
        self.generate_step = generate_step

    async def run(
        self,
        input_data: RetrievalPipelineInput,
        ctx: RequestContext,
    ) -> RetrievalPipelineOutput:
        state = RetrievalState(ctx=ctx, input=input_data)

        await self.create_log_step.run(state)
        await self.rewrite_step.run(state)
        await self.retrieve_step.run(state)
        await self.rerank_step.run(state)
        await self.generate_step.run(state)

        if state.output is None:
            raise RuntimeError("Retrieval pipeline completed without output")
        return state.output

