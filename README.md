# CC Switch Telegram Bot

[![Platform](https://img.shields.io/badge/platform-macOS-blue)](https://github.com/JMOKSZ/cc-switch-telegram-bot)
[![Python](https://img.shields.io/badge/python-3.9+-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

🤖 **通过 Telegram 远程控制你的 CC Switch，随时切换 Claude Code 使用的 AI 模型**

---

## ✨ 功能特性

- 📱 **Telegram 远程控制** - 随时随地用手机切换模型
- 🖥️ **菜单栏应用** - 从 macOS 菜单栏快速控制
- 🔒 **用户权限管理** - 只允许特定用户使用
- 🚀 **一键安装** - 自动配置，开箱即用
- 🔄 **多机器支持** - 可在多台 Mac 上部署
- 📝 **完整日志** - 方便排查问题

---

## 🚀 快速开始

### 一键安装（推荐）

```bash
curl -fsSL https://raw.githubusercontent.com/JMOKSZ/cc-switch-telegram-bot/main/installer/install.sh | bash
```

### 手动安装

```bash
git clone https://github.com/JMOKSZ/cc-switch-telegram-bot.git
cd cc-switch-telegram-bot
./installer/install.sh
```

---

## 📱 使用方法

### Telegram Bot 命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/start` | 开始使用 | - |
| `/list` | 列出所有模型（带切换按钮） | - |
| `/current` | 查看当前模型 | - |
| `/switch` | 切换模型 | `/switch Kimi` |
| `/help` | 显示帮助 | - |

### 终端命令

```bash
cc-bot start      # 启动 Bot
cc-bot stop       # 停止 Bot
cc-bot restart    # 重启 Bot
cc-bot status     # 查看状态
cc-bot log        # 查看日志
cc-bot config     # 编辑配置
cc-bot uninstall  # 卸载
```

---

## 🎬 使用场景

### 场景 1：外出时切换模型
```
你在外面使用手机 → 打开 Telegram → /switch Claude
                              ↓
家里 Mac 上的 Claude Code → 新对话自动使用 Claude
```

### 场景 2：对比不同模型效果
```
在 Telegram 快速切换 → 在 Claude Code 测试同一个问题
                              ↓
比较 Kimi / Claude / GLM 的回答差异
```

### 场景 3：多台 Mac 统一管理
```
Mac Mini: 运行 Bot
Mac Studio: 同样被控制
                ↓
一个 Telegram Bot 控制多台机器
```

---

## 📦 系统要求

- **macOS** 11.0 或更高版本
- **CC Switch** 已安装并配置
- **Claude Code** 已安装
- **Python** 3.9 或更高版本
- **Telegram** 账号

---

## 🖥️ 菜单栏应用

安装 `rumps` 获得更好的体验：

```bash
pip3 install rumps
~/.cc-switch-telegram-bot/start-menu-bar.sh
```

菜单栏功能：
- 🟢/🔴 实时显示 Bot 状态
- 一键启动/停止/重启
- 查看当前模型
- 快速查看日志

---

## 🔒 安全性

- ✅ **Token 本地存储** - 不上传到任何服务器
- ✅ **用户白名单** - 可限制只允许特定用户使用
- ✅ **只读操作** - 不会修改 CC Switch 以外的配置

---

## 🔄 多机器部署

在另一台 Mac（如 Mac Studio）上部署：

```bash
# 同样的安装命令
curl -fsSL https://raw.githubusercontent.com/JMOKSZ/cc-switch-telegram-bot/main/installer/install.sh | bash

# 可以选择：
# 1. 使用同一个 Bot Token（统一控制）
# 2. 创建新的 Bot（独立控制）
```

---

## 📁 项目结构

```
cc-switch-telegram-bot/
├── src/
│   ├── telegram_bot.py      # Telegram Bot 主程序
│   ├── cc_switch_cli.py     # CLI 工具
│   └── menu_bar_app.py      # 菜单栏应用
├── installer/
│   └── install.sh           # 一键安装脚本
├── app/
│   └── create_app.sh        # macOS App Bundle 创建器
├── docs/
│   └── INSTALL_GUIDE.md     # 详细安装指南
└── README.md                # 本文件
```

---

## 🛠️ 故障排查

### Bot 无法启动

```bash
# 查看日志
tail -f ~/.cc-switch-telegram-bot/logs/bot.log

# 检查配置
cat ~/.cc-switch-telegram-bot/.env
```

### 切换模型失败

```bash
# 检查 CC Switch 数据库
sqlite3 ~/.cc-switch/cc-switch.db "SELECT name, is_current FROM providers"

# 手动测试
cc-bot status
python3 ~/.cc-switch-telegram-bot/src/cc_switch_cli.py current
```

---

## 📝 工作原理

```
┌─────────────────┐     ┌─────────────┐     ┌─────────────────┐
│  Telegram Bot   │────▶│ CC Switch   │────▶│  Claude Code    │
│  (你的手机)      │     │  数据库      │     │  (新对话生效)    │
└─────────────────┘     └─────────────┘     └─────────────────┘
         │                                               ▲
         │     修改配置后，Claude Code 读取新配置           │
         └───────────────────────────────────────────────┘
```

---

## 🗺️ 路线图

- [x] 基础 Telegram Bot
- [x] CLI 工具
- [x] 菜单栏应用
- [x] 一键安装脚本
- [x] 用户权限管理
- [ ] 多机器同步
- [ ] 切换历史记录
- [ ] Web 管理界面
- [ ] 自动模型推荐

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 💖 感谢

- [CC Switch](https://www.ccswitch.com/) - 优秀的 Claude Code 模型管理工具
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot 框架

---

**开始远程控制你的 Claude Code 吧！** 🚀
