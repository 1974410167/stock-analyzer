from __future__ import annotations

from typing import Any
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class NewsItem:
    """新闻条目"""
    title: str
    summary: str
    source: str
    published_at: str
    sentiment: str  # positive, negative, neutral
    relevance_score: float


def analyze_price_change_reasons(position: dict[str, Any]) -> dict[str, Any]:
    """
    分析单只股票的涨跌原因

    这里使用基于规则的模拟分析
    实际应用中应该调用新闻 API
    """
    symbol = position.get('symbol', '')
    pnl_pct = position.get('pnl_pct', 0)
    description = position.get('description', '')
    trend = position.get('trend', '')

    reasons = []

    # 基于盈亏幅度的原因分析
    if pnl_pct > 20:
        reasons.append({
            'type': 'strong_performance',
            'description': f"{symbol} 表现强劲，涨幅超过 {pnl_pct:.1f}%",
            'possible_causes': [
                "行业整体上涨",
                "公司财报超预期",
                "重要利好消息发布",
                "分析师上调评级"
            ],
            'sentiment': 'positive'
        })
    elif pnl_pct > 10:
        reasons.append({
            'type': 'good_performance',
            'description': f"{symbol} 表现良好，涨幅为 {pnl_pct:.1f}%",
            'possible_causes': [
                "市场情绪回暖",
                "行业利好消息",
                "技术面突破"
            ],
            'sentiment': 'positive'
        })
    elif pnl_pct < -20:
        reasons.append({
            'type': 'poor_performance',
            'description': f"{symbol} 表现疲软，跌幅超过 {abs(pnl_pct):.1f}%",
            'possible_causes': [
                "行业整体下跌",
                "公司财报不及预期",
                "重要负面消息",
                "监管政策影响"
            ],
            'sentiment': 'negative'
        })
    elif pnl_pct < -10:
        reasons.append({
            'type': 'weak_performance',
            'description': f"{symbol} 表现较弱，跌幅为 {abs(pnl_pct):.1f}%",
            'possible_causes': [
                "短期回调",
                "市场情绪波动",
                "获利回吐压力"
            ],
            'sentiment': 'negative'
        })
    else:
        reasons.append({
            'type': 'normal_performance',
            'description': f"{symbol} 波动在正常范围内",
            'possible_causes': [
                "市场正常波动",
                "缺乏重大消息刺激"
            ],
            'sentiment': 'neutral'
        })

    # 基于股票类型的额外分析
    symbol_lower = symbol.lower()
    description_lower = description.lower()

    # 科技股
    if any(tech in description_lower for tech in ['technology', 'semi', 'micro', 'chip']):
        reasons.append({
            'type': 'sector_analysis',
            'description': f"{symbol} 属于科技/半导体板块",
            'sector_factors': [
                "AI 需求增长",
                "芯片周期性波动",
                "地缘政治影响"
            ],
            'sentiment': 'neutral'
        })

    # 能源股
    if 'energy' in description_lower or 'oil' in description_lower:
        reasons.append({
            'type': 'sector_analysis',
            'description': f"{symbol} 属于能源板块",
            'sector_factors': [
                "原油价格波动",
                "地缘政治风险",
                "新能源转型政策"
            ],
            'sentiment': 'neutral'
        })

    # 新兴市场/ADR
    if 'adr' in description_lower or 'unsp' in description_lower:
        reasons.append({
            'type': 'market_risk',
            'description': f"{symbol} 为 ADR 或新兴市场股票",
            'additional_risks': [
                "汇率波动风险",
                "当地政策变化",
                "跨境投资限制"
            ],
            'sentiment': 'neutral'
        })

    return {
        'symbol': symbol,
        'trend': trend,
        'pnl_pct': pnl_pct,
        'reasons': reasons,
        'analysis_summary': _generate_summary(reasons, trend, pnl_pct)
    }


def _generate_summary(reasons: list[dict[str, Any]], trend: str, pnl_pct: float) -> str:
    """生成分析摘要"""
    main_reason = reasons[0]['description'] if reasons else ""

    if trend == "up":
        if pnl_pct > 30:
            return f"📈 表现卓越！{main_reason} 建议关注是否需要止盈。"
        elif pnl_pct > 10:
            return f"📈 表现良好。{main_reason} 可以继续持有观察。"
        else:
            return f"📈 小幅上涨。{main_reason}"
    elif trend == "down":
        if pnl_pct < -30:
            return f"📉 表现疲软！{main_reason} 建议深入研究基本面，考虑止损。"
        elif pnl_pct < -10:
            return f"📉 表现较弱。{main_reason} 关注风险，谨慎操作。"
        else:
            return f"📉 小幅下跌。{main_reason} 可能是短期波动。"
    else:
        return f"➡️ 价格持平。{main_reason}"


def analyze_all_positions(positions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """分析所有持仓的涨跌原因"""
    analyses = []

    for position in positions:
        analysis = analyze_price_change_reasons(position)
        analyses.append(analysis)

    return analyses


def format_reasons_report(analyses: list[dict[str, Any]]) -> str:
    """格式化涨跌原因报告"""
    lines = []
    lines.append("📰 **涨跌原因分析**")
    lines.append("=" * 40)
    lines.append("")

    for analysis in analyses:
        lines.append(f"### {analysis['symbol']}")
        lines.append(f"趋势: {analysis['trend'].upper()} | 盈亏: {analysis['pnl_pct']:.2f}%")
        lines.append(f"摘要: {analysis['analysis_summary']}")
        lines.append("")

        lines.append("可能原因:")
        for reason in analysis['reasons']:
            lines.append(f"  • {reason['description']}")
            if 'possible_causes' in reason:
                for cause in reason['possible_causes']:
                    lines.append(f"    - {cause}")
        lines.append("")

    return "\n".join(lines)
