#!/usr/bin/env python
"""章节摘要聚合 CLI — 将单元化分析摘要（ch_*_digest.json）聚合为合集 JSON。

用法:
    python scripts/aggregate_chapter_digests.py <book_dir>
    python scripts/aggregate_chapter_digests.py <book_dir> -v
"""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="将各章 ch_N_digest.json 聚合成 chapter_summaries.json 和 chapters_analysis.json"
    )
    parser.add_argument(
        "book_dir",
        type=str,
        help="书籍输出目录（含 data/ 子目录）",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="打印详细信息",
    )
    args = parser.parse_args()

    from ebook_analyst.digest_aggregator import aggregate_all

    book_dir = Path(args.book_dir)
    data_dir = book_dir / "data"
    if not data_dir.exists():
        print(f"错误: 目录不存在: {data_dir}", file=sys.stderr)
        sys.exit(1)

    digests = list(data_dir.glob("ch_*_digest.json"))
    if not digests:
        print(f"错误: 在 {data_dir} 中未找到 ch_*_digest.json 文件", file=sys.stderr)
        print("请先完成阶段 2（单元化逐章深读）生成章节摘要。", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"[聚合 {len(digests)} 个章节摘要]")

    summaries_path, analysis_path = aggregate_all(data_dir, verbose=args.verbose)

    print(f"聚合完成: {len(digests)} 章")
    print(f"  chapter_summaries.json → {summaries_path}")
    print(f"  chapters_analysis.json → {analysis_path}")


if __name__ == "__main__":
    main()
