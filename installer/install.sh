#!/bin/bash
# CC Switch Telegram Bot - 一键安装脚本
# 适用于 macOS

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置
APP_NAME="CC Switch Remote"
INSTALL_DIR="$HOME/.cc-switch-telegram-bot"
LAUNCH_AGENT_PLIST="$HOME/Library/LaunchAgents/com.ccswitch.telegrambot.plist"
REPO_URL="https://github.com/JMOKSZ/cc-switch-telegram-bot"

print_header() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}        ${GREEN}CC Switch Telegram Bot 一键安装器${NC}                ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}              ${YELLOW}远程控制你的 Claude Code 模型${NC}              ${CYAN}║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}[步骤 $1]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# 检查 macOS
check_macos() {
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "此安装程序仅适用于 macOS"
        exit 1
    fi
    print_success "检测到 macOS 系统"
}

# 检查 CC Switch
check_cc_switch() {
    print_step "1" "检查 CC Switch 安装"

    if [ ! -d "$HOME/.cc-switch" ]; then
        print_error "未检测到 CC Switch"
        echo ""
        echo "请先安装 CC Switch："
        echo "  https://www.ccswitch.com/"
        echo ""
        exit 1
    fi

    # 检查是否有 Claude 配置
    local provider_count=$(sqlite3 "$HOME/.cc-switch/cc-switch.db" "SELECT COUNT(*) FROM providers WHERE app_type='claude'" 2>/dev/null || echo "0")

    if [ "$provider_count" -eq 0 ]; then
        print_error "CC Switch 中没有配置 Claude Code 模型"
        echo ""
        echo "请先在 CC Switch 中至少添加一个模型"
        exit 1
    fi

    print_success "检测到 CC Switch，已配置 $provider_count 个模型"
}

# 检查 Python
check_python() {
    print_step "2" "检查 Python 环境"

    if ! command -v python3 &> /dev/null; then
        print_error "未安装 Python3"
        echo ""
        echo "请安装 Python 3.9 或更高版本："
        echo "  brew install python3"
        exit 1
    fi

    local python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Python 版本: $python_version"
}

# 安装依赖
install_dependencies() {
    print_step "3" "安装依赖"

    # 创建虚拟环境
    if [ ! -d "$INSTALL_DIR/venv" ]; then
        python3 -m venv "$INSTALL_DIR/venv"
        print_success "创建虚拟环境"
    fi

    # 激活虚拟环境并安装依赖
    source "$INSTALL_DIR/venv/bin/activate"
    pip install --upgrade pip -q
    pip install python-telegram-bot httpx python-dotenv -q

    print_success "依赖安装完成"
}

# 下载应用文件
download_app() {
    print_step "4" "下载应用程序"

    # 创建安装目录
    mkdir -p "$INSTALL_DIR"

    # 检查当前目录是否有源码
    if [ -f "src/telegram_bot.py" ]; then
        # 本地安装（开发模式）
        cp -r src "$INSTALL_DIR/"
        cp start_bot.sh "$INSTALL_DIR/"
        print_success "从本地复制应用文件"
    else
        # 从 GitHub 下载
        print_warning "从 GitHub 下载最新版本..."
        curl -fsSL "$REPO_URL/archive/refs/heads/main.tar.gz" | tar -xz -C /tmp/
        cp -r "/tmp/cc-switch-telegram-bot-main/src" "$INSTALL_DIR/"
        cp "/tmp/cc-switch-telegram-bot-main/start_bot.sh" "$INSTALL_DIR/"
        rm -rf "/tmp/cc-switch-telegram-bot-main"
        print_success "下载完成"
    fi
}

