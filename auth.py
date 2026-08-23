"""API-key authentication for the bot-facing REST API.

Configure one key with ``RVG_API_KEY``.  During key rotation, comma-separated
keys may be supplied in ``RVG_API_KEYS``; both variables are accepted at the
same time so a new key can be rolled out before the old one is removed.
"""

from __future__ import annotations

import hashlib
import os
import secrets
from typing import Annotated

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER_NAME = "X-API-KEY"
_api_key_header = APIKeyHeader(
    name=API_KEY_HEADER_NAME,
    scheme_name="BotApiKey",
    description="Admin API key configured through RVG_API_KEY.",
    auto_error=False,
)


def _error_detail(code: str, message: str) -> dict[str, object]:
    return {"code": code, "message": message, "details": None}


def configured_api_keys() -> tuple[str, ...]:
    """Return configured keys without caching, enabling zero-downtime rotation."""

    values: list[str] = []
    single = os.getenv("RVG_API_KEY", "").strip()
    if single:
        values.append(single)

    rotating = os.getenv("RVG_API_KEYS", "")
    if rotating:
        values.extend(key.strip() for key in rotating.split(",") if key.strip())

    # ``API_KEY`` is retained as a deployment compatibility alias, while the
    # RVG-prefixed names remain the documented and preferred configuration.
    compatibility = os.getenv("API_KEY", "").strip()
    if compatibility:
        values.append(compatibility)

    # Preserve order but remove duplicates without ever logging key material.
    return tuple(dict.fromkeys(values))


def _matches_any_key(provided: str, expected_keys: tuple[str, ...]) -> bool:
    """Compare fixed-length digests to avoid key length/timing disclosures."""

    supplied_digest = hashlib.sha256(provided.encode("utf-8")).digest()
    matched = False
    # Do not short-circuit.  Rotation key position should not affect timing.
    for expected in expected_keys:
        expected_digest = hashlib.sha256(expected.encode("utf-8")).digest()
        matched = secrets.compare_digest(supplied_digest, expected_digest) or matched
    return matched


async def require_api_key(
    api_key: Annotated[str | None, Security(_api_key_header)],
) -> None:
    """Fail closed before a request can reach panel state or a core process."""

    expected_keys = configured_api_keys()
    if not expected_keys:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_error_detail(
                "API_KEY_NOT_CONFIGURED",
                "The admin API is disabled until RVG_API_KEY is configured.",
            ),
        )

    # Use one response for missing and incorrect credentials to avoid providing
    # an oracle to callers.  A generous cap also bounds hashing work on hostile
    # oversized headers.
    if (
        not api_key
        or len(api_key) > 4096
        or not _matches_any_key(api_key, expected_keys)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_error_detail(
                "INVALID_API_KEY", "A valid X-API-KEY header is required."
            ),
            headers={"WWW-Authenticate": "ApiKey"},
        )
