from __future__ import annotations
from typing import Protocol

from app.core.errors import InvalidStateError
from app.domain.cleaning.models import CleanDocumentsInput, CleanDocumentsOutput, CleanedDocument


class CleanerStrategy(Protocol):
    async def clean(self, input_data: CleanDocumentsInput) -> CleanDocumentsOutput:
        ...


class MockCleanerStrategy:
    async def clean(self, input_data: CleanDocumentsInput) -> CleanDocumentsOutput:
        documents = [
            CleanedDocument(
                title=document.title.strip(),
                content_raw=document.content_raw,
                content_cleaned=" ".join(document.content_raw.split()),
            )
            for document in input_data.documents
        ]
        return CleanDocumentsOutput(documents=documents)


class CleanerStrategyFactory:
    def __init__(self) -> None:
        self._strategies: dict[str, CleanerStrategy] = {
            "mock_clean": MockCleanerStrategy(),
        }

    def get(self, strategy_key: str) -> CleanerStrategy:
        try:
            return self._strategies[strategy_key]
        except KeyError as exc:
            raise InvalidStateError(f"Unknown cleaner strategy: {strategy_key}") from exc


class CleanDomain:
    def __init__(self, strategy_factory: CleanerStrategyFactory):
        self.strategy_factory = strategy_factory

    async def clean(self, input_data: CleanDocumentsInput) -> CleanDocumentsOutput:
        strategy = self.strategy_factory.get(input_data.config.strategy_key)
        return await strategy.clean(input_data)

