from __future__ import annotations

import os
from typing import Any

# 检查是否有 matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')  # 非交互式后端
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def check_dependencies() -> bool:
    """检查是否有必要的依赖"""
    return HAS_MATPLOTLIB


def install_dependencies_message() -> str:
    """返回安装依赖的提示"""
    return "需要安装 matplotlib: pip install matplotlib"


def create_portfolio_charts(positions: list[dict[str, Any]], output_dir: str = None) -> dict[str, str]:
    """
    创建投资组合图表

    返回生成的图表文件路径
    """
    if not HAS_MATPLOTLIB:
        return {'error': install_dependencies_message()}

    if not output_dir:
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data',
            'charts'
        )
    
    os.makedirs(output_dir, exist_ok=True)

    charts = {}

    # 图表1：持仓分布饼图
    charts['allocation'] = _create_allocation_chart(positions, output_dir)
    
    # 图表2：盈亏条形图
    charts['pnl_bar'] = _create_pnl_bar_chart(positions, output_dir)
    
    # 图表3：持仓 vs 盈亏散点图
    charts['value_vs_pnl'] = _create_value_vs_pnl_chart(positions, output_dir)

    return charts


def _create_allocation_chart(positions: list[dict[str, Any]], output_dir: str) -> str:
    """创建持仓分布饼图"""
    symbols = [pos.get('symbol', 'UNK') for pos in positions]
    values = [pos.get('position_value', 0) for pos in positions]
    pcts = [pos.get('percent_of_nav', 0) for pos in positions]

    plt.figure(figsize=(12, 8))
    
    # 使用渐变色
    colors = plt.cm.Set3(range(len(symbols)))
    
    wedges, texts, autotexts = plt.pie(
        values,
        labels=[f"{s}\n{p:.1f}%" for s, p in zip(symbols, pcts)],
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 10}
    )
    
    # 美化
    plt.title('Portfolio Allocation (持仓分布)', fontsize=14, fontweight='bold')
    plt.axis('equal')
    
    # 添加图例
    plt.legend(
        [f"{s} - ${v:,.0f}" for s, v in zip(symbols, values)],
        loc='center left',
        bbox_to_anchor=(1, 0.5)
    )
    
    output_path = os.path.join(output_dir, 'allocation_pie.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()
    
    return output_path


def _create_pnl_bar_chart(positions: list[dict[str, Any]], output_dir: str) -> str:
    """创建盈亏条形图"""
    symbols = [pos.get('symbol', 'UNK') for pos in positions]
    pnls = [pos.get('pnl', 0) for pos in positions]
    pnl_pcts = [pos.get('pnl_pct', 0) for pos in positions]

    plt.figure(figsize=(14, 8))
    
    # 根据盈亏正负设置颜色
    colors = ['green' if pnl > 0 else 'red' for pnl in pnls]
    
    bars = plt.bar(range(len(symbols)), pnls, color=colors, alpha=0.7)
    
    # 添加数值标签
    for i, (bar, pnl, pct) in enumerate(zip(bars, pnls, pnl_pcts)):
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2.,
            height + (50 if height > 0 else -150),
            f'${pnl:,.0f}\n({pct:.1f}%)',
            ha='center',
            va='bottom' if height > 0 else 'top',
            fontsize=8
        )
    
    plt.axhline(y=0, color='black', linestyle='-', linewidth=1)
    plt.xlabel('Stock Symbol', fontsize=12)
    plt.ylabel('P&L (USD)', fontsize=12)
    plt.title('Portfolio P&L by Position (个股盈亏)', fontsize=14, fontweight='bold')
    plt.xticks(range(len(symbols)), symbols, rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    output_path = os.path.join(output_dir, 'pnl_bar.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()
    
    return output_path


def _create_value_vs_pnl_chart(positions: list[dict[str, Any]], output_dir: str) -> str:
    """创建持仓价值 vs 盈亏散点图"""
    values = [pos.get('position_value', 0) for pos in positions]
    pnls = [pos.get('pnl', 0) for pos in positions]
    pnl_pcts = [pos.get('pnl_pct', 0) for pos in positions]
    symbols = [pos.get('symbol', 'UNK') for pos in positions]

    plt.figure(figsize=(12, 8))
    
    # 根据盈亏百分比着色
    scatter = plt.scatter(
        values,
        pnls,
        c=pnl_pcts,
        cmap='RdYlGn',
        s=200,
        alpha=0.6,
        edgecolors='black',
        linewidth=1
    )
    
    # 添加符号标签
    for i, symbol in enumerate(symbols):
        plt.annotate(
            symbol,
            (values[i], pnls[i]),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=9
        )
    
    plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    plt.xlabel('Position Value (USD)', fontsize=12)
    plt.ylabel('P&L (USD)', fontsize=12)
    plt.title('Position Value vs P&L (持仓价值 vs 盈亏)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # 添加颜色条
    cbar = plt.colorbar(scatter)
    cbar.set_label('P&L %', rotation=270, labelpad=20)
    
    output_path = os.path.join(output_dir, 'value_vs_pnl.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()
    
    return output_path


def format_charts_report(charts: dict[str, str]) -> str:
    """格式化图表报告"""
    if 'error' in charts:
        return f"❌ 图表生成失败：{charts['error']}"
    
    lines = []
    lines.append("📊 **投资组合图表**")
    lines.append("=" * 40)
    lines.append("")
    lines.append("已生成以下图表:")
    lines.append("")
    
    chart_names = {
        'allocation': '🥧 持仓分布饼图',
        'pnl_bar': '📊 盈亏条形图',
        'value_vs_pnl': '🔍 持仓价值 vs 盈亏散点图'
    }
    
    for key, name in chart_names.items():
        if key in charts:
            lines.append(f"• {name}: `{charts[key]}`")
    
    lines.append("")
    lines.append("图表已保存到 data/charts/ 目录")
    
    return "\n".join(lines)
