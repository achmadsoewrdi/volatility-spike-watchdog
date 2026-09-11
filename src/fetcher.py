"""
Data ingestion module for fetching data from CoinGecko API.
Handles HTTP communication, error handling, and response parsing.
"""

from typing import Any
import requests

from src.config import(
    COINGECKO_API_URL,
    COINGECKO_PARAMS,
    REQUEST_TIMEOUT_SECONDS,
)

def fetch_top_coins() -> list[dict[str, Any]]:
    """
    Fetche the top 50 crcyptocurrencies by market cap from CoinGecko API.

    Returns:
        List[dict[str, Any]]: List of coin market data dictionaries.
        Empty list if an error accours
    """

    headers = {
        "Accept": "application/json",
        "User-Agent": "VotalityWatchdog/1.0",
    }

    try:
        response = requests.get(
            COINGECKO_API_URL,
            params=COINGECKO_PARAMS,
            header=headers,
            timout=REQUEST_TIMEOUT_SECONDS,
        )

        if response.status_code == 429:
            print("[ERROR] CoinGecko API rate limit exceeded (HTTP 429)")
            return []

        if response.status_code >= 500:
            print(f"[ERROR] CoinGecko API Server error (HTTP {response.status_code})")
            return []

        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            print("[ERROR] Unexpected response format from CoinGecko API")
            return []

        return data

    except requests.exceptions.Timeout:
        print(f"[ERROR] CoinGecko API timeout After {REQUEST_TIMEOUT_SECONDS}s")
        return []

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] CoinGecko API Request Failed: {e}")
        return []