from datetime import datetime, timezone
from pathlib import Path

from crypto_data.config import load_config
from crypto_data.planner import build_repair_plan


def test_repair_plan_covers_every_symbol_interval() -> None:
    config = load_config(Path("config/assets.toml"))
    now = datetime(2026, 7, 9, tzinfo=timezone.utc)

    plans = build_repair_plan(config, now)

    assert len(plans) == len(config.symbols) * len(config.intervals)
    assert {plan.reason for plan in plans} == {"repair"}

