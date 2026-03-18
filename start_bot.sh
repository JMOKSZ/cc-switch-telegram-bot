#!/bin/bash
# CC Switch Telegram Bot 启动脚本

cd "$(dirname "$0")"

# Load environment variables from .env if exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check if token is set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "错误: 请设置 TELEGRAM_BOT_TOKEN"
    echo "方法1: export TELEGRAM_BOT_TOKEN='your_token'"
    echo "方法2: 编辑 .env 文件"
    exit 1
fi

# Start the bot
echo "🚀 启动 CC Switch Telegram Bot..."
python3 src/telegram_bot.py
