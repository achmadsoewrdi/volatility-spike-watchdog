"""
Market Volatility Analyzer module.
Detects anomalies based on 1-hour price fluctuation thresholds.
"""

from typing import Any
from src.config import VOLATILITY_THRESHOLD_PERCENT

def filter_anomalies(coins: list[dict[str, Any]], threshold_percent: float = VOLATILITY_THRESHOLD_PERCENT,) -> list[dict[str, Any]]:
    """
    Filters coins that experience price fluctuations >= threshold_percent in the last hour.
    Safely ignores coins with null or invalid price change values.
    Args:
        coins: List of coin market data dictionaries from CoinGecko.
        threshold_percent: Minimum absolute percentage change to qualify as anomaly.
    Returns:
        List of anomalous coins sorted by absolute volatility (highest first).
    """

    anomalies: list[dict[str, Any]] = []

    for coin in coins:
        change = coin.get("price_change_percentage_1h_in_currency")

        # defensive check: ignore null, missing, or non-numeric values
        if change is None or not isinstance(change, (int, float)):
            continue

        if abs(change) >= threshold_percent:
            anomalies.append(coin)

    # sort descending based on magnitude of vloatility
    anomalies.sort(key=lambda item: abs(item["price_change_percentage_1h_in_currency"]), reverse=True)


    return anomalies

def get_market_sentiment(anomalies: list[dict[str,Any]]) -> str:
    """
    Determines overall anomaly sentiment based on PRD Section 6:
    - 'pump' (Green) if majority of anomalies are positive.
    - 'drop' (Red) if majority of anomalies are negative or equal.
    Args:
        anomalies: List of anomalous coins.
    Returns:
        'pump' or 'drop'
    """
    if not anomalies:
        return "drop"

    positive_count = sum(1 for c in anomalies if (c.get("price_change_percentage_1h_in_currency") or 0) > 0)

    negative_count = len(anomalies) - positive_count

    return "pump" if positive_count > negative_count else "drop"
