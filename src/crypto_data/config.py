from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


SUPPORTED_BINANCE_INTERVALS = {
    "1m",
}

SUPPORTED_DERIVED_INTERVALS = {"5m", "10m", "30m", "1h", "1d", "1w", "1mo", "1yr"}


@dataclass(frozen=True)
class CollectorConfig:
    base_url: str
    symbols: tuple[str, ...]
    base_interval: str
    derived_intervals: tuple[str, ...]
    max_requests_per_run: int
    repair_lookback_days: int
    backfill_calls_per_pair: int
    request_limit: int


def load_config(path: Path) -> CollectorConfig:
    with path.open("rb") as handle:
        raw = tomllib.load(handle)

    settings = raw["settings"]
    base_interval = settings.get("base_interval", "1m")
    if base_interval not in SUPPORTED_BINANCE_INTERVALS:
        raise ValueError(f"Unsupported Binance base interval in config: {base_interval}")

    derived_intervals = tuple(settings.get("derived_intervals", ()))
    unsupported_derived = sorted(set(derived_intervals) - SUPPORTED_DERIVED_INTERVALS)
    if unsupported_derived:
        raise ValueError(f"Unsupported derived intervals in config: {', '.join(unsupported_derived)}")

    return CollectorConfig(
        base_url=settings.get("base_url", "https://api.binance.com").rstrip("/"),
        symbols=tuple(settings["symbols"]),
        base_interval=base_interval,
        derived_intervals=derived_intervals,
        max_requests_per_run=int(settings.get("max_requests_per_run", 80)),
        repair_lookback_days=int(settings.get("repair_lookback_days", 3)),
        backfill_calls_per_pair=int(settings.get("backfill_calls_per_pair", 2)),
        request_limit=int(settings.get("request_limit", 1000)),
    )
