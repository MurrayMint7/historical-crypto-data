from crypto_data.binance import BinanceClient


class FakeSession:
    def get(self, url, timeout):
        if url.endswith("/exchangeInfo"):
            return FakeResponse({
                "symbols": [
                    {"symbol": "BTCUSDT", "baseAsset": "BTC", "quoteAsset": "USDT", "status": "TRADING"},
                    {"symbol": "ETHUSDT", "baseAsset": "ETH", "quoteAsset": "USDT", "status": "TRADING"},
                    {"symbol": "USDCUSDT", "baseAsset": "USDC", "quoteAsset": "USDT", "status": "TRADING"},
                    {"symbol": "USD1USDT", "baseAsset": "USD1", "quoteAsset": "USDT", "status": "TRADING"},
                    {"symbol": "DEADUSDT", "baseAsset": "DEAD", "quoteAsset": "USDT", "status": "BREAK"},
                ]
            })
        return FakeResponse([
            {"symbol": "ETHUSDT", "quoteVolume": "50"},
            {"symbol": "BTCUSDT", "quoteVolume": "100"},
            {"symbol": "USDCUSDT", "quoteVolume": "1000"},
            {"symbol": "USD1USDT", "quoteVolume": "900"},
            {"symbol": "DEADUSDT", "quoteVolume": "10000"},
        ])


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_top_symbols_by_quote_volume_filters_and_ranks() -> None:
    client = BinanceClient("https://example.test")
    client.session = FakeSession()

    symbols = client.top_symbols_by_quote_volume("USDT", 2, frozenset({"USDC", "USD1"}))

    assert symbols == ["BTCUSDT", "ETHUSDT"]
