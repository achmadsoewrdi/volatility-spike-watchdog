"""
Unit tests for analyzer module.
Validates anomaly detection thresholds, null handling, sorting, and sentiment.
"""

from src.analyzer import filter_anomalies, get_market_sentiment


def test_filter_anomalies_detects_spikes() -> None:
    dummy_coins = [
        {"id": "bitcoin", "symbol": "btc", "price_change_percentage_1h_in_currency": 1.2},    # Normal (<5%)
        {"id": "ethereum", "symbol": "eth", "price_change_percentage_1h_in_currency": 5.0},   # Boundary Anomaly (+5%)
        {"id": "solana", "symbol": "sol", "price_change_percentage_1h_in_currency": -6.5},   # Anomaly Drop (-6.5%)
        {"id": "dogecoin", "symbol": "doge", "price_change_percentage_1h_in_currency": 12.0}, # Big Anomaly (+12%)
    ]

    result = filter_anomalies(dummy_coins, threshold_percent=5.0)

    # Hanya 3 koin yang memenuhi syarat >= 5.0%
    assert len(result) == 3
    # Harus terurut dari yang perubahannya paling ekstrem (doge: 12%, sol: -6.5%, eth: 5.0%)
    assert result[0]["symbol"] == "doge"
    assert result[1]["symbol"] == "sol"
    assert result[2]["symbol"] == "eth"


def test_filter_anomalies_handles_null_safely() -> None:
    dummy_coins_with_null = [
        {"id": "broken_coin_1", "symbol": "bk1", "price_change_percentage_1h_in_currency": None},
        {"id": "broken_coin_2", "symbol": "bk2"},  # Key tidak ada
        {"id": "broken_coin_3", "symbol": "bk3", "price_change_percentage_1h_in_currency": "invalid_string"},
        {"id": "real_pump", "symbol": "pump", "price_change_percentage_1h_in_currency": 7.5},
    ]

    # Tidak boleh crash TypeError, dan harus mengekstrak hanya koin valid
    result = filter_anomalies(dummy_coins_with_null, threshold_percent=5.0)
    assert len(result) == 1
    assert result[0]["symbol"] == "pump"


def test_get_market_sentiment() -> None:
    pump_anomalies = [
        {"price_change_percentage_1h_in_currency": 8.0},
        {"price_change_percentage_1h_in_currency": 6.0},
        {"price_change_percentage_1h_in_currency": -7.0},
    ]
    # 2 positif vs 1 negatif -> pump
    assert get_market_sentiment(pump_anomalies) == "pump"

    drop_anomalies = [
        {"price_change_percentage_1h_in_currency": -8.0},
        {"price_change_percentage_1h_in_currency": 6.0},
        {"price_change_percentage_1h_in_currency": -7.0},
    ]
    # 1 positif vs 2 negatif -> drop
    assert get_market_sentiment(drop_anomalies) == "drop"