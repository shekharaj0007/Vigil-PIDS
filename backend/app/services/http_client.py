"""Shared async HTTP client and a small TTL cache for external API calls."""

import time
from typing import Any, Optional

import httpx

_client: Optional[httpx.AsyncClient] = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=20.0)
    return _client


async def close_client() -> None:
    global _client
    if _client is not None and not _client.is_closed:
        await _client.aclose()
    _client = None


class TTLCache:
    """In-memory cache with per-entry expiry; oldest entry evicted when full."""

    def __init__(self, ttl_seconds: float, max_items: int = 256):
        self.ttl = ttl_seconds
        self.max_items = max_items
        self._data: dict[Any, tuple[Any, float]] = {}

    def get(self, key: Any) -> Any:
        item = self._data.get(key)
        if item is None:
            return None
        value, expires_at = item
        if time.monotonic() > expires_at:
            self._data.pop(key, None)
            return None
        return value

    def set(self, key: Any, value: Any) -> None:
        if len(self._data) >= self.max_items:
            oldest = min(self._data, key=lambda k: self._data[k][1])
            self._data.pop(oldest, None)
        self._data[key] = (value, time.monotonic() + self.ttl)
