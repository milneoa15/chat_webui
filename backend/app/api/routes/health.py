"""Health endpoints."""

from fastapi import APIRouter

from backend.app.schemas.system import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Backend heartbeat")
def get_health() -> HealthResponse:
    """Return static metadata so CI/env checks can verify the API is live."""
    return HealthResponse()
