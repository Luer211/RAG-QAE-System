from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKeyConstraint, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.repository.models.base import Base


class EvaluationItemOrm(Base):
    __tablename__ = "evaluation_items"
    __table_args__ = (
        ForeignKeyConstraint(
            ["evaluation_run_id", "release_id"],
            ["evaluation_runs.id", "evaluation_runs.release_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["question_id"],
            ["evaluation_questions.id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["retrieval_log_id", "release_id"],
            ["retrieval_logs.id", "retrieval_logs.release_id"],
            ondelete="CASCADE",
        ),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    evaluation_run_id: Mapped[str] = mapped_column(String(64), nullable=False)
    question_id: Mapped[str] = mapped_column(String(64), nullable=False)
    release_id: Mapped[str] = mapped_column(String(64), nullable=False)
    retrieval_log_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    citations_snapshot: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=text("'[]'::jsonb"),
    )
    judge_result: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
