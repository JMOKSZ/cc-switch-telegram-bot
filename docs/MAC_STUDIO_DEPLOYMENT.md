# Mac Studio 部署指南

本指南帮助你在 Mac Studio (Stu Mok) 上部署 CC Switch Telegram Bot。

## 📋 部署前准备

### 1. 确认 Mac Studio 环境

在 Mac Studio 上打开终端，执行：

```bash
# 检查 macOS 版本
sw_vers -productVersion
# 要求: 11.0 (Big Sur) 或更高

# 检查 Python
python3 --version
# 要求: 3.9 或更高

# 检查 CC Switch
ls -la ~/.cc-switch/
# 应该显示 cc-switch.db 等文件

# 检查 Claude Code
which claude
claude --version
```

### 2. 确认网络环境

```bash
# 检查能否访问 GitHub
ping -c 3 github.com

# 检查能否访问 Telegram API
curl -I https://api.telegram.org
```

---

## 🚀 部署方案

### 方案 A: 独立部署（推荐）

Mac Studio 使用独立的 Telegram Bot，单独控制。

**优点：**
- 两台机器互不干扰
- 可以分别切换不同模型
- 故障隔离

**步骤：**

#### 步骤 1: 下载安装脚本

在 Mac Studio 上：

```bash
# 创建项目目录
mkdir -p ~/github
cd ~/github

# 下载安装脚本
curl -fsSL -o install.sh \
  https://raw.githubusercontent.com/JMOKSZ/cc-switch-telegram-bot/main/installer/install.sh

# 添加执行权限
chmod +x install.sh
```

#### 步骤 2: 创建新的 Telegram Bot

1. 在 Telegram 搜索 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot`
3. 输入 Bot 名称：`CC Switch Studio`
4. 输入用户名：`yourname_studio_bot`（必须以 bot 结尾）
5. **保存 Token**（格式：`123456789:ABCdefGHI...`）

#### 步骤 3: 运行安装

```bash
./install.sh
```

按提示操作：
- 输入 Bot Token
- 输入你的 Telegram ID（只允许你使用）
- 选择开机自启：`y`

#### 步骤 4: 验证安装

```bash
# 检查 Bot 状态
cc-bot status

# 应该显示: ✓ Bot 运行中
```

在 Telegram 中搜索你的新 Bot，发送：
```
/start
/list
/switch 2
```

---

### 方案 B: 配置同步（高级）

Mac Studio 使用与 Mac Mini **相同的 Bot Token**，统一控制。

**优点：**
- 一个 Bot 控制多台机器
- 统一管理

**缺点：**
- 切换时会同时影响两台机器
- 需要手动同步配置

**步骤：**

#### 步骤 1: 从 Mac Mini 复制配置

**在 Mac Mini 上：**

```bash
# 压缩配置文件
tar czf ~/cc-studio-deploy.tar.gz \
  -C ~/.cc-switch-telegram-bot \
  .env src/ venv/

# 传输到 Mac Studio
# 方法 1: Airdrop
# 方法 2: scp
scp ~/cc-studio-deploy.tar.gz stu-mok:~/

# 方法 3: 共享文件夹
# 方法 4: U盘
```

**或使用共享记忆仓库：**

```bash
# 如果已配置 openclaw-memory
cp ~/.cc-switch-telegram-bot/.env \
   ~/github/openclaw-memory/config/cc-bot-studio.env
```

#### 步骤 2: 在 Mac Studio 安装

```bash
# 创建目录
mkdir -p ~/.cc-switch-telegram-bot
cd ~/.cc-switch-telegram-bot

# 解压配置
tar xzf ~/cc-studio-deploy.tar.gz

# 安装依赖（如果 venv 不包含）
source venv/bin/activate
pip install -r requirements.txt

# 启动 Bot
cc-bot start
```

#### 步骤 3: 创建 LaunchAgent（开机自启）

```bash
cat > ~/Library/LaunchAgents/com.ccswitch.telegrambot.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ccswitch.telegrambot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/mominjian/.cc-switch-telegram-bot/launch.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/mominjian/.cc-switch-telegram-bot</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/mominjian/.cc-switch-telegram-bot/logs/bot.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/mominjian/.cc-switch-telegram-bot/logs/bot.error.log</string>
</dict>
</plist>
EOF

# 加载
launchctl load ~/Library/LaunchAgents/com.ccswitch.telegrambot.plist
```

---

## ⚙️ 配置优化（Mac Studio）

### 1. 配置 CC Switch 模型

确保 Mac Studio 的 CC Switch 已配置好模型：

```bash
# 检查配置
sqlite3 ~/.cc-switch/cc-switch.db \
  "SELECT name, is_current FROM providers WHERE app_type='claude'"

# 应该显示类似：
# Kimi For Coding|1
# Claude|0
# GLM|0
# Volcengine|0
```

如果模型不同，需要同步 Mac Mini 的配置：

```bash
# 从 Mac Mini 复制 CC Switch 数据库
scp mac-mini:~/.cc-switch/cc-switch.db ~/.cc-switch/
```

### 2. 配置环境变量

编辑配置文件：

```bash
cc-bot config
```

或：

```bash
open -e ~/.cc-switch-telegram-bot/.env
```

### 3. 配置菜单栏应用（可选）

```bash
# 安装 rumps
pip3 install rumps

