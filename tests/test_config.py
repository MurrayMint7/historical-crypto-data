from pathlib import Path

from crypto_data.config import load_config


def test_load_default_config() -> None:
    config = load_config(Path("config/assets.toml"))

    assert config.top_n_symbols == 10
    assert config.base_interval == "1m"
    assert "5m" in config.derived_intervals
    assert "10m" in config.derived_intervals
    assert "1mo" in config.derived_intervals
    assert "1yr" in config.derived_intervals
