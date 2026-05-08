from __future__ import annotations
from fastapi import APIRouter

from app.api.v1 import evaluation, ingestion, releases, retrieval

router = APIRouter()
router.include_router(releases.router)
router.include_router(ingestion.router)
router.include_router(retrieval.router)
router.include_router(evaluation.router)

