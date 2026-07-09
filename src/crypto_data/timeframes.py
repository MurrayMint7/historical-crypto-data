from __future__ import annotations

from datetime import timedelta


INTERVALS = {
    "1s": timedelta(seconds=1),
    "1m": timedelta(minutes=1),
    "3m": timedelta(minutes=3),
    "5m": timedelta(minutes=5),
    "10m": timedelta(minutes=10),
    "15m": timedelta(minutes=15),
    "30m": timedelta(minutes=30),
    "1h": timedelta(hours=1),
    "2h": timedelta(hours=2),
    "4h": timedelta(hours=4),
    "6h": timedelta(hours=6),
    "8h": timedelta(hours=8),
    "12h": timedelta(hours=12),
    "1d": timedelta(days=1),
    "3d": timedelta(days=3),
    "1w": timedelta(weeks=1),
}


def interval_delta(interval: str) -> timedelta:
    if interval == "1M":
        raise ValueError("Monthly intervals are calendar-based and are not represented by a fixed timedelta.")
    return INTERVALS[interval]
