from __future__ import annotations

import math
from typing import Any
from dataclasses import dataclass


@dataclass
class RiskMetrics:
    """风险指标"""
    # 组合整体风险
    total_value: float
    total_pnl: float
    total_pnl_pct: float
    
    # 集中度风险
    top_position_pct: float  # 最大持仓占比
    top3_positions_pct: float  # 前三大持仓占比
    herfindahl_index: float  # 赫芬达尔指数
    
    # 波动性指标
    avg_position_pnl_pct: float  # 平均个股盈亏比例
    max_position_pnl_pct: float  # 最大个股盈亏
    min_position_pnl_pct: float  # 最小个股盈亏
    pnl_std: float  # 盈亏标准差
    
    # 风险评级
    concentration_risk: str  # low/medium/high
    volatility_risk: str  # low/medium/high
    overall_risk: str  # low/medium/high


def calculate_risk_metrics(positions: list[dict[str, Any]]) -> dict[str, Any]:
    """
    计算投资组合风险指标
    """
    if not positions:
        return {
            'error': 'No positions to analyze',
            'metrics': None
        }

    total_value = sum(pos.get('position_value', 0) for pos in positions)
    total_pnl = sum(pos.get('pnl', 0) for pos in positions)
    total_pnl_pct = (total_pnl / (total_value - total_pnl)) * 100 if (total_value - total_pnl) != 0 else 0

    # 持仓集中度分析
    position_values = [pos.get('position_value', 0) for pos in positions]
    position_pcts = [(pv / total_value) * 100 for pv in position_values] if total_value > 0 else []
    
    sorted_pcts = sorted(position_pcts, reverse=True)
    top_position_pct = sorted_pcts[0] if sorted_pcts else 0
    top3_positions_pct = sum(sorted_pcts[:3]) if len(sorted_pcts) >= 3 else sum(sorted_pcts)
    
    # 赫芬达尔指数 (HHI) - 衡量集中度
    herfindahl_index = sum(pct ** 2 for pct in position_pcts) / 10000  # 归一化到 0-1

    # 盈亏分布分析
    position_pnls = [pos.get('pnl_pct', 0) for pos in positions]
    avg_position_pnl_pct = sum(position_pnls) / len(position_pnls) if position_pnls else 0
    max_position_pnl_pct = max(position_pnls) if position_pnls else 0
    min_position_pnl_pct = min(position_pnls) if position_pnls else 0
    
    # 标准差
    if len(position_pnls) > 1:
        mean = avg_position_pnl_pct
        variance = sum((x - mean) ** 2 for x in position_pnls) / len(position_pnls)
        pnl_std = math.sqrt(variance)
    else:
        pnl_std = 0

    # 风险评级
    concentration_risk = _assess_concentration_risk(top_position_pct, top3_positions_pct, herfindahl_index)
    volatility_risk = _assess_volatility_risk(pnl_std, max_position_pnl_pct, min_position_pnl_pct)
    overall_risk = _assess_overall_risk(concentration_risk, volatility_risk)

    return {
        'metrics': {
            'total_value': round(total_value, 2),
            'total_pnl': round(total_pnl, 2),
            'total_pnl_pct': round(total_pnl_pct, 2),
            
            'concentration': {
                'top_position_pct': round(top_position_pct, 2),
                'top3_positions_pct': round(top3_positions_pct, 2),
                'herfindahl_index': round(herfindahl_index, 4),
            },
            
            'volatility': {
                'avg_position_pnl_pct': round(avg_position_pnl_pct, 2),
                'max_position_pnl_pct': round(max_position_pnl_pct, 2),
                'min_position_pnl_pct': round(min_position_pnl_pct, 2),
                'pnl_std': round(pnl_std, 2),
            },
            
            'risk_ratings': {
                'concentration_risk': concentration_risk,
                'volatility_risk': volatility_risk,
                'overall_risk': overall_risk,
            }
        },
        'analysis': _generate_risk_analysis(
            total_value, total_pnl, total_pnl_pct,
            top_position_pct, top3_positions_pct,
            pnl_std, concentration_risk, volatility_risk, overall_risk
        )
    }


def _assess_concentration_risk(top_pct: float, top3_pct: float, hhi: float) -> str:
    """评估集中度风险"""
    if top_pct > 30 or top3_pct > 60 or hhi > 0.25:
        return "high"
    elif top_pct > 20 or top3_pct > 50 or hhi > 0.15:
        return "medium"
    else:
        return "low"


