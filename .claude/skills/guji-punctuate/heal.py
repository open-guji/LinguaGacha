#!/usr/bin/env python3
"""修复 batch-punctuate.sh 输出里的两类已知问题：

1. 少量字符被模型"纠正"掉（去标点比对后只有零星差异）——直接用原文字符改回去，
   保留模型加的标点，不用重新调用模型。
2. 整段完全没加标点，或改动幅度太大不敢自动改——收集起来，打包成一个临时
   {"id":..., "pages":[...]} 文件，只对这些页重新跑一次 --cli translate
   （LZH），用新结果替换。只重试一次，重试后依然有问题的会在报告里列出来，
   不会无限重跑。

用法:
  heal.py <源文件> <待修复的输出文件> [--max-op-size N] [--max-total-diff N] [--dry-run]

会原地覆盖“待修复的输出文件”（先备份成 <文件>.pre-heal.json）。
"""

from __future__ import annotations

import argparse
import copy
import difflib
import json
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

PUNCT_CHARS = set(
    "，。、；：？！“”‘’「」『』《》〈〉（）()［］[]【】…—-·,.:;!?\"'"
)

# 去标点后字数不超过这个阈值、且模型原样返回的页面，大概率是标题/卷末标记这类
# 本来就不需要断句的短语，不计入"需要重转"，避免浪费模型调用和误报。
SHORT_HEADING_MAX_CHARS = 15

SKILL_DIR = Path(__file__).resolve().parent
REPO_ROOT = SKILL_DIR.parents[2]
ELECTRON_BUNDLE = REPO_ROOT / "build" / "dist-electron" / "index.js"


def is_punct_or_space(ch: str) -> bool:
    return ch in PUNCT_CHARS or unicodedata.category(ch).startswith("Z")


def strip_with_positions(text: str) -> tuple[str, list[int]]:
    """返回去标点/空白后的文本，以及每个保留字符在原文里的下标。"""
    chars: list[str] = []
    positions: list[int] = []
    for i, ch in enumerate(text):
        if is_punct_or_space(ch):
            continue
        chars.append(ch)
        positions.append(i)
    return "".join(chars), positions


def classify_and_heal_page(
    src_text: str, dst_text: str, max_op_size: int, max_total_diff: int
) -> tuple[str, str]:
    """返回 (处理后的文本, 状态)。
    状态: unchanged / healed / needs_retranslate / likely_heading。
    """
    if src_text.strip() == "":
        return dst_text, "unchanged"
    if src_text == dst_text:
        stripped_len = len(strip_with_positions(src_text)[0])
        if stripped_len <= SHORT_HEADING_MAX_CHARS:
            # 短标题/卷末标记本来就可能不需要标点，不算失败，也不浪费一次重转
            return dst_text, "likely_heading"
        return dst_text, "needs_retranslate"  # 完全没加标点

    dst_stripped, dst_positions = strip_with_positions(dst_text)
    src_stripped, _ = strip_with_positions(src_text)
    if src_stripped == dst_stripped:
        return dst_text, "unchanged"  # 只是标点不同，用字完全一致，没问题

    opcodes = [
        op
        for op in difflib.SequenceMatcher(None, src_stripped, dst_stripped).get_opcodes()
        if op[0] != "equal"
    ]
    total_diff = sum(max(i2 - i1, j2 - j1) for _, i1, i2, j1, j2 in opcodes)
    too_big = total_diff > max_total_diff or any(
        max(i2 - i1, j2 - j1) > max_op_size for _, i1, i2, j1, j2 in opcodes
    )
    if too_big:
        return dst_text, "needs_retranslate"

    dst_chars = list(dst_text)
    # 按 j1 从大到小处理，保证插入/删除不会打乱还没处理的更早位置的下标
    for tag, i1, i2, j1, j2 in sorted(opcodes, key=lambda op: op[3], reverse=True):
        if tag == "replace" and (i2 - i1) == (j2 - j1):
            for k in range(i2 - i1):
                dst_chars[dst_positions[j1 + k]] = src_stripped[i1 + k]
        elif tag == "replace":
            start_pos = dst_positions[j1]
            end_pos = dst_positions[j2 - 1] + 1
            dst_chars[start_pos:end_pos] = list(src_stripped[i1:i2])
        elif tag == "delete":
            # 原文有、译文丢掉的字，插回去
            insert_pos = dst_positions[j1] if j1 < len(dst_positions) else len(dst_chars)
            dst_chars[insert_pos:insert_pos] = list(src_stripped[i1:i2])
        elif tag == "insert":
            # 译文多出来原文没有的字，删掉
            start_pos = dst_positions[j1]
            end_pos = dst_positions[j2 - 1] + 1
            del dst_chars[start_pos:end_pos]

    return "".join(dst_chars), "healed"


