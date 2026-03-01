from __future__ import annotations

from typing import Any


def generate_advice(analysis: dict[str, Any]) -> dict[str, Any]:
    """
    根据分析结果生成投资建议

    包括整体建议和每只股票的具体建议
    """
    total = analysis.get("total_positions", 0)
    rising = analysis.get("rising_positions", 0)
    falling = analysis.get("falling_positions", 0)
    flat = analysis.get("flat_positions", 0)
    total_pnl = analysis.get("total_pnl", 0)
    total_pnl_pct = analysis.get("total_pnl_pct", 0)
    symbol_analysis = analysis.get("symbol_analysis", [])

    if total == 0:
        return {
            "overall": "没有足够的持仓数据，暂时无法提供建议。",
            "per_symbol": []
        }

    # 整体建议
    if total_pnl_pct > 5:
        overall_advice = f"✅ 整体表现优秀！总盈亏为 {total_pnl_pct:.2f}% (${total_pnl:,.2f})。可以考虑适当止盈锁定收益。"
    elif total_pnl_pct > 0:
        overall_advice = f"📈 整体表现良好，总盈亏为 {total_pnl_pct:.2f}% (${total_pnl:,.2f})。继续保持观察。"
    elif total_pnl_pct > -5:
        overall_advice = f"📉 整体表现一般，总亏损为 {total_pnl_pct:.2f}% (${total_pnl:,.2f})。建议关注下跌标的的基本面。"
    else:
        overall_advice = f"⚠️ 整体表现较弱，总亏损为 {total_pnl_pct:.2f}% (${total_pnl:,.2f})。建议控制风险，考虑止损。"

    # 趋势分析
    if rising > falling:
        trend_advice = f"上涨标的较多 ({rising}个) vs 下跌 ({falling}个)，市场情绪偏强。"
    elif falling > rising:
        trend_advice = f"下跌标的较多 ({falling}个) vs 上涨 ({rising}个)，市场情绪偏弱。"
    else:
        trend_advice = "涨跌持平，市场分化明显。"

    # 每只股票的建议
    per_symbol_advice = []

    for pos in symbol_analysis:
        symbol = pos.get("symbol")
        pnl = pos.get("pnl")
        pnl_pct = pos.get("pnl_pct")
        trend = pos.get("trend")
        description = pos.get("description", "")

        if trend == "up" and pnl_pct > 10:
            advice = f"✅ 强劲上涨 (盈亏 {pnl_pct:.2f}%)。考虑分批止盈，锁定收益。"
        elif trend == "up" and pnl_pct > 0:
            advice = f"📈 上涨 (盈亏 {pnl_pct:.2f}%)。继续持有，观察走势。"
        elif trend == "down" and pnl_pct < -10:
            advice = f"⚠️ 深度下跌 (盈亏 {pnl_pct:.2f}%)。建议止损或加仓前深入研究。"
        elif trend == "down" and pnl_pct < -5:
            advice = f"📉 下跌 (盈亏 {pnl_pct:.2f}%)。关注基本面，谨慎操作。"
        elif trend == "down":
            advice = f"📉 轻微下跌 (盈亏 {pnl_pct:.2f}%)。短期波动，持续观察。"
        else:
            advice = f"➡️ 持平 (盈亏 {pnl_pct:.2f}%)。暂时无动作。"

        per_symbol_advice.append({
            "symbol": symbol,
            "description": description,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "trend": trend,
            "advice": advice
        })

    # 找出表现最好和最差的3只股票
    sorted_by_pnl = sorted(symbol_analysis, key=lambda x: x.get('pnl', 0), reverse=True)
    top_performers = sorted_by_pnl[:3]
    worst_performers = sorted_by_pnl[-3:]

    return {
        "overall": overall_advice,
        "trend": trend_advice,
        "top_performers": [
            {
                "symbol": p["symbol"],
                "pnl": p["pnl"],
                "pnl_pct": p["pnl_pct"],
                "description": p["description"]
            }
            for p in top_performers
        ],
        "worst_performers": [
            {
                "symbol": p["symbol"],
                "pnl": p["pnl"],
                "pnl_pct": p["pnl_pct"],
                "description": p["description"]
            }
            for p in worst_performers
        ],
        "per_symbol": per_symbol_advice
    }
