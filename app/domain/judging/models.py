from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from app.domain.common import DomainStrategyConfig


@dataclass(frozen=True)
class JudgeAnswerInput:
    question: str
    answer: str | None
    reference_answer: str | None
    contexts: list[str]
    config: DomainStrategyConfig


@dataclass(frozen=True)
class JudgeAnswerOutput:
    result: dict[str, Any]

"""
JudgeAnswerOutput:
    {
    "strategy": "ragas_like_judge",
    "faithfulness": {
        "score": 0.8,
        "reason": "The answer is mostly supported by the retrieved context."
    },
    "answer_relevancy": {
        "score": 0.9,
        "reason": "The answer directly addresses the question."
    },
    "context_recall": {
        "score": 0.7,
        "reason": "The retrieved context contains the main evidence, but misses some detail."
    },
    "overall_score": 0.8,
    "passed": true,
    "reason": "The answer is relevant and mostly grounded in context."
    }
"""
