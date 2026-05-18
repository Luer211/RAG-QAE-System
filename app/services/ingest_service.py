from __future__ import annotations
from app.core.context import new_request_context
from app.repository.release_dao import ReleaseDao
from app.pipelines.ingestion import IngestDocumentInput, IngestPipeline, IngestPipelineInput
from app.services.dto.ingestion import IngestServiceInput, IngestServiceOutput
from app.services.mapping import to_pipeline_config


class IngestService:
    def __init__(self, release_dao: ReleaseDao, ingest_pipeline: IngestPipeline):
        self.release_dao = release_dao
        self.ingest_pipeline = ingest_pipeline

    async def ingest(self, input_data: IngestServiceInput) -> IngestServiceOutput:
        await self.release_dao.get_or_raise(input_data.release_id)
        await self.ingest_pipeline.run(
            IngestPipelineInput(
                release_id=input_data.release_id,
                documents=[
                    IngestDocumentInput(
                        title=document.title,
                        content_raw=document.content_raw,
                    )
                    for document in input_data.documents
                ],
                cleaner_config=to_pipeline_config(input_data.cleaner_config),
                chunker_config=to_pipeline_config(input_data.chunker_config),
                embedding_config=to_pipeline_config(input_data.embedding_config),
            ),
            ctx=new_request_context(),
        )
        return IngestServiceOutput()

