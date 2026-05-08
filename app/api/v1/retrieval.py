from __future__ import annotations
from fastapi import APIRouter, Depends

from app.dependencies import get_retrieval_service
from app.schemas.retrieval import (
    AnswerCitationResponse,
    RetrievalItemResponse,
    RetrievalLogResponse,
    RetrievalRequest,
    RetrievalResult,
)
from app.services.dto.common import StrategyConfigDTO
from app.services.dto.retrieval import RetrievalServiceInput
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.post("/query", response_model=RetrievalResult)
async def query(
    req: RetrievalRequest,
    service: RetrievalService = Depends(get_retrieval_service),
) -> RetrievalResult:
    output = await service.query(
        RetrievalServiceInput(
            release_id=req.release_id,
            query=req.query,
            rewrite_config=StrategyConfigDTO(
                strategy_key=req.rewrite_config.strategy_key,
                params=req.rewrite_config.params,
            ),
            retrieval_config=StrategyConfigDTO(
                strategy_key=req.retrieval_config.strategy_key,
                params=req.retrieval_config.params,
            ),
            rerank_config=StrategyConfigDTO(
                strategy_key=req.rerank_config.strategy_key,
                params=req.rerank_config.params,
            ),
            generation_config=StrategyConfigDTO(
                strategy_key=req.generation_config.strategy_key,
                params=req.generation_config.params,
            ),
        )
    )
    return RetrievalResult(
        answer=output.answer,
        citations=[AnswerCitationResponse(**citation.__dict__) for citation in output.citations],
        release_id=output.release_id,
        retrieval_log_id=output.retrieval_log_id,
    )


@router.get("/logs/{retrieval_log_id}", response_model=RetrievalLogResponse)
async def get_log(
    retrieval_log_id: str,
    service: RetrievalService = Depends(get_retrieval_service),
) -> RetrievalLogResponse:
    return RetrievalLogResponse(**(await service.get_log(retrieval_log_id)).__dict__)


@router.get("/logs/{retrieval_log_id}/items", response_model=list[RetrievalItemResponse])
async def list_items(
    retrieval_log_id: str,
    service: RetrievalService = Depends(get_retrieval_service),
) -> list[RetrievalItemResponse]:
    return [
        RetrievalItemResponse(**item.__dict__)
        for item in await service.list_items(retrieval_log_id)
    ]


@router.get("/logs/{retrieval_log_id}/citations", response_model=list[AnswerCitationResponse])
async def list_citations(
    retrieval_log_id: str,
    service: RetrievalService = Depends(get_retrieval_service),
) -> list[AnswerCitationResponse]:
    return [
        AnswerCitationResponse(**citation.__dict__)
        for citation in await service.list_citations(retrieval_log_id)
    ]

