from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from crypto_data.collector import run_update

MINUTE_MS = 60_000


class FakeClient:
    """Serves continuous 1m klines for any requested window up to now."""

    def __init__(self, first_ms: int, now_ms: int) -> None:
        self.first_ms = first_ms
        self.now_ms = now_ms
        self.calls = 0

    def klines(self, symbol, interval, start_time_ms, end_time_ms=None, limit=1000):
        self.calls += 1
        start = max(start_time_ms, self.first_ms)
        start += -start % MINUTE_MS
        end = min(end_time_ms if end_time_ms is not None else self.now_ms, self.now_ms)
        rows = []
        open_ms = start
        while open_ms + MINUTE_MS - 1 <= end and len(rows) < limit:
            rows.append([open_ms, "1", "2", "0.5", "1.5", "1", open_ms + MINUTE_MS - 1, "1", 1, "1", "1", "0"])
            open_ms += MINUTE_MS
        return rows


def _write_config(root: Path, repair_days: int = 3) -> None:
    (root / "config").mkdir()
    (root / "config" / "assets.toml").write_text(
        "[settings]\n"
        f"repair_lookback_days = {repair_days}\n"
        "max_requests_per_run = 80\n"
        "backfill_calls_per_pair = 0\n"
        'base_interval = "1m"\n'
        'symbols = ["BTCUSDT"]\n'
        'derived_intervals = ["1d"]\n'
    )


def test_repair_pages_through_the_whole_lookback_window(tmp_path) -> None:
    _write_config(tmp_path)
    now = datetime.now(timezone.utc)
    client = FakeClient(first_ms=0, now_ms=int(now.timestamp() * 1000))

    summary = run_update(tmp_path, client=client)

    minutes = pd.read_parquet(tmp_path / "data" / "BTCUSDT" / "1m" / f"{now.year}.parquet")
    if (now - timedelta(days=3)).year != now.year:
        minutes = pd.concat(
            [minutes, pd.read_parquet(tmp_path / "data" / "BTCUSDT" / "1m" / f"{now.year - 1}.parquet")]
        )
    assert summary.requests_used == client.calls == 5
    assert len(minutes) >= 3 * 1440 - 1

    daily = pd.read_parquet(tmp_path / "data" / "BTCUSDT" / "1d" / f"{now.year}.parquet")
    two_days_ago = datetime(now.year, now.month, now.day, tzinfo=timezone.utc) - timedelta(days=2)
    row = daily[daily["open_time"] == int(two_days_ago.timestamp() * 1000)]
    assert int(row["close_time"].iloc[0]) == int((two_days_ago + timedelta(days=1)).timestamp() * 1000) - 1


def test_repair_days_override_and_budget(tmp_path) -> None:
    _write_config(tmp_path)
    client = FakeClient(first_ms=0, now_ms=int(datetime.now(timezone.utc).timestamp() * 1000))

    summary = run_update(tmp_path, client=client, repair_days=10, max_requests=4)

    assert summary.requests_used == 4
    assert summary.rows_received == 4000
