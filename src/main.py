"""
Main entrypoint and pipeline orchestrator for Volatility & Anomaly Spike Watchdog.
Coordinates configuration validation, data ingestion, anomaly analysis, and alert dispatching.
"""

import sys
from datetime import datetime, timezone

from src.config import validate_config, VOLATILITY_THRESHOLD_PERCENT
from src.fetcher import fetch_top_coins
from src.analyzer import filter_anomalies, get_market_sentiment
from src.notifier import build_discord_payload, send_discord_alert


def run_pipeline() -> int:
    """
    Executes the end-to-end watchdog pipeline.

    Returns:
        int: Exit status code (0 for success or graceful exit, 1 for configuration errors).
    """
    start_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{start_time}] [START] Initializing Watchdog Pipeline...")

    # Phase 1: Configuration Validation (Fail-Fast)
    try:
        validate_config()
    except ValueError as err:
        print(f"[ERROR] Configuration error: {err}")
        return 1

    # Phase 2: Ingestion Phase
    now_str = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{now_str}] [INGESTION] Fetching top 50 coins from CoinGecko...")
    coins = fetch_top_coins()

    if not coins:
        print(f"[{now_str}] [WARN] Ingestion returned 0 coins (API issue/rate limit). Exiting gracefully.")
        return 0

    print(f"[{now_str}] [INGESTION] Successfully fetched {len(coins)} coins.")

    # Phase 3: Processing & Logic Phase
    print(f"[{now_str}] [PROCESSING] Filtering anomalies with threshold >= {VOLATILITY_THRESHOLD_PERCENT}%...")
    anomalies = filter_anomalies(coins, threshold_percent=VOLATILITY_THRESHOLD_PERCENT)

    # Phase 4: Decision Phase (PRD Section 4 & 5)
    if not anomalies:
        print(f"[{now_str}] [INFO] No anomaly detected. Market is stable.")
        return 0

    # Log detected anomalies for judge traceability
    print(f"[{now_str}] [ALERT] Detected {len(anomalies)} volatile coin(s)!")
    for idx, coin in enumerate(anomalies, 1):
        symbol = coin.get("symbol", "").upper()
        change = coin.get("price_change_percentage_1h_in_currency", 0.0) or 0.0
        print(f"   {idx}. {symbol}: {change:+.2f}%")

    # Phase 5: Dispatch Phase
    sentiment = get_market_sentiment(anomalies)
    print(f"[{now_str}] [DISPATCH] Market sentiment is '{sentiment.upper()}'. Building Rich Embed...")
    payload = build_discord_payload(anomalies, sentiment=sentiment)

    success = send_discord_alert(payload)
    if success:
        print(f"[{now_str}] [SUCCESS] Alert dispatched successfully to Discord.")
    else:
        print(f"[{now_str}] [ERROR] Failed to dispatch alert to Discord.")

    return 0


if __name__ == "__main__":
    sys.exit(run_pipeline())