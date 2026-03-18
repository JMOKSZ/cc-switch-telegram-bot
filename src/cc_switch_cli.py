#!/usr/bin/env python3
"""
CC Switch CLI - 命令行控制 CC Switch 模型切换

使用方法:
    cc-switch-cli list                      # 列出所有模型
    cc-switch-cli current                   # 显示当前模型
    cc-switch-cli switch <name|index>       # 切换到指定模型
    cc-switch-cli config [provider_id]      # 查看模型配置
    cc-switch-cli seturl <id> <url>         # 修改 Base URL
    cc-switch-cli setkey <id> <key>         # 修改 API Key
    cc-switch-cli rename <id> <name>        # 重命名模型
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

    def get_provider_config(self, provider_id: str = None, app_type: str = "claude") -> dict:
        """获取模型配置详情"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 如果未指定 provider_id，获取当前使用的
        if not provider_id:
            cursor.execute("""
                SELECT id FROM providers
                WHERE app_type = ? AND is_current = 1
            """, (app_type,))
            row = cursor.fetchone()
            if row:
                provider_id = row[0]
            else:
                conn.close()
                return {}

        cursor.execute("""
            SELECT name, settings_config FROM providers
            WHERE id = ? AND app_type = ?
        """, (provider_id, app_type))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return {}

        try:
            config = json.loads(row[1])
            return {
                'name': row[0],
                'id': provider_id,
                'config': config
            }
        except:
            return {'name': row[0], 'id': provider_id, 'config': {}}

    def update_provider_config(self, provider_id: str, new_config: dict, app_type: str = "claude") -> bool:
        """更新模型配置"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # 获取当前配置
            cursor.execute("""
                SELECT settings_config FROM providers
                WHERE id = ? AND app_type = ?
            """, (provider_id, app_type))

            row = cursor.fetchone()
            if not row:
                print(f"错误: 找不到模型 '{provider_id}'")
                return False

            # 合并配置
            try:
                current_config = json.loads(row[0])
            except:
                current_config = {}

            current_config.update(new_config)

            # 更新数据库
            cursor.execute("""
                UPDATE providers
                SET settings_config = ?
                WHERE id = ? AND app_type = ?
            """, (json.dumps(current_config), provider_id, app_type))

            conn.commit()
            return True

        except Exception as e:
            print(f"更新失败: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def update_base_url(self, provider_id: str, base_url: str, app_type: str = "claude") -> bool:
        """更新 Base URL"""
        return self.update_provider_config(provider_id, {
            'env': {'ANTHROPIC_BASE_URL': base_url}
        }, app_type)

    def update_api_key(self, provider_id: str, api_key: str, app_type: str = "claude") -> bool:
        """更新 API Key"""
        return self.update_provider_config(provider_id, {
            'env': {'ANTHROPIC_AUTH_TOKEN': api_key}
        }, app_type)

    def rename_provider(self, provider_id: str, new_name: str, app_type: str = "claude") -> bool:
        """重命名模型"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE providers
                SET name = ?
                WHERE id = ? AND app_type = ?
            """, (new_name, provider_id, app_type))

            conn.commit()
            return True

        except Exception as e:
            print(f"重命名失败: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()


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

    elif command == "config":
        # 显示当前模型的配置
        provider_id = sys.argv[2] if len(sys.argv) > 2 else None
        config = cli.get_provider_config(provider_id)
        if config:
            print(f"\n模型: {config['name']}")
            print(f"ID: {config['id']}")
            print("\n配置:")
            print(json.dumps(config['config'], indent=2, ensure_ascii=False))
            print()
        else:
            print("错误: 无法获取配置")
            sys.exit(1)

    elif command == "seturl":
        if len(sys.argv) < 4:
            print("用法: cc-switch-cli seturl <provider_id> <base_url>")
            print("示例:")
            print('  cc-switch-cli seturl "model-uuid" "https://api.example.com"')
            sys.exit(1)

        provider_id = sys.argv[2]
        base_url = sys.argv[3]
        success = cli.update_base_url(provider_id, base_url)
        if success:
            print(f"✅ 已更新 Base URL: {base_url}")
        sys.exit(0 if success else 1)

    elif command == "setkey":
        if len(sys.argv) < 4:
            print("用法: cc-switch-cli setkey <provider_id> <api_key>")
            print("示例:")
            print('  cc-switch-cli setkey "model-uuid" "sk-xxx"')
            sys.exit(1)

        provider_id = sys.argv[2]
        api_key = sys.argv[3]
        success = cli.update_api_key(provider_id, api_key)
        if success:
            print("✅ 已更新 API Key")
        sys.exit(0 if success else 1)

    elif command == "rename":
        if len(sys.argv) < 4:
            print("用法: cc-switch-cli rename <provider_id> <new_name>")
            print("示例:")
            print('  cc-switch-cli rename "model-uuid" "My Custom Model"')
            sys.exit(1)

        provider_id = sys.argv[2]
        new_name = sys.argv[3]
        success = cli.rename_provider(provider_id, new_name)
        if success:
            print(f"✅ 已重命名为: {new_name}")
        sys.exit(0 if success else 1)

    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
