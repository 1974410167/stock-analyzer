#!/bin/bash
# Cron 任务脚本 - 生成并发送每日股票分析报告 + 小红书内容
# 每天北京时间 19:00 (UTC 11:00) 执行

# 设置环境变量
export PATH="/root/miniconda3/envs/stock-analyzer/bin:$PATH"
export HOME="/root"

# 进入项目目录
cd /root/.openclaw/workspace/stock-analyzer

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 开始执行每日股票分析..."

# 生成报告（包含标准报告 + 小红书内容）
python src/daily_report.py

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 报告生成成功"

    # 生成发送标记文件（供 heartbeat/巡检使用）
    SENT_FILE="data/report-$(date '+%Y-%m-%d')-sent.txt"
    cp -f data/report.txt "$SENT_FILE" 2>/dev/null || echo "sent at $(date '+%F %T')" > "$SENT_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 已写入发送标记: $SENT_FILE"

    # 显示文件列表
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📄 生成的文件:"
    echo "  标准报告：data/report.txt"
    echo "  小红书文案：data/xiaohongshu.txt"
    echo "  标准图表：data/charts/"
    echo "  小红书图表：data/xiaohongshu/"
    
    # 显示图表文件
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📊 图表文件:"
    ls -lh data/charts/*.png 2>/dev/null | while read line; do
        echo "  $line"
    done
    ls -lh data/xiaohongshu/*.png 2>/dev/null | while read line; do
        echo "  $line"
    done
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 报告生成失败"
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🎉 任务完成"
echo ""
echo "📬 下一步："
echo "  1. 查看 data/report.txt - 完整持仓分析"
echo "  2. 查看 data/xiaohongshu.txt - 小红书文案"
echo "  3. 复制文案 + 图表到小红书发布"
