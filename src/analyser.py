from __future__ import annotations

from collections import defaultdict
from typing import Any


def analyse_price_movements(trades: list[dict[str, Any]]) -> dict[str, Any]:
    grouped_prices: dict[str, list[float]] = defaultdict(list)

    for trade in trades:
        symbol = trade.get("symbol")
        price = trade.get("trade_price")
        if symbol and isinstance(price, (int, float)):
            grouped_prices[symbol].append(float(price))

    per_symbol: list[dict[str, Any]] = []
    rising_count = 0
    falling_count = 0

    for symbol, prices in sorted(grouped_prices.items()):
        if len(prices) < 2:
            trend = "insufficient_data"
            change = 0.0
        else:
            change = prices[-1] - prices[0]
            trend = "up" if change > 0 else "down" if change < 0 else "flat"

        if trend == "up":
            rising_count += 1
        elif trend == "down":
            falling_count += 1

        per_symbol.append(
            {
                "symbol": symbol,
                "first_price": prices[0],
                "last_price": prices[-1],
                "change": round(change, 2),
                "trend": trend,
                "trade_count": len(prices),
            }
        )

    return {
        "total_symbols": len(per_symbol),
        "rising_symbols": rising_count,
        "falling_symbols": falling_count,
        "symbol_analysis": per_symbol,
    }
