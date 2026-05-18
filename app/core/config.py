from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True)
class Settings:
    app_name: str
    api_prefix: str
    environment: str
    database_url: str

@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME"),
        api_prefix=os.getenv("API_PREFIX"),
        environment=os.getenv("APP_ENV"),
        database_url=os.getenv("DATABASE_URL")
    )
