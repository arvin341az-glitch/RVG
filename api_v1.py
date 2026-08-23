"""Versioned, API-key protected administration API for Telegram bots.

RVG uses a live in-process core for VLESS/Trojan/Shadowsocks and a managed
process for MTProto.  Mutating this panel's ``LINKS`` store therefore updates
the live core immediately; MTProto lifecycle operations are delegated to the
same core helpers used by the dashboard.
"""

from __future__ import annotations

import asyncio
import base64
import copy
import logging
import math
import os
import shutil
import time
from collections.abc import Callable, Coroutine
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Any, NoReturn, cast
from urllib.parse import quote

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import (
    http_exception_handler as default_http_exception_handler,
)
from fastapi.exception_handlers import (
    request_validation_exception_handler as default_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException as StarletteHTTPException

from auth import require_api_key
from schemas import (
    APIErrorDetail,
    APIResponse,
    ConnectionLink,
    CreateUserRequest,
    DeleteUserResponse,
    DeleteUserResult,
    ExtendUserRequest,
    LinksResponse,
    SetUserStatusRequest,
    SubscriptionEncoding,
    SubscriptionOutput,
    SubscriptionResponse,
    SystemStats,
    SystemStatsResponse,
    UserDetails,
    UserLinks,
    Username,
    UserProtocol,
    UserResponse,
)

logger = logging.getLogger("RVG-Gateway.api-v1")
GIB = 1024**3
_API_RESPONSE_HEADERS = {
    "Cache-Control": "no-store, max-age=0",
    "Pragma": "no-cache",
    "X-Content-Type-Options": "nosniff",
}


def _error_payload(
    code: str,
    message: str,
    details: Any | None = None,
) -> dict[str, Any]:
    return APIResponse[Any](
        success=False,
        data=None,
        error=APIErrorDetail(code=code, message=message, details=details),
        message=message,
    ).model_dump(mode="json")


def _raise_api_error(
    status_code: int,
    code: str,
    message: str,
    details: Any | None = None,
    *,
    headers: dict[str, str] | None = None,
) -> NoReturn:
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message, "details": details},
        headers=headers,
    )


def _success(data: Any, message: str) -> dict[str, Any]:
    return {"success": True, "data": data, "error": None, "message": message}


class UnifiedAPIRoute(APIRoute):
    """Guarantee an envelope even for an unforeseen service/core exception."""

    def get_route_handler(
        self,
    ) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original = super().get_route_handler()

        async def wrapped(request: Request) -> Response:
            try:
                response = await original(request)
                for name, value in _API_RESPONSE_HEADERS.items():
                    response.headers.setdefault(name, value)
                return response
            except (HTTPException, RequestValidationError):
                raise
            except Exception:
                # Never return exception text: a core command can contain paths,
                # domains, or other operational details that should stay in logs.
                logger.exception(
                    "Unhandled API v1 error on %s %s", request.method, request.url.path
                )
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    headers=_API_RESPONSE_HEADERS,
                    content=_error_payload(
                        "INTERNAL_ERROR",
                        "An unexpected database or VPN core error occurred.",
                    ),
                )

        return wrapped


router = APIRouter(
    prefix="/api/v1",
    tags=["Bot administration"],
    dependencies=[Depends(require_api_key)],
    route_class=UnifiedAPIRoute,
)


_CORE_PROTOCOLS: dict[UserProtocol, str] = {
    UserProtocol.VLESS: "vless-ws",
    UserProtocol.VLESS_WS: "vless-ws",
    UserProtocol.VLESS_XHTTP_PACKET_UP: "xhttp-packet-up",
    UserProtocol.VLESS_XHTTP_STREAM_UP: "xhttp-stream-up",
    UserProtocol.TROJAN: "trojan-ws",
    UserProtocol.TROJAN_WS: "trojan-ws",
    UserProtocol.TROJAN_XHTTP_PACKET_UP: "trojan-xhttp-packet-up",
    UserProtocol.TROJAN_XHTTP_STREAM_UP: "trojan-xhttp-stream-up",
    UserProtocol.SHADOWSOCKS: "shadowsocks",
    UserProtocol.MTPROTO: "mtproto",
}


