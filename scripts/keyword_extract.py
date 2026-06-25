#!/usr/bin/env python
"""关键词提取 CLI — 从 book.json 提取关键词。

用法:
    python scripts/keyword_extract.py <book.json>
    python scripts/keyword_extract.py <book.json> --output keywords.json
"""

import sys

# 强制使用 UTF-8 输出，避免 Windows 终端 GBK 编码导致中文乱码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="从 book.json 提取关键词（TF-IDF + TextRank）"
    )
    parser.add_argument(
        "book_json", type=str, help="book.json 文件路径"
    )
    parser.add_argument(
        "--top-overall",
        type=int,
        default=50,
        help="整体关键词数量 (默认: 50)",
    )
    parser.add_argument(
        "--top-chapter",
        type=int,
        default=30,
        help="每章关键词数量 (默认: 30)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="输出 JSON 路径 (默认: 同目录 keywords.json)",
    )
    args = parser.parse_args()

    from ebook_analyst.keyword_extractor import extract_from_book_json

    book_path = Path(args.book_json)
    if not book_path.exists():
        print(f"错误: 文件不存在: {book_path}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = book_path.parent / "keywords.json"

    print(f"提取: {book_path.parent.name} ...")

    result = extract_from_book_json(
        book_path,
        output_path=output_path,
        top_k_overall=args.top_overall,
        top_k_chapter=args.top_chapter,
    )

    print(f"关键词: 整体{len(result['overall_keywords'])}个, 高频{len(result['top_frequent_words'])}个, 逐章{len(result['chapter_keywords'])}章")
    print(f"输出: {output_path.resolve()}")


if __name__ == "__main__":
    main()
