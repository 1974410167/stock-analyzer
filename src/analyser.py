from __future__ import annotations

from typing import Any


def analyse_positions(positions: list[dict[str, Any]]) -> dict[str, Any]:
    """
    分析持仓数据

    计算每只股票的涨跌情况、盈亏比例
    """
    per_symbol: list[dict[str, Any]] = []
    rising_count = 0
    falling_count = 0
    flat_count = 0

    total_value = sum(pos.get('position_value', 0) for pos in positions)
    total_pnl = sum(pos.get('pnl', 0) for pos in positions)

    for pos in positions:
        symbol = pos.get('symbol')
        mark_price = pos.get('mark_price')
        open_price = pos.get('open_price')
        pnl = pos.get('pnl')
        position_value = pos.get('position_value')

        if not symbol or mark_price is None or open_price is None:
            continue

        # 计算价格变动
        price_change = mark_price - open_price
        price_change_pct = (price_change / open_price) * 100 if open_price != 0 else 0

        # 计算盈亏比例
        pnl_pct = (pnl / (position_value - pnl)) * 100 if (position_value - pnl) != 0 else 0

        # 判断趋势
        if price_change > 0:
            trend = "up"
            rising_count += 1
        elif price_change < 0:
            trend = "down"
            falling_count += 1
        else:
            trend = "flat"
            flat_count += 1

        per_symbol.append({
            "symbol": symbol,
            "description": pos.get('description', ''),
            "quantity": pos.get('quantity'),
            "open_price": round(open_price, 2),
            "mark_price": round(mark_price, 2),
            "price_change": round(price_change, 2),
            "price_change_pct": round(price_change_pct, 2),
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
            "position_value": round(position_value, 2),
            "percent_of_nav": round(pos.get('percent_of_nav', 0), 2),
            "trend": trend,
        })

    return {
        "total_positions": len(per_symbol),
        "rising_positions": rising_count,
        "falling_positions": falling_count,
        "flat_positions": flat_count,
        "total_value": round(total_value, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round((total_pnl / (total_value - total_pnl)) * 100, 2) if (total_value - total_pnl) != 0 else 0,
        "symbol_analysis": per_symbol,
    }
