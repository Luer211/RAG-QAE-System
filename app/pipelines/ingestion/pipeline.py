from __future__ import annotations
from app.core.context import RequestContext
from app.pipelines.ingestion.models import IngestPipelineInput, IngestPipelineOutput, IngestState
from app.steps.ingestion.chunk_documents import ChunkDocumentsStep
from app.steps.ingestion.clean_documents import CleanDocumentsStep
from app.steps.ingestion.embed_chunks import EmbedChunksStep
from app.steps.ingestion.mark_release_ready import MarkReleaseReadyStep


class IngestPipeline:
    def __init__(
        self,
        clean_step: CleanDocumentsStep,
        chunk_step: ChunkDocumentsStep,
        embed_step: EmbedChunksStep,
        mark_ready_step: MarkReleaseReadyStep,
    ) -> None:
        self.clean_step = clean_step
        self.chunk_step = chunk_step
        self.embed_step = embed_step
        self.mark_ready_step = mark_ready_step

    async def run(
        self,
        input_data: IngestPipelineInput,
        ctx: RequestContext,
    ) -> IngestPipelineOutput:
        state = IngestState(ctx=ctx, input=input_data)

        await self.clean_step.run(state)
        await self.chunk_step.run(state)
        await self.embed_step.run(state)
        await self.mark_ready_step.run(state)

        if state.output is None:
            raise RuntimeError("Ingest pipeline completed without output")
        return state.output

