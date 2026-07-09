from crypto_data.storage import klines_to_frame
from crypto_data.storage import ParquetStore


def test_klines_to_frame_keeps_expected_columns() -> None:
    rows = [[
        1502942400000,
        "4261.48000000",
        "4261.48000000",
        "4261.48000000",
        "4261.48000000",
        "1.00000000",
        1502942459999,
        "4261.48000000",
        1,
        "1.00000000",
        "4261.48000000",
        "0",
    ]]

    frame = klines_to_frame(rows, "BTCUSDT", "1m")

    assert list(frame["symbol"]) == ["BTCUSDT"]
    assert list(frame["interval"]) == ["1m"]
    assert frame["open"].iloc[0] == 4261.48
    assert frame["open_time"].iloc[0] == 1502942400000


def test_find_first_gap_start_detects_missing_candle(tmp_path) -> None:
    rows = [
        [0, "1", "1", "1", "1", "1", 59999, "1", 1, "1", "1", "0"],
        [60000, "1", "1", "1", "1", "1", 119999, "1", 1, "1", "1", "0"],
        [180000, "1", "1", "1", "1", "1", 239999, "1", 1, "1", "1", "0"],
    ]
    frame = klines_to_frame(rows, "BTCUSDT", "1m")
    store = ParquetStore(tmp_path)
    store.write(frame)

    assert store.find_first_gap_start("BTCUSDT", "1m", 60000, 0, 240000) == 120000
