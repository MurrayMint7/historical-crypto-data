from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


def dt_to_ms(value: datetime) -> int:
    return int(value.astimezone(timezone.utc).timestamp() * 1000)


def ms_to_dt(value: int) -> datetime:
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc)


def now_ms() -> int:
    return dt_to_ms(datetime.now(timezone.utc))


class StateStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"pairs": {}}
        return json.loads(self.path.read_text())

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, sort_keys=True) + "\n")

    def get_pair(self, symbol: str, interval: str) -> dict[str, Any]:
        key = f"{symbol}:{interval}"
        return self.data.setdefault("pairs", {}).setdefault(key, {})

    def set_backfill_cursor(self, symbol: str, interval: str, value_ms: int) -> None:
        self.get_pair(symbol, interval)["backfill_cursor_ms"] = value_ms

    def mark_repaired(self, symbol: str, interval: str, value_ms: int) -> None:
        self.get_pair(symbol, interval)["last_repaired_through_ms"] = value_ms

    def mark_update(
        self,
        symbol: str,
        interval: str,
        oldest_open_time_ms: int,
        newest_open_time_ms: int,
        rows: int,
    ) -> None:
        pair = self.get_pair(symbol, interval)
        existing_first = pair.get("first_open_time_ms")
        pair["first_open_time_ms"] = (
            oldest_open_time_ms
            if existing_first is None
            else min(int(existing_first), oldest_open_time_ms)
        )
        pair["latest_open_time_ms"] = max(int(pair.get("latest_open_time_ms", 0)), newest_open_time_ms)
        pair["last_rows_written"] = rows
        pair["updated_at_ms"] = now_ms()
