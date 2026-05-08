from __future__ import annotations
from fastapi import APIRouter, Depends

from app.dependencies import get_ingest_service
from app.schemas.common import SuccessResponse
from app.schemas.ingestion import IngestJobRequest
from app.services.dto.common import StrategyConfigDTO
from app.services.dto.ingestion import IngestDocumentServiceInput, IngestServiceInput
from app.services.ingest_service import IngestService

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("", response_model=SuccessResponse)
async def ingest(
    req: IngestJobRequest,
    service: IngestService = Depends(get_ingest_service),
) -> SuccessResponse:
    output = await service.ingest(
        IngestServiceInput(
            release_id=req.release_id,
            documents=[
                IngestDocumentServiceInput(
                    title=document.title,
                    content_raw=document.content_raw,
                )
                for document in req.documents
            ],
            cleaner_config=StrategyConfigDTO(
                strategy_key=req.cleaner_config.strategy_key,
                params=req.cleaner_config.params,
            ),
            chunker_config=StrategyConfigDTO(
                strategy_key=req.chunker_config.strategy_key,
                params=req.chunker_config.params,
            ),
            embedding_config=StrategyConfigDTO(
                strategy_key=req.embedding_config.strategy_key,
                params=req.embedding_config.params,
            ),
        )
    )
    return SuccessResponse(message=output.message)

