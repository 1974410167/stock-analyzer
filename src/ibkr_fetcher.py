from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from typing import Any

import requests

from config import FlexConfig


class FlexServiceError(RuntimeError):
    pass


def _get_text(root: ET.Element, tag: str) -> str | None:
    node = root.find(tag)
    if node is None or node.text is None:
        return None
    return node.text.strip()


def _parse_xml(xml_text: str) -> ET.Element:
    try:
        return ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise FlexServiceError("Failed to parse IBKR Flex XML response.") from exc


def request_reference_code(config: FlexConfig) -> str:
    response = requests.get(
        config.send_request_url,
        params={"t": config.token, "q": config.query_id, "v": config.api_version},
        timeout=config.timeout_seconds,
    )
    response.raise_for_status()

    root = _parse_xml(response.text)
    status = (_get_text(root, "Status") or "").lower()
    if status != "success":
        message = _get_text(root, "ErrorMessage") or "Unknown IBKR Flex request error."
        raise FlexServiceError(message)

    reference_code = _get_text(root, "ReferenceCode")
    if not reference_code:
        raise FlexServiceError("IBKR Flex did not return a reference code.")

    return reference_code


def fetch_statement_xml(config: FlexConfig) -> str:
    reference_code = request_reference_code(config)

    for attempt in range(1, config.max_poll_attempts + 1):
        response = requests.get(
            config.get_statement_url,
            params={"t": config.token, "q": reference_code, "v": config.api_version},
            timeout=config.timeout_seconds,
        )
        response.raise_for_status()

        root = _parse_xml(response.text)
        status = (_get_text(root, "Status") or "").lower()
        if not status:
            return response.text

        if status == "success":
            return response.text

        message = _get_text(root, "ErrorMessage") or ""
        if "generation in progress" not in message.lower():
            raise FlexServiceError(message or "Unknown IBKR Flex statement error.")

        if attempt < config.max_poll_attempts:
            time.sleep(config.poll_interval_seconds)

    raise FlexServiceError("IBKR Flex statement generation timed out.")


def extract_trade_rows(statement_xml: str) -> list[dict[str, Any]]:
    root = _parse_xml(statement_xml)
    rows: list[dict[str, Any]] = []

    for trade in root.findall(".//Trade"):
        symbol = trade.attrib.get("symbol")
        quantity = _to_float(trade.attrib.get("quantity"))
        trade_price = _to_float(trade.attrib.get("tradePrice"))

        if not symbol or quantity is None or trade_price is None:
            continue

        rows.append(
            {
                "symbol": symbol,
                "quantity": quantity,
                "trade_price": trade_price,
                "buy_sell": trade.attrib.get("buySell"),
                "trade_date": trade.attrib.get("tradeDate"),
            }
        )

    return rows


def _to_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None
