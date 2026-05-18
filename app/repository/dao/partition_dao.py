from __future__ import annotations

import re

from sqlalchemy import text


class PartitionDao:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def ensure_release_partitions(self, release_id: str) -> None:
        suffix = self._partition_suffix(release_id)
        release_literal = release_id.replace("'", "''")
        statements = [
            f"CREATE TABLE IF NOT EXISTS documents_{suffix} "
            f"PARTITION OF documents FOR VALUES IN ('{release_literal}')",
            f"CREATE TABLE IF NOT EXISTS chunks_{suffix} "
            f"PARTITION OF chunks FOR VALUES IN ('{release_literal}')",
            f"CREATE TABLE IF NOT EXISTS chunk_embeddings_{suffix} "
            f"PARTITION OF chunk_embeddings FOR VALUES IN ('{release_literal}')",
        ]
        async with self.session_factory() as session:
            async with session.begin():
                for statement in statements:
                    await session.execute(text(statement))

    def _partition_suffix(self, release_id: str) -> str:
        suffix = re.sub(r"[^a-zA-Z0-9_]", "_", release_id).lower()
        if not suffix or suffix[0].isdigit():
            suffix = f"rel_{suffix}"
        return suffix
