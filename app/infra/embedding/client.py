from __future__ import annotations
class EmbeddingClient:
    async def embed(self, text: str) -> list[float]:
        return [float(len(text))]

