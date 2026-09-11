"""
Unit tests for notifier module.
Validates payload construction, embed colors, field count limits, and price formatting.
"""

from src.notifier import build_discord_payload, format_currency


def test_format_currency() -> None:
    assert format_currency(65432.10) == "$65,432.10"
    assert format_currency(0.00543) == "$0.00543"
    assert format_currency(None) == "N/A"


def test_build_discord_payload_color_and_fields() -> None:
    dummy_anomalies = [
        {"symbol": "btc", "name": "Bitcoin", "current_price": 70000.0, "price_change_percentage_1h_in_currency": 6.5},
        {"symbol": "eth", "name": "Ethereum", "current_price": 3500.0, "price_change_percentage_1h_in_currency": 5.2},
    ]

    # Uji warna Hijau saat sentiment "pump"
    payload_pump = build_discord_payload(dummy_anomalies, sentiment="pump")
    embed_pump = payload_pump["embeds"][0]
    assert embed_pump["color"] == 0x00FF00  # Green
    assert len(embed_pump["fields"]) == 2
    assert "BTC - Bitcoin" in embed_pump["fields"][0]["name"]
    assert "+6.50%" in embed_pump["fields"][0]["value"]

    # Uji warna Merah saat sentiment "drop"
    payload_drop = build_discord_payload(dummy_anomalies, sentiment="drop")
    embed_drop = payload_drop["embeds"][0]
    assert embed_drop["color"] == 0xFF0000  # Red


def test_build_discord_payload_caps_at_max_display() -> None:
    # Buat 10 koin dummy
    ten_anomalies = [
        {"symbol": f"c{i}", "name": f"Coin {i}", "current_price": 10.0, "price_change_percentage_1h_in_currency": 5.5}
        for i in range(10)
    ]

    # Batasi maksimal 5 sesuai PRD
    payload = build_discord_payload(ten_anomalies, max_display=5)
    fields = payload["embeds"][0]["fields"]
    assert len(fields) == 5