# 启动菜单栏
~/.cc-switch-telegram-bot/start-menu-bar.sh
```

---

## 🧪 测试验证

### 测试 1: CLI 工具

```bash
# 列出模型
python3 ~/.cc-switch-telegram-bot/src/cc_switch_cli.py list

# 查看当前
python3 ~/.cc-switch-telegram-bot/src/cc_switch_cli.py current

# 切换测试
python3 ~/.cc-switch-telegram-bot/src/cc_switch_cli.py switch Claude
```

### 测试 2: Telegram Bot

在 Telegram 中：

```
/start
# 应显示: 你好 [你的名字]!

/list
# 应显示: 4 个模型列表

/switch 2
# 应显示: 已切换到: Claude

/current
# 应显示: 当前模型: Claude
```

### 测试 3: Claude Code 验证

```bash
# 新开 Claude Code
claude --new

# 询问当前模型
# 你: 你是什么模型？
# Claude: 应该回答 Claude 相关信息

# 切换回 Kimi
# 在 Telegram 发送: /switch Kimi

# 再开新对话
claude --new
# 你: 你是什么模型？
# 应该回答 Kimi 相关信息
```

### 测试 4: 重启后自动启动

```bash
# 重启 Mac Studio
sudo reboot

# 重启后检查
cc-bot status
# 应该显示: ✓ Bot 运行中
```

---

## 🔧 故障排查

### 问题 1: Bot 无法启动

```bash
# 查看日志
tail -50 ~/.cc-switch-telegram-bot/logs/bot.log

# 常见问题：
# - Token 无效
# - 权限不足
# - 端口被占用

# 手动测试
source ~/.cc-switch-telegram-bot/venv/bin/activate
cd ~/.cc-switch-telegram-bot
export $(cat .env | grep -v '^#' | xargs)
python3 src/telegram_bot.py
```

### 问题 2: 无法切换模型

```bash
# 检查 CC Switch 数据库权限
ls -la ~/.cc-switch/cc-switch.db

# 修复权限
chmod 644 ~/.cc-switch/cc-switch.db

# 检查数据库是否被锁定
lsof ~/.cc-switch/cc-switch.db
```

### 问题 3: 与 Mac Mini 冲突

如果两台机器使用相同 Token：

```bash
# 在 Mac Studio 创建新 Bot
# 编辑配置
cc-bot config

# 更新 Token
# 重启 Bot
cc-bot restart
```

### 问题 4: Python 版本问题

```bash
# 检查版本
python3 --version

# 如果低于 3.9
brew install python3

# 重新创建虚拟环境
rm -rf ~/.cc-switch-telegram-bot/venv
cd ~/.cc-switch-telegram-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📝 部署检查清单

部署完成后，确认以下项目：

- [ ] Python 3.9+ 已安装
- [ ] CC Switch 已安装并配置
- [ ] Claude Code 已安装
- [ ] Telegram Bot 已创建
- [ ] 安装脚本运行成功
- [ ] Bot 正在运行 (`cc-bot status`)
- [ ] Telegram 命令正常响应
- [ ] 模型切换功能正常
- [ ] 开机自启已配置
- [ ] 日志文件正常写入
- [ ] 菜单栏应用（可选）

---

## 🔄 与 Mac Mini 的协作

### 场景 1: 各自独立

```
Mac Mini (Cii)          Mac Studio (Stu)
   ↓                        ↓
Bot: @CiiBot            Bot: @StuBot
   ↓                        ↓
模型: Kimi               模型: Claude
   ↓                        ↓
各自独立控制            各自独立控制
```

### 场景 2: 配置同步

定期同步模型配置：

```bash
# 从 Mac Mini 导出配置
ssh mac-mini 'tar czf - ~/.cc-switch/cc-switch.db' | tar xzf - -C ~/

# 重启 CC Switch 应用
# 重新打开即可生效
```

---

## 💡 使用技巧

### 技巧 1: 快捷切换别名

添加到 `~/.zshrc`：

```bash
# 快速切换模型
alias cc-kimi='python3 ~/.cc-switch-telegram-bot/src/cc_switch_cli.py switch Kimi'
alias cc-claude='python3 ~/.cc-switch-telegram-bot/src/cc_switch_cli.py switch Claude'
alias cc-glm='python3 ~/.cc-switch-telegram-bot/src/cc_switch_cli.py switch GLM'
alias cc-volc='python3 ~/.cc-switch-telegram-bot/src/cc_switch_cli.py switch Volcengine'
```

### 技巧 2: 查看当前模型

```bash
# 添加到提示符
export PS1='$(python3 ~/.cc-switch-telegram-bot/src/cc_switch_cli.py current 2>/dev/null | grep "当前模型" | cut -d: -f2 | xargs) $ '
```

### 技巧 3: 与 Claude Code 集成

创建脚本 `~/bin/claude-with-model`：

```bash
#!/bin/bash
MODEL=$1
if [ -n "$MODEL" ]; then
    cc-bot switch "$MODEL"
fi
claude --new
```

使用：
```bash
claude-with-model Claude
```

---

## 📞 支持

遇到问题？

1. 查看日志：`cc-bot log`
2. 检查配置：`cat ~/.cc-switch-telegram-bot/.env`
3. GitHub Issues：https://github.com/JMOKSZ/cc-switch-telegram-bot/issues
4. 参考 Mac Mini 的配置对比

---

**祝你部署顺利！** 🚀
