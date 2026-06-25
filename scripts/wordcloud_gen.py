#!/usr/bin/env python
"""词云生成 CLI — 从 book.json 生成词云图。

用法:
    python scripts/wordcloud_gen.py <book.json>
    python scripts/wordcloud_gen.py <book.json> --mode chapters
    python scripts/wordcloud_gen.py <book.json> --mode themes --themes themes.json
    python scripts/wordcloud_gen.py <book.json> --colormap plasma --font simkai
    python scripts/wordcloud_gen.py <book.json> --list-fonts
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
        default=100,
        help="最大词数 (默认: 100)",
    )
    parser.add_argument(
        "--colormap", "-c",
        type=str,
        default="viridis",
        help="matplotlib 配色方案 (默认: viridis；可选: plasma/inferno/magma/turbo/cool/winter/autumn/spring 等)",
    )
    parser.add_argument(
        "--font",
        type=str,
        default=None,
        help="中文字体简称 (默认: msyh；可选: simhei/simkai/simsun/simfang/fzstk 等；--list-fonts 查看全部)",
    )
    parser.add_argument(
        "--title-fontsize",
        type=int,
        default=24,
        help="标题字号 (默认: 24)",
    )
    parser.add_argument(
        "--list-fonts",
        action="store_true",
        help="列出系统中可用的中文字体后退出",
    )
    args = parser.parse_args()

    import json
    from ebook_analyst.wordcloud_maker import (
        WordcloudMaker,
        resolve_font_path,
        list_available_fonts,
    )

    # --list-fonts：列出可用字体后退出
    if args.list_fonts:
        available = list_available_fonts()
        if not available:
            print("未检测到可用中文字体")
        else:
            print("可用的中文字体 (--font 参数值):")
            print(f"  {'简称':<12} 路径")
            print(f"  {'-'*10}  {'-'*40}")
            for name, path in available.items():
                print(f"  {name:<12} {path}")
        return

    book_path = Path(args.book_json)
    if not book_path.exists():
        print(f"错误: 文件不存在: {book_path}", file=sys.stderr)
        sys.exit(1)

    with open(book_path, "r", encoding="utf-8") as f:
        book_data = json.load(f)

    output_dir = book_path.parent.parent  # data/ 的上一级
    chapters = book_data["chapters"]

    # 解析字体
    font_path = resolve_font_path(args.font) if args.font else None
    maker = WordcloudMaker(font_path=font_path)

    # 通用参数
    common_kwargs = {
        "max_words": args.max_words,
        "colormap": args.colormap,
        "title_fontsize": args.title_fontsize,
    }

    if args.mode == "full":
        print("生成全书词云...")
        path = maker.generate_full(
            chapters,
            output_dir / "wordcloud_full.png",
            **common_kwargs,
        )
        print(f"输出: {path.resolve()}")

    elif args.mode == "chapters":
        print(f"逐章词云 ({len(chapters)} 章)...")
        paths = maker.generate_chapters(
            chapters,
            output_dir,
            **common_kwargs,
        )
        first_rel = str(paths[0].resolve()) if paths else 'none'
        last_rel = str(paths[-1].resolve()) if len(paths) > 1 else ''
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
            **common_kwargs,
        )
        first_rel = str(paths[0].resolve()) if paths else 'none'
        print(f"生成 {len(paths)} 个: {first_rel} ...")


if __name__ == "__main__":
    main()
