"""Pydantic v2 contracts for the bot-facing REST API.

The API models deliberately reject unknown fields.  This prevents misspelled
package fields from being silently ignored by an automation client and causing
a user to be provisioned with an unintended quota or expiry.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Generic, TypeVar

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)


class StrictAPIModel(BaseModel):
    """Base contract shared by all public v1 request/response models."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
        validate_default=True,
        populate_by_name=True,
    )


Username = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=64,
        pattern=r"^[A-Za-z0-9](?:[A-Za-z0-9_.-]*[A-Za-z0-9])?$",
    ),
]


class UserProtocol(str, Enum):
    """Protocols/transports that the currently bundled RVG core can serve.

    ``vless`` and ``trojan`` are convenient aliases for their WebSocket
    transports.  VMess is intentionally not advertised: this gateway does not
    implement a VMess inbound and returning a fabricated link would be unsafe.
    """

    VLESS = "vless"
    VLESS_WS = "vless-ws"
    VLESS_XHTTP_PACKET_UP = "xhttp-packet-up"
    VLESS_XHTTP_STREAM_UP = "xhttp-stream-up"
    TROJAN = "trojan"
    TROJAN_WS = "trojan-ws"
    TROJAN_XHTTP_PACKET_UP = "trojan-xhttp-packet-up"
    TROJAN_XHTTP_STREAM_UP = "trojan-xhttp-stream-up"
    SHADOWSOCKS = "shadowsocks"
    MTPROTO = "mtproto"


class CreateUserRequest(StrictAPIModel):
    username: Username
    traffic_limit_gb: float = Field(
        ge=0,
        le=1_048_576,
        allow_inf_nan=False,
        strict=True,
        description="Binary gigabytes (GiB). Zero means unlimited.",
    )
    expire_days: int = Field(
        ge=0,
        le=36_500,
        strict=True,
        description="Days from creation. Zero means no expiry.",
    )
    protocol: UserProtocol


class ExtendUserRequest(StrictAPIModel):
    add_traffic_gb: float = Field(
        default=0,
        ge=0,
        le=1_048_576,
        allow_inf_nan=False,
        strict=True,
        validation_alias=AliasChoices(
            "add_traffic_gb", "add_gb", "traffic_gb", "traffic_limit_gb"
        ),
        description="Additional binary gigabytes (GiB).",
    )
    add_days: int = Field(
        default=0,
        ge=0,
        le=36_500,
        strict=True,
        validation_alias=AliasChoices("add_days", "days", "expire_days"),
        description="Days added to the current expiry, or from now if expired.",
    )

    @model_validator(mode="after")
    def require_at_least_one_extension(self) -> ExtendUserRequest:
        if self.add_traffic_gb <= 0 and self.add_days <= 0:
            raise ValueError(
                "at least one of add_traffic_gb or add_days must be greater than zero"
            )
        return self


class SetUserStatusRequest(StrictAPIModel):
    is_active: bool = Field(
        strict=True,
        validation_alias=AliasChoices("is_active", "active", "enabled"),
    )


class ConnectionLink(StrictAPIModel):
    protocol: str
    uri: str


class UserDetails(StrictAPIModel):
    username: str
    uuid: str
    protocol: str
    protocol_family: str
    created_at: datetime
    expires_at: datetime | None
    expire_days_remaining: int | None

    traffic_limit_bytes: int
    traffic_limit_gb: float
    used_traffic_bytes: int
    used_traffic_gb: float
    upload_bytes: int
    upload_gb: float
    download_bytes: int
    download_gb: float
    remaining_traffic_bytes: int | None
    remaining_traffic_gb: float | None

    enabled: bool
    is_active: bool
    online: bool
    online_connections: int
    status_reason: str

    links: dict[str, str]
    connection_links: list[ConnectionLink]
    subscription_url: str
    api_subscription_url: str


class DeleteUserResult(StrictAPIModel):
    username: str
    uuid: str
    deleted: bool = True


class UserLinks(StrictAPIModel):
    username: str
    uuid: str
    links: dict[str, str]
    connection_links: list[ConnectionLink]


class SubscriptionEncoding(str, Enum):
    BASE64 = "base64"
    PLAIN = "plain"


class SubscriptionOutput(StrictAPIModel):
    username: str
    uuid: str
    format: SubscriptionEncoding
    content: str
    links_count: int
    is_active: bool
    subscription_url: str


class SystemStats(StrictAPIModel):
    timestamp: datetime
    uptime_seconds: int
    cpu_percent: float
    cpu_count: int
    ram_percent: float
    ram_used_bytes: int
    ram_total_bytes: int
    disk_percent: float
    disk_used_bytes: int
    disk_total_bytes: int
    total_users: int
    active_users: int
    online_users: int
    active_connections: int
    total_bandwidth_consumed_bytes: int
    total_bandwidth_consumed_gb: float
    total_upload_bytes: int
    total_download_bytes: int


class APIErrorDetail(StrictAPIModel):
    code: str
    message: str
    details: Any | None = None


DataT = TypeVar("DataT")


class APIResponse(StrictAPIModel, Generic[DataT]):
    success: bool
    data: DataT | None = None
    error: APIErrorDetail | None = None
    message: str

    @model_validator(mode="after")
    def validate_envelope(self) -> APIResponse[DataT]:
        if self.success and (self.data is None or self.error is not None):
            raise ValueError("successful responses require data and no error")
        if not self.success and (self.data is not None or self.error is None):
            raise ValueError("failed responses require an error and no data")
        return self


# Concrete aliases keep the generated OpenAPI schema readable and allow every
# endpoint to validate its output as well as its input.
UserResponse = APIResponse[UserDetails]
DeleteUserResponse = APIResponse[DeleteUserResult]
LinksResponse = APIResponse[UserLinks]
SubscriptionResponse = APIResponse[SubscriptionOutput]
SystemStatsResponse = APIResponse[SystemStats]