def _panel() -> Any:
    # Lazy import avoids a circular import while ``main.py`` registers routers.
    import main

    return main


def _username_key(value: str) -> str:
    return value.strip().casefold()


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def _now_for(value: datetime | None = None) -> datetime:
    if value is not None and value.tzinfo is not None:
        return datetime.now(value.tzinfo)
    return datetime.now()


def _public_base_url(panel: Any) -> str:
    configured = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")
    if configured:
        if not configured.startswith(("http://", "https://")):
            configured = f"https://{configured}"
        return configured

    host = str(panel.get_host()).strip().rstrip("/")
    if host.startswith(("http://", "https://")):
        return host
    scheme = "http" if host.startswith(("localhost", "127.0.0.1", "[::1]")) else "https"
    return f"{scheme}://{host}"


def _protocol_family(protocol: str) -> str:
    if protocol.startswith("trojan"):
        return "trojan"
    if protocol.startswith("xhttp") or protocol.startswith("vless"):
        return "vless"
    if protocol.startswith("shadow"):
        return "shadowsocks"
    if protocol == "mtproto":
        return "mtproto"
    return protocol


def _link_key(uri: str, protocol: str) -> str:
    scheme = uri.split(":", 1)[0].lower() if ":" in uri else ""
    if scheme == "tg":
        return "mtproto"
    return scheme or _protocol_family(protocol)


def _status_reason(panel: Any, link: dict[str, Any]) -> str:
    if not bool(link.get("active", True)):
        return "disabled"
    if panel.is_link_expired(link):
        return "expired"
    limit = max(0, int(link.get("limit_bytes") or 0))
    used = max(0, int(link.get("used_bytes") or 0))
    if limit > 0 and used >= limit:
        return "traffic_exhausted"
    return "active"


def _connection_count(panel: Any, uid: str, protocol: str) -> int:
    count = sum(
        1 for conn in list(panel.connections.values()) if conn.get("uuid") == uid
    )
    if protocol == "mtproto":
        try:
            count += len(panel.mtproto.get_instance_connections(uid))
        except Exception:
            logger.exception("Could not read MTProto online state for %s", uid[:8])
    return count


