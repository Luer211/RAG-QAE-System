from __future__ import annotations
from app.repository.dao.chunk_dao import ChunkDao
from app.repository.dao.document_dao import DocumentDao
from app.repository.records import ChunkCreate
from app.domain.chunking import ChunkDocumentInput, ChunkDocumentsInput, ChunkDomain
from app.pipelines.ingestion.models import IngestState


class ChunkDocumentsStep:
    def __init__(
        self,
        chunk_domain: ChunkDomain,
        document_dao: DocumentDao,
        chunk_dao: ChunkDao,
    ):
        self.chunk_domain = chunk_domain
        self.document_dao = document_dao
        self.chunk_dao = chunk_dao

    async def run(self, state: IngestState) -> None:
        documents = await self.document_dao.list_by_ids(
            release_id=state.input.release_id,
            document_ids=state.runtime.documents_cleaned_ids,
        )
        domain_input = ChunkDocumentsInput(
            documents=[
                ChunkDocumentInput(
                    document_id=document.id,
                    content_cleaned=document.content_cleaned or document.content_raw,
                )
                for document in documents
            ],
            config=state.input.chunker_config.to_domain_config(),
        )
        domain_output = await self.chunk_domain.chunk(domain_input)

        state.runtime.chunk_ids = await self.chunk_dao.batch_insert_chunks(
            release_id=state.input.release_id,
            chunks=[
                ChunkCreate(
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                )
                for chunk in domain_output.chunks
            ],
        )

