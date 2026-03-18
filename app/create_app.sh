#!/bin/bash
# 创建 macOS App Bundle

set -e

APP_NAME="CC Switch Remote"
APP_BUNDLE="$HOME/Applications/${APP_NAME}.app"
INSTALL_DIR="$HOME/.cc-switch-telegram-bot"

echo "Creating macOS App Bundle..."

# 创建目录结构
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

# 创建 Info.plist
cat > "$APP_BUNDLE/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>CC Switch Remote</string>
    <key>CFBundleDisplayName</key>
    <string>CC Switch Remote</string>
    <key>CFBundleIdentifier</key>
    <string>com.ccswitch.telegrambot</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# 创建启动脚本
cat > "$APP_BUNDLE/Contents/MacOS/launcher" << EOF
#!/bin/bash

INSTALL_DIR="$INSTALL_DIR"

# 检查是否已安装
if [ ! -d "$\INSTALL_DIR" ]; then
    osascript -e 'display dialog "请先运行安装脚本:
\ncurl -fsSL https://raw.githubusercontent.com/JMOKSZ/cc-switch-telegram-bot/main/installer/install.sh | bash" buttons {"OK"} default button "OK"'
    exit 1
fi

# 启动菜单栏应用
cd "$\INSTALL_DIR"
source venv/bin/activate
python3 src/menu_bar_app.py
EOF

chmod +x "$APP_BUNDLE/Contents/MacOS/launcher"

# 创建图标（使用 emoji 作为占位符）
cat > "$APP_BUNDLE/Contents/Resources/AppIcon.iconset" << 'EOF'
# 图标将使用系统默认
EOF

echo "✅ App Bundle created at:"
echo "   $APP_BUNDLE"
echo ""
echo "You can now launch it from Applications folder or Launchpad"
