#!/bin/bash
set -e

# 设置时区
export TZ=Asia/Shanghai

# 获取当天日期
DATE=$(date -d '8 hours' +%Y-%m-%d)
BASE_DIR="public/arxiv"
DATE=2025-07-21

# 运行 get_arxiv.py
python get_data/get_arxiv_paper/get_arxiv.py --date "$DATE" --base_dir "$BASE_DIR"

# 运行 get_overview.py
python get_data/get_gemini_overview/get_overview.py --task arxiv --date "$DATE"