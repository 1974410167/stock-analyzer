#!/bin/bash
# Cron 任务脚本 - 生成报告并发送到飞书

# 设置环境变量
export PATH="/root/miniconda3/envs/stock-analyzer/bin:$PATH"
export HOME="/root"

# 进入项目目录
cd /root/.openclaw/workspace/stock-analyzer

# 生成报告
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始生成股票分析报告..."
python src/generate_report.py

if [ $? -eq 0 ]; then
    # 发送报告到飞书
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 发送报告到飞书..."
    python src/send_feishu.py

    if [ $? -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 任务完成"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 发送飞书消息失败"
        exit 1
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 生成报告失败"
    exit 1
fi