# 交互式配置
interactive_config() {
    print_step "5" "配置 Telegram Bot"
    echo ""

    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "要创建 Telegram Bot，请按以下步骤操作："
    echo ""
    echo "1. 在 Telegram 中搜索 @BotFather"
    echo "2. 发送 /newbot"
    echo "3. 输入 Bot 名称（如：CC Switch 控制器）"
    echo "4. 输入 Bot 用户名（如：yourname_cc_bot）"
    echo "5. 复制获得的 Token"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # 获取 Token
    local token=""
    while [ -z "$token" ]; do
        read -p "请输入 Bot Token: " token
        if [ -z "$token" ]; then
            print_error "Token 不能为空"
        fi
    done

    # 验证 Token
    echo ""
    echo "正在验证 Token..."
    local bot_info=$(curl -s "https://api.telegram.org/bot$token/getMe")

    if echo "$bot_info" | grep -q '"ok":true'; then
        local bot_name=$(echo "$bot_info" | grep -o '"first_name":"[^"]*"' | cut -d'"' -f4)
        local bot_username=$(echo "$bot_info" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
        print_success "验证成功！Bot: $bot_name (@$bot_username)"
    else
        print_error "Token 无效，请检查"
        exit 1
    fi

    # 获取用户 ID
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "为了安全起见，建议只允许你的账号使用此 Bot"
    echo ""
    echo "获取你的 Telegram ID："
    echo "1. 在 Telegram 中搜索 @userinfobot"
    echo "2. 点击开始，它会显示你的 ID"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    read -p "请输入你的 Telegram ID (留空允许所有人): " user_id

    # 创建配置文件
    cat > "$INSTALL_DIR/.env" << EOF
# CC Switch Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=$token
ALLOWED_USERS=${user_id:-}
EOF

    print_success "配置已保存"
}

# 创建启动脚本
create_launcher() {
    print_step "6" "创建启动器"

    cat > "$INSTALL_DIR/launch.sh" << 'EOF'
#!/bin/bash
# CC Switch Telegram Bot 启动脚本

cd "$(dirname "$0")"
source venv/bin/activate
export $(cat .env | grep -v '^#' | xargs)
python3 src/telegram_bot.py
EOF

    chmod +x "$INSTALL_DIR/launch.sh"

    # 创建菜单栏应用启动器（使用 Automator）
    cat > "$INSTALL_DIR/start-menu-bar.sh" << 'EOF'
#!/bin/bash
# 启动菜单栏应用

cd "$(dirname "$0")"
source venv/bin/activate
export $(cat .env | grep -v '^#' | xargs)

# 使用 Python 启动简单的菜单栏
python3 << 'PYEOF'
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.menu_bar_app import MenuBarApp
    app = MenuBarApp()
    app.run()
except ImportError:
    # 如果没有菜单栏支持，直接启动 bot
    os.system("python3 src/telegram_bot.py &")
PYEOF
EOF

    chmod +x "$INSTALL_DIR/start-menu-bar.sh"

    print_success "启动器已创建"
}

# 配置开机自启
setup_autostart() {
    print_step "7" "配置开机自启"
    echo ""

    read -p "是否设置为开机自动启动? (y/n): " autostart

    if [[ $autostart =~ ^[Yy]$ ]]; then
        cat > "$LAUNCH_AGENT_PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ccswitch.telegrambot</string>
    <key>ProgramArguments</key>
    <array>
        <string>$INSTALL_DIR/launch.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$INSTALL_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$INSTALL_DIR/logs/bot.log</string>
    <key>StandardErrorPath</key>
    <string>$INSTALL_DIR/logs/bot.error.log</string>
</dict>
</plist>
EOF

        mkdir -p "$INSTALL_DIR/logs"
        launchctl load "$LAUNCH_AGENT_PLIST" 2>/dev/null || true

        print_success "已设置为开机自启"
    else
        print_warning "跳过开机自启配置"
    fi
}

# 创建快捷命令
create_shortcuts() {
    print_step "8" "创建快捷命令"

    # 创建 bin 目录
    mkdir -p "$HOME/bin"

    # 创建 cc-bot 命令
    cat > "$HOME/bin/cc-bot" << EOF
#!/bin/bash
# CC Switch Telegram Bot 管理命令

INSTALL_DIR="$INSTALL_DIR"

show_help() {
    echo "CC Switch Telegram Bot 管理工具"
    echo ""
    echo "用法: cc-bot <命令>"
    echo ""
    echo "命令:"
    echo "  start      启动 Bot"
    echo "  stop       停止 Bot"
    echo "  restart    重启 Bot"
    echo "  status     查看状态"
    echo "  log        查看日志"
    echo "  config     编辑配置"
    echo "  uninstall  卸载"
    echo ""
}

case "\$1" in
    start)
        cd "\$INSTALL_DIR"
        nohup ./launch.sh > logs/bot.log 2>&1 &
        echo "Bot 已启动"
        ;;
    stop)
        pkill -f "telegram_bot.py" 2>/dev/null
        echo "Bot 已停止"
        ;;
    restart)
        pkill -f "telegram_bot.py" 2>/dev/null
        sleep 1
        cd "\$INSTALL_DIR"
        nohup ./launch.sh > logs/bot.log 2>&1 &
        echo "Bot 已重启"
        ;;
    status)
        if pgrep -f "telegram_bot.py" > /dev/null; then
            echo "✓ Bot 运行中"
        else
            echo "✗ Bot 未运行"
        fi
        ;;
    log)
        tail -f "\$INSTALL_DIR/logs/bot.log"
        ;;
    config)
        open -e "\$INSTALL_DIR/.env"
        ;;
    uninstall)
        read -p "确定要卸载吗? (y/n): " confirm
        if [[ \$confirm =~ ^[Yy]$ ]]; then
            pkill -f "telegram_bot.py" 2>/dev/null
            launchctl unload "$LAUNCH_AGENT_PLIST" 2>/dev/null
            rm -rf "\$INSTALL_DIR"
            rm -f "$LAUNCH_AGENT_PLIST"
            rm -f "$HOME/bin/cc-bot"
            echo "已卸载"
        fi
        ;;
    *)
        show_help
        ;;
