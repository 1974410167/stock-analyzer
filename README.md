# Stock Analyzer Agent

使用 IBKR Flex Web Service 分析股票持仓，提供涨跌原因分析和投资建议。

## 环境要求

- Python 3.10+
- Miniconda

## 安装

```bash
# 创建 conda 环境
conda env create -f environment.yml

# 激活环境
conda activate stock-analyzer

# 安装依赖
pip install -r requirements.txt
```

## 配置

在 `.env` 文件中配置 IBKR Flex Web Service：

```
IBKR_TOKEN=134125430631770270589696
IBKR_QUERY_ID=1419985
```

## 使用

```bash
python src/main.py
```

## 功能

- 从 IBKR 拉取每日持仓数据
- 分析每个持仓的涨跌情况
- 生成涨跌原因分析
- 提供投资建议