class PanelUserService:
    """Thin transactional adapter around RVG's persistent link/core state."""

    def __init__(self) -> None:
        # Serializes bot writes so duplicate usernames and package extensions
        # cannot race each other.  Dashboard writes remain protected by the
        # panel's own LINKS_LOCK/SUBS_LOCK.
        self._mutation_lock = asyncio.Lock()

    async def _resolve(self, username: str) -> tuple[str, dict[str, Any]]:
        panel = _panel()
        wanted = _username_key(username)
        async with panel.LINKS_LOCK:
            explicit = [
                (uid, copy.deepcopy(link))
                for uid, link in panel.LINKS.items()
                if link.get("username")
                and _username_key(str(link.get("username"))) == wanted
            ]
            # Existing dashboard-created links predate the username field.  A
            # unique exact label remains manageable by the bot as a migration
            # path, without rewriting state during a read request.
            matches = explicit or [
                (uid, copy.deepcopy(link))
                for uid, link in panel.LINKS.items()
                if not link.get("username")
                and _username_key(str(link.get("label") or "")) == wanted
            ]

        if not matches:
            _raise_api_error(
                status.HTTP_404_NOT_FOUND,
                "USER_NOT_FOUND",
                f"User '{username}' was not found.",
            )
        if len(matches) > 1:
            _raise_api_error(
                status.HTTP_409_CONFLICT,
                "AMBIGUOUS_USERNAME",
                f"More than one legacy configuration uses the label '{username}'.",
            )
        return matches[0]

    async def _assert_username_available(self, username: str) -> None:
        panel = _panel()
        wanted = _username_key(username)
        async with panel.LINKS_LOCK:
            exists = any(
                _username_key(str(link.get("username") or link.get("label") or ""))
                == wanted
                for link in panel.LINKS.values()
            )
        if exists:
            _raise_api_error(
                status.HTTP_409_CONFLICT,
                "USERNAME_EXISTS",
                f"User '{username}' already exists.",
            )

    async def _strict_save(self) -> None:
        panel = _panel()
        result = await panel.save_state(strict=True)
        if result is False:
            raise OSError("state persistence failed")

    async def _build_details(self, uid: str) -> UserDetails:
        panel = _panel()
        async with panel.LINKS_LOCK:
            current = panel.LINKS.get(uid)
            if current is None:
                _raise_api_error(
                    status.HTTP_404_NOT_FOUND,
                    "USER_NOT_FOUND",
                    "The user no longer exists.",
                )
            link = copy.deepcopy(current)
            protocol = str(link.get("protocol") or panel.DEFAULT_PROTOCOL)
            uri = panel.generate_share_link(
                uid,
                panel.get_host(),
                remark=f"CB-{link.get('label') or link.get('username') or uid[:8]}",
                protocol=protocol,
            )

        username = str(link.get("username") or link.get("label") or uid)
        used = max(0, int(link.get("used_bytes") or 0))
        limit = max(0, int(link.get("limit_bytes") or 0))
        upload = max(0, int(link.get("upload_bytes") or 0))
        download = max(0, int(link.get("download_bytes") or 0))
        # Legacy records only contain aggregate traffic.  Account any
        # unclassified bytes as download so upload+download never understates
        # total usage while new directional counters are adopted.
        if upload + download < used:
            download += used - upload - download

        remaining = None if limit == 0 else max(0, limit - used)
        expires_at = _parse_datetime(link.get("expires_at"))
        if expires_at is None:
            days_remaining = None
        else:
            seconds = (expires_at - _now_for(expires_at)).total_seconds()
            days_remaining = max(0, math.ceil(seconds / 86_400))

        connection_count = _connection_count(panel, uid, protocol)
        reason = _status_reason(panel, link)
        links = {_link_key(uri, protocol): uri}
        base_url = _public_base_url(panel)
        created_at = _parse_datetime(link.get("created_at")) or datetime.now(
            timezone.utc
        )

        return UserDetails(
            username=username,
            uuid=uid,
            protocol=protocol,
            protocol_family=_protocol_family(protocol),
            created_at=created_at,
            expires_at=expires_at,
            expire_days_remaining=days_remaining,
            traffic_limit_bytes=limit,
            traffic_limit_gb=round(limit / GIB, 6),
            used_traffic_bytes=used,
            used_traffic_gb=round(used / GIB, 6),
            upload_bytes=upload,
            upload_gb=round(upload / GIB, 6),
            download_bytes=download,
            download_gb=round(download / GIB, 6),
            remaining_traffic_bytes=remaining,
            remaining_traffic_gb=None
            if remaining is None
            else round(remaining / GIB, 6),
            enabled=bool(link.get("active", True)),
            is_active=reason == "active",
            online=connection_count > 0,
            online_connections=connection_count,
            status_reason=reason,
            links=links,
            connection_links=[
                ConnectionLink(protocol=key, uri=value) for key, value in links.items()
            ],
            subscription_url=f"{base_url}/sub/{uid}",
            api_subscription_url=(
                f"{base_url}/api/v1/users/{quote(username, safe='')}/subscription"
            ),
        )

    async def get(self, username: str) -> UserDetails:
        uid, _ = await self._resolve(username)
        return await self._build_details(uid)

    async def create(self, request: CreateUserRequest) -> UserDetails:
        panel = _panel()
        async with self._mutation_lock:
            await self._assert_username_available(request.username)
            protocol = _CORE_PROTOCOLS[request.protocol]
            if protocol == "mtproto" and not panel.bottokentcpproxy.has_saved_token():
                _raise_api_error(
                    status.HTTP_503_SERVICE_UNAVAILABLE,
                    "MTPROTO_PROXY_NOT_CONFIGURED",
                    (
                        "MTProto provisioning requires a saved Railway token "
                        "for its public TCP proxy."
                    ),
                )
            try:
                created = await panel._create_link_core(
                    {
                        "username": request.username,
                        "label": request.username,
                        "limit_value": request.traffic_limit_gb,
                        "limit_unit": "GB",
                        "expires_days": request.expire_days,
                        "protocol": protocol,
                        "note": "Created through API v1",
                        "_await_mtproto_public_proxy": protocol == "mtproto",
                    }
                )
            except HTTPException:
                raise
            except (TypeError, ValueError) as exc:
                _raise_api_error(
                    status.HTTP_400_BAD_REQUEST,
                    "INVALID_PACKAGE",
                    "The user package could not be created from the supplied values.",
                    str(exc),
                )

            uid = str(created["uuid"])
            # ``_create_link_core`` accepts username in current releases.  Keep
            # this assignment for state restored from a transitional build.
            async with panel.LINKS_LOCK:
                if uid not in panel.LINKS:
                    _raise_api_error(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "CORE_SYNC_FAILED",
                        "The VPN core did not retain the newly created user.",
                    )
                panel.LINKS[uid]["username"] = request.username
                panel.LINKS[uid]["api_managed"] = True
                panel.LINKS[uid].setdefault("upload_bytes", 0)
                panel.LINKS[uid].setdefault("download_bytes", 0)
                mtproto_ready = bool(
                    panel.LINKS[uid].get("mtproto_public_host")
                    and panel.LINKS[uid].get("mtproto_public_port")
                )

            if protocol == "mtproto" and not mtproto_ready:
                await panel._delete_link_core(uid)
                await panel.save_state()
                _raise_api_error(
                    status.HTTP_502_BAD_GATEWAY,
                    "MTPROTO_PROXY_PROVISION_FAILED",
                    "The MTProto public TCP proxy could not be provisioned.",
                )

            try:
                await self._strict_save()
            except Exception:
                logger.exception(
                    "Could not persist newly created API user %s", request.username
                )
                try:
                    await panel._delete_link_core(uid)
                    await panel.save_state()
                except Exception:
                    logger.exception(
                        "Could not roll back failed creation for %s", uid[:8]
                    )
                _raise_api_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "DATABASE_ERROR",
                    (
                        "The user was rolled back because persistent storage "
                        "could not be updated."
                    ),
                )

            return await self._build_details(uid)

    async def extend(self, username: str, request: ExtendUserRequest) -> UserDetails:
        panel = _panel()
        async with self._mutation_lock:
            uid, _ = await self._resolve(username)
            added_bytes = int(request.add_traffic_gb * GIB)
            if request.add_traffic_gb > 0 and added_bytes <= 0:
                _raise_api_error(
                    status.HTTP_400_BAD_REQUEST,
                    "INVALID_TRAFFIC_EXTENSION",
                    "The traffic extension is too small to represent in bytes.",
                )

            async with panel.LINKS_LOCK:
                link = panel.LINKS.get(uid)
                if link is None:
                    _raise_api_error(
                        status.HTTP_404_NOT_FOUND,
                        "USER_NOT_FOUND",
                        "The user no longer exists.",
                    )
                old_limit = int(link.get("limit_bytes") or 0)
                old_expiry = link.get("expires_at")

                if added_bytes > 0:
                    # A zero limit means unlimited.  Converting it to a finite
                    # package grants the requested amount *remaining*, rather
                    # than immediately exhausting a previously busy account.
                    if old_limit == 0:
                        link["limit_bytes"] = (
                            int(link.get("used_bytes") or 0) + added_bytes
                        )
                    else:
                        link["limit_bytes"] = old_limit + added_bytes

                if request.add_days > 0:
                    parsed_expiry = _parse_datetime(old_expiry)
                    now = _now_for(parsed_expiry)
                    base = (
                        parsed_expiry if parsed_expiry and parsed_expiry > now else now
                    )
                    link["expires_at"] = (
                        base + timedelta(days=request.add_days)
                    ).isoformat()

            try:
                await self._strict_save()
            except Exception:
                async with panel.LINKS_LOCK:
                    if uid in panel.LINKS:
                        panel.LINKS[uid]["limit_bytes"] = old_limit
                        panel.LINKS[uid]["expires_at"] = old_expiry
                await panel.save_state()
                logger.exception("Package extension persistence failed for %s", uid[:8])
                _raise_api_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "DATABASE_ERROR",
                    (
                        "The package extension was rolled back because it could not "
                        "be persisted."
                    ),
                )

            panel.log_activity("link", f"بسته کاربر «{username}» از API تمدید شد", "ok")
            return await self._build_details(uid)

    async def set_status(
        self, username: str, request: SetUserStatusRequest
    ) -> UserDetails:
        panel = _panel()
        async with self._mutation_lock:
            uid, snapshot = await self._resolve(username)
            old_active = bool(snapshot.get("active", True))
            try:
                await panel._update_link_core(uid, {"active": request.is_active})
                await self._strict_save()
            except HTTPException:
                raise
            except Exception:
                logger.exception("Status/core synchronization failed for %s", uid[:8])
                if old_active != request.is_active:
                    try:
                        await panel._update_link_core(uid, {"active": old_active})
                        await panel.save_state()
                    except Exception:
                        logger.critical(
                            "Status rollback also failed for %s", uid[:8], exc_info=True
                        )
                _raise_api_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "CORE_SYNC_FAILED",
                    "The status change failed and was rolled back.",
                )
            return await self._build_details(uid)

    async def reset_traffic(self, username: str) -> UserDetails:
        panel = _panel()
        async with self._mutation_lock:
            uid, _ = await self._resolve(username)
            async with panel.LINKS_LOCK:
                link = panel.LINKS.get(uid)
                if link is None:
                    _raise_api_error(
                        status.HTTP_404_NOT_FOUND,
                        "USER_NOT_FOUND",
                        "The user no longer exists.",
                    )
                previous = (
                    int(link.get("used_bytes") or 0),
                    int(link.get("upload_bytes") or 0),
                    int(link.get("download_bytes") or 0),
                )
                link["used_bytes"] = 0
                link["upload_bytes"] = 0
                link["download_bytes"] = 0

            try:
                await self._strict_save()
            except Exception:
                async with panel.LINKS_LOCK:
                    if uid in panel.LINKS:
                        (
                            panel.LINKS[uid]["used_bytes"],
                            panel.LINKS[uid]["upload_bytes"],
                            panel.LINKS[uid]["download_bytes"],
                        ) = previous
                await panel.save_state()
                logger.exception("Traffic reset persistence failed for %s", uid[:8])
                _raise_api_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "DATABASE_ERROR",
                    (
                        "The traffic reset was rolled back because it could not be "
                        "persisted."
                    ),
                )

            panel.log_activity(
                "link", f"مصرف کاربر «{username}» از API ریست شد", "info"
            )
            return await self._build_details(uid)

    async def _restore_deleted(
        self,
        uid: str,
        link_snapshot: dict[str, Any],
        sub_snapshot: tuple[str, list[str]] | None,
    ) -> None:
        panel = _panel()
        async with panel.LINKS_LOCK:
            panel.LINKS[uid] = copy.deepcopy(link_snapshot)
        if sub_snapshot is not None:
            sub_id, link_ids = sub_snapshot
            async with panel.SUBS_LOCK:
                if sub_id in panel.SUBS:
                    panel.SUBS[sub_id]["link_ids"] = list(link_ids)

        if link_snapshot.get("protocol") == "mtproto" and link_snapshot.get(
            "active", True
        ):
            try:
                instance = await panel.mtproto.start_instance(
                    uid,
                    secret=link_snapshot.get("mtproto_secret"),
                    domain=link_snapshot.get(
                        "mtproto_domain", panel.mtproto.DEFAULT_FAKE_TLS_DOMAIN
                    ),
                    preferred_port=link_snapshot.get("mtproto_port"),
                    force_port=link_snapshot.get("mtproto_manual_port", False),
                    ad_tag=link_snapshot.get("ad_tag"),
                )
                async with panel.LINKS_LOCK:
                    if uid in panel.LINKS:
                        panel.LINKS[uid]["mtproto_port"] = instance["port"]
                        panel.LINKS[uid]["mtproto_secret"] = instance["secret"]
            except Exception:
                logger.critical(
                    "Could not restart MTProto during delete rollback for %s",
                    uid[:8],
                    exc_info=True,
                )

    async def delete(self, username: str) -> DeleteUserResult:
        panel = _panel()
        async with self._mutation_lock:
            uid, snapshot = await self._resolve(username)
            sub_snapshot: tuple[str, list[str]] | None = None
            sub_id = snapshot.get("sub_id")
            if sub_id:
                async with panel.SUBS_LOCK:
                    if sub_id in panel.SUBS:
                        sub_snapshot = (
                            sub_id,
                            list(panel.SUBS[sub_id].get("link_ids", [])),
                        )

            try:
                await panel._delete_link_core(uid)
                await self._strict_save()
            except HTTPException:
                raise
            except Exception:
                logger.exception("Delete/core synchronization failed for %s", uid[:8])
                await self._restore_deleted(uid, snapshot, sub_snapshot)
                await panel.save_state()
                _raise_api_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "DELETE_FAILED",
                    "The user deletion failed and panel state was restored.",
                )

            return DeleteUserResult(
                username=str(
                    snapshot.get("username") or snapshot.get("label") or username
                ),
                uuid=uid,
            )

    async def links(self, username: str) -> UserLinks:
        details = await self.get(username)
        return UserLinks(
            username=details.username,
            uuid=details.uuid,
            links=details.links,
            connection_links=details.connection_links,
        )

    async def subscription(
        self,
        username: str,
        output_format: SubscriptionEncoding,
    ) -> SubscriptionOutput:
        details = await self.get(username)
        raw = "\n".join(details.links.values())
        content = (
            base64.b64encode(raw.encode("utf-8")).decode("ascii")
            if output_format is SubscriptionEncoding.BASE64
            else raw
        )
        return SubscriptionOutput(
            username=details.username,
            uuid=details.uuid,
            format=output_format,
            content=content,
            links_count=len(details.links),
            is_active=details.is_active,
            subscription_url=details.subscription_url,
        )


