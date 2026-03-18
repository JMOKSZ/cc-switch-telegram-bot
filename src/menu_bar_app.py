#!/usr/bin/env python3
"""
CC Switch Telegram Bot - macOS 菜单栏应用
提供图形界面控制 Bot 状态
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# 尝试导入 rumps，如果没有则使用备选方案
try:
    import rumps
    HAS_RUMPS = True
except ImportError:
    HAS_RUMPS = False
    print("提示: 安装 rumps 可获得更好的菜单栏体验")
    print("  pip install rumps")


class CCSwitchMenuBar:
    """菜单栏控制器"""

    def __init__(self):
        self.app_name = "CC Switch Remote"
        self.install_dir = Path.home() / ".cc-switch-telegram-bot"
        self.log_file = self.install_dir / "logs" / "bot.log"
        self.pid_file = self.install_dir / "bot.pid"

        if HAS_RUMPS:
            self.app = rumps.App(self.app_name, "🤖")
            self._setup_menu()
        else:
            self.app = None

    def _setup_menu(self):
        """设置菜单项"""
        self.app.menu = [
            rumps.MenuItem("启动 Bot", callback=self.start_bot),
            rumps.MenuItem("停止 Bot", callback=self.stop_bot),
            rumps.MenuItem("重启 Bot", callback=self.restart_bot),
            None,  # 分隔线
            rumps.MenuItem("查看状态", callback=self.show_status),
            rumps.MenuItem("查看日志", callback=self.show_log),
            None,
            rumps.MenuItem("编辑配置", callback=self.edit_config),
            None,
            rumps.MenuItem("退出", callback=self.quit),
        ]

        # 启动时更新状态
        self._update_menu_state()

    def _is_running(self) -> bool:
        """检查 Bot 是否运行"""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "telegram_bot.py"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False

    def _update_menu_state(self):
        """更新菜单状态"""
        if not HAS_RUMPS:
            return

        is_running = self._is_running()

        # 更新图标和菜单
        if is_running:
            self.app.title = "🟢"
            self.app.menu["启动 Bot"].set_callback(None)
            self.app.menu["停止 Bot"].set_callback(self.stop_bot)
        else:
            self.app.title = "🔴"
            self.app.menu["启动 Bot"].set_callback(self.start_bot)
            self.app.menu["停止 Bot"].set_callback(None)

    def start_bot(self, _=None):
        """启动 Bot"""
        if self._is_running():
            rumps.notification("CC Switch Remote", "提示", "Bot 已经在运行中")
            return

        try:
            subprocess.Popen(
                [str(self.install_dir / "launch.sh")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=str(self.install_dir)
            )
            time.sleep(2)
            self._update_menu_state()

            if HAS_RUMPS:
                rumps.notification("CC Switch Remote", "成功", "Bot 已启动")

        except Exception as e:
            if HAS_RUMPS:
                rumps.notification("CC Switch Remote", "错误", str(e))

    def stop_bot(self, _=None):
        """停止 Bot"""
        try:
            subprocess.run(["pkill", "-f", "telegram_bot.py"], check=False)
            time.sleep(1)
            self._update_menu_state()

            if HAS_RUMPS:
                rumps.notification("CC Switch Remote", "成功", "Bot 已停止")

        except Exception as e:
            if HAS_RUMPS:
                rumps.notification("CC Switch Remote", "错误", str(e))

    def restart_bot(self, _=None):
        """重启 Bot"""
        self.stop_bot()
        time.sleep(2)
        self.start_bot()

        if HAS_RUMPS:
            rumps.notification("CC Switch Remote", "成功", "Bot 已重启")

    def show_status(self, _=None):
        """显示状态"""
        is_running = self._is_running()
        status = "运行中 🟢" if is_running else "已停止 🔴"

        # 获取当前模型
        try:
            result = subprocess.run(
                ["python3", str(self.install_dir / "src" / "cc_switch_cli.py"), "current"],
                capture_output=True,
                text=True,
                cwd=str(self.install_dir)
            )
            model_info = result.stdout.strip()
        except:
            model_info = "无法获取"

        message = f"状态: {status}\n\n{model_info}"

        if HAS_RUMPS:
            rumps.alert("CC Switch Remote 状态", message, ok="确定")
        else:
            print(message)

    def show_log(self, _=None):
        """查看日志"""
        log_path = str(self.log_file)

        # 使用 Console.app 或 TextEdit 打开
        subprocess.Popen(["open", "-a", "Console", log_path])

    def edit_config(self, _=None):
        """编辑配置"""
        config_path = str(self.install_dir / ".env")
        subprocess.Popen(["open", "-e", config_path])

    def quit(self, _=None):
        """退出应用"""
        if HAS_RUMPS:
            rumps.quit_application()

    def run(self):
        """运行应用"""
        if HAS_RUMPS and self.app:
            self.app.run()
        else:
            # 没有 rumps 时，使用简单菜单
            self._run_cli_mode()

    def _run_cli_mode(self):
        """CLI 模式（无 GUI）"""
        print("=" * 50)
        print("CC Switch Remote - 控制台模式")
        print("=" * 50)
        print()

        while True:
            is_running = self._is_running()
            status = "🟢 运行中" if is_running else "🔴 已停止"

            print(f"当前状态: {status}")
            print()
            print("选项:")
            print("  1. 启动 Bot")
            print("  2. 停止 Bot")
            print("  3. 重启 Bot")
            print("  4. 查看状态")
            print("  5. 查看日志")
            print("  6. 编辑配置")
            print("  0. 退出")
            print()

            choice = input("请选择 (0-6): ").strip()

            if choice == "1":
                self.start_bot()
            elif choice == "2":
                self.stop_bot()
            elif choice == "3":
                self.restart_bot()
            elif choice == "4":
                self.show_status()
            elif choice == "5":
                self.show_log()
            elif choice == "6":
                self.edit_config()
            elif choice == "0":
                break
            else:
                print("无效选择")

            print()
            time.sleep(1)


def main():
    """主函数"""
    app = CCSwitchMenuBar()
    app.run()


if __name__ == "__main__":
    main()
