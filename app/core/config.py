from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str
    api_prefix: str
    environment: str
    database_url: str
    embedding_base_url: str
    embedding_api_key: str
    llm_base_url: str
    llm_api_key: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME"),
        api_prefix=os.getenv("API_PREFIX"),
        environment=os.getenv("APP_ENV"),
        database_url=os.getenv("DATABASE_URL"),
        embedding_base_url=os.getenv("EMBEDDING_BASE_URL"),
        embedding_api_key=os.getenv("EMBEDDING_API_KEY"),
        llm_base_url=os.getenv("LLM_BASE_URL"),
        llm_api_key=os.getenv("LLM_API_KEY"),
    )
