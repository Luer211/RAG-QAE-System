from __future__ import annotations

import os

import httpx


class EmbeddingClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    # Todo: 我们这里做的就是传入一系列文本，返回一系列向量
    async def embed(self, texts: list[str], model: str) -> list[list[float]]:
        async with httpx.AsyncClient() as client:
            # Todo: 要看看实际的接口 API 是怎么设计的，看文档
            resp = await client.post(
                json={
                    "model": model,
                    "input": texts,
                    "encoding_format": "float",
                }
            )
        
        data = resp.json()["data"]
        data.sort(key=lambda item: item["index"])

        return [item["embedding"] for item in data]

