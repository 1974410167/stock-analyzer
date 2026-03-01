from __future__ import annotations

from typing import Any


def generate_advice(analysis: dict[str, Any]) -> str:
    total = analysis.get("total_symbols", 0)
    rising = analysis.get("rising_symbols", 0)
    falling = analysis.get("falling_symbols", 0)

    if total == 0:
        return "没有足够的交易数据，暂时无法提供建议。"

    if rising > falling:
        return "整体趋势偏强，可以重点关注表现持续上涨的标的，但仍需结合仓位和风险控制。"

    if falling > rising:
        return "整体趋势偏弱，建议优先控制风险，谨慎加仓，并复核下跌标的的基本面。"

    return "市场表现分化不明显，建议保持观察，结合更多时间维度和基本面信息再做决策。"
