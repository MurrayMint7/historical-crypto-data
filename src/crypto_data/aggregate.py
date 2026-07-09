from __future__ import annotations

import pandas as pd


RESAMPLE_RULES = {
    "5m": "5min",
    "10m": "10min",
    "30m": "30min",
    "1h": "1h",
    "1d": "1D",
    "1w": "W-MON",
    "1mo": "MS",
    "1yr": "YS",
}


def aggregate_ohlcv(frame: pd.DataFrame, interval: str) -> pd.DataFrame:
    if frame.empty:
        return frame

    rule = RESAMPLE_RULES[interval]
    source = frame.copy()
    source["timestamp"] = pd.to_datetime(source["open_time"], unit="ms", utc=True)
    source = source.sort_values("timestamp").set_index("timestamp")

    resample_kwargs = {"label": "left", "closed": "left"}
    if rule not in {"1D", "W-MON", "MS", "YS"}:
        resample_kwargs["origin"] = "epoch"
    grouped = source.resample(rule, **resample_kwargs)
    output = grouped.agg(
        {
            "symbol": "first",
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
            "close_time": "max",
            "quote_asset_volume": "sum",
            "number_of_trades": "sum",
            "taker_buy_base_asset_volume": "sum",
            "taker_buy_quote_asset_volume": "sum",
        }
    )
    output = output.dropna(subset=["open", "high", "low", "close"]).reset_index()
    output["open_time"] = output["timestamp"].map(lambda value: int(value.timestamp() * 1000))
    output["interval"] = interval
    output = output[
        [
            "symbol",
            "interval",
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
        ]
    ]
    output["number_of_trades"] = output["number_of_trades"].astype("int64")
    output["close_time"] = output["close_time"].astype("int64")
    return output