service = PanelUserService()


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Provision a VPN user",
)
async def create_user(body: CreateUserRequest) -> dict[str, Any]:
    data = await service.create(body)
    return _success(data, "User created and synchronized with the VPN core.")


@router.get(
    "/users/{username}", response_model=UserResponse, summary="Get complete user status"
)
async def get_user(username: Username) -> dict[str, Any]:
    data = await service.get(username)
    return _success(data, "User status retrieved.")


@router.patch(
    "/users/{username}/extend",
    response_model=UserResponse,
    summary="Extend traffic and/or expiry",
)
async def extend_user(username: Username, body: ExtendUserRequest) -> dict[str, Any]:
    data = await service.extend(username, body)
    return _success(data, "User package extended and synchronized with the VPN core.")


@router.patch(
    "/users/{username}/status",
    response_model=UserResponse,
    summary="Enable or disable a user",
)
async def set_user_status(
    username: Username, body: SetUserStatusRequest
) -> dict[str, Any]:
    data = await service.set_status(username, body)
    action = "enabled" if body.is_active else "disabled"
    return _success(data, f"User {action} and synchronized with the VPN core.")


@router.post(
    "/users/{username}/reset-traffic",
    response_model=UserResponse,
    summary="Reset consumed traffic",
)
async def reset_user_traffic(username: Username) -> dict[str, Any]:
    data = await service.reset_traffic(username)
    return _success(data, "User traffic counters reset.")


