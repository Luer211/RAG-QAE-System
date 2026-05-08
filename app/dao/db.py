from __future__ import annotations
from app.dao.memory_store import MemoryStore, store


def get_store() -> MemoryStore:
    return store

