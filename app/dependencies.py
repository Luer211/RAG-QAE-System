from __future__ import annotations
from app.repository.db import SessionLocal
from app.core.config import get_settings
from app.infra.embedding import EmbeddingClient
from app.infra.llm import LLMClient
from app.repository.dao.document_dao import DocumentDao
from app.repository.dao.chunk_dao import ChunkDao
from app.repository.dao.embedding_dao import EmbeddingDao
from app.repository.dao.evaluation_dao import EvaluationDao
from app.repository.dao.partition_dao import PartitionDao
from app.repository.dao.release_dao import ReleaseDao
from app.repository.dao.retrieval_log_dao import RetrievalLogDao
from app.domain.chunking import ChunkDomain, ChunkerStrategyFactory
from app.domain.cleaning import CleanDomain, CleanerStrategyFactory
from app.domain.embedding import EmbedDomain, EmbeddingStrategyFactory
from app.domain.generation import GenerationDomain, GenerationStrategyFactory
from app.domain.judging import JudgeDomain, JudgeStrategyFactory
from app.domain.query_rewrite import QueryRewriteDomain, QueryRewriteStrategyFactory
from app.domain.reranking import RerankDomain, RerankStrategyFactory
from app.domain.retrieval import RetrievalDomain, RetrievalStrategyFactory
from app.pipelines.evaluation import EvaluationPipeline
from app.pipelines.ingestion import IngestPipeline
from app.pipelines.retrieval import RetrievalPipeline
from app.services.evaluation_service import EvaluationService
from app.services.ingest_service import IngestService
from app.services.release_service import ReleaseService
from app.services.retrieval_service import RetrievalService
from app.steps.evaluation import (
    CreateEvaluationMetricsStep,
    CreateEvaluationRunStep,
    FinalizeEvaluationRunStep,
    JudgeEvaluationItemsStep,
    RunEvaluationItemsStep,
)
from app.steps.ingestion import (
    ChunkDocumentsStep,
    CleanDocumentsStep,
    EmbedChunksStep,
    MarkReleaseReadyStep,
)
from app.steps.retrieval import (
    CreateRetrievalLogStep,
    GenerateAnswerStep,
    RerankChunksStep,
    RetrieveChunksStep,
    RewriteQueryStep,
)

settings = get_settings()

embedding_client = EmbeddingClient(
    embedding_base_url=settings.embedding_base_url,
    embedding_api_key=settings.embedding_api_key,
    embedding_model_name=settings.embedding_model_name
)

llm_client = LLMClient(
    llm_base_url=settings.llm_base_url,
    llm_api_key=settings.llm_api_key,
    llm_model_name=settings.llm_model_name
)

release_dao = ReleaseDao(SessionLocal)
partition_dao = PartitionDao(SessionLocal)
document_dao = DocumentDao(SessionLocal)
chunk_dao = ChunkDao(SessionLocal)
embedding_dao = EmbeddingDao(SessionLocal)
retrieval_log_dao = RetrievalLogDao(SessionLocal)
evaluation_dao = EvaluationDao(SessionLocal)

clean_domain = CleanDomain(CleanerStrategyFactory())
chunk_domain = ChunkDomain(ChunkerStrategyFactory())
embed_domain = EmbedDomain(EmbeddingStrategyFactory(embedding_client=embedding_client))
query_rewrite_domain = QueryRewriteDomain(QueryRewriteStrategyFactory())
retrieval_domain = RetrievalDomain(
    RetrievalStrategyFactory(
        embedding_client=embedding_client,
        embedding_dao=embedding_dao,
        chunk_dao=chunk_dao,
    )
)
rerank_domain = RerankDomain(RerankStrategyFactory())
generation_domain = GenerationDomain(GenerationStrategyFactory(llm_client=llm_client))
judge_domain = JudgeDomain(JudgeStrategyFactory(llm_client=llm_client))

ingest_pipeline = IngestPipeline(
    clean_step=CleanDocumentsStep(clean_domain, document_dao),
    chunk_step=ChunkDocumentsStep(chunk_domain, document_dao, chunk_dao),
    embed_step=EmbedChunksStep(embed_domain, chunk_dao, embedding_dao),
    mark_ready_step=MarkReleaseReadyStep(release_dao),
)

retrieval_pipeline = RetrievalPipeline(
    create_log_step=CreateRetrievalLogStep(retrieval_log_dao),
    rewrite_step=RewriteQueryStep(query_rewrite_domain, retrieval_log_dao),
    retrieve_step=RetrieveChunksStep(retrieval_domain),
    rerank_step=RerankChunksStep(rerank_domain, retrieval_log_dao),
    generate_step=GenerateAnswerStep(generation_domain, retrieval_log_dao),
)

evaluation_pipeline = EvaluationPipeline(
    create_run_step=CreateEvaluationRunStep(evaluation_dao),
    run_items_step=RunEvaluationItemsStep(evaluation_dao, retrieval_pipeline),
    judge_items_step=JudgeEvaluationItemsStep(evaluation_dao, judge_domain),
    finalize_run_step=FinalizeEvaluationRunStep(evaluation_dao),
    create_metrics_step=CreateEvaluationMetricsStep(evaluation_dao),
)

release_service = ReleaseService(release_dao, partition_dao, document_dao, chunk_dao)
ingest_service = IngestService(release_dao, ingest_pipeline)
retrieval_service = RetrievalService(release_dao, retrieval_log_dao, retrieval_pipeline)
evaluation_service = EvaluationService(release_dao, evaluation_dao, evaluation_pipeline)


def get_release_service() -> ReleaseService:
    return release_service


def get_ingest_service() -> IngestService:
    return ingest_service


def get_retrieval_service() -> RetrievalService:
    return retrieval_service


def get_evaluation_service() -> EvaluationService:
    return evaluation_service
