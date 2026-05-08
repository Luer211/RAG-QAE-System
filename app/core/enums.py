from __future__ import annotations
from enum import Enum


class ReleaseStatus(str, Enum):
    DRAFT = "draft"
    TESTING = "testing"
    READY = "ready"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class EvaluationRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PARTIAL_SUCCESS = "partial_success"
    SUCCESS = "success"
    FAILED = "failed"

