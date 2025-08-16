#!/usr/bin/env bash
set -euo pipefail

# 定义卷和源目录的映射
declare -A VOLUME_MAP=(
  ["myblog-prod_images-data"]="frontend/public/images"
  ["myblog-prod_pdfs-data"]="frontend/public/pdfs"
  ["myblog-prod_videos-data"]="frontend/public/videos"
)

# 检查依赖
command -v docker >/dev/null 2>&1 || { echo "❌ docker 未安装或未在 PATH"; exit 1; }
command -v realpath >/dev/null 2>&1 || { echo "❌ 需要 realpath 命令 (coreutils/bsdutils 提供)"; exit 1; }

for volume in "${!VOLUME_MAP[@]}"; do
  src_dir="${VOLUME_MAP[$volume]}"
  abs_src="$(realpath "$src_dir")"

  echo "=============================="
  echo "处理卷: $volume"
  echo "源目录: $abs_src"
  echo "=============================="

  # 检查源目录是否存在
  if [[ ! -d "$abs_src" ]]; then
    echo "⚠️  源目录 $abs_src 不存在，跳过 $volume"
    continue
  fi

  # 删除旧卷（如果存在）
  if docker volume inspect "$volume" >/dev/null 2>&1; then
    echo "🗑️  删除旧卷 $volume"
    docker volume rm "$volume"
  fi

  # 创建新卷
  echo "📦 创建新卷 $volume"
  docker volume create "$volume" >/dev/null

  # 拷贝数据
  echo "📂 迁移文件到 $volume ..."
  docker run --rm \
    -v "$abs_src":/src:ro \
    -v "$volume":/dest \
    alpine sh -c "cp -r /src/* /dest/ && ls -l /dest"

  echo "✅ 卷 $volume 迁移完成"
done

echo "🎉 所有卷已迁移完成！"
