from __future__ import annotations

from openai import OpenAI

from app.core.errors import InvalidStateError


class LLMClient:
    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model_name = "gpt-4o"

    def generate(self, message: list[dict[str, str]],) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content

        return content