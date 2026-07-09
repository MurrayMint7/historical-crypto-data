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

    def exchange_info(self) -> dict[str, Any]:
        response = self.session.get(f"{self.base_url}/api/v3/exchangeInfo", timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def ticker_24hr(self) -> list[dict[str, Any]]:
        response = self.session.get(f"{self.base_url}/api/v3/ticker/24hr", timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def top_symbols_by_quote_volume(
        self,
        quote_asset: str,
        top_n: int,
        excluded_base_assets: frozenset[str],
    ) -> list[str]:
        exchange_info = self.exchange_info()
        tradable: dict[str, str] = {}
        for item in exchange_info.get("symbols", []):
            if item.get("status") != "TRADING":
                continue
            if item.get("quoteAsset") != quote_asset:
                continue
            base_asset = str(item.get("baseAsset", ""))
            if base_asset in excluded_base_assets:
                continue
            tradable[str(item["symbol"])] = base_asset

        tickers = self.ticker_24hr()
        ranked = sorted(
            (
                item
                for item in tickers
                if str(item.get("symbol")) in tradable
            ),
            key=lambda item: float(item.get("quoteVolume", 0)),
            reverse=True,
        )
        return [str(item["symbol"]) for item in ranked[:top_n]]
