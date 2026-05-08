from __future__ import annotations
from dataclasses import dataclass

from app.core.ids import new_id


@dataclass(frozen=True)
class RequestContext:
    trace_id: str
    operator_id: str | None = None


def new_request_context(operator_id: str | None = None) -> RequestContext:
    return RequestContext(trace_id=new_id("trace"), operator_id=operator_id)

