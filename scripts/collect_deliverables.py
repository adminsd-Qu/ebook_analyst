#!/usr/bin/env python
"""成品收集 CLI — 将分析产物整理到统一目录。

将所有 .png 图片和 .md 报告收集到 deliverables/ 目录，
自动将 JSON 分析文件转换为 Markdown。

用法:
    python scripts/collect_deliverables.py output/<book_name>
    python scripts/collect_deliverables.py output/<book_name> --target ./my_report
"""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="收集分析成品（.png + .md）到统一目录"
    )
    parser.add_argument(
        "output_dir", type=str, help="分析输出目录 (如 output/额尔古纳河右岸/)"
    )
    parser.add_argument(
        "--target",
        "-t",
        type=str,
        default=None,
        help="目标目录 (默认: <output_dir>/deliverables/)",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="不清空目标目录（追加模式）",
    )
    args = parser.parse_args()

    from ebook_analyst.collector import collect_deliverables

    output_dir = Path(args.output_dir)
    if not output_dir.exists():
        print(f"错误: 目录不存在: {output_dir}", file=sys.stderr)
        sys.exit(1)

    target = collect_deliverables(
        output_dir,
        target_dir=args.target,
        clean=not args.no_clean,
    )

    print(f"成品: {target.absolute()}")


if __name__ == "__main__":
    main()
