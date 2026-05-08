from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from app.domain.common import DomainStrategyConfig


@dataclass(frozen=True)
class JudgeAnswerInput:
    question: str
    answer: str | None
    reference_answer: str | None
    config: DomainStrategyConfig


@dataclass(frozen=True)
class JudgeAnswerOutput:
    result: dict[str, Any]