def _assess_volatility_risk(pnl_std: float, max_pct: float, min_pct: float) -> str:
    """评估波动性风险"""
    if pnl_std > 30 or max_pct > 50 or min_pct < -30:
        return "high"
    elif pnl_std > 15 or max_pct > 20 or min_pct < -15:
        return "medium"
    else:
        return "low"


def _assess_overall_risk(concentration: str, volatility: str) -> str:
    """评估整体风险"""
    if concentration == "high" or volatility == "high":
        return "high"
    elif concentration == "medium" or volatility == "medium":
        return "medium"
    else:
        return "low"


def _generate_risk_analysis(
    total_value: float,
    total_pnl: float,
    total_pnl_pct: float,
    top_pct: float,
    top3_pct: float,
    pnl_std: float,
    concentration_risk: str,
    volatility_risk: str,
    overall_risk: str
) -> dict[str, Any]:
    """生成风险分析报告"""
    
    # 集中度分析
    if concentration_risk == "high":
        concentration_advice = "⚠️ 持仓集中度过高！建议分散投资，降低单一持仓风险。"
    elif concentration_risk == "medium":
        concentration_advice = "⚡ 持仓集中度适中，但可以进一步优化分散。"
    else:
        concentration_advice = "✅ 持仓分散良好，风险分散合理。"

    # 波动性分析
    if volatility_risk == "high":
        volatility_advice = "⚠️ 组合波动性较大！建议关注高风险持仓，考虑对冲或减仓。"
    elif volatility_risk == "medium":
        volatility_advice = "⚡ 组合波动性中等，属于正常范围。"
    else:
        volatility_advice = "✅ 组合波动性较低，表现稳定。"

    # 整体建议
    if overall_risk == "high":
        overall_advice = "🔴 整体风险较高，建议重新评估投资组合，适当降低风险敞口。"
    elif overall_risk == "medium":
        overall_advice = "🟡 整体风险中等，可以继续持有但需保持关注。"
    else:
        overall_advice = "🟢 整体风险较低，投资组合健康。"

    return {
        'concentration': {
            'rating': concentration_risk,
            'advice': concentration_advice,
            'details': f"最大持仓占比 {top_pct:.1f}%, 前三大持仓占比 {top3_pct:.1f}%"
        },
        'volatility': {
            'rating': volatility_risk,
            'advice': volatility_advice,
            'details': f"盈亏标准差 {pnl_std:.1f}%"
        },
        'overall': {
            'rating': overall_risk,
            'advice': overall_advice,
            'summary': f"总市值 ${total_value:,.2f}, 总盈亏 ${total_pnl:,.2f} ({total_pnl_pct:.2f}%)"
        }
    }


def format_risk_report(metrics_data: dict[str, Any]) -> str:
    """格式化风险报告"""
    if not metrics_data.get('metrics'):
        return "❌ 无法计算风险指标"

    m = metrics_data['metrics']
    a = metrics_data['analysis']

    lines = []
    lines.append("⚠️ **投资组合风险分析**")
    lines.append("=" * 40)
    lines.append("")
    
    lines.append("📊 **整体情况**")
    lines.append(f"• 总市值: ${m['total_value']:,.2f}")
    lines.append(f"• 总盈亏: ${m['total_pnl']:,.2f} ({m['total_pnl_pct']:.2f}%)")
    lines.append("")

    lines.append("🎯 **集中度风险**")
    lines.append(f"• 评级: {a['concentration']['rating'].upper()}")
    lines.append(f"• 最大持仓占比: {m['concentration']['top_position_pct']:.1f}%")
    lines.append(f"• 前三大持仓占比: {m['concentration']['top3_positions_pct']:.1f}%")
    lines.append(f"• {a['concentration']['advice']}")
    lines.append("")

    lines.append("📈 **波动性风险**")
    lines.append(f"• 评级: {a['volatility']['rating'].upper()}")
    lines.append(f"• 平均个股盈亏: {m['volatility']['avg_position_pnl_pct']:.1f}%")
    lines.append(f"• 盈亏标准差: {m['volatility']['pnl_std']:.1f}%")
    lines.append(f"• {a['volatility']['advice']}")
    lines.append("")

    lines.append("🔔 **整体风险评估**")
    lines.append(f"• 评级: {a['overall']['rating'].upper()}")
    lines.append(f"• {a['overall']['advice']}")
    lines.append("")

    return "\n".join(lines)
