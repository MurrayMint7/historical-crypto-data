from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import tomllib


SUPPORTED_BINANCE_INTERVALS = {
    "1s",
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
    "6h",
    "8h",
    "12h",
    "1d",
    "3d",
    "1w",
    "1M",
}


@dataclass(frozen=True)
class CollectorConfig:
    base_url: str
    symbols: tuple[str, ...]
    intervals: tuple[str, ...]
    start_dates: dict[str, datetime]
    max_requests_per_run: int
    repair_lookback_days: int
    backfill_calls_per_pair: int
    request_limit: int


def parse_datetime(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_config(path: Path) -> CollectorConfig:
    with path.open("rb") as handle:
        raw = tomllib.load(handle)

    settings = raw["settings"]
    symbols = tuple(settings["symbols"])
    intervals = tuple(settings["intervals"])
    unsupported = sorted(set(intervals) - SUPPORTED_BINANCE_INTERVALS)
    if unsupported:
        raise ValueError(f"Unsupported Binance intervals in config: {', '.join(unsupported)}")

    start_dates = {
        symbol: parse_datetime(raw["start_dates"][symbol])
        for symbol in symbols
    }

    return CollectorConfig(
        base_url=settings.get("base_url", "https://api.binance.com").rstrip("/"),
        symbols=symbols,
        intervals=intervals,
        start_dates=start_dates,
        max_requests_per_run=int(settings.get("max_requests_per_run", 80)),
        repair_lookback_days=int(settings.get("repair_lookback_days", 3)),
        backfill_calls_per_pair=int(settings.get("backfill_calls_per_pair", 2)),
        request_limit=int(settings.get("request_limit", 1000)),
    )

