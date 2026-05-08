from __future__ import annotations
import asyncio

from app.dependencies import evaluation_service, ingest_service, release_service, retrieval_service
from app.services.dto.common import StrategyConfigDTO
from app.services.dto.evaluation import AddQuestionServiceInput, CreateDatasetServiceInput, EvaluationRunServiceInput
from app.services.dto.ingestion import IngestDocumentServiceInput, IngestServiceInput
from app.services.dto.release import CreateReleaseServiceInput
from app.services.dto.retrieval import RetrievalServiceInput


def test_smoke_ingest_retrieve_evaluate() -> None:
    async def scenario() -> None:
        release = await release_service.create_release(
            CreateReleaseServiceInput(
                name="smoke-release",
                description="",
                config_snapshot={},
            )
        )
        mock_clean = StrategyConfigDTO(strategy_key="mock_clean")
        mock_chunk = StrategyConfigDTO(strategy_key="mock_chunk")
        mock_embedding = StrategyConfigDTO(strategy_key="mock_model")
        mock_rewrite = StrategyConfigDTO(strategy_key="mock_rewrite")
        mock_retrieval = StrategyConfigDTO(strategy_key="mock_retrieval")
        mock_rerank = StrategyConfigDTO(strategy_key="mock_rerank")
        mock_generation = StrategyConfigDTO(strategy_key="mock_gen")
        mock_judge = StrategyConfigDTO(strategy_key="mock_judge")

        await ingest_service.ingest(
            IngestServiceInput(
                release_id=release.id,
                documents=[
                    IngestDocumentServiceInput(
                        title="RAG",
                        content_raw="RAG combines retrieval and generation for question answering.",
                    )
                ],
                cleaner_config=mock_clean,
                chunker_config=mock_chunk,
                embedding_config=mock_embedding,
            )
        )

        retrieval = await retrieval_service.query(
            RetrievalServiceInput(
                release_id=release.id,
                query="retrieval generation",
                rewrite_config=mock_rewrite,
                retrieval_config=mock_retrieval,
                rerank_config=mock_rerank,
                generation_config=mock_generation,
            )
        )
        assert retrieval.retrieval_log_id
        assert retrieval.answer

        dataset = await evaluation_service.create_dataset(
            CreateDatasetServiceInput(name="smoke-dataset", description="")
        )
        await evaluation_service.add_questions(
            dataset_id=dataset.id,
            questions=[
                AddQuestionServiceInput(
                    question_text="What does RAG combine?",
                    reference_answer="retrieval",
                )
            ],
        )
        run = await evaluation_service.run_evaluation(
            EvaluationRunServiceInput(
                release_id=release.id,
                dataset_id=dataset.id,
                rewrite_config=mock_rewrite,
                retrieval_config=mock_retrieval,
                rerank_config=mock_rerank,
                generation_config=mock_generation,
                judge_config=mock_judge,
            )
        )
        assert run.total_count == 1

    asyncio.run(scenario())

