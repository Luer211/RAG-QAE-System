from __future__ import annotations

from openai import OpenAI

import httpx


class EmbeddingClient:
    """负责连接 client 供业务使用"""

    def __init__(self, embedding_base_url: str, embedding_api_key: str, embedding_model_name: str):
        self.client = OpenAI(
            api_key=embedding_api_key,
            base_url=embedding_base_url,
        )
        self.embedding_model_name=embedding_model_name

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

