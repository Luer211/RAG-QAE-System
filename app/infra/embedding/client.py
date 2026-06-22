from __future__ import annotations

from openai import OpenAI

import httpx


class EmbeddingClient:
    """负责连接 client 供业务使用"""

    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.embedding_model_name = "gpt-4-embedding"

    # Todo: 我们这里做的就是传入一系列文本，返回一系列向量
    async def embed(self, texts: list[str]) -> list[list[float]]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                json={
                    "model": self.embedding_model_name,
                    "input": texts,
                    "encoding_format": "float",
                }
            )
        
        data = resp.json()["data"]
        data.sort(key=lambda item: item["index"])

        return [item["embedding"] for item in data]

