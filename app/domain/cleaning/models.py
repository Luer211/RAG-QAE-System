from __future__ import annotations
from dataclasses import dataclass

from app.domain.common import DomainStrategyConfig


@dataclass(frozen=True)
class RawDocument:
    title: str
    content_raw: str


@dataclass(frozen=True)
class CleanedDocument:
    title: str
    content_raw: str
    content_cleaned: str


@dataclass(frozen=True)
class CleanDocumentsInput:
    documents: list[RawDocument]
    config: DomainStrategyConfig


@dataclass(frozen=True)
class CleanDocumentsOutput:
    documents: list[CleanedDocument]

