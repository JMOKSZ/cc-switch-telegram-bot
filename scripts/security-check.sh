#!/bin/bash
# Git 提交前安全检查脚本
# 用法: ./scripts/security-check.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔒 Git 安全检查启动..."
echo ""

# 检查 .gitignore 是否存在
if [ ! -f ".gitignore" ]; then
    echo -e "${RED}✗ 错误: .gitignore 文件不存在${NC}"
    echo "请创建 .gitignore 文件并添加 .env 到忽略列表"
    exit 1
fi

# 检查 .gitignore 是否包含 .env
if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo -e "${RED}✗ 错误: .gitignore 未包含 '.env'${NC}"
    echo "请添加 .env 到 .gitignore"
    exit 1
fi
echo -e "${GREEN}✓ .gitignore 配置正确${NC}"

# 检查是否有敏感文件在暂存区
SENSITIVE_FILES=$(git diff --cached --name-only | grep -E "\.env$|\.env\.local$|config\.json$|secrets\.|\.key$|\.pem$|\.log$" || true)

if [ -n "$SENSITIVE_FILES" ]; then
    echo -e "${RED}✗ 错误: 检测到敏感文件在暂存区:${NC}"
    echo "$SENSITIVE_FILES"
    echo ""
    echo "请从暂存区移除:"
    echo "  git reset HEAD $SENSITIVE_FILES"
    exit 1
fi
echo -e "${GREEN}✓ 暂存区无敏感文件${NC}"

# 检查暂存区内容中的敏感信息
echo ""
echo "🔍 扫描敏感信息..."

# Telegram Bot Token
TOKENS=$(git diff --cached | grep -oE "[0-9]{8,10}:[A-Za-z0-9_-]{35}" || true)
if [ -n "$TOKENS" ]; then
    echo -e "${RED}✗ 检测到 Telegram Bot Token!${NC}"
    echo "  $TOKENS"
    exit 1
fi

# API Keys
API_KEYS=$(git diff --cached | grep -oE "(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36}|AK[0-9A-Z]{16,})" || true)
if [ -n "$API_KEYS" ]; then
    echo -e "${RED}✗ 检测到可能的 API Key!${NC}"
    echo "  $API_KEYS"
    exit 1
fi

# 带凭证的 URL
CRED_URLS=$(git diff --cached | grep -oE "https?://[^:]+:[^@]+@" || true)
if [ -n "$CRED_URLS" ]; then
    echo -e "${RED}✗ 检测到带凭证的 URL!${NC}"
    echo "  $CRED_URLS"
    exit 1
fi

echo -e "${GREEN}✓ 未发现敏感信息泄露${NC}"

# 检查大文件
LARGE_FILES=$(git diff --cached --name-only | while read file; do
    if [ -f "$file" ]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
        if [ "$size" -gt 1048576 ]; then
            echo "$file ($((size/1024/1024))MB)"
        fi
    fi
done)

if [ -n "$LARGE_FILES" ]; then
    echo ""
    echo -e "${YELLOW}⚠ 警告: 检测到大于 1MB 的文件:${NC}"
    echo "$LARGE_FILES"
    echo "建议使用 Git LFS 或从提交中移除"
fi

echo ""
echo -e "${GREEN}✅ 安全检查通过！可以安全提交。${NC}"
