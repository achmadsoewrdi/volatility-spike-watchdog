"""
Configuration module for Volatility & Anomaly Spike Watchdog.
Centralizes environment variables, API endpoints, and business constants.
"""

import os
from dotenv import load_dotenv

# 1. Load environment variables from .env file
load_dotenv()

# 2. Environment Variables & Credentials
DISCORD_WEBHOOK_URL: str | None = os.environ.get("DISCORD_WEBHOOK_URL")

# 3. CoinGecko API Constants (as specified in PRD Section 5)
COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3/coins/markets"
COINGECKO_PARAMS: dict[str, str | int] = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 50,
    "price_change_percentage": "1h",
}

# 4. Business Logic Thresholds (as specified in PRD Section 1 & 6)
VOLATILITY_THRESHOLD_PERCENT: float = 5.0
MAX_ANOMALY_DISPLAY: int = 5
REQUEST_TIMEOUT_SECONDS: int = 15


def validate_config() -> None:
    """
    Fail-fast validator to ensure critical configurations exist before pipeline starts.
    """
    if not DISCORD_WEBHOOK_URL:
        raise ValueError(
            "[ERROR] DISCORD_WEBHOOK_URL is not set. "
            "Please provide it in .env (locally) or in GitHub Secrets (CI/CD)."
        )