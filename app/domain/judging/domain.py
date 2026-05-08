from __future__ import annotations
from typing import Protocol

from app.core.errors import InvalidStateError
from app.domain.judging.models import JudgeAnswerInput, JudgeAnswerOutput


class JudgeStrategy(Protocol):
    async def judge(self, input_data: JudgeAnswerInput) -> JudgeAnswerOutput:
        ...


class MockJudgeStrategy:
    async def judge(self, input_data: JudgeAnswerInput) -> JudgeAnswerOutput:
        answer = input_data.answer or ""
        reference = input_data.reference_answer or ""
        score = 1.0 if reference and reference.lower() in answer.lower() else 0.0
        if not reference and answer:
            score = 0.5
        return JudgeAnswerOutput(
            result={
                "strategy": input_data.config.strategy_key,
                "score": score,
                "passed": score >= 0.5,
            }
        )


class JudgeStrategyFactory:
    def __init__(self) -> None:
        self._strategies: dict[str, JudgeStrategy] = {
            "mock_judge": MockJudgeStrategy(),
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

