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


def fetch_flex_statement(config: FlexConfig) -> str:
    """
    从 IBKR Flex Query 获取数据

    步骤：
    1. 发送请求获取 Reference Code 和下载 URL
    2. 等待 IBKR 服务器准备数据
    3. 使用下载 URL 获取 CSV 数据
    """
    # 第一步：发送请求，获取下载凭证
    print(f"🚀 正在向 IBKR 发送生成报表请求 (Query ID: {config.query_id})...")

    request_url = f"{config.send_request_url}?t={config.token}&q={config.query_id}&v={config.api_version}"
    response = requests.get(request_url, timeout=config.timeout_seconds)

    if response.status_code != 200:
        raise FlexServiceError(f"请求失败，状态码: {response.status_code}")

    # 解析返回的 XML
    root = _parse_xml(response.text)
    status = _get_text(root, "Status")

    if status != "Success":
        error_message = _get_text(root, "ErrorMessage") or "未知错误"
        raise FlexServiceError(f"IBKR Flex Query 失败: {error_message}")

    reference_code = _get_text(root, "ReferenceCode")
    download_url = _get_text(root, "Url")

    if not reference_code:
        raise FlexServiceError("IBKR 未返回 Reference Code")

    if not download_url:
        raise FlexServiceError("IBKR 未返回下载 URL")

    print(f"✅ 报表生成成功！拿到下载凭证: {reference_code}")

    # 第二步：等待 IBKR 服务器准备数据
    print(f"⏳ 等待 {config.wait_seconds} 秒钟让 IBKR 服务器准备文件...")
    time.sleep(config.wait_seconds)

    # 第三步：使用凭证下载数据
    print("📥 正在下载数据...")
    dl_url = f"{download_url}?q={reference_code}&t={config.token}&v={config.api_version}"
    csv_response = requests.get(dl_url, timeout=config.timeout_seconds)

    if csv_response.status_code != 200:
        raise FlexServiceError(f"下载失败，状态码: {csv_response.status_code}")

    print(f"🎉 数据下载成功！大小: {len(csv_response.text)} 字节")

    return csv_response.text
