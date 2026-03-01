from __future__ import annotations

import csv
import io
from typing import Any

from config import FlexConfig
from ibkr_fetcher import fetch_flex_statement


class FlexServiceError(RuntimeError):
    pass


def extract_position_data(csv_text: str) -> list[dict[str, Any]]:
    """
    从 IBKR CSV 数据中提取持仓信息

    解析 Position (POST) 报表
    """
    lines = csv_text.split('\n')

    # 找到 Position (POST) 报表
    header_line = None
    for i, line in enumerate(lines):
        if line.startswith('"HEADER","POST"'):
            header_line = i
            break

    if not header_line:
        raise FlexServiceError("未找到 Position 报表")

    # 解析表头
    reader = csv.reader(io.StringIO(lines[header_line]))
    headers = next(reader)

    # 解析数据行
    positions = []

    for line in lines[header_line + 1:]:
        if line.startswith('"DATA","POST"'):
            reader = csv.reader(io.StringIO(line))
            values = next(reader)

            position = {}
            for header, value in zip(headers, values):
                position[header] = value

            positions.append(position)

        elif line.startswith('"EOS","POST"'):
            break

    return positions


def parse_positions(positions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    解析持仓数据，提取关键字段

    返回格式：
    {
        'symbol': 'AMD',
        'quantity': 46,
        'mark_price': 200.21,
        'open_price': 151.083837696,
        'cost_basis_price': 151.083837696,
        'pnl': 2259.803466,
        'position_value': 9209.66,
        'description': 'ADVANCED MICRO DEVICES',
        ...
    }
    """
    parsed = []

    for pos in positions:
        try:
            symbol = pos.get('Symbol')
            if not symbol:
                continue

            quantity = float(pos.get('Quantity', 0))
            mark_price = float(pos.get('MarkPrice', 0))
            open_price = float(pos.get('OpenPrice', 0))
            cost_basis_price = float(pos.get('CostBasisPrice', 0))
            pnl = float(pos.get('FifoPnlUnrealized', 0))
            position_value = float(pos.get('PositionValue', 0))

            parsed.append({
                'symbol': symbol,
                'quantity': quantity,
                'mark_price': mark_price,
                'open_price': open_price,
                'cost_basis_price': cost_basis_price,
                'pnl': pnl,
                'position_value': position_value,
                'description': pos.get('Description', ''),
                'asset_class': pos.get('AssetClass', ''),
                'sub_category': pos.get('SubCategory', ''),
                'listing_exchange': pos.get('ListingExchange', ''),
                'report_date': pos.get('ReportDate', ''),
                'percent_of_nav': float(pos.get('PercentOfNAV', 0)),
            })
        except (ValueError, TypeError) as e:
            # 跳过解析失败的记录
            continue

    return parsed
