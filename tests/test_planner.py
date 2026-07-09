from datetime import datetime, timezone
from pathlib import Path

from crypto_data.config import load_config
from crypto_data.planner import build_repair_plan, next_backfill_start_ms


def test_repair_plan_covers_every_symbol_interval() -> None:
    config = load_config(Path("config/assets.toml"))
    now = datetime(2026, 7, 9, tzinfo=timezone.utc)
    symbols = ["BTCUSDT", "ETHUSDT"]

    plans = build_repair_plan(config, symbols, now)

    assert len(plans) == len(symbols)
    assert {plan.reason for plan in plans} == {"repair"}
    assert {plan.interval for plan in plans} == {"1m"}


def test_next_backfill_start_ignores_repair_only_first_open() -> None:
    assert next_backfill_start_ms({"first_open_time_ms": 123}) == 0
    assert next_backfill_start_ms({"backfill_cursor_ms": 456, "first_open_time_ms": 123}) == 456
