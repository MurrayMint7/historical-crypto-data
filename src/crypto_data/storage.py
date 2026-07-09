from __future__ import annotations

from pathlib import Path

import pandas as pd


COLUMNS = [
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


def klines_to_frame(rows: list[list[object]], symbol: str, interval: str) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=["symbol", "interval", *COLUMNS])

    frame = pd.DataFrame(rows)
    frame = frame.iloc[:, :11]
    frame.columns = COLUMNS
    frame.insert(0, "interval", interval)
    frame.insert(0, "symbol", symbol)

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_asset_volume",
        "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume",
    ]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    int_columns = ["open_time", "close_time", "number_of_trades"]
    for column in int_columns:
        frame[column] = pd.to_numeric(frame[column], errors="raise").astype("int64")

    return frame


class ParquetStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def find_first_gap_start(
        self,
        symbol: str,
        interval: str,
        expected_delta_ms: int,
        lower_bound_ms: int,
        upper_bound_ms: int,
    ) -> int:
        interval_dir = self.root / symbol / interval
        if not interval_dir.exists():
            return lower_bound_ms

        frames = [
            pd.read_parquet(path, columns=["open_time"])
            for path in sorted(interval_dir.glob("*.parquet"))
        ]
        if not frames:
            return lower_bound_ms

        open_times = pd.concat(frames, ignore_index=True)["open_time"]
        open_times = open_times[
            (open_times >= lower_bound_ms) & (open_times <= upper_bound_ms)
        ].drop_duplicates()
        if open_times.empty:
            return lower_bound_ms

        ordered = open_times.sort_values().reset_index(drop=True)
        first = int(ordered.iloc[0])
        if first > lower_bound_ms:
            return lower_bound_ms

        gaps = ordered.diff().fillna(expected_delta_ms)
        gap_indexes = gaps[gaps > expected_delta_ms].index
        if len(gap_indexes) > 0:
            previous = int(ordered.iloc[int(gap_indexes[0]) - 1])
            return previous + expected_delta_ms

        return int(ordered.iloc[-1]) + expected_delta_ms

    def write(self, frame: pd.DataFrame) -> int:
        if frame.empty:
            return 0

        rows_written = 0
        frame = frame.copy()
        frame["year"] = pd.to_datetime(frame["open_time"], unit="ms", utc=True).dt.year

        for (symbol, interval, year), group in frame.groupby(["symbol", "interval", "year"]):
            path = self.root / str(symbol) / str(interval) / f"{int(year)}.parquet"
            path.parent.mkdir(parents=True, exist_ok=True)

            output = group.drop(columns=["year"])
            if path.exists():
                existing = pd.read_parquet(path)
                output = pd.concat([existing, output], ignore_index=True)

            output = output.drop_duplicates(subset=["open_time"], keep="last")
            output = output.sort_values("open_time").reset_index(drop=True)
            output.to_parquet(path, index=False)
            rows_written += len(group)

        return rows_written
