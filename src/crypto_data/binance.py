from __future__ import annotations

import time
from typing import Any

import requests


class BinanceClient:
    def __init__(self, base_url: str, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def klines(
        self,
        symbol: str,
        interval: str,
        start_time_ms: int,
        end_time_ms: int | None = None,
        limit: int = 1000,
    ) -> list[list[Any]]:
        params: dict[str, Any] = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time_ms,
            "limit": limit,
        }
        if end_time_ms is not None:
            params["endTime"] = end_time_ms

        url = f"{self.base_url}/api/v3/klines"
        response = self.session.get(url, params=params, timeout=self.timeout)
        if response.status_code in {418, 429}:
            retry_after = int(response.headers.get("Retry-After", "60"))
            time.sleep(retry_after)
            response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

