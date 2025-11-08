"""System level Pydantic schemas."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from backend.app.version import __version__


class HealthResponse(BaseModel):
    """Shape of the `/health` response."""

    status: str = Field(default="ok")
    version: str = Field(default=__version__)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
