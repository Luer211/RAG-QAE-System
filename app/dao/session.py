from __future__ import annotations
class UnitOfWork:
    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

