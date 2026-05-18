from __future__ import annotations

from sqlalchemy import Enum as SAEnum

from app.core.enums import EvaluationRunStatus, ReleaseStatus


release_status = SAEnum(
    ReleaseStatus,
    name="release_status",
    native_enum=True,
    create_type=False,
    values_callable=lambda items: [item.value for item in items],
)

evaluation_run_status = SAEnum(
    EvaluationRunStatus,
    name="evaluation_run_status",
    native_enum=True,
    create_type=False,
    values_callable=lambda items: [item.value for item in items],
)
