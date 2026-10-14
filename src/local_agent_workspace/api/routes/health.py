"""Application liveness endpoint; no dependency readiness checks."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["health"])


class HealthResponse(BaseModel):
    """Public health response contract."""

    status: Literal["ok"]


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Report that the application can serve requests."""
    return HealthResponse(status="ok")
