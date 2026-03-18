# CC Switch Telegram Bot - 安装指南

## 🚀 一键安装（推荐）

打开终端，复制粘贴以下命令：

```bash
curl -fsSL https://raw.githubusercontent.com/JMOKSZ/cc-switch-telegram-bot/main/installer/install.sh | bash
```

安装程序会自动完成：
- ✅ 检查系统环境
- ✅ 安装依赖
- ✅ 配置 Telegram Bot
- ✅ 设置开机自启
- ✅ 创建快捷命令

---

## 📦 手动安装

### 1. 克隆仓库

```bash
cd ~/github
git clone https://github.com/JMOKSZ/cc-switch-telegram-bot.git
cd cc-switch-telegram-bot
```

### 2. 运行安装脚本

```bash
chmod +x installer/install.sh
./installer/install.sh
```

### 3. 按提示配置

- 输入 Telegram Bot Token
- 输入你的 Telegram ID（可选）
- 选择是否开机自启

---

## 🔧 配置 Telegram Bot

### 创建 Bot

1. 在 Telegram 搜索 **@BotFather**
2. 发送 `/newbot`
3. 输入 Bot 名称（如：`CC Switch 控制器`）
4. 输入 Bot 用户名（如：`yourname_cc_bot`，必须以 bot 结尾）
5. **复制获得的 Token**（格式：`123456789:ABCdef...`）

### 获取你的 Telegram ID

1. 在 Telegram 搜索 **@userinfobot**
2. 点击开始
3. 复制显示的 ID（如：`5528268909`）

---

## 🎮 使用方法

### Telegram 命令

| 命令 | 说明 |
|------|------|
| `/start` | 开始使用 |
| `/list` | 列出所有模型（带切换按钮） |
| `/current` | 查看当前模型 |
| `/switch <名称>` | 切换模型（支持模糊匹配） |
| `/switch 1` | 按序号切换 |
| `/help` | 显示帮助 |

### 终端命令

安装完成后，使用 `cc-bot` 命令管理：

```bash
cc-bot start      # 启动 Bot
cc-bot stop       # 停止 Bot
cc-bot restart    # 重启 Bot
cc-bot status     # 查看状态
cc-bot log        # 查看日志
cc-bot config     # 编辑配置
cc-bot uninstall  # 卸载
```

### 菜单栏应用（可选）

安装 `rumps` 获得菜单栏图标：

```bash
pip3 install rumps
~/.cc-switch-telegram-bot/start-menu-bar.sh
```

---

## 📁 安装目录结构

```
~/.cc-switch-telegram-bot/
├── venv/                   # Python 虚拟环境
├── src/                    # 源代码
│   ├── telegram_bot.py    # Telegram Bot
│   ├── cc_switch_cli.py   # CLI 工具
│   └── menu_bar_app.py    # 菜单栏应用
├── .env                    # 配置文件
├── launch.sh               # 启动脚本
├── logs/                   # 日志目录
│   ├── bot.log
│   └── bot.error.log
└── ...
```

---

## 🔒 安全配置

### 只允许特定用户使用

编辑配置文件：

```bash
cc-bot config
```

修改 `ALLOWED_USERS`：

```env
ALLOWED_USERS=5528268909,123456789
```

多个用户用逗号分隔，留空允许所有人。

---

## 🔄 多机器部署

### Mac Studio 部署步骤

1. **确保 Mac Studio 已安装：**
   - CC Switch
   - Claude Code
   - Python 3.9+

2. **运行安装脚本：**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/JMOKSZ/cc-switch-telegram-bot/main/installer/install.sh | bash
   ```

3. **使用相同的 Bot Token 或创建新 Bot**

4. **（可选）使用相同的配置文件：**
   ```bash
   # 从 Mac Mini 复制配置到 Mac Studio
   scp ~/.cc-switch-telegram-bot/.env user@mac-studio:~/.cc-switch-telegram-bot/
   ```

---

## ❓ 故障排查

### Bot 无法启动

```bash
# 检查日志
cat ~/.cc-switch-telegram-bot/logs/bot.log

# 检查配置
cat ~/.cc-switch-telegram-bot/.env

# 手动测试
python3 ~/.cc-switch-telegram-bot/src/telegram_bot.py
```

### 切换模型失败

```bash
# 检查 CC Switch 数据库
sqlite3 ~/.cc-switch/cc-switch.db "SELECT name, is_current FROM providers WHERE app_type='claude'"

# 手动测试 CLI
python3 ~/.cc-switch-telegram-bot/src/cc_switch_cli.py list
```

### 权限被拒绝

```bash
# 确保文件权限正确
chmod +x ~/.cc-switch-telegram-bot/launch.sh
chmod +x ~/bin/cc-bot
```

---

## 🗑️ 卸载

```bash
cc-bot uninstall
```

或手动删除：

```bash
# 停止 Bot
pkill -f telegram_bot.py

# 卸载开机自启
launchctl unload ~/Library/LaunchAgents/com.ccswitch.telegrambot.plist

# 删除文件
rm -rf ~/.cc-switch-telegram-bot
rm -f ~/Library/LaunchAgents/com.ccswitch.telegrambot.plist
rm -f ~/bin/cc-bot
```

---

## 💡 使用技巧

### 快速切换模型

在 Telegram 中发送：
```
/switch Kimi    # 切换到 Kimi
/switch 2       # 切换到第2个模型
/switch Claude  # 切换到 Claude
```

### 查看切换是否成功

1. **新开一个 Claude Code 对话**
   ```bash
   claude --new
   ```

2. **询问当前模型**
   ```
   你是什么模型？
   ```

3. **或查看配置**
   ```bash
   cat ~/.claude/settings.json | grep BASE_URL
   ```

---

## 📞 支持

- **GitHub Issues**: https://github.com/JMOKSZ/cc-switch-telegram-bot/issues
- **作者**: Cii Mok

---

## 📝 更新日志

### v1.0.0
- 初始版本
- 支持 Telegram Bot 远程控制
- 支持菜单栏应用
- 一键安装脚本
