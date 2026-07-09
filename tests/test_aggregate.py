from crypto_data.aggregate import aggregate_ohlcv
from crypto_data.storage import klines_to_frame


def test_aggregate_ohlcv_builds_10m_candle() -> None:
    rows = []
    for index in range(10):
        open_time = 1_699_999_800_000 + (index * 60_000)
        rows.append([
            open_time,
            str(index + 1),
            str(index + 2),
            str(index),
            str(index + 1.5),
            "1",
            open_time + 59_999,
            "10",
            2,
            "0.5",
            "5",
            "0",
        ])

    source = klines_to_frame(rows, "BTCUSDT", "1m")
    output = aggregate_ohlcv(source, "10m")

    assert len(output) == 1
    row = output.iloc[0]
    assert row["interval"] == "10m"
    assert row["open_time"] == 1_699_999_800_000
    assert row["open"] == 1
    assert row["high"] == 11
    assert row["low"] == 0
    assert row["close"] == 10.5
    assert row["volume"] == 10
    assert row["number_of_trades"] == 20
