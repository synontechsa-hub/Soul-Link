# backend/app/core/utils.py
# Shared utilities for the SoulLink backend.

from datetime import datetime, timezone

def utcnow() -> datetime:
    """Return the current UTC time as a naive datetime (no tzinfo).

    PostgreSQL columns defined as TIMESTAMP WITHOUT TIME ZONE require naive
    datetimes. Using datetime.now(timezone.utc) produces an offset-aware
    datetime that asyncpg will reject with:
        "can't subtract offset-naive and offset-aware datetimes"

    Always use this helper instead of datetime.now(timezone.utc) when writing
    to the database.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
