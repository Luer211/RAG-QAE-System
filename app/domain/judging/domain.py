from __future__ import annotations
from typing import Protocol

import json

from app.core.errors import InvalidStateError
from app.domain.judging.models import JudgeAnswerInput, JudgeAnswerOutput
from app.infra.llm import LLMClient


class JudgeStrategy(Protocol):
    async def judge(self, input_data: JudgeAnswerInput) -> JudgeAnswerOutput:
        ...


class LLMRagasLikeJudgeStrategy:
    model = "gpt-4o"

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.model = self.model
    
    async def judge(self, input_data: JudgeAnswerInput) -> JudgeAnswerOutput:
        answer = input_data.answer
        reference = input_data.reference_answer
        context = "\n\n".join(
            f"[{index + 1}] {text}"
            for index, text in enumerate(input_data.contexts)
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an evaluator for a RAG question-answering system. "
                    "Evaluate strictly and return only valid JSON."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question:\n{input_data.question}\n\n"
                    f"Retrieved Context:\n{context}\n\n"
                    f"Generated Answer:\n{answer}\n\n"
                    f"Reference Answer:\n{reference}\n\n"
                    "Evaluate the answer with these dimensions:\n"
                    "- faithfulness: whether the answer is supported by retrieved context\n"
                    "- answer_relevancy: whether the answer directly answers the question\n"
                    "- context_recall: whether retrieved context contains enough information for the reference answer\n\n"
                    "Return JSON with this schema:\n"
                    "{"
                    "\"faithfulness\": {\"score\": 0.0, \"reason\": \"...\"}, "
                    "\"answer_relevancy\": {\"score\": 0.0, \"reason\": \"...\"}, "
                    "\"context_recall\": {\"score\": 0.0, \"reason\": \"...\"}, "
                    "\"overall_score\": 0.0, "
                    "\"passed\": false, "
                    "\"reason\": \"...\""
                    "}"
                ),
            },
        ]

        raw = await self.llm_client.generate(
            message=messages,
            model=input_data.config.params.get("model", self.model),
        )

        result = json.loads(raw)
        result["strategy"] = input_data.config.strategy_key

        return JudgeAnswerOutput(result=result)


class JudgeStrategyFactory:
    def __init__(self, llm_client: LLMClient) -> None:
        self._strategies: dict[str, JudgeStrategy] = {
            "ragas_judge": LLMRagasLikeJudgeStrategy(llm_client),
        }

    def get(self, strategy_key: str) -> JudgeStrategy:
        try:
            return self._strategies[strategy_key]
        except KeyError as exc:
            raise InvalidStateError(f"Unknown judge strategy: {strategy_key}") from exc


class JudgeDomain:
    def __init__(self, strategy_factory: JudgeStrategyFactory):
        self.strategy_factory = strategy_factory

    async def judge(self, input_data: JudgeAnswerInput) -> JudgeAnswerOutput:
        strategy = self.strategy_factory.get(input_data.config.strategy_key)
        return await strategy.judge(input_data)

