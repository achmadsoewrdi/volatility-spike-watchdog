"""
Notification module for Discord Webhook integration.
Constructs structured Rich Embeds and dispatches alerts.
"""

from datetime import datetime, timezone
from typing import Any
import requests

from src.config import (
    DISCORD_WEBHOOK_URL,
    MAX_ANOMALY_DISPLAY,
    REQUEST_TIMEOUT_SECONDS,
)


def format_currency(price: float | int | None) -> str:
    """Formats price into human-readable USD string."""
    if price is None:
        return "N/A"
    if price >= 1.0:
        return f"${price:,.2f}"
    return f"${price:.6f}".rstrip("0").rstrip(".")


def build_discord_payload(
    anomalies: list[dict[str, Any]],
    sentiment: str = "drop",
    max_display: int = MAX_ANOMALY_DISPLAY,
) -> dict[str, Any]:
    """
    Builds a Discord Rich Embed payload dictionary according to PRD Section 6.

    Args:
        anomalies: Filtered list of anomalous coins.
        sentiment: 'pump' (Green) or 'drop' (Red).
        max_display: Limit for fields to prevent chat clutter.

    Returns:
        Dictionary formatted for Discord Webhook execution.
    """
    # Hex Color Mapping: Green (#00FF00) for pump, Red (#FF0000) for drop
    embed_color = 0x00FF00 if sentiment == "pump" else 0xFF0000

    fields = []
    # Take top N most volatile coins
    for coin in anomalies[:max_display]:
        name_text = f"{coin.get('symbol', 'UNKNOWN').upper()} - {coin.get('name', 'Unknown')}"
        price_text = format_currency(coin.get("current_price"))
        
        change = coin.get("price_change_percentage_1h_in_currency", 0.0) or 0.0
        change_sign = "+" if change > 0 else ""
        change_text = f"{change_sign}{change:.2f}%"

        fields.append({
            "name": name_text,
            "value": f"Current Price: **{price_text}** | 1h Change: **{change_text}**",
            "inline": False,
        })

    current_utc = datetime.now(timezone.utc)
    utc_str = current_utc.strftime("%Y-%m-%d %H:%M:%S UTC")

    embed = {
        "title": "⚠️ Market Volatility Alert!",
        "description": f"Detected **{len(anomalies)}** coin(s) with 1h price movement exceeding threshold.",
        "color": embed_color,
        "fields": fields,
        "footer": {
            "text": f"Automated run by GitHub Actions | Timestamp: {utc_str}",
        },
        "timestamp": current_utc.isoformat(),
    }

    return {"embeds": [embed]}


def send_discord_alert(
    payload: dict[str, Any],
    webhook_url: str | None = None,
) -> bool:
    """
    Dispatches formatted embed payload to Discord Webhook URL.

    Returns:
        bool: True if alert successfully posted (HTTP 200/204), False otherwise.
    """
    target_url = webhook_url or DISCORD_WEBHOOK_URL

    if not target_url:
        print("[ERROR] Discord Webhook URL is missing. Alert aborted.")
        return False

    try:
        response = requests.post(
            target_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        if response.status_code in (200, 204):
            print("[INFO] Successfully dispatched Discord volatility alert.")
            return True

        print(f"[ERROR] Discord Webhook returned HTTP {response.status_code}: {response.text}")
        return False

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to connect to Discord Webhook: {e}")
        return False