#!/usr/bin/env python3
"""
发送飞书消息
"""
import os
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def send_report_to_feishu(report_file: str = None) -> bool:
    """
    读取报告文件并发送到飞书

    注意：这需要配置飞书集成
    """
    if not report_file:
        report_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "report.txt"
        )

    if not os.path.exists(report_file):
        print(f"❌ 报告文件不存在: {report_file}")
        return False

    # 读取报告内容
    with open(report_file, "r", encoding="utf-8") as f:
        report_content = f.read()

    # 添加时间戳
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"{report_content}\n\n📅 生成时间: {timestamp}"

    # TODO: 这里需要实际调用飞书 API
    # 目前只是打印消息
    print("=" * 60)
    print("飞书消息内容：")
    print("=" * 60)
    print(message)
    print("=" * 60)

    # 在实际的实现中，可以使用 message 工具发送
    # 或者调用飞书的 web API

    return True


if __name__ == "__main__":
    success = send_report_to_feishu()
    sys.exit(0 if success else 1)
