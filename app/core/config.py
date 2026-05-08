from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "RAG-QAE-System"
    api_prefix: str = "/api/v1"
    environment: str = "local"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "RAG-QAE-System"),
        api_prefix=os.getenv("API_PREFIX", "/api/v1"),
        environment=os.getenv("APP_ENV", "local"),
    )

