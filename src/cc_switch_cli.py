#!/usr/bin/env python3
"""
CC Switch CLI - 命令行控制 CC Switch 模型切换

使用方法:
    cc-switch-cli list              # 列出所有模型
    cc-switch-cli current           # 显示当前模型
    cc-switch-cli switch <name>     # 切换到指定模型
    cc-switch-cli switch --index 1  # 按索引切换
"""

import sqlite3
import json
import os
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Provider:
    id: str
    name: str
    is_current: bool
    provider_type: Optional[str]
    index: int


class CCSwitchCLI:
    """CC Switch 命令行控制工具"""

    def __init__(self):
        self.db_path = Path.home() / ".cc-switch" / "cc-switch.db"
        self.settings_path = Path.home() / ".cc-switch" / "settings.json"

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        return sqlite3.connect(str(self.db_path))

    def list_providers(self, app_type: str = "claude") -> List[Provider]:
        """列出所有提供商"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, is_current, provider_type, sort_index
            FROM providers
            WHERE app_type = ?
            ORDER BY sort_index
        """, (app_type,))

        providers = []
        for idx, row in enumerate(cursor.fetchall(), 1):
            providers.append(Provider(
                id=row[0],
                name=row[1],
                is_current=bool(row[2]),
                provider_type=row[3],
                index=idx
            ))

        conn.close()
        return providers

    def get_current_provider(self, app_type: str = "claude") -> Optional[Provider]:
        """获取当前使用的提供商"""
        providers = self.list_providers(app_type)
        for p in providers:
            if p.is_current:
                return p
        return providers[0] if providers else None

    def switch_provider(self, identifier: str, app_type: str = "claude") -> bool:
        """
        切换到指定提供商

        Args:
            identifier: 可以是名称、ID 或索引 (如 "Kimi", "1", "uuid")
        """
        providers = self.list_providers(app_type)

        target = None

        # 尝试按索引匹配
        try:
            idx = int(identifier)
            for p in providers:
                if p.index == idx:
                    target = p
                    break
        except ValueError:
            pass

        # 尝试按名称匹配（模糊匹配）
        if not target:
            identifier_lower = identifier.lower()
            for p in providers:
                if identifier_lower in p.name.lower():
                    target = p
                    break

        # 尝试按 ID 匹配
        if not target:
            for p in providers:
                if p.id == identifier:
                    target = p
                    break

        if not target:
            print(f"错误: 找不到匹配的模型 '{identifier}'")
            return False

        if target.is_current:
            print(f"'{target.name}' 已经是当前使用的模型")
            return True

        # 更新数据库
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # 先重置所有 is_current
            cursor.execute("""
                UPDATE providers
                SET is_current = 0
                WHERE app_type = ?
            """, (app_type,))

            # 设置目标为当前
            cursor.execute("""
                UPDATE providers
                SET is_current = 1
                WHERE id = ? AND app_type = ?
            """, (target.id, app_type))

            conn.commit()

            # 更新 settings.json
            self._update_settings(target.id)

            print(f"✅ 已切换到: {target.name}")
            print(f"   ID: {target.id}")

            return True

        except Exception as e:
            print(f"切换失败: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def _update_settings(self, provider_id: str):
        """更新 settings.json"""
        try:
            with open(self.settings_path, 'r') as f:
                settings = json.load(f)

            settings['currentProviderClaude'] = provider_id

            with open(self.settings_path, 'w') as f:
                json.dump(settings, f, indent=2)

        except Exception as e:
            print(f"警告: 更新 settings.json 失败: {e}")


def print_providers(providers: List[Provider]):
    """打印提供商列表"""
    print("\n可用的 Claude Code 模型:\n")
    print(f"{'索引':<6}{'名称':<20}{'当前':<8}{'ID'}")
    print("-" * 70)

    for p in providers:
        current = "✓" if p.is_current else ""
        print(f"{p.index:<6}{p.name:<20}{current:<8}{p.id[:8]}...")

    print()


def main():
    cli = CCSwitchCLI()

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        providers = cli.list_providers()
        print_providers(providers)

    elif command == "current":
        current = cli.get_current_provider()
        if current:
            print(f"\n当前模型: {current.name}")
            print(f"ID: {current.id}\n")
        else:
            print("错误: 无法获取当前模型")
            sys.exit(1)

    elif command == "switch":
        if len(sys.argv) < 3:
            print("用法: cc-switch-cli switch <name|index>")
            print("示例:")
            print("  cc-switch-cli switch Kimi")
            print("  cc-switch-cli switch 1")
            sys.exit(1)

        identifier = sys.argv[2]
        success = cli.switch_provider(identifier)
        sys.exit(0 if success else 1)

    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
