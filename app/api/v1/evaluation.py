from __future__ import annotations
from fastapi import APIRouter, Depends

from app.dependencies import get_evaluation_service
from app.schemas.evaluation import (
    AddQuestionsRequest,
    AddSuccessResponse,
    CreateDatasetRequest,
    DatasetResponse,
    EvaluationItemResponse,
    EvaluationMetricResponse,
    EvaluationRunRequest,
    EvaluationRunResponse,
    EvaluationRunSubmitResponse,
    QuestionResponse,
)
from app.services.dto.common import StrategyConfigDTO
from app.services.dto.evaluation import (
    AddQuestionServiceInput,
    CreateDatasetServiceInput,
    EvaluationRunServiceInput,
)
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/datasets", response_model=DatasetResponse)
async def create_dataset(
    req: CreateDatasetRequest,
    service: EvaluationService = Depends(get_evaluation_service),
) -> DatasetResponse:
    output = await service.create_dataset(
        CreateDatasetServiceInput(name=req.name, description=req.description)
    )
    return DatasetResponse(**output.__dict__)


@router.get("/datasets", response_model=list[DatasetResponse])
async def list_datasets(
    service: EvaluationService = Depends(get_evaluation_service),
) -> list[DatasetResponse]:
    return [DatasetResponse(**dataset.__dict__) for dataset in await service.list_datasets()]


@router.post("/datasets/{dataset_id}/questions", response_model=AddSuccessResponse)
async def add_questions(
    dataset_id: str,
    req: AddQuestionsRequest,
    service: EvaluationService = Depends(get_evaluation_service),
) -> AddSuccessResponse:
    added = await service.add_questions(
        dataset_id=dataset_id,
        questions=[
            AddQuestionServiceInput(
                question_text=question.question_text,
                reference_answer=question.reference_answer,
            )
            for question in req.questions
        ],
    )
    return AddSuccessResponse(dataset_id=dataset_id, added_count=len(added))


@router.get("/datasets/{dataset_id}/questions", response_model=list[QuestionResponse])
async def list_questions(
    dataset_id: str,
    service: EvaluationService = Depends(get_evaluation_service),
) -> list[QuestionResponse]:
    return [
        QuestionResponse(**question.__dict__)
        for question in await service.list_questions(dataset_id)
    ]


@router.post("/runs", response_model=EvaluationRunSubmitResponse)
async def run_evaluation(
    req: EvaluationRunRequest,
    service: EvaluationService = Depends(get_evaluation_service),
) -> EvaluationRunSubmitResponse:
    output = await service.run_evaluation(
        EvaluationRunServiceInput(
            release_id=req.release_id,
            dataset_id=req.dataset_id,
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
            judge_config=StrategyConfigDTO(
                strategy_key=req.judge_config.strategy_key,
                params=req.judge_config.params,
            ),
        )
    )
    return EvaluationRunSubmitResponse(
        evaluation_run_id=output.id,
        run_status=output.run_status,
    )


@router.get("/runs/{evaluation_run_id}", response_model=EvaluationRunResponse)
async def get_run(
    evaluation_run_id: str,
    service: EvaluationService = Depends(get_evaluation_service),
) -> EvaluationRunResponse:
    return EvaluationRunResponse(**(await service.get_run(evaluation_run_id)).__dict__)


@router.get("/runs/{evaluation_run_id}/items", response_model=list[EvaluationItemResponse])
async def list_run_items(
    evaluation_run_id: str,
    service: EvaluationService = Depends(get_evaluation_service),
) -> list[EvaluationItemResponse]:
    return [
        EvaluationItemResponse(**item.__dict__)
        for item in await service.list_run_items(evaluation_run_id)
    ]


@router.get("/runs/{evaluation_run_id}/metrics", response_model=EvaluationMetricResponse)
async def get_metrics(
    evaluation_run_id: str,
    service: EvaluationService = Depends(get_evaluation_service),
) -> EvaluationMetricResponse:
    return EvaluationMetricResponse(**(await service.get_metrics(evaluation_run_id)).__dict__)

