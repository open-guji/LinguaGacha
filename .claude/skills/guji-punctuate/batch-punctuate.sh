#!/usr/bin/env bash
# 批量给古籍 JSON（{"id":..., "pages": [...]}）加标点，封装 LinguaGacha 的 --cli translate。
# 每个输入文件/目录只调一次电子进程，内部由引擎自己并发处理，不需要外层再套 for 循环调多次进程。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

SOURCE_LANGUAGE="ZH"
TARGET_LANGUAGE="LZH"
OUTPUT_DIR=""
INPUTS=()

usage() {
  cat <<'EOF'
用法: batch-punctuate.sh <输入文件或目录...> --output-dir <目录> [--source-language CODE] [--target-language CODE]

  <输入文件或目录>       一个或多个 {"id":..., "pages":[...]} 结构的 JSON 文件，或包含它们的目录；可重复传入
  --output-dir <目录>    必填，输出目录，产物文件名与输入同名
  --source-language      默认 ZH（原文语言仅用于分块提示，不影响标点复原逻辑）
  --target-language      默认 LZH（文言文标点复原专用模式，不要改成别的，否则会变成真翻译）

示例:
  batch-punctuate.sh ~/texts/00155.json ~/texts/00156.json --output-dir ~/texts/out
  batch-punctuate.sh ~/texts/whole-dir --output-dir ~/texts/out
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --source-language)
      SOURCE_LANGUAGE="$2"
      shift 2
      ;;
    --target-language)
      TARGET_LANGUAGE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      INPUTS+=("$1")
      shift
      ;;
  esac
done

if [[ ${#INPUTS[@]} -eq 0 || -z "$OUTPUT_DIR" ]]; then
  usage
  exit 2
fi

BUNDLE="$REPO_ROOT/build/dist-electron/index.js"
if [[ ! -f "$BUNDLE" ]]; then
  echo "未找到构建产物 $BUNDLE，先执行一次轻量构建（不打包安装包）..." >&2
  (cd "$REPO_ROOT" && npx electron-vite build --config buildtools/vite/electron.vite.config.ts)
fi

mkdir -p "$OUTPUT_DIR"

INPUT_ARGS=()
for input in "${INPUTS[@]}"; do
  INPUT_ARGS+=(--input "$input")
done

cd "$REPO_ROOT"
exec npx electron "$BUNDLE" --cli translate \
  "${INPUT_ARGS[@]}" \
  --output-dir "$OUTPUT_DIR" \
  --source-language "$SOURCE_LANGUAGE" \
  --target-language "$TARGET_LANGUAGE"