@router.delete(
    "/users/{username}",
    response_model=DeleteUserResponse,
    summary="Delete a user permanently",
)
async def delete_user(username: Username) -> dict[str, Any]:
    data = await service.delete(username)
    return _success(data, "User deleted from persistent storage and the VPN core.")


@router.get(
    "/users/{username}/subscription",
    response_model=SubscriptionResponse,
    summary="Generate a plain or base64 subscription payload",
)
async def get_user_subscription(
    username: Username,
    output_format: Annotated[
        SubscriptionEncoding,
        Query(
            alias="format",
            description=(
                "Use 'plain' for newline-delimited URIs or 'base64' for a "
                "standard subscription payload."
            ),
        ),
    ] = SubscriptionEncoding.BASE64,
) -> dict[str, Any]:
    data = await service.subscription(username, output_format)
    return _success(data, f"{output_format.value} subscription generated.")


@router.get(
    "/users/{username}/links",
    response_model=LinksResponse,
    summary="Get raw connection URIs",
)
async def get_user_links(username: Username) -> dict[str, Any]:
    data = await service.links(username)
    return _success(data, "Raw connection links retrieved.")


def _existing_disk_path(candidate: Path) -> Path:
    path = candidate
    while not path.exists() and path != path.parent:
        path = path.parent
    return path if path.exists() else Path("/")


