from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .config import CollectorConfig
from .state import dt_to_ms


@dataclass(frozen=True)
class FetchPlan:
    symbol: str
    interval: str
    start_ms: int
    end_ms: int | None
    reason: str


def build_repair_plan(config: CollectorConfig, symbols: list[str], now: datetime) -> list[FetchPlan]:
    now = now.astimezone(timezone.utc)
    start = now - timedelta(days=config.repair_lookback_days)
    return [
        FetchPlan(
            symbol=symbol,
            interval=config.base_interval,
            start_ms=dt_to_ms(start),
            end_ms=dt_to_ms(now),
            reason="repair",
        )
        for symbol in symbols
    ]


def next_backfill_start_ms(pair_state: dict[str, object]) -> int:
    cursor = pair_state.get("backfill_cursor_ms")
    if cursor is not None:
        return int(cursor)
    return 0
