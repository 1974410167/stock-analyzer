from __future__ import annotations

import os
from typing import Any
from datetime import datetime

# 检查 matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
    
    # 全部使用英文，不需要中文字体
    rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
    rcParams['axes.unicode_minus'] = False
    
    print("✅ Using English labels for charts")
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def generate_xiaohongshu_content(analysis: dict, advice: dict, risk_result: dict) -> dict[str, Any]:
    """生成小红书风格内容"""
    
    content = generate_caption(analysis, advice, risk_result)
    charts = generate_xiaohongshu_charts(analysis, advice)
    hashtags = generate_hashtags(analysis, advice)
    
    return {
        'caption': content,
        'charts': charts,
        'hashtags': hashtags,
        'full_content': content + '\n\n' + hashtags
    }


def generate_caption(analysis: dict, advice: dict, risk_result: dict) -> str:
    """生成小红书文案"""
    
    total_value = analysis['total_value']
    total_pnl = analysis['total_pnl']
    total_pnl_pct = analysis['total_pnl_pct']
    rising = analysis['rising_positions']
    falling = analysis['falling_positions']
    
    if total_pnl_pct > 10:
        mood = "🎉 爽翻了！"
        emoji = "💰"
    elif total_pnl_pct > 5:
        mood = "😊 今天不错！"
        emoji = "📈"
    elif total_pnl_pct > 0:
        mood = "🙂 还行还行"
        emoji = "💚"
    else:
        mood = "😭 今天吃面"
        emoji = "📉"
    
    top = advice['top_performers'][0] if advice.get('top_performers') else None
    worst = advice['worst_performers'][0] if advice.get('worst_performers') else None
    
    lines = []
    lines.append(f"{emoji} 美股持仓日记 | {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append(f"💰 总收益 {total_pnl_pct:+.2f}% | ${total_pnl:,.2f}")
    lines.append(f"📊 总市值 ${total_value:,.2f}")
    lines.append(f"📈 上涨 {rising} 只 | 📉 下跌 {falling} 只")
    lines.append("")
    lines.append(f"{mood}")
    lines.append("")
    
    if top:
        lines.append(f"🏆 今日最佳：{top['symbol']} {top['pnl_pct']:+.2f}% 🚀")
        lines.append(f"   盈利 ${top['pnl']:,.2f}")
    
    if worst:
        lines.append(f"📉 今日最差：{worst['symbol']} {worst['pnl_pct']:+.2f}% 💔")
        lines.append(f"   亏损 ${worst['pnl']:,.2f}")
    
    lines.append("")
    lines.append("💡 操作思路：")
    
    if top and 'INTC' in top['symbol']:
        lines.append("   AI 芯片持续看好，半导体周期复苏中")
        lines.append("   英特尔这波翻倍了，考虑分批止盈")
    elif top and 'AMD' in top['symbol']:
        lines.append("   AMD YES！数据中心需求强劲")
        lines.append("   继续持有，看高一线")
    
    risk_rating = risk_result.get('metrics', {}).get('risk_ratings', {}).get('overall_risk', 'unknown')
    risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(risk_rating, '⚪')
    lines.append(f"   组合风险：{risk_emoji} {risk_rating.upper()}")
    
    lines.append("")
    lines.append("📊 Charts:")
    lines.append("   Fig 2: Portfolio Allocation (Donut)")
    lines.append("   Fig 3: Best vs Worst Performers")
    lines.append("   Fig 4: Sector Allocation")
    lines.append("")
    
    return "\n".join(lines)


def generate_hashtags(analysis: dict, advice: dict) -> str:
    """生成话题标签"""
    
    tags = [
        "#美股",
        "#投资理财",
        "#股票",
        "#价值投资",
        "#持仓记录",
        "#理财日记",
    ]
    
    symbols = [pos['symbol'] for pos in analysis.get('symbol_analysis', [])]
    
    if 'INTC' in symbols or 'AMD' in symbols or 'NVDA' in symbols:
        tags.extend(["#半导体", "#芯片"])
    
    if 'TSLA' in symbols:
        tags.extend(["#特斯拉", "#电动车"])
    
    if 'MSFT' in symbols or 'META' in symbols:
        tags.extend(["#科技股", "#FAANG"])
    
    if any('ADR' in pos.get('description', '') for pos in analysis.get('symbol_analysis', [])):
        tags.extend(["#中概股"])
    
    return " ".join(tags)


def generate_xiaohongshu_charts(analysis: dict, advice: dict) -> dict[str, str]:
    """生成适合小红书的图表"""
    
    if not HAS_MATPLOTLIB:
        return {'error': 'matplotlib not installed'}
    
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data',
        'xiaohongshu'
    )
    os.makedirs(output_dir, exist_ok=True)
    
    charts = {}
    
    charts['allocation'] = _create_donut_chart(analysis, output_dir)
    charts['pnl'] = _create_horizontal_pnl_chart(analysis, advice, output_dir)
    charts['sector'] = _create_sector_chart(analysis, output_dir)
    
    return charts