def _read_proc_memory() -> tuple[int, int, float]:
    values: dict[str, int] = {}
    with open("/proc/meminfo", encoding="utf-8") as proc:
        for line in proc:
            key, raw = line.split(":", 1)
            values[key] = int(raw.strip().split()[0]) * 1024
    total = values.get("MemTotal", 0)
    available = values.get("MemAvailable", values.get("MemFree", 0))
    used = max(0, total - available)
    percent = (used / total * 100) if total else 0.0
    return total, used, percent


def _collect_resources(data_dir: Path) -> dict[str, int | float]:
    """Collect host resources off the event loop, with a Linux stdlib fallback."""

    cpu_count = os.cpu_count() or 1
    try:
        import psutil

        cpu_percent = float(psutil.cpu_percent(interval=0.1))
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(str(_existing_disk_path(data_dir)))
        return {
            "cpu_percent": round(cpu_percent, 2),
            "cpu_count": int(psutil.cpu_count(logical=True) or cpu_count),
            "ram_percent": round(float(memory.percent), 2),
            "ram_used_bytes": int(memory.used),
            "ram_total_bytes": int(memory.total),
            "disk_percent": round(float(disk.percent), 2),
            "disk_used_bytes": int(disk.used),
            "disk_total_bytes": int(disk.total),
        }
    except ImportError:
        load_one = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0.0
        cpu_percent = min(100.0, max(0.0, load_one / cpu_count * 100))
        try:
            ram_total, ram_used, ram_percent = _read_proc_memory()
        except (OSError, ValueError):
            ram_total = ram_used = 0
            ram_percent = 0.0
        disk = shutil.disk_usage(_existing_disk_path(data_dir))
        disk_percent = disk.used / disk.total * 100 if disk.total else 0.0
        return {
            "cpu_percent": round(cpu_percent, 2),
            "cpu_count": cpu_count,
            "ram_percent": round(ram_percent, 2),
            "ram_used_bytes": ram_used,
            "ram_total_bytes": ram_total,
            "disk_percent": round(disk_percent, 2),
            "disk_used_bytes": disk.used,
            "disk_total_bytes": disk.total,
        }


