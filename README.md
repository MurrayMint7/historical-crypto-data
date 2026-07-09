# Historical Crypto Data

Daily-updated Binance spot kline archive stored directly in GitHub as Parquet.

The repository keeps the daily workflow lightweight. Each run:

- uses a fixed Binance USDT spot-market list
- fetches only native `1m` candles from Binance
- repairs a recent lookback window for every selected symbol
- spends the remaining request budget backfilling older missing history
- derives higher intervals locally from stored `1m` candles
- writes partitioned Parquet files under `data/<symbol>/<interval>/<year>.parquet`
- updates `metadata/state.json`
- commits only when data or metadata changed

## Scope

Tracked symbols are fixed to this `USDT` spot-market list:

- `BTCUSDT`
- `ETHUSDT`
- `XLMUSDT`
- `SOLUSDT`
- `ADAUSDT`
- `DOGEUSDT`
- `XRPUSDT`
- `BNBUSDT`
- `TRXUSDT`

Only `1m` candles are collected from Binance. The repo then derives these intervals from local `1m` data:

- `5m`
- `10m`
- `30m`
- `1h`
- `1d`
- `1w`
- `1mo`
- `1yr`

The backfill starts from the earliest history available from Binance for each selected market. That is API availability, not necessarily the true market inception date of each coin.

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

Edit [config/assets.toml](config/assets.toml) to change the fixed symbols, derived intervals, request budgets, or repair behavior.

Key settings:

- `max_requests_per_run`: total Binance kline requests for one cron run
- `repair_lookback_days`: recent history repaired every run
- `backfill_calls_per_pair`: cap for older backfill calls per symbol/interval per run

## GitHub Action

[.github/workflows/update-data.yml](.github/workflows/update-data.yml) runs daily and can also be triggered manually. It installs the package, runs the updater, then commits `data/` and `metadata/` changes back to the repository.
