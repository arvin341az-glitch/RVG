"""Minimal async client used by a Telegram bot to provision an RVG user.

Environment:
    RVG_BASE_URL=https://panel.example.com
    RVG_API_KEY=<the same value configured on the panel>
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

import httpx


class PanelAPIError(RuntimeError):
    """A safe error that a Telegram command handler can display or log."""


async def create_vpn_user(
    username: str,
    traffic_limit_gb: float,
    expire_days: int,
    protocol: str = "vless",
) -> dict[str, Any]:
    base_url = os.environ["RVG_BASE_URL"].rstrip("/")
    api_key = os.environ["RVG_API_KEY"]

    timeout = httpx.Timeout(20.0, connect=5.0)
    async with httpx.AsyncClient(
        base_url=base_url,
        timeout=timeout,
        headers={"X-API-KEY": api_key, "Accept": "application/json"},
    ) as client:
        try:
            response = await client.post(
                "/api/v1/users",
                json={
                    "username": username,
                    "traffic_limit_gb": traffic_limit_gb,
                    "expire_days": expire_days,
                    "protocol": protocol,
                },
            )
            payload = response.json()
        except httpx.RequestError as exc:
            raise PanelAPIError("VPN panel is currently unreachable") from exc
        except ValueError as exc:
            raise PanelAPIError("VPN panel returned a non-JSON response") from exc

    if not response.is_success or not payload.get("success"):
        error = payload.get("error") or {}
        # Do not include the API key or full request headers in Telegram logs.
        code = error.get("code", f"HTTP_{response.status_code}")
        message = error.get("message", "VPN panel request failed")
        raise PanelAPIError(f"{code}: {message}")

    return payload["data"]


async def example() -> None:
    user = await create_vpn_user(
        username="telegram_123456789",
        traffic_limit_gb=50,
        expire_days=30,
        protocol="vless",
    )
    print("Subscription:", user["subscription_url"])
    print("Connection links:", user["links"])


if __name__ == "__main__":
    asyncio.run(example())
