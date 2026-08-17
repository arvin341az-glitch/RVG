# shadowsocks.py
import asyncio
import hashlib
import hmac
import secrets
import socket
import struct
import time
from datetime import datetime


from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305, AESGCM
from fastapi import WebSocket

from main import (
    LINKS,
    LINKS_LOCK,
    logger,
    is_link_allowed,
)

RELAY_BUF = 1024 * 1024
SOCK_BUF = 4 * 1024 * 1024
WRITE_HIGH_WATER = 512 * 1024

CIPHERS = {
    "chacha20-ietf-poly1305": {"key_len": 32, "salt_len": 32, "nonce_len": 12, "cls": ChaCha20Poly1305},
    "aes-256-gcm": {"key_len": 32, "salt_len": 32, "nonce_len": 12, "cls": AESGCM},
}
DEFAULT_CIPHER = "chacha20-ietf-poly1305"


def _ws_client_ip(ws: WebSocket) -> str:
    fwd = ws.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    real_ip = ws.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return ws.client.host if ws.client else "نامشخص"


def _tune_socket(writer: asyncio.StreamWriter):
    sock = writer.transport.get_extra_info("socket")
    if not sock:
        return
    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SOCK_BUF)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, SOCK_BUF)
        if hasattr(socket, "TCP_QUICKACK"):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
    except OSError as e:
        logger.warning(f"SS _tune_socket failed: {e}")


# ── HKDF-SHA1 برای مشتق‌سازی subkey از master key + salt (طبق spec شادوساکس) ──
def _hkdf_sha1(key: bytes, salt: bytes, info: bytes, length: int) -> bytes:
    prk = hmac.HMAC(salt, key, hashlib.sha1).digest()
    okm, t, i = b"", b"", 1
    while len(okm) < length:
        t = hmac.new(prk, t + info + bytes([i]), hashlib.sha1).digest()
        okm += t
        i += 1
    return okm[:length]


def derive_key(password: str, key_len: int) -> bytes:
    """EVP_BytesToKey سازگار با shadowsocks (مثل قدیم) برای گرفتن master key از پسورد."""
    d = d_prev = b""
    while len(d) < key_len:
        d_prev = hashlib.md5(d_prev + password.encode()).digest()
        d += d_prev
    return d[:key_len]


def _subkey(master_key: bytes, salt: bytes, key_len: int) -> bytes:
    return _hkdf_sha1(master_key, salt, b"ss-subkey", key_len)


class _AEADStream:
    """
    رمزگشایی/رمزنگاری فریم‌های AEAD SS به‌صورت stream:
      chunk = len(2B, encrypted+tag) + payload(encrypted+tag)
    nonce به‌صورت little-endian counter افزایش پیدا می‌کند (طبق spec).
    """
    def __init__(self, master_key: bytes, cipher_name: str):
        info = CIPHERS[cipher_name]
        self.key_len = info["key_len"]
        self.salt_len = info["salt_len"]
        self.nonce_len = info["nonce_len"]
        self.cipher_cls = info["cls"]
        self.master_key = master_key

        self.enc_salt = secrets.token_bytes(self.salt_len)
        self.enc_key = _subkey(master_key, self.enc_salt, self.key_len)
        self.enc_aead = self.cipher_cls(self.enc_key)
        self.enc_nonce = 0
        self.enc_salt_sent = False

        self.dec_salt = None
        self.dec_aead = None
        self.dec_nonce = 0
        self._buf = bytearray()

    def _nonce_bytes(self, counter: int) -> bytes:
        return counter.to_bytes(self.nonce_len, "little")

    # ---------- encrypt (server -> client) ----------
    def encrypt_chunk(self, payload: bytes) -> bytes:
        out = bytearray()
        if not self.enc_salt_sent:
            out += self.enc_salt
            self.enc_salt_sent = True
        length = struct.pack(">H", len(payload))
        enc_len = self.enc_aead.encrypt(self._nonce_bytes(self.enc_nonce), length, None)
        self.enc_nonce += 1
        enc_payload = self.enc_aead.encrypt(self._nonce_bytes(self.enc_nonce), payload, None)
        self.enc_nonce += 1
        out += enc_len + enc_payload
        return bytes(out)

    # ---------- decrypt (client -> server), استریمی ----------
    def feed(self, data: bytes):
        self._buf += data

    def _ensure_dec_key(self) -> bool:
        if self.dec_aead is not None:
            return True
        if len(self._buf) < self.salt_len:
            return False
        self.dec_salt = bytes(self._buf[: self.salt_len])
        del self._buf[: self.salt_len]
        dec_key = _subkey(self.master_key, self.dec_salt, self.key_len)
        self.dec_aead = self.cipher_cls(dec_key)
        return True

    def try_decrypt_chunks(self):
        """generator که هر chunk کامل رمزگشایی‌شده رو yield می‌کند."""
        if not self._ensure_dec_key():
            return
        tag_len = 16
        while True:
            if len(self._buf) < 2 + tag_len:
                return
            enc_len = bytes(self._buf[: 2 + tag_len])
            try:
                length_bytes = self.dec_aead.decrypt(self._nonce_bytes(self.dec_nonce), enc_len, None)
            except Exception:
                raise ValueError("AEAD decrypt (length) failed — bad key/tag")
            self.dec_nonce += 1
            length = struct.unpack(">H", length_bytes)[0]
            if length > 0x3FFF:
                raise ValueError("invalid SS AEAD chunk length (exceeds spec limit)")
            need = 2 + tag_len + length + tag_len
            if len(self._buf) < need:
                return
            del self._buf[: 2 + tag_len]
            enc_payload = bytes(self._buf[: length + tag_len])
            del self._buf[: length + tag_len]
            try:
                payload = self.dec_aead.decrypt(self._nonce_bytes(self.dec_nonce), enc_payload, None)
            except Exception:
                raise ValueError("AEAD decrypt (payload) failed — bad key/tag")
            self.dec_nonce += 1
            yield payload


