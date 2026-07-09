# Historical Crypto Data

Daily-updated Binance spot kline archive stored directly in GitHub as Parquet.

The repository keeps the daily workflow lightweight. Each run:

- repairs a recent lookback window for every configured symbol and interval
- spends the remaining request budget backfilling older missing history
- writes partitioned Parquet files under `data/<symbol>/<interval>/<year>.parquet`
- updates `metadata/state.json`
- commits only when data or metadata changed

## Scope

Tracked symbols:

- `BTCUSDT`
- `ETHUSDT`
- `BNBUSDT`
- `ADAUSDT`
- `XRPUSDT`

Tracked intervals:

- `1m`
- `5m`
- `30m`
- `1h`
- `1d`
- `1w`

Only native Binance spot kline intervals are collected. Requested intervals that Binance does not expose directly, such as `10m` and `1yr`, are intentionally excluded for now.

The default start dates are the earliest useful Binance spot-history dates for these pairs. That is the earliest available history from this API, not necessarily the true market inception date of each coin.

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run a small update:

```bash
crypto-data update --max-requests 40
```

Run tests:

```bash
pytest
```

## Configuration

Edit [config/assets.toml](config/assets.toml) to change symbols, intervals, start dates, request budgets, or repair behavior.

Key settings:

- `max_requests_per_run`: total Binance kline requests for one cron run
- `repair_lookback_days`: recent history repaired every run
- `backfill_calls_per_pair`: cap for older backfill calls per symbol/interval per run

## GitHub Action

[.github/workflows/update-data.yml](.github/workflows/update-data.yml) runs daily and can also be triggered manually. It installs the package, runs the updater, then commits `data/` and `metadata/` changes back to the repository.

