# CC Switch Telegram Bot

通过 Telegram 远程控制 CC Switch，切换 Claude Code 使用的 AI 模型。

## 功能

- 📱 **Telegram 远程控制** - 随时随地切换模型
- 🎯 **快速切换** - 支持名称、序号、ID 多种方式
- 📋 **实时列表** - 查看所有可用模型
- ✅ **当前状态** - 随时查看正在使用的模型

## 适用场景

- 在外面用手机远程切换家里的 Mac 上的模型
- 不想打开 CC Switch GUI 时快速切换
- 自动化脚本集成

## 支持的模型

根据你的 CC Switch 配置，目前支持：
1. **Kimi For Coding** - Kimi 编程专用
2. **Claude** - Claude 官方
3. **GLM** - 智谱 GLM
4. **Volcengine** - 火山引擎

## 快速开始

### 1. 安装依赖

```bash
cd ~/github/cc-switch-telegram-bot
pip3 install -r requirements.txt
```

### 2. 配置 Telegram Bot

1. 在 Telegram 中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新 Bot
3. 复制 Bot Token
4. 配置环境变量：

```bash
cp .env.example .env
# 编辑 .env 填入你的 Token
export TELEGRAM_BOT_TOKEN="your_token_here"
```

### 3. 启动 Bot

```bash
python src/telegram_bot.py
```

### 4. 在 Telegram 中使用

向你的 Bot 发送命令：

```
/start - 开始使用
/list - 列出所有模型
/current - 查看当前模型
/switch Kimi - 切换到 Kimi
/switch 1 - 切换到第1个模型
/help - 查看帮助
```

## CLI 独立使用

即使不用 Telegram，你也可以单独使用 CLI：

```bash
# 列出所有模型
python src/cc_switch_cli.py list

# 查看当前模型
python src/cc_switch_cli.py current

# 切换模型
python src/cc_switch_cli.py switch Kimi
python src/cc_switch_cli.py switch 1
python src/cc_switch_cli.py switch "Claude"
```

## 系统要求

- macOS (CC Switch 仅支持 Mac)
- Python 3.9+
- 已安装 CC Switch 并配置好模型

## 工作原理

1. Bot 直接读取 `~/.cc-switch/cc-switch.db` SQLite 数据库
2. 修改 `providers` 表的 `is_current` 字段
3. 同时更新 `settings.json` 的 `currentProviderClaude`
4. CC Switch 会自动检测到配置变化

## 安全提示

⚠️ **Token 保密** - 不要将 `TELEGRAM_BOT_TOKEN` 提交到 Git

## 后台运行

使用 `nohup` 或 `screen` 让 Bot 在后台运行：

```bash
# 使用 nohup
nohup python src/telegram_bot.py > bot.log 2>&1 &

# 或使用 screen
screen -S cc-switch-bot
python src/telegram_bot.py
# Ctrl+A, D 分离
```

## 故障排查

### Bot 无法启动
```bash
# 检查 Token 是否正确
echo $TELEGRAM_BOT_TOKEN

# 检查依赖
pip3 list | grep telegram
```

### 切换模型失败
```bash
# 检查 CC Switch 数据库权限
ls -la ~/.cc-switch/cc-switch.db

# 手动测试 CLI
python src/cc_switch_cli.py list
```

## License

MIT
