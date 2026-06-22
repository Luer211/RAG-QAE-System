from __future__ import annotations

from openai import OpenAI

from app.core.errors import InvalidStateError


class LLMClient:
    def __init__(self, llm_api_key: str, llm_base_url: str, llm_model_name: str):
        self.client = OpenAI(
            api_key=llm_api_key,
            base_url=llm_base_url,
        )
        self.model_name=llm_model_name

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