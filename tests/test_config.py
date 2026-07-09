from pathlib import Path

from crypto_data.config import load_config


def test_load_default_config() -> None:
    config = load_config(Path("config/assets.toml"))

    assert len(config.symbols) == 9
    assert len(set(config.symbols)) == len(config.symbols)
    assert config.symbols[:2] == ("BTCUSDT", "ETHUSDT")
    assert "ADAUSDT" in config.symbols
    assert "DOGEUSDT" in config.symbols
    assert "SENTUSDT" not in config.symbols
    assert "ZECUSDT" not in config.symbols
    assert "SPCXBUSDT" not in config.symbols
    assert config.base_interval == "1m"
    assert "5m" in config.derived_intervals
    assert "10m" in config.derived_intervals
    assert "1mo" in config.derived_intervals
    assert "1yr" in config.derived_intervals
