#!/usr/bin/env python3
"""
生成报告并发送到飞书
"""
import json
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from advisor import generate_advice
from analyser import analyse_positions
from config import load_config
from ibkr_fetcher import fetch_flex_statement
from position_parser import extract_position_data, parse_positions


def format_feishu_message(analysis: dict, advice: dict) -> str:
    """格式化飞书消息"""
    lines = []
    lines.append("📈 **股票持仓分析报告**")
    lines.append("=" * 40)
    lines.append("")
    
    # 整体情况
    lines.append("📊 **整体情况**")
    lines.append(f"• 持仓数量: {analysis['total_positions']}")
    lines.append(f"• 上涨: {analysis['rising_positions']} | 下跌: {analysis['falling_positions']}")
    lines.append(f"• 总市值: ${analysis['total_value']:,.2f}")
    lines.append(f"• 总盈亏: ${analysis['total_pnl']:,.2f} ({analysis['total_pnl_pct']:.2f}%)")
    lines.append("")
    
    # 表现最佳
    lines.append("🏆 **表现最佳 (前3名)**")
    for p in advice['top_performers']:
        lines.append(f"• {p['symbol']}: ${p['pnl']:,.2f} ({p['pnl_pct']:.2f}%)")
    lines.append("")
    
    # 表现最差
    lines.append("📉 **表现最差 (后3名)**")
    for p in advice['worst_performers']:
        lines.append(f"• {p['symbol']}: ${p['pnl']:,.2f} ({p['pnl_pct']:.2f}%)")
    lines.append("")
    
    # 整体建议
    lines.append("💡 **整体建议**")
    lines.append(f"{advice['overall']}")
    lines.append("")
    
    # 详细分析（只显示有意义的）
    lines.append("📋 **持仓详情**")
    for pos in analysis['symbol_analysis']:
        symbol = pos['symbol']
        pnl_pct = pos['pnl_pct']
        emoji = "📈" if pnl_pct > 0 else "📉" if pnl_pct < 0 else "➡️"
        lines.append(f"{emoji} {symbol}: ${pos['pnl']:,.2f} ({pnl_pct:.2f}%)")
    
    return "\n".join(lines)


def main():
    config = load_config()

    try:
        # 生成报告
        csv_data = fetch_flex_statement(config)
        positions = extract_position_data(csv_data)
        parsed_positions = parse_positions(positions)
        analysis = analyse_positions(parsed_positions)
        advice = generate_advice(analysis)

        # 格式化消息
        message = format_feishu_message(analysis, advice)

        # 保存到文件（供 cron 脚本读取）
        output_dir = "/root/.openclaw/workspace/stock-analyzer/data"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, "report.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(message)
        
        # 同时保存 JSON 格式
        json_file = os.path.join(output_dir, "report.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump({"analysis": analysis, "advice": advice}, f, indent=2, ensure_ascii=False)

        print(f"✅ 报告已生成: {output_file}")
        print(f"✅ JSON 数据已保存: {json_file}")
        
        return 0

    except Exception as exc:
        print(f"❌ 生成报告失败: {exc}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