def parse_socks5_addr(buf: bytes):
    """ATYP(1) + ADDR + PORT(2) -> (address, port, consumed_len)"""
    if len(buf) < 2:
        raise ValueError("too short")
    atyp = buf[0]
    pos = 1
    if atyp == 1:
        if len(buf) < pos + 4 + 2:
            raise ValueError("short ipv4")
        address = ".".join(str(b) for b in buf[pos:pos + 4]); pos += 4
    elif atyp == 3:
        dlen = buf[pos]; pos += 1
        if len(buf) < pos + dlen + 2:
            raise ValueError("short domain")
        address = buf[pos:pos + dlen].decode("utf-8", errors="ignore"); pos += dlen
    elif atyp == 4:
        if len(buf) < pos + 16 + 2:
            raise ValueError("short ipv6")
        ab = buf[pos:pos + 16]; pos += 16
        address = ":".join(f"{ab[i]:02x}{ab[i+1]:02x}" for i in range(0, 16, 2))
    else:
        raise ValueError(f"unknown atyp {atyp}")
    port = int.from_bytes(buf[pos:pos + 2], "big"); pos += 2
    return address, port, pos


# ── تشخیص لینک از روی رمزنگاری موفق (چون SS پسورد را در URL/هدر نمی‌فرستد،
#    باید روی همه‌ی لینک‌های shadowsocks فعال امتحان کنیم تا سالت/تگ جور دربیاید) ──
async def _find_matching_ss_link(first_bytes: bytes):
    async with LINKS_LOCK:
        candidates = [
            (uid, d) for uid, d in LINKS.items()
            if d.get("protocol") == "shadowsocks" and is_link_allowed(d)
        ]
    for uid, d in candidates:
        cipher_name = d.get("ss_cipher", DEFAULT_CIPHER)
        info = CIPHERS.get(cipher_name)
        if not info:
            continue
        master_key = derive_key(d.get("ss_password", ""), info["key_len"])
        stream = _AEADStream(master_key, cipher_name)
        stream.feed(first_bytes)
        try:
            chunks = list(stream.try_decrypt_chunks())
        except ValueError:
            continue
        if chunks:
            return uid, stream, chunks
    return None, None, None


# shadowsocks_ws_tunnel و توابع relay آن به protocol/shadowsocks/websocket.py منتقل شدند.


def generate_ss_link(host: str, port: int, cipher: str, password: str, remark: str) -> str:
    """ss://base64(method:password)@host:port?plugin=...#remark — با پلاگین v2ray-plugin برای WS+TLS"""
    import base64
    from urllib.parse import quote

    userinfo = base64.urlsafe_b64encode(f"{cipher}:{password}".encode()).decode().rstrip("=")
    plugin = quote(f"v2ray-plugin;tls;mux=0;path=/ss-ws;host={host}")
    return f"ss://{userinfo}@{host}:{port}/?plugin={plugin}#{quote(remark)}"
