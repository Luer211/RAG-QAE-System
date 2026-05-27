from __future__ import annotations

import httpx

from app.core.errors import InvalidStateError


class LLMClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    async def generate(
        self,
        message: list[dict[str, str]],
        model: str,
    ) -> str:
        # Todo: 连接API，发送消息，接收响应，取出回答
        pass

