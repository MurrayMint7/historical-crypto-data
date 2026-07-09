from pathlib import Path

from crypto_data.config import load_config


def test_load_default_config() -> None:
    config = load_config(Path("config/assets.toml"))

    assert "BTCUSDT" in config.symbols
    assert "5m" in config.intervals
    assert "10m" not in config.intervals
    assert "1yr" not in config.intervals

