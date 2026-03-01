#!/usr/bin/env python3
"""
每日股票分析报告 - 完整版
包含：持仓分析、风险分析、图表生成、飞书推送
"""
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from advisor import generate_advice
from analyser import analyse_positions
from config import load_config
from ibkr_fetcher import fetch_flex_statement
from position_parser import extract_position_data, parse_positions
from risk_analyzer import calculate_risk_metrics, format_risk_report
from news_analyzer import analyze_all_positions
from chart_generator import create_portfolio_charts


def format_complete_report(analysis: dict, advice: dict, risk_result: dict) -> str:
    """格式化完整报告"""
    lines = []
    lines.append("# 📈 股票持仓分析报告")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%M')} (北京时间)")
    lines.append("")
    
    # 整体情况
    lines.append("## 📊 整体情况")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|------|------|")
    lines.append(f"| 持仓数量 | {analysis['total_positions']} 只 |")
    lines.append(f"| 上涨 | {analysis['rising_positions']} 只 📈 |")
    lines.append(f"| 下跌 | {analysis['falling_positions']} 只 📉 |")
    lines.append(f"| 总市值 | **${analysis['total_value']:,.2f}** |")
    lines.append(f"| 总盈亏 | **+${analysis['total_pnl']:,.2f} ({analysis['total_pnl_pct']:.2f}%)** |")
    lines.append("")
    
    # 表现最佳
    lines.append("## 🏆 表现最佳 (前 3 名)")
    for i, p in enumerate(advice['top_performers'], 1):
        medal = ["🥇", "🥈", "🥉"][i-1]
        lines.append(f"{medal} **{p['symbol']}** - {p['description']}: +${p['pnl']:,.2f} (**+{p['pnl_pct']:.2f}%**)")
    lines.append("")
    
    # 表现最差
    lines.append("## 📉 表现最差 (后 3 名)")
    for p in advice['worst_performers']:
        lines.append(f"- **{p['symbol']}** - {p['description']}: ${p['pnl']:,.2f} ({p['pnl_pct']:.2f}%)")
    lines.append("")
    
    # 整体建议
    lines.append("## 💡 整体建议")
    lines.append(advice['overall'])
    lines.append("")
    
    # 持仓详情
    lines.append("## 📋 持仓详情")
    lines.append("")
    lines.append("| 股票 | 描述 | 盈亏 | 盈亏% | 占净值 |")
    lines.append("|------|------|------|-------|--------|")
    for pos in analysis['symbol_analysis']:
        emoji = "📈" if pos['pnl'] > 0 else "📉" if pos['pnl'] < 0 else "➡️"
        lines.append(f"| {emoji} {pos['symbol']} | {pos['description']} | ${pos['pnl']:,.2f} | {pos['pnl_pct']:.2f}% | {pos['percent_of_nav']:.2f}% |")
    lines.append("")
    
    # 风险分析
    if risk_result.get('metrics'):
        m = risk_result['metrics']
        a = risk_result['analysis']
        lines.append("## ⚠️ 投资组合风险分析")
        lines.append("")
        lines.append(f"### 整体风险评级：{'🟢' if a['overall']['rating'] == 'low' else '🟡' if a['overall']['rating'] == 'medium' else '🔴'} **{a['overall']['rating'].upper()}**")
        lines.append("")
        lines.append("| 风险类型 | 评级 | 详情 |")
        lines.append("|----------|------|------|")
        lines.append(f"| 集中度风险 | {'✅' if a['concentration']['rating'] == 'low' else '⚠️'} {a['concentration']['rating'].upper()} | 最大持仓占比 {m['concentration']['top_position_pct']:.1f}% |")
        lines.append(f"| 波动性风险 | {'✅' if a['volatility']['rating'] == 'low' else '⚠️'} {a['volatility']['rating'].upper()} | 盈亏标准差 {m['volatility']['pnl_std']:.1f}% |")
        lines.append(f"| 整体风险 | {'✅' if a['overall']['rating'] == 'low' else '⚠️'} {a['overall']['rating'].upper()} | {a['overall']['advice']} |")
        lines.append("")
    
    return "\n".join(lines)


def main():
    """主函数：生成完整报告并发送"""
    config = load_config()
    
    try:
        print("🚀 开始生成每日股票分析报告...")
        
        # 1. 获取数据
        print("📥 从 IBKR 获取数据...")
        csv_data = fetch_flex_statement(config)
        positions = extract_position_data(csv_data)
        parsed = parse_positions(positions)
        print(f"✅ 成功解析 {len(parsed)} 个持仓")
        
        # 2. 分析
        print("📊 分析持仓数据...")
        analysis = analyse_positions(parsed)
        advice = generate_advice(analysis)
        
        # 3. 风险分析
        print("⚠️  计算风险指标...")
        risk_result = calculate_risk_metrics(parsed)
        
        # 4. 生成图表
        print("📈 生成可视化图表...")
        chart_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'charts')
        os.makedirs(chart_dir, exist_ok=True)
        charts = create_portfolio_charts(parsed, chart_dir)
        
        # 5. 格式化报告
        print("📝 格式化报告...")
        report_text = format_complete_report(analysis, advice, risk_result)
        
        # 6. 保存报告
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(output_dir, exist_ok=True)
        
        report_file = os.path.join(output_dir, 'report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        json_file = os.path.join(output_dir, 'report.json')
        import json
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'analysis': analysis,
                'advice': advice,
                'risk': risk_result,
                'charts': charts,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 报告已保存: {report_file}")
        print(f"✅ 图表已保存: {chart_dir}")
        
        # 7. 返回成功状态
        print("\n🎉 报告生成完成！")
        print("\n📄 报告预览:")
        print("="*60)
        print(report_text[:2000])
        print("...")
        print("="*60)
        
        return 0
        
    except Exception as exc:
        print(f"❌ 生成报告失败: {exc}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
