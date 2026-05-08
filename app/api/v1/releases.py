from __future__ import annotations
from fastapi import APIRouter, Depends

from app.dependencies import get_release_service
from app.schemas.release import (
    ChunkListResponse,
    ChunkResponse,
    CreateReleaseRequest,
    DocumentListResponse,
    DocumentResponse,
    ReleaseListResponse,
    ReleaseResponse,
)
from app.services.dto.release import CreateReleaseServiceInput
from app.services.release_service import ReleaseService

router = APIRouter(prefix="/releases", tags=["releases"])


@router.post("", response_model=ReleaseResponse)
async def create_release(
    req: CreateReleaseRequest,
    service: ReleaseService = Depends(get_release_service),
) -> ReleaseResponse:
    output = await service.create_release(
        CreateReleaseServiceInput(
            name=req.name,
            description=req.description,
            config_snapshot=req.config_snapshot,
        )
    )
    return ReleaseResponse(**output.__dict__)


@router.get("", response_model=ReleaseListResponse)
async def list_releases(
    service: ReleaseService = Depends(get_release_service),
) -> ReleaseListResponse:
    items = [ReleaseResponse(**item.__dict__) for item in await service.list_releases()]
    return ReleaseListResponse(items=items, total=len(items))


@router.get("/{release_id}/documents", response_model=DocumentListResponse)
async def list_documents(
    release_id: str,
    service: ReleaseService = Depends(get_release_service),
) -> DocumentListResponse:
    items = [
        DocumentResponse(**item.__dict__)
        for item in await service.list_documents(release_id)
    ]
    return DocumentListResponse(items=items, total=len(items))


@router.get("/{release_id}/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    release_id: str,
    document_id: str,
    service: ReleaseService = Depends(get_release_service),
) -> DocumentResponse:
    return DocumentResponse(**(await service.get_document(release_id, document_id)).__dict__)


@router.get("/{release_id}/documents/{document_id}/chunks", response_model=ChunkListResponse)
async def list_chunks(
    release_id: str,
    document_id: str,
    service: ReleaseService = Depends(get_release_service),
) -> ChunkListResponse:
    items = [
        ChunkResponse(**item.__dict__)
        for item in await service.list_chunks(release_id, document_id)
    ]
    return ChunkListResponse(items=items, total=len(items))

