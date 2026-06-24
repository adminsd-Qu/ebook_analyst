"""成品收集器 — 将所有分析产物（.png 和 .md）收集到统一目录。

将 JSON 分析文件自动转换为 Markdown，然后与词云图、人物关系图、
报告等一起整理到 deliverables/ 子目录。
"""

import shutil
from pathlib import Path

from ebook_analyst.json_to_md import convert_all


def collect_deliverables(
    output_dir: str | Path,
    target_dir: str | Path | None = None,
    clean: bool = True,
    verbose: bool = False,
) -> Path:
    """收集指定分析输出目录下的所有成品文件。

    成品定义:
    - .png 图片（词云、人物关系图等）
    - .md 报告文件
    - JSON 自动转换为 .md

    参数:
        output_dir: 分析输出目录（如 /path/to/山河纪事/）
        target_dir: 目标收集目录（默认为 output_dir/deliverables/）
        clean: 是否先清空目标目录

    返回:
        目标目录路径
    """
    output_dir = Path(output_dir)
    if target_dir is None:
        target_dir = output_dir / "deliverables"
    else:
        target_dir = Path(target_dir)

    if clean and target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    collected = []
    skipped = []

    # 1. JSON → MD 转换
    data_dir = output_dir / "data"
    if data_dir.exists():
        if verbose:
            print("[JSON → MD 转换]")
        md_paths = convert_all(data_dir, target_dir, verbose=verbose)
        collected.extend(md_paths)

    # 2. 收集根目录下的 .md 文件
    if verbose:
        print("[收集 .md 文件]")
    for md_file in output_dir.glob("*.md"):
        dest = target_dir / md_file.name
        shutil.copy2(md_file, dest)
        collected.append(dest)
        if verbose:
            print(f"  {md_file.name}")

    # 3. 收集根目录下的 .png 文件
    if verbose:
        print("[收集 .png 文件]")
    for png_file in output_dir.glob("*.png"):
        dest = target_dir / png_file.name
        shutil.copy2(png_file, dest)
        collected.append(dest)
        if verbose:
            print(f"  {png_file.name}")

    # 4. 检查 data/ 下的 JSON（仅报告，不收集）
    if data_dir.exists() and verbose:
        json_files = list(data_dir.glob("*.json"))
        if json_files:
            print(f"[跳过 JSON 文件（已转换为 .md）]")
            for jf in json_files:
                print(f"  {jf.name}")

    # 5. 生成索引
    _generate_index(target_dir, collected)

    print(f"收集: {len(collected)} 个文件 → {target_dir.absolute()}")
    return target_dir


def _generate_index(target_dir: Path, files: list[Path]):
    """在收集目录生成 README.md 索引文件。"""
    lines = [
        "# 分析成品索引",
        "",
        "## 文件列表",
        "",
    ]

    for f in sorted(files):
        rel = f.relative_to(target_dir)
        size = f.stat().st_size
        if size > 1024 * 1024:
            size_str = f"{size / (1024*1024):.1f} MB"
        elif size > 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size} B"

        emoji = "🖼️" if f.suffix == ".png" else "📄"
        lines.append(f"- {emoji} [{rel.name}]({rel.name}) — {size_str}")

    lines.extend([
        "",
        "---",
        f"*共 {len(files)} 个文件*",
        f"*生成时间: {Path.cwd()}*",
    ])

    index_path = target_dir / "README.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
