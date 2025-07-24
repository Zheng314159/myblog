#!/bin/bash

set -e

echo "📦 开始将 requirements.txt 迁移为 Poetry 项目..."

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

if ! command -v poetry &>/dev/null; then
    echo "❌ Poetry 未安装，请先运行: pip install poetry"
    exit 1
fi

if [ ! -f pyproject.toml ]; then
    poetry init --no-interaction --name "$(basename "$PROJECT_ROOT")" --dependency ""
    echo "✅ 初始化 pyproject.toml 完成"
else
    echo "⚠️ pyproject.toml 已存在，跳过初始化"
fi

REQ_FILE="$PROJECT_ROOT/requirements.txt"
if [ -f "$REQ_FILE" ]; then
    echo "📥 导入依赖项..."
    while IFS= read -r line || [[ -n "$line" ]]; do
        [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
        # 过滤掉 editable 和 git 依赖
        if [[ "$line" == -e* ]] || [[ "$line" == git+* ]]; then
            echo "⚠️ 跳过特殊依赖行: $line"
            continue
        fi
        echo "➕ 添加依赖: $line"
        if ! poetry add "$line"; then
            echo "❌ 添加依赖失败: $line"
            exit 1
        fi
    done < "$REQ_FILE"
else
    echo "⚠️ 找不到 requirements.txt，跳过依赖导入"
fi

DEV_REQ_FILE="$PROJECT_ROOT/dev-requirements.txt"
if [ -f "$DEV_REQ_FILE" ]; then
    echo "📥 导入开发依赖..."
    while IFS= read -r line || [[ -n "$line" ]]; do
        [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
        if [[ "$line" == -e* ]] || [[ "$line" == git+* ]]; then
            echo "⚠️ 跳过特殊开发依赖行: $line"
            continue
        fi
        echo "➕ 添加开发依赖: $line"
        if ! poetry add --group dev "$line"; then
            echo "❌ 添加开发依赖失败: $line"
            exit 1
        fi
    done < "$DEV_REQ_FILE"
else
    echo "ℹ️ 未找到 dev-requirements.txt，跳过开发依赖"
fi

echo "🔧 安装依赖..."
poetry install

echo "🎉 迁移完成！"
