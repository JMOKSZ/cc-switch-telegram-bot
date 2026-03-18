#!/bin/bash
# Mac Studio 快速部署脚本
# 一键部署 CC Switch Telegram Bot 到 Mac Studio

set -e

APP_NAME="CC Switch Studio"
INSTALL_DIR="$HOME/.cc-switch-telegram-bot"
REPO_URL="https://github.com/JMOKSZ/cc-switch-telegram-bot"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}     ${GREEN}CC Switch Telegram Bot - Mac Studio 部署${NC}           ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}              ${YELLOW}Stu Mok 快速安装程序${NC}                      ${CYAN}║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}[$1]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 检查环境
check_environment() {
    print_step "检查" "系统环境"

    # 检查 macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        echo "错误: 此脚本仅适用于 macOS"
        exit 1
    fi

    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        echo "错误: 未安装 Python3"
        echo "请运行: brew install python3"
        exit 1
    fi

    # 检查 CC Switch
    if [ ! -d "$HOME/.cc-switch" ]; then
        echo "错误: 未检测到 CC Switch"
        echo "请先安装 CC Switch"
        exit 1
    fi

    print_success "环境检查通过"
}

# 选择部署模式
select_mode() {
    echo ""
    echo "请选择部署模式:"
    echo ""
    echo "  1) 独立部署 - 创建新的 Telegram Bot (推荐)"
    echo "     Mac Studio 有独立的 Bot，与 Mac Mini 互不干扰"
    echo ""
    echo "  2) 配置同步 - 使用 Mac Mini 的配置"
    echo "     从 Mac Mini 复制配置"
    echo ""
    read -p "请选择 (1 或 2): " mode

    if [ "$mode" != "1" ] && [ "$mode" != "2" ]; then
        echo "无效选择，默认使用独立部署"
        mode="1"
    fi
}

# 独立部署
standalone_deploy() {
    print_step "部署" "独立模式"
    echo ""

    # 下载安装脚本
    echo "下载安装脚本..."
    curl -fsSL -o /tmp/install.sh "$REPO_URL/raw/main/installer/install.sh"
    chmod +x /tmp/install.sh

    # 运行安装
    echo ""
    echo "开始安装..."
    /tmp/install.sh

    print_success "独立部署完成"
}

# 配置同步部署
sync_deploy() {
    print_step "部署" "配置同步模式"
    echo ""

    echo "此模式需要从 Mac Mini 复制配置"
    echo ""
    echo "请在 Mac Mini 上运行以下命令:"
    echo ""
    echo -e "${CYAN}  tar czf ~/cc-studio-config.tar.gz -C ~/.cc-switch-telegram-bot .env${NC}"
    echo ""
    echo "然后通过 Airdrop/SCP/U盘 复制到 Mac Studio 的 ~/ 目录"
    echo ""
    read -p "配置已复制? (y/n): " copied

    if [[ ! $copied =~ ^[Yy]$ ]]; then
        echo "请先复制配置后再运行"
        exit 1
    fi

    if [ ! -f "$HOME/cc-studio-config.tar.gz" ]; then
        print_warning "未找到配置文件"
        echo "将使用独立部署模式"
        standalone_deploy
        return
    fi

    # 创建目录
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"

    # 解压配置
    echo "解压配置..."
    tar xzf "$HOME/cc-studio-config.tar.gz"

    # 创建虚拟环境
    echo "创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate

    # 安装依赖
    echo "安装依赖..."
    pip install -q python-telegram-bot httpx python-dotenv

    # 创建启动脚本
    cat > "$INSTALL_DIR/launch.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export $(cat .env | grep -v '^#' | xargs)
python3 src/telegram_bot.py
EOF
    chmod +x "$INSTALL_DIR/launch.sh"

    # 创建 cc-bot 命令
    mkdir -p "$HOME/bin"
    cat > "$HOME/bin/cc-bot" << EOF
#!/bin/bash
INSTALL_DIR="$INSTALL_DIR"
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
    *)
        echo "用法: cc-bot {start|stop|restart|status|log|config}"
        ;;
esac
EOF
    chmod +x "$HOME/bin/cc-bot"

    # 添加 PATH
    if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
        echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.zshrc"
    fi

    # 启动 Bot
    echo "启动 Bot..."
    mkdir -p logs
    cd "$INSTALL_DIR"
    nohup ./launch.sh > logs/bot.log 2>&1 &

    print_success "配置同步完成"
}

# 完成提示
finish() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}              ${CYAN}🎉 部署完成！${NC}                              ${GREEN}║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    if [ "$mode" == "1" ]; then
        echo "你的 Mac Studio 现在有独立的 Telegram Bot"
        echo ""
        echo "使用方法:"
        echo "  1. 在 Telegram 中搜索你创建的 Bot"
        echo "  2. 发送 /start 开始使用"
        echo "  3. 使用 /switch 命令切换模型"
        echo ""
    else
        echo "Mac Studio 已与 Mac Mini 配置同步"
        echo ""
    fi

    echo "快捷命令:"
    echo "  cc-bot start    - 启动 Bot"
    echo "  cc-bot stop     - 停止 Bot"
    echo "  cc-bot status   - 查看状态"
    echo "  cc-bot log      - 查看日志"
    echo ""

    # 显示当前状态
    sleep 2
    if pgrep -f "telegram_bot.py" > /dev/null; then
        print_success "Bot 正在运行"
    else
        print_warning "Bot 可能未启动，请检查日志"
    fi
}

# 主函数
main() {
    print_header
    check_environment
    select_mode

    if [ "$mode" == "1" ]; then
        standalone_deploy
    else
        sync_deploy
    fi

    finish
}

main "$@"