def _classify_sector(symbol: str, description: str) -> str:
    """根据股票分类行业（英文版）"""
    desc_lower = description.lower()
    symbol_upper = symbol.upper()
    
    if any(kw in desc_lower for kw in ['intel', 'amd', 'nvidia', 'advanced micro', 'semi', 'chip']):
        return 'Semiconductors'
    
    if any(kw in desc_lower for kw in ['microsoft', 'meta', 'software', 'internet', 'platform']):
        return 'Software/Internet'
    
    if 'tesla' in desc_lower or symbol_upper == 'TSLA':
        return 'Electric Vehicles'
    
    if 'amazon' in desc_lower or symbol_upper == 'AMZN':
        return 'E-commerce'
    
    if 'qualcomm' in desc_lower or symbol_upper == 'QCOM':
        return 'Telecom Chips'
    
    if 'micro strategy' in desc_lower or symbol_upper == 'MSTR':
        return 'Crypto-related'
    
    if 'broker' in desc_lower or 'interactive brokers' in desc_lower or symbol_upper == 'IBKR':
        return 'Financial'
    
    if 'treasury' in desc_lower or symbol_upper == 'SGOV':
        return 'Fixed Income'
    
    if 'xiaomi' in desc_lower or 'china' in desc_lower or symbol_upper == 'XIACY':
        return 'Chinese ADR'
    
    if 'arm' in desc_lower and symbol_upper == 'ARM':
        return 'Semiconductors'
    
    return 'Other'


def _create_sector_chart(analysis: dict, output_dir: str) -> str:
    """创建行业分布饼图（英文版）"""
    
    sector_data = {}
    for pos in analysis['symbol_analysis']:
        sector = _classify_sector(pos['symbol'], pos['description'])
        if sector not in sector_data:
            sector_data[sector] = 0
        sector_data[sector] += pos['position_value']
    
    sorted_sectors = sorted(sector_data.items(), key=lambda x: x[1], reverse=True)
    sectors = [s[0] for s in sorted_sectors]
    values = [s[1] for s in sorted_sectors]
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
              '#F7DC6F', '#BB8FCE', '#82E0AA', '#F5B7B1', '#D7BDE2']
    
    plt.figure(figsize=(10, 10))
    
    wedges, texts, autotexts = plt.pie(
        values,
        labels=sectors,
        autopct='%1.1f%%',
        colors=colors[:len(sectors)],
        startangle=90,
        pctdistance=0.85,
        textprops={'fontsize': 11, 'weight': 'bold'}
    )
    
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    plt.gca().add_artist(centre_circle)
    
    total = sum(values)
    plt.text(0, 0, f"Total\n${total/1000:.1f}K", 
             ha='center', va='center', fontsize=16, weight='bold')
    
    plt.title('Sector Allocation', fontsize=18, weight='bold', pad=20)
    plt.axis('equal')
    
    output_path = os.path.join(output_dir, 'sector_allocation.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=150, facecolor='white')
    plt.close()
    
    return output_path


def _create_donut_chart(analysis: dict, output_dir: str) -> str:
    """创建环形图（英文版）"""
    
    symbols = [pos['symbol'] for pos in analysis['symbol_analysis'][:8]]
    values = [pos['position_value'] for pos in analysis['symbol_analysis'][:8]]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#82E0AA']
    
    plt.figure(figsize=(10, 10))
    
    wedges, texts, autotexts = plt.pie(
        values,
        labels=symbols,
        autopct='%1.1f%%',
        colors=colors[:len(symbols)],
        startangle=90,
        pctdistance=0.85,
        textprops={'fontsize': 12, 'weight': 'bold'}
    )
    
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    plt.gca().add_artist(centre_circle)
    
    total = sum(values)
    plt.text(0, 0, f"Total\n${total/1000:.1f}K", 
             ha='center', va='center', fontsize=16, weight='bold')
    
    plt.title('Portfolio Allocation', fontsize=18, weight='bold', pad=20)
    plt.axis('equal')
    
    output_path = os.path.join(output_dir, 'allocation_donut.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=150, facecolor='white')
    plt.close()
    
    return output_path


def _create_horizontal_pnl_chart(analysis: dict, advice: dict, output_dir: str) -> str:
    """创建横向盈亏条形图"""
    
    sorted_by_pnl = sorted(analysis['symbol_analysis'], key=lambda x: x['pnl'], reverse=True)
    top_gainers = sorted_by_pnl[:3]
    top_losers = sorted_by_pnl[-3:]
    
    symbols = [p['symbol'] for p in top_gainers] + [p['symbol'] for p in reversed(top_losers)]
    pnls = [p['pnl'] for p in top_gainers] + [p['pnl'] for p in reversed(top_losers)]
    colors = ['#4ECDC4'] * 3 + ['#FF6B6B'] * 3
    
    plt.figure(figsize=(10, 8))
    
    bars = plt.barh(range(len(symbols)), pnls, color=colors)
    
    for i, (bar, pnl) in enumerate(zip(bars, pnls)):
        width = bar.get_width()
        plt.text(
            width + (100 if width > 0 else -200),
            i,
            f'${pnl:,.0f}',
            ha='left' if width > 0 else 'right',
            va='center',
            fontsize=10,
            weight='bold'
        )
    
    plt.axhline(y=2.5, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    
    plt.xlabel('P&L (USD)', fontsize=12)
    plt.title('Best vs Worst Performers', fontsize=16, weight='bold', pad=20)
    
    plt.yticks(range(len(symbols)), symbols, fontsize=11)
    plt.grid(axis='x', alpha=0.3)
    
    output_path = os.path.join(output_dir, 'pnl_comparison.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=150, facecolor='white')
    plt.close()
    
    return output_path
