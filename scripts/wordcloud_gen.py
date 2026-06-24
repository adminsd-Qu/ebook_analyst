#!/usr/bin/env python
"""词云生成 CLI — 从 book.json 生成词云图。

用法:
    python scripts/wordcloud_gen.py <book.json>
    python scripts/wordcloud_gen.py <book.json> --mode chapters
    python scripts/wordcloud_gen.py <book.json> --mode themes --themes themes.json
"""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="从 book.json 生成词云图"
    )
    parser.add_argument(
        "book_json", type=str, help="book.json 文件路径"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="full",
        choices=["full", "chapters", "themes"],
        help="生成模式: full(全书), chapters(逐章), themes(专题)",
    )
    parser.add_argument(
        "--themes",
        type=str,
        default=None,
        help="themes.json 路径 (mode=themes 时必填)",
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=200,
        help="最大词数 (默认: 200)",
    )
    args = parser.parse_args()

    import json
    from ebook_analyst.wordcloud_maker import WordcloudMaker

    book_path = Path(args.book_json)
    if not book_path.exists():
        print(f"错误: 文件不存在: {book_path}", file=sys.stderr)
        sys.exit(1)

    with open(book_path, "r", encoding="utf-8") as f:
        book_data = json.load(f)

    output_dir = book_path.parent.parent  # data/ 的上一级
    chapters = book_data["chapters"]

    maker = WordcloudMaker()

    if args.mode == "full":
        print("生成全书词云...")
        path = maker.generate_full(
            chapters,
            output_dir / "wordcloud_full.png",
            max_words=args.max_words,
        )
        print(f"输出: {path.resolve().relative_to(_PROJECT_ROOT)}")

    elif args.mode == "chapters":
        print(f"逐章词云 ({len(chapters)} 章)...")
        paths = maker.generate_chapters(
            chapters,
            output_dir,
            max_words=args.max_words,
        )
        first_rel = paths[0].resolve().relative_to(_PROJECT_ROOT) if paths else 'none'
        last_rel = paths[-1].resolve().relative_to(_PROJECT_ROOT) if len(paths) > 1 else ''
        print(f"生成 {len(paths)} 个: {first_rel} ... {last_rel}")

    elif args.mode == "themes":
        if not args.themes:
            print("错误: --mode themes 需要 --themes <themes.json>", file=sys.stderr)
            sys.exit(1)
        themes_path = Path(args.themes)
        if not themes_path.exists():
            print(f"错误: 文件不存在: {themes_path}", file=sys.stderr)
            sys.exit(1)
        with open(themes_path, "r", encoding="utf-8") as f:
            themes_data = json.load(f)

        print(f"专题词云 ({len(themes_data.get('themes', []))} 个主题)...")
        paths = maker.generate_themes(
            themes_data,
            chapters,
            output_dir,
            max_words=args.max_words,
        )
        first_rel = paths[0].resolve().relative_to(_PROJECT_ROOT) if paths else 'none'
        print(f"生成 {len(paths)} 个: {first_rel} ...")


if __name__ == "__main__":
    main()
