"""Time helpers."""

import datetime as dt
from datetime import datetime


def utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(dt.UTC)