async def _system_stats() -> SystemStats:
    panel = _panel()
    async with panel.LINKS_LOCK:
        links = {uid: copy.deepcopy(link) for uid, link in panel.LINKS.items()}

    connection_snapshot = list(panel.connections.values())
    online_ids = {
        str(conn.get("uuid"))
        for conn in connection_snapshot
        if conn.get("uuid") and str(conn.get("uuid")) in links
    }
    mtproto_connections = 0
    for uid, link in links.items():
        if link.get("protocol") != "mtproto":
            continue
        try:
            count = len(panel.mtproto.get_instance_connections(uid))
        except Exception:
            logger.exception("Could not inspect MTProto connections for system stats")
            count = 0
        if count:
            online_ids.add(uid)
            mtproto_connections += count

    total_used = sum(
        max(0, int(link.get("used_bytes") or 0)) for link in links.values()
    )
    total_upload = sum(
        max(0, int(link.get("upload_bytes") or 0)) for link in links.values()
    )
    total_download = sum(
        max(0, int(link.get("download_bytes") or 0)) for link in links.values()
    )
    classified = total_upload + total_download
    if classified < total_used:
        total_download += total_used - classified

    resources = await asyncio.to_thread(_collect_resources, Path(panel.DATA_DIR))
    return SystemStats(
        timestamp=datetime.now(timezone.utc),
        uptime_seconds=max(
            0, int(time.time() - float(panel.stats.get("start_time", time.time())))
        ),
        cpu_percent=float(resources["cpu_percent"]),
        cpu_count=int(resources["cpu_count"]),
        ram_percent=float(resources["ram_percent"]),
        ram_used_bytes=int(resources["ram_used_bytes"]),
        ram_total_bytes=int(resources["ram_total_bytes"]),
        disk_percent=float(resources["disk_percent"]),
        disk_used_bytes=int(resources["disk_used_bytes"]),
        disk_total_bytes=int(resources["disk_total_bytes"]),
        total_users=len(links),
        active_users=sum(1 for link in links.values() if panel.is_link_allowed(link)),
        online_users=len(online_ids),
        active_connections=len(connection_snapshot) + mtproto_connections,
        total_bandwidth_consumed_bytes=total_used,
        total_bandwidth_consumed_gb=round(total_used / GIB, 6),
        total_upload_bytes=total_upload,
        total_download_bytes=total_download,
    )


