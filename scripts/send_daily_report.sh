#!/bin/bash
# Cron 任务脚本 - 生成并发送每日股票分析报告
# 每天北京时间 19:00 (UTC 11:00) 执行

# 设置环境变量
export PATH="/root/miniconda3/envs/stock-analyzer/bin:$PATH"
export HOME="/root"

# 进入项目目录
cd /root/.openclaw/workspace/stock-analyzer

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 开始执行每日股票分析..."

# 生成报告
python src/daily_report.py

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 报告生成成功"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📊 图表文件:"
    ls -lh data/charts/*.png 2>/dev/null | while read line; do
        echo "  $line"
    done
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 报告生成失败"
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🎉 任务完成"
