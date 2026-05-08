from __future__ import annotations
from app.dao.document_dao import DocumentDao
from app.dao.records import DocumentCreate
from app.domain.cleaning import CleanDocumentsInput, CleanDomain, RawDocument
from app.pipelines.ingestion.models import IngestState


class CleanDocumentsStep:
    def __init__(self, clean_domain: CleanDomain, document_dao: DocumentDao):
        self.clean_domain = clean_domain
        self.document_dao = document_dao

    async def run(self, state: IngestState) -> None:
        domain_input = CleanDocumentsInput(
            documents=[
                RawDocument(title=document.title, content_raw=document.content_raw)
                for document in state.input.documents
            ],
            config=state.input.cleaner_config.to_domain_config(),
        )
        domain_output = await self.clean_domain.clean(domain_input)

        state.runtime.documents_cleaned_ids = await self.document_dao.batch_insert_cleaned_documents(
            release_id=state.input.release_id,
            documents=[
                DocumentCreate(
                    title=document.title,
                    content_raw=document.content_raw,
                    content_cleaned=document.content_cleaned,
                )
                for document in domain_output.documents
            ],
        )

