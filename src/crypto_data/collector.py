from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .aggregate import aggregate_ohlcv
from .binance import BinanceClient
from .config import CollectorConfig, load_config
from .planner import FetchPlan, build_repair_plan, next_backfill_start_ms
from .state import StateStore, now_ms
from .storage import ParquetStore, klines_to_frame
from .timeframes import interval_delta


@dataclass
class UpdateSummary:
    requests_used: int = 0
    rows_received: int = 0
    rows_written: int = 0


def run_update(
    repo_root: Path,
    config_path: Path | None = None,
    max_requests: int | None = None,
) -> UpdateSummary:
    config = load_config(config_path or repo_root / "config" / "assets.toml")
    budget = max_requests or config.max_requests_per_run
    state = StateStore(repo_root / "metadata" / "state.json")
    store = ParquetStore(repo_root / "data")
    client = BinanceClient(config.base_url)
    summary = UpdateSummary()
    symbols = client.top_symbols_by_quote_volume(
        quote_asset=config.quote_asset,
        top_n=config.top_n_symbols,
        excluded_base_assets=config.excluded_base_assets,
    )
    print(f"selected symbols: {', '.join(symbols)}")

    repair_plans = build_repair_plan(config, symbols, datetime.now(timezone.utc))
    for plan in repair_plans:
        if summary.requests_used >= budget:
            break
        _execute_plan(client, store, state, config, plan, summary)
        state.mark_repaired(plan.symbol, plan.interval, now_ms())

    for symbol in symbols:
        if summary.requests_used >= budget:
            state.save()
            return summary

        calls_for_pair = 0
        pair_state = state.get_pair(symbol, config.base_interval)
        while calls_for_pair < config.backfill_calls_per_pair and summary.requests_used < budget:
            start_ms = _next_start_ms(store, pair_state, symbol, config.base_interval)
            plan = FetchPlan(
                symbol=symbol,
                interval=config.base_interval,
                start_ms=start_ms,
                end_ms=None,
                reason="backfill",
            )
            rows = _execute_plan(client, store, state, config, plan, summary)
            calls_for_pair += 1
            if not rows:
                break
            pair_state = state.get_pair(symbol, config.base_interval)

    state.save()
    return summary


def _next_start_ms(
    store: ParquetStore,
    pair_state: dict[str, object],
    symbol: str,
    interval: str,
) -> int:
    cursor_ms = next_backfill_start_ms(pair_state)
    first_open_ms = int(pair_state.get("first_open_time_ms", cursor_ms)) if cursor_ms else 0
    gap_ms = store.find_first_gap_start(
        symbol=symbol,
        interval=interval,
        expected_delta_ms=int(interval_delta(interval).total_seconds() * 1000),
        lower_bound_ms=first_open_ms,
        upper_bound_ms=now_ms(),
    )
    return min(cursor_ms, gap_ms)


def _execute_plan(
    client: BinanceClient,
    store: ParquetStore,
    state: StateStore,
    config: CollectorConfig,
    plan: FetchPlan,
    summary: UpdateSummary,
) -> int:
    rows = client.klines(
        symbol=plan.symbol,
        interval=plan.interval,
        start_time_ms=plan.start_ms,
        end_time_ms=plan.end_ms,
        limit=config.request_limit,
    )
    summary.requests_used += 1
    summary.rows_received += len(rows)
    if not rows:
        return 0

    frame = klines_to_frame(rows, plan.symbol, plan.interval)
    written = store.write(frame)
    written += _write_derived_intervals(store, config, plan.symbol, frame)
    oldest = int(frame["open_time"].min())
    newest = int(frame["open_time"].max())
    state.mark_update(plan.symbol, plan.interval, oldest, newest, written)
    summary.rows_written += written

    if plan.reason == "backfill":
        state.set_backfill_cursor(plan.symbol, plan.interval, newest + 1)

    print(
        f"{plan.reason}: {plan.symbol} {plan.interval} "
        f"rows={len(rows)} start_ms={plan.start_ms}"
    )
    return len(rows)


def _write_derived_intervals(
    store: ParquetStore,
    config: CollectorConfig,
    symbol: str,
    base_frame: pd.DataFrame,
) -> int:
    if base_frame.empty:
        return 0

    touched_years = set(pd.to_datetime(base_frame["open_time"], unit="ms", utc=True).dt.year)
    read_years = {year + offset for year in touched_years for offset in (-1, 0, 1)}
    source = store.read_interval_years(symbol, config.base_interval, read_years)
    if source.empty:
        return 0

    total = 0
    for interval in config.derived_intervals:
        total += store.write(aggregate_ohlcv(source, interval))
    return total
