from __future__ import annotations

import json

from advisor import generate_advice
from analyser import analyse_positions
from config import load_config
from ibkr_fetcher import fetch_flex_statement
from position_parser import extract_position_data, parse_positions


def main() -> None:
    config = load_config()

    try:
        # 第一步：获取数据
        csv_data = fetch_flex_statement(config)

        # 第二步：提取持仓数据
        positions = extract_position_data(csv_data)
        print(f"\n📊 解析到 {len(positions)} 条持仓记录")

        # 第三步：解析持仓
        parsed_positions = parse_positions(positions)
        print(f"💹 成功解析 {len(parsed_positions)} 个持仓")

        if not parsed_positions:
            print("⚠️ 没有找到有效的持仓数据")
            return

        # 第四步：分析
        analysis = analyse_positions(parsed_positions)

        # 第五步：生成建议
        advice = generate_advice(analysis)

        # 输出结果
        print("\n" + "="*80)
        print("📈 股票持仓分析报告")
        print("="*80)
        print(f"\n📊 整体情况:")
        print(f"  持仓数量: {analysis['total_positions']}")
        print(f"  上涨: {analysis['rising_positions']} | 下跌: {analysis['falling_positions']} | 持平: {analysis['flat_positions']}")
        print(f"  总市值: ${analysis['total_value']:,.2f}")
        print(f"  总盈亏: ${analysis['total_pnl']:,.2f} ({analysis['total_pnl_pct']:.2f}%)")

        print(f"\n🏆 表现最佳 (前3名):")
        for p in advice['top_performers']:
            print(f"  {p['symbol']}: ${p['pnl']:,.2f} ({p['pnl_pct']:.2f}%) - {p['description']}")

        print(f"\n📉 表现最差 (后3名):")
        for p in advice['worst_performers']:
            print(f"  {p['symbol']}: ${p['pnl']:,.2f} ({p['pnl_pct']:.2f}%) - {p['description']}")

        print(f"\n💡 整体建议:")
        print(f"  {advice['overall']}")
        print(f"  {advice['trend']}")

        print(f"\n📋 每只股票详细分析:")
        print("-"*80)
        for pos in analysis['symbol_analysis']:
            print(f"\n  {pos['symbol']} - {pos['description']}")
            print(f"    数量: {pos['quantity']}, 开仓价: ${pos['open_price']}, 市价: ${pos['mark_price']}")
            print(f"    价格变动: ${pos['price_change']} ({pos['price_change_pct']:.2f}%)")
            print(f"    盈亏: ${pos['pnl']} ({pos['pnl_pct']:.2f}%), 占净值: {pos['percent_of_nav']}%")

        print("\n" + "="*80)
        print("📄 JSON 格式输出")
        print("="*80)
        print(json.dumps({
            "analysis": analysis,
            "advice": advice
        }, indent=2, ensure_ascii=False))

    except Exception as exc:
        print(f"\n❌ 错误: {exc}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
