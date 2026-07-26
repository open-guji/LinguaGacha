#!/usr/bin/env python3
"""校验 batch-punctuate.sh 的输出是否只加了标点、没有改动原文用字。

LZH 标点复原模式要求模型逐字保留原文，但实测发现部分模型会在不小的比例
的页面上"顺手纠正"看起来像错字/异体字/简繁不一致的字（比如 户<->戶、
並<->并），这种改动表面上看不出来（输出依然通顺、标点也对），必须靠
去掉标点后逐字比对才能发现。这个脚本就做这一件事。

用法:
  verify-fidelity.py <源文件或目录> <输出文件或目录> [--source-language ZH]

退出码: 0 = 全部通过；1 = 发现字符被改动或整页未加标点；2 = 参数/配对错误
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path

# 覆盖常见中文标点、书名号/引号变体、控制标点；不含汉字本身
PUNCT_CHARS = set(
    "，。、；：？！“”‘’「」『』《》〈〉（）()［］[]【】…—-·,.:;!?\"'"
)


def strip_punct(text: str) -> str:
    return "".join(ch for ch in text if ch not in PUNCT_CHARS and not unicodedata.category(ch).startswith("Z"))


def collect_json_files(root: Path) -> dict[str, Path]:
    if root.is_file():
        return {root.name: root}
    return {p.name: p for p in sorted(root.rglob("*.json"))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="标点前的原始文件或目录")
    parser.add_argument("output", type=Path, help="batch-punctuate.sh 产出的文件或目录")
    args = parser.parse_args()

    if not args.source.exists():
        print(f"源路径不存在: {args.source}", file=sys.stderr)
        return 2
    if not args.output.exists():
        print(f"输出路径不存在: {args.output}", file=sys.stderr)
        return 2

    source_files = collect_json_files(args.source)
    output_files = collect_json_files(args.output)
    common_names = sorted(set(source_files) & set(output_files))
    if not common_names:
        print("源和输出没有同名 JSON 文件可比对", file=sys.stderr)
        return 2

    has_issue = False
    for name in common_names:
        src_data = json.loads(source_files[name].read_text(encoding="utf-8"))
        dst_data = json.loads(output_files[name].read_text(encoding="utf-8"))
        src_pages = src_data.get("pages", [])
        dst_pages = dst_data.get("pages", [])
        if len(src_pages) != len(dst_pages):
            print(f"[{name}] 页数不一致：源 {len(src_pages)} vs 输出 {len(dst_pages)}")
            has_issue = True
            continue

        untouched: list[int] = []
        altered: list[int] = []
        for i, (s, d) in enumerate(zip(src_pages, dst_pages)):
            if s.strip() == "":
                continue
            if s == d:
                untouched.append(i)
            if strip_punct(s) != strip_punct(d):
                altered.append(i)

        if untouched:
            print(f"[{name}] 完全未加标点（模型没处理）：{untouched}")
            has_issue = True
        if altered:
            print(f"[{name}] 疑似改动了原文用字（去标点后不一致），需人工核对：{altered}")
            has_issue = True
        if not untouched and not altered:
            print(f"[{name}] OK（{len(src_pages)} 页）")

    return 1 if has_issue else 0


if __name__ == "__main__":
    raise SystemExit(main())