esac
EOF

    chmod +x "$HOME/bin/cc-bot"

    # 添加到 PATH
    if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
        echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.zshrc"
        echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.bash_profile"
    fi

    print_success "快捷命令已创建: cc-bot"
}

# 启动 Bot
start_bot() {
    print_step "9" "启动 Bot"
    echo ""

    cd "$INSTALL_DIR"
    mkdir -p logs
    nohup ./launch.sh > logs/bot.log 2>&1 &
    sleep 2

    if pgrep -f "telegram_bot.py" > /dev/null; then
        print_success "Bot 启动成功！"
    else
        print_error "启动失败，请检查日志: $INSTALL_DIR/logs/bot.log"
    fi
}

# 完成安装
finish() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}              ${CYAN}🎉 安装完成！${NC}                              ${GREEN}║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "使用方法:"
    echo ""
    echo "  1. 在 Telegram 中搜索你的 Bot"
    echo "     发送 /start 开始使用"
    echo ""
    echo "  2. 常用命令:"
    echo "     cc-bot start    启动 Bot"
    echo "     cc-bot stop     停止 Bot"
    echo "     cc-bot status   查看状态"
    echo "     cc-bot log      查看日志"
    echo ""
    echo "  3. 配置文件:"
    echo "     $INSTALL_DIR/.env"
    echo ""
    echo "  4. 日志文件:"
    echo "     $INSTALL_DIR/logs/bot.log"
    echo ""
    echo -e "${YELLOW}提示: 新开一个终端窗口才能使用 cc-bot 命令${NC}"
    echo ""
}

# 主函数
main() {
    print_header

    check_macos
    check_cc_switch
    check_python

    echo ""
    read -p "按回车开始安装..."
    echo ""

    install_dependencies
    download_app
    interactive_config
    create_launcher
    setup_autostart
    create_shortcuts
    start_bot

    finish
}

# 运行
main "$@"
