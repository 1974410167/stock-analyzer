from __future__ import annotations

import os
import sys
import json
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
from detailed_analyzer import analyze_all_top_and_worst
from xiaohongshu_generator import generate_xiaohongshu_content
import subprocess


def send_to_feishu_with_charts(report_text: str, chart_files: list, output_dir: str):
    """发送报告和图表到飞书"""
    try:
        # 使用 OpenClaw message 工具发送
        # 先发送文字报告
        print(f"    📤 发送报告到飞书...")
        
        # 调用 OpenClaw CLI 发送消息
        cmd = [
            'openclaw', 'message', 'send',
            '--channel', 'feishu',
            '--target', 'user:ou_1f0dfac373311ed5ab5cb9de75539dcc',
            '--message', report_text[:2000]  # 限制长度
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"    ✅ 报告已发送")
        else:
            print(f"    ⚠️  发送失败：{result.stderr}")
        
        # 发送图表
        for chart_path in chart_files:
            if os.path.exists(chart_path):
                print(f"    📤 发送图表：{os.path.basename(chart_path)}")
                cmd = [
                    'openclaw', 'message', 'send',
                    '--channel', 'feishu',
                    '--target', 'user:ou_1f0dfac373311ed5ab5cb9de75539dcc',
                    '--media', chart_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print(f"    ✅ 图表已发送：{os.path.basename(chart_path)}")
                else:
                    print(f"    ⚠️  图表发送失败：{result.stderr}")
        
    except Exception as e:
        print(f"    ⚠️  发送失败：{e}")


def format_daily_change_report(analysis: dict, advice: dict, positions_with_daily: list, risk_result: dict, detailed: dict = None) -> str:
    """格式化每日涨跌报告（重点突出今日变化）"""
    lines = []
    lines.append("# 📈 股票持仓 - 今日涨跌报告")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
    lines.append("")
    
    # 整体情况
    lines.append("## 📊 今日整体表现")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 持仓数量 | {analysis['total_positions']} 只 |")
    lines.append(f"| **今日上涨** | {analysis['rising_positions']} 只 📈 |")
    lines.append(f"| **今日下跌** | {analysis['falling_positions']} 只 📉 |")
    lines.append(f"| 总市值 | **${analysis['total_value']:,.2f}** |")
    lines.append(f"| **今日涨跌** | **+${analysis['total_pnl']:,.2f} ({analysis['total_pnl_pct']:.2f}%)** |")
    lines.append("")
    
    # 🎯 今日涨跌详情（按今日涨跌幅排序）
    lines.append("## 🎯 今日涨跌详情（每只股票）")
    lines.append("")
    lines.append("| 股票 | **今日涨跌** | 今日% | 总盈亏 | 占净值 |")
    lines.append("|------|-----------|-------|--------|--------|")
    
    # 按今日涨跌排序
    sorted_positions = sorted(positions_with_daily, key=lambda x: x.get('today_change_pct', 0), reverse=True)
    for pos in sorted_positions:
        symbol = pos.get('symbol', 'N/A')
        today_change = pos.get('today_change', 0)
        today_change_pct = pos.get('today_change_pct', 0)
        total_pnl = pos.get('pnl', 0)
        percent_nav = pos.get('percent_of_nav', 0)
        emoji = "📈" if today_change > 0 else "📉" if today_change < 0 else "➡️"
        change_str = f"+${today_change:,.2f}" if today_change > 0 else f"${today_change:,.2f}"
        lines.append(f"| {emoji} {symbol} | **{change_str}** | {today_change_pct:+.2f}% | ${total_pnl:,.2f} | {percent_nav:.2f}% |")
    lines.append("")
    
    # 表现最佳
    lines.append("## 🏆 表现最佳 (总盈亏前 3 名)")
    for i, p in enumerate(advice['top_performers'], 1):
        medal = ["🥇", "🥈", "🥉"][i-1]
        lines.append(f"{medal} **{p['symbol']}**: +${p['pnl']:,.2f} (**+{p['pnl_pct']:.2f}%)")
    lines.append("")
    
    # 表现最差
    lines.append("## 📉 表现最差 (总盈亏后 3 名)")
    for p in advice['worst_performers']:
        lines.append(f"- **{p['symbol']}**: ${p['pnl']:,.2f} ({p['pnl_pct']:.2f}%)")
    lines.append("")
    
    # 整体建议
    lines.append("## 💡 整体建议")
    lines.append(advice['overall'])
    lines.append("")
    
    # 风险分析
    if risk_result.get('metrics'):
        m = risk_result['metrics']
        a = risk_result['analysis']
        lines.append("## ⚠️  投资组合风险分析")
        lines.append("")
        emoji_map = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
        lines.append(f"### 整体风险评级：{emoji_map.get(a['overall']['rating'], '⚪')} **{a['overall']['rating'].upper()}**")
        lines.append("")
        lines.append("| 风险类型 | 评级 | 详情 |")
        lines.append("|----------|------|------|")
        lines.append(f"| 集中度风险 | {'✅' if a['concentration']['rating'] == 'low' else '⚠️'} {a['concentration']['rating'].upper()} | 最大持仓占比 {m['concentration']['top_position_pct']:.1f}% |")
        lines.append(f"| 波动性风险 | {'✅' if a['volatility']['rating'] == 'low' else '⚠️'} {a['volatility']['rating'].upper()} | 盈亏标准差 {m['volatility']['pnl_std']:.1f}% |")
        lines.append(f"| 整体风险 | {'✅' if a['overall']['rating'] == 'low' else '⚠️'} {a['overall']['rating'].upper()} | {a['overall']['advice']} |")
        lines.append("")
    
    # 详细分析（表现最佳和最差）
    if detailed:
        lines.append(detailed['formatted'])
    
    return "\n".join(lines)


def main():
    """主函数：生成完整报告并发送"""
    config = load_config()
    total_steps = 8
    current_step = 0
    
    try:
        print("="*60)
        print("🚀 开始生成每日股票分析报告")
        print("="*60)
        print(f"⏱️  预计耗时：约 10-15 秒")
        print()
        
        # 1. 获取数据
        current_step += 1
        print(f"[{current_step}/{total_steps}] 📥 从 IBKR 获取数据...")
        csv_data = fetch_flex_statement(config)
        positions = extract_position_data(csv_data)
        parsed = parse_positions(positions)
        print(f"    ✅ 成功解析 {len(parsed)} 个持仓")
        
        # 2. 分析
        current_step += 1
        print(f"[{current_step}/{total_steps}] 📊 分析持仓数据...")
        analysis = analyse_positions(parsed)
        advice = generate_advice(analysis)
        print(f"    ✅ 分析完成，上涨{analysis['rising_positions']}只，下跌{analysis['falling_positions']}只")
        
        # 3. 风险分析
        current_step += 1
        print(f"[{current_step}/{total_steps}] ⚠️  计算风险指标...")
        risk_result = calculate_risk_metrics(parsed)
        risk_rating = risk_result.get('metrics', {}).get('risk_ratings', {}).get('overall_risk', 'unknown')
        print(f"    ✅ 风险评级：{risk_rating.upper()}")
        
        # 4. 计算每日涨跌
        current_step += 1
        print(f"[{current_step}/{total_steps}] 📊 计算每日涨跌...")
        from daily_change import get_yesterday_report_path, load_yesterday_prices, calculate_daily_change
        yesterday_path = get_yesterday_report_path()
        if yesterday_path:
            yesterday_prices = load_yesterday_prices(yesterday_path)
            positions_with_daily = calculate_daily_change(parsed, yesterday_prices)
            print(f"    ✅ 已计算每日涨跌（对比昨日）")
        else:
            positions_with_daily = parsed
            print(f"    ⚠️  未找到昨日数据，使用总盈亏")
        
        # 5. 生成图表
        current_step += 1
        print(f"[{current_step}/{total_steps}] 📈 生成可视化图表 (3 张)...")
        chart_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'charts')
        os.makedirs(chart_dir, exist_ok=True)
        charts = create_portfolio_charts(parsed, chart_dir)
        print(f"    ✅ 图表生成完成：{list(charts.keys())}")
        
        # 6. 详细分析
        current_step += 1
        print(f"[{current_step}/{total_steps}] 🔍 深度分析重点股票...")
        detailed = analyze_all_top_and_worst(advice)
        print(f"    ✅ 完成 {len(detailed['top_performers']) + len(detailed['worst_performers'])} 只股票分析")
        
        # 7. 小红书内容
        current_step += 1
        print(f"[{current_step}/{total_steps}] 📕 生成小红书内容...")
        xiaohongshu = generate_xiaohongshu_content(analysis, advice, risk_result)
        print(f"    ✅ 小红书文案 + {len(xiaohongshu['charts'])} 张图表")
        
        # 8. 格式化报告
        current_step += 1
        print(f"[{current_step}/{total_steps}] 📝 格式化报告...")
        report_text = format_daily_change_report(analysis, advice, positions_with_daily, risk_result, detailed)
        print(f"    ✅ 报告格式化完成")
        
        # 9. 保存报告
        current_step += 1
        print(f"[{current_step}/{total_steps}] 💾 保存报告文件...")
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存标准报告
        report_file = os.path.join(output_dir, 'report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        # 保存小红书内容
        xiaohongshu_file = os.path.join(output_dir, 'xiaohongshu.txt')
        with open(xiaohongshu_file, 'w', encoding='utf-8') as f:
            f.write(xiaohongshu['full_content'])
        
        # 保存 JSON
        json_file = os.path.join(output_dir, 'report.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'analysis': analysis,
                'advice': advice,
                'risk': risk_result,
                'detailed': detailed,
                'xiaohongshu': {
                    'caption': xiaohongshu['caption'],
                    'hashtags': xiaohongshu['hashtags'],
                    'charts': list(xiaohongshu['charts'].keys())
                },
                'timestamp': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        print(f"    ✅ 报告已保存")
        print(f"    ✅ 小红书内容已保存")
        
        # 10. 发送图表到飞书
        current_step += 1
        print(f"[{current_step}/{total_steps}] 📤 发送图表到飞书...")
        chart_files = [charts[key] for key in charts.keys()]
        send_to_feishu_with_charts(report_text, chart_files, output_dir)
        print(f"    ✅ 已发送到飞书")
        
        # 完成
        print()
        print("="*60)
        print("🎉 报告生成并发送完成！")
        print("="*60)
        print(f"📊 总市值：${analysis['total_value']:,.2f}")
        print(f"💰 总盈亏：+${analysis['total_pnl']:,.2f} ({analysis['total_pnl_pct']:.2f}%)")
        print(f"📈 图表：{len(charts)} 张 - 已发送")
        print(f"📕 小红书：已生成")
        print()
        print("📄 文件列表:")
        print(f"   • data/report.txt - 标准报告")
        print(f"   • data/xiaohongshu.txt - 小红书文案")
        print(f"   • data/charts/ - 标准图表 (已发送)")
        print(f"   • data/xiaohongshu/ - 小红书图表")
        print()
        
        return 0
        
    except Exception as exc:
        print(f"\n❌ 生成报告失败：{exc}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