def run_retranslate(pages_id: str, pages: list[str]) -> list[str] | None:
    """对一批页面重新跑一次 CLI 标点复原，返回结果 pages（顺序与输入一致），失败返回 None。"""
    if not ELECTRON_BUNDLE.exists():
        print(f"[重转] 未找到构建产物 {ELECTRON_BUNDLE}，跳过重试", file=sys.stderr)
        return None

    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        input_path = tmp_dir / "retry.json"
        output_dir = tmp_dir / "out"
        input_path.write_text(
            json.dumps({"id": pages_id, "pages": pages}, ensure_ascii=False), encoding="utf-8"
        )
        result = subprocess.run(
            [
                "npx",
                "electron",
                str(ELECTRON_BUNDLE),
                "--cli",
                "translate",
                "--input",
                str(input_path),
                "--output-dir",
                str(output_dir),
                "--source-language",
                "ZH",
                "--target-language",
                "LZH",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=600,
        )
        finished_ok = any(
            json.loads(line).get("type") == "finished" and json.loads(line).get("status") == "done"
            for line in result.stdout.splitlines()
            if line.strip().startswith("{")
        )
        if not finished_ok or result.returncode != 0:
            print(f"[重转] CLI 未成功完成（exit={result.returncode}）：{result.stderr.strip()[:500]}", file=sys.stderr)
            return None
        output_path = output_dir / "retry.json"
        if not output_path.exists():
            print("[重转] 没有找到输出文件", file=sys.stderr)
            return None
        return json.loads(output_path.read_text(encoding="utf-8"))["pages"]


def heal_file(source_path: Path, output_path: Path, max_op_size: int, max_total_diff: int, dry_run: bool) -> bool:
    src_data = json.loads(source_path.read_text(encoding="utf-8"))
    dst_data = json.loads(output_path.read_text(encoding="utf-8"))
    src_pages = src_data.get("pages", [])
    dst_pages = dst_data.get("pages", [])
    if len(src_pages) != len(dst_pages):
        print(f"[{output_path.name}] 页数不一致（源 {len(src_pages)} / 输出 {len(dst_pages)}），跳过", file=sys.stderr)
        return False

    healed_pages = copy.deepcopy(dst_pages)
    healed_count = 0
    retranslate_indices: list[int] = []
    likely_heading_indices: list[int] = []

    for i, (s, d) in enumerate(zip(src_pages, dst_pages)):
        healed_text, status = classify_and_heal_page(s, d, max_op_size, max_total_diff)
        if status == "healed":
            healed_pages[i] = healed_text
            healed_count += 1
        elif status == "needs_retranslate":
            retranslate_indices.append(i)
        elif status == "likely_heading":
            likely_heading_indices.append(i)

    print(f"[{output_path.name}] 直接改字修复: {healed_count} 页；需要重转: {len(retranslate_indices)} 页 {retranslate_indices}")
    if likely_heading_indices:
        print(
            f"[{output_path.name}] 疑似标题/卷末标记，本来就可能不需要标点，未计入失败，建议扫一眼确认："
            f"{likely_heading_indices}"
        )

    still_bad: list[int] = []
    if retranslate_indices and not dry_run:
        retry_pages = [src_pages[i] for i in retranslate_indices]
        result_pages = run_retranslate(dst_data.get("id", output_path.stem), retry_pages)
        if result_pages is None or len(result_pages) != len(retranslate_indices):
            print(f"[{output_path.name}] 重转失败或结果数量对不上，这些页保持原样：{retranslate_indices}", file=sys.stderr)
            still_bad = list(retranslate_indices)
        else:
            for idx, new_text in zip(retranslate_indices, result_pages):
                # 重转结果再跑一遍同样的判定：小范围残留差异要用改字修复而不是原样写回
                healed_text, status = classify_and_heal_page(
                    src_pages[idx], new_text, max_op_size, max_total_diff
                )
                if status == "needs_retranslate":
                    still_bad.append(idx)
                healed_pages[idx] = healed_text
    elif retranslate_indices and dry_run:
        still_bad = list(retranslate_indices)

    if still_bad:
        print(f"[{output_path.name}] 重转后仍需人工处理：{still_bad}")

    if dry_run:
        print(f"[{output_path.name}] --dry-run，未写回文件")
        return len(still_bad) == 0

    backup_path = output_path.with_suffix(".pre-heal.json")
    if not backup_path.exists():
        shutil.copy2(output_path, backup_path)

    dst_data["pages"] = healed_pages
    output_path.write_text(json.dumps(dst_data, ensure_ascii=False, indent=4), encoding="utf-8")
    print(f"[{output_path.name}] 已写回，原文件备份到 {backup_path.name}")
    return len(still_bad) == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--max-op-size", type=int, default=2, help="单个改动块允许的最大字符数，默认 2")
    parser.add_argument("--max-total-diff", type=int, default=6, help="单页允许自动修复的最大总差异字符数，默认 6")
    parser.add_argument("--dry-run", action="store_true", help="只报告不写回，也不调用模型重转")
    args = parser.parse_args()

    if not args.source.exists() or not args.output.exists():
        print("源文件或输出文件不存在", file=sys.stderr)
        return 2

    ok = heal_file(args.source, args.output, args.max_op_size, args.max_total_diff, args.dry_run)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
