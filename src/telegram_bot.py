#!/usr/bin/env python3
"""
CC Switch Telegram Bot - 通过 Telegram 远程控制 CC Switch

使用方法:
    1. 配置环境变量 TELEGRAM_BOT_TOKEN
    2. 运行: python telegram_bot.py
    3. 在 Telegram 中使用命令
"""

import os
import sys
import logging
from typing import Optional

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler
)

from src.cc_switch_cli import CCSwitchCLI

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for conversation
SELECTING_MODEL = 1


class CCSwitchTelegramBot:
    """CC Switch Telegram 机器人"""

    def __init__(self, token: str):
        self.token = token
        self.cli = CCSwitchCLI()
        self.application = Application.builder().token(token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """设置命令处理器"""
        # Basic commands
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("list", self.cmd_list))
        self.application.add_handler(CommandHandler("current", self.cmd_current))

        # Switch command
        self.application.add_handler(CommandHandler("switch", self.cmd_switch))

        # Callback queries for inline keyboards
        self.application.add_handler(CallbackQueryHandler(self.on_callback))

        # Error handler
        self.application.add_error_handler(self.on_error)

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start 命令"""
        user = update.effective_user
        await update.message.reply_text(
            f"👋 你好 {user.first_name}!\n\n"
            "我是 CC Switch 远程控制器，可以帮你切换 Claude Code 的模型。\n\n"
            "可用命令:\n"
            "/list - 列出所有模型\n"
            "/current - 查看当前模型\n"
            "/switch <名称> - 切换到指定模型\n"
            "/menu - 打开交互式菜单\n"
            "/help - 显示帮助",
            parse_mode='HTML'
        )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help 命令"""
        help_text = """
<b>📱 CC Switch Telegram 控制器</b>

<b>命令列表:</b>
• /list - 显示所有可用模型
• /current - 显示当前使用的模型
• /switch &lt;名称&gt; - 切换到指定模型
  例如: /switch Kimi
       /switch 1
• /menu - 打开图形化选择菜单

<b>快捷操作:</b>
直接点击按钮即可切换模型

<b>注意事项:</b>
• 切换后会立即生效
• 新的对话将使用新模型
        """
        await update.message.reply_text(help_text, parse_mode='HTML')

    async def cmd_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List 命令 - 列出所有模型"""
        providers = self.cli.list_providers()

        if not providers:
            await update.message.reply_text("❌ 未找到任何模型配置")
            return

        # Build message
        lines = ["<b>📋 可用模型列表</b>\n"]

        for p in providers:
            status = "✅ 当前" if p.is_current else ""
            lines.append(f"<code>{p.index}</code>. {p.name} {status}")

        lines.append("\n使用 /switch &lt;名称&gt; 或 /switch &lt;序号&gt; 切换")

        # Add inline keyboard for quick switch
        keyboard = []
        for p in providers:
            if not p.is_current:
                keyboard.append([InlineKeyboardButton(
                    f"切换到 {p.name}",
                    callback_data=f"switch:{p.id}"
                )])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "\n".join(lines),
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    async def cmd_current(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Current 命令 - 显示当前模型"""
        current = self.cli.get_current_provider()

        if not current:
            await update.message.reply_text("❌ 无法获取当前模型信息")
            return

        providers = self.cli.list_providers()

        message = (
            f"<b>🎯 当前模型</b>\n\n"
            f"名称: <b>{current.name}</b>\n"
            f"ID: <code>{current.id}</code>\n\n"
            f"共 {len(providers)} 个可用模型"
        )

        await update.message.reply_text(message, parse_mode='HTML')

    async def cmd_switch(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Switch 命令 - 切换模型"""
        if not context.args:
            await update.message.reply_text(
                "❌ 请指定要切换的模型\n"
                "用法: /switch <名称> 或 /switch <序号>\n"
                "例如: /switch Kimi\n"
                "      /switch 1",
                parse_mode='HTML'
            )
            return

        identifier = " ".join(context.args)

        # Show "processing" message
        processing_msg = await update.message.reply_text("🔄 正在切换模型...")

        # Perform switch
        success = self.cli.switch_provider(identifier)

        if success:
            current = self.cli.get_current_provider()
            await processing_msg.edit_text(
                f"✅ <b>切换成功!</b>\n\n"
                f"当前模型: <b>{current.name}</b>",
                parse_mode='HTML'
            )
        else:
            await processing_msg.edit_text(
                f"❌ <b>切换失败</b>\n\n"
                f"找不到匹配的模型: <code>{identifier}</code>\n"
                f"使用 /list 查看所有可用模型",
                parse_mode='HTML'
            )

    async def on_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理回调查询（内联键盘按钮点击）"""
        query = update.callback_query
        await query.answer()

        data = query.data

        if data.startswith("switch:"):
            provider_id = data.split(":", 1)[1]

            # Show processing
            await query.edit_message_text("🔄 正在切换模型...")

            # Perform switch
            success = self.cli.switch_provider(provider_id)

            if success:
                current = self.cli.get_current_provider()
                await query.edit_message_text(
                    f"✅ <b>切换成功!</b>\n\n"
                    f"当前模型: <b>{current.name}</b>",
                    parse_mode='HTML'
                )
            else:
                await query.edit_message_text(
                    "❌ <b>切换失败</b>\n\n"
                    "请重试或联系管理员",
                    parse_mode='HTML'
                )

    async def on_error(self, update: Optional[Update], context: ContextTypes.DEFAULT_TYPE):
        """Error handler"""
        logger.error(f"Update {update} caused error {context.error}")

        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ 发生错误，请稍后重试\n"
                f"错误: <code>{str(context.error)[:100]}</code>",
                parse_mode='HTML'
            )

    def run(self):
        """启动 Bot"""
        logger.info("Starting CC Switch Telegram Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not token:
        print("错误: 请设置环境变量 TELEGRAM_BOT_TOKEN")
        print("例如: export TELEGRAM_BOT_TOKEN='your_token_here'")
        sys.exit(1)

    bot = CCSwitchTelegramBot(token)
    bot.run()


if __name__ == "__main__":
    main()
