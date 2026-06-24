#!/usr/bin/env python
"""EPUB 解析 CLI — 将 EPUB 文件解析为结构化 JSON。

用法:
    python scripts/parse_epub.py <epub_file> [--output <output_dir>]

示例:
    python scripts/parse_epub.py "我的书.epub"
    python scripts/parse_epub.py "我的书.epub" --output ./我的分析输出
"""

import sys
from pathlib import Path

# 将项目根目录加入 Python 路径
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="解析 EPUB 文件为结构化 JSON"
    )
    parser.add_argument(
        "epub_file", type=str, help="EPUB 文件路径"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="输出目录 (默认: EPUB 同目录下的 <书名>/)",
    )
    args = parser.parse_args()

    # 延迟导入，让 argparse 错误更快
    from ebook_analyst.epub_reader import EpubReader

    epub_path = Path(args.epub_file)
    if not epub_path.exists():
        print(f"错误: 文件不存在: {epub_path}", file=sys.stderr)
        sys.exit(1)

    print(f"解析: {epub_path.name} ...")

    reader = EpubReader(epub_path)
    data = reader.extract_all()

    # 确定输出路径 (默认: EPUB 同目录)
    if args.output:
        output_dir = Path(args.output)
    else:
        safe_name = data["title"].replace("/", "_").replace("\\", "_")
        output_dir = epub_path.resolve().parent / safe_name

    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "book.json"
    reader.save_json(json_path)

    print(f"书名: {data['title']} | 作者: {data['author']} | 字数: {data['total_chars']:,} | 章节: {data['chapter_count']}")
    print(f"输出: {json_path.resolve()}")


if __name__ == "__main__":
    main()