@router.get(
    "/system/stats",
    response_model=SystemStatsResponse,
    summary="Get host and VPN usage statistics",
)
async def get_system_stats() -> dict[str, Any]:
    data = await _system_stats()
    return _success(data, "System statistics retrieved.")


def _is_v1_path(request: Request) -> bool:
    path = request.url.path.rstrip("/")
    return path == "/api/v1" or path.startswith("/api/v1/")


def _code_for_status(status_code: int) -> str:
    return {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR",
        502: "CORE_SYNC_FAILED",
        503: "SERVICE_UNAVAILABLE",
    }.get(status_code, f"HTTP_{status_code}")


def install_exception_handlers(app: FastAPI) -> None:
    """Install v1-only envelope handlers while preserving legacy API behavior."""

    if getattr(app.state, "api_v1_exception_handlers_installed", False):
        return
    app.state.api_v1_exception_handlers_installed = True

    async def http_error_handler(request: Request, exc: StarletteHTTPException) -> Any:
        if not _is_v1_path(request):
            return await default_http_exception_handler(request, exc)

        detail = exc.detail
        if isinstance(detail, dict):
            code = str(detail.get("code") or _code_for_status(exc.status_code))
            message = str(detail.get("message") or "Request failed.")
            details = detail.get("details")
        else:
            code = _code_for_status(exc.status_code)
            message = str(detail or "Request failed.")
            details = None
        headers = {**_API_RESPONSE_HEADERS, **(exc.headers or {})}
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(code, message, jsonable_encoder(details)),
            headers=headers,
        )

    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> Any:
        if not _is_v1_path(request):
            return await default_validation_exception_handler(request, exc)
        details = jsonable_encoder(exc.errors())
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers=_API_RESPONSE_HEADERS,
            content=_error_payload(
                "VALIDATION_ERROR",
                "Request validation failed.",
                details,
            ),
        )

    app.add_exception_handler(StarletteHTTPException, cast(Any, http_error_handler))
    app.add_exception_handler(
        RequestValidationError,
        cast(Any, validation_error_handler),
    )
