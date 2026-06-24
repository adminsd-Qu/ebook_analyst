"""JSON-to-Markdown 转换器 — 将分析 JSON 文件转换为可读的 Markdown 文件。

将 chapters_analysis.json 和 themes.json 独立转换为 .md 文件，
使分析结果不依赖 JSON 读取即可查看。
"""

import json
from datetime import datetime
from pathlib import Path


def chapters_to_md(json_path: str | Path, output_path: str | Path | None = None) -> Path:
    """将 chapters_analysis.json 转换为 Markdown。

    参数:
        json_path: chapters_analysis.json 路径
        output_path: 输出 .md 路径（默认同目录）

    返回:
        输出的 .md 路径
    """
    json_path = Path(json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if output_path is None:
        output_path = json_path.with_suffix(".md")
    else:
        output_path = Path(output_path)

    lines = []
    lines.append(f"# 《{data.get('book', '未知')}》逐章详解")
    lines.append(f"作者: {data.get('author', '未知')}")
    lines.append(f"分析日期: {data.get('analysis_date', '')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for ch in data.get("chapters", []):
        idx = ch["chapter_index"] + 1
        title = ch.get("chapter_title", f"第{idx}章")
        lines.append(f"## 第{idx}章: {title}")
        lines.append(f"*{ch.get('char_count', 0):,} 字*")
        lines.append("")

        analysis = ch.get("analysis", {})

        if "plot_summary" in analysis:
            lines.append(f"### 情节概要")
            lines.append(analysis["plot_summary"])
            lines.append("")

        if "character_development" in analysis:
            lines.append(f"### 人物发展")
            lines.append(analysis["character_development"])
            lines.append("")

        if "language_style" in analysis:
            lines.append(f"### 语言与叙事")
            lines.append(analysis["language_style"])
            lines.append("")

        if "imagery_sensory" in analysis:
            lines.append(f"### 意象与感官")
            lines.append(analysis["imagery_sensory"])
            lines.append("")

        key_passages = analysis.get("key_passages", [])
        if key_passages:
            lines.append(f"### 关键段落")
            for kp in key_passages:
                lines.append(f"> {kp['text']}")
                lines.append(f"> *— {kp.get('commentary', '')}*")
                lines.append("")

        if "cultural_elements" in analysis:
            lines.append(f"### 文化元素")
            lines.append(analysis["cultural_elements"])
            lines.append("")

        theme_signals = analysis.get("theme_signals", [])
        if theme_signals:
            labels = "、".join(f"[{t}]" for t in theme_signals)
            lines.append(f"→ **本章主题线索**: {labels}")
            lines.append("")

        lines.append("---")
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def themes_to_md(json_path: str | Path, output_path: str | Path | None = None) -> Path:
    """将 themes.json 转换为 Markdown。

    参数:
        json_path: themes.json 路径
        output_path: 输出 .md 路径（默认同目录）

    返回:
        输出的 .md 路径
    """
    json_path = Path(json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if output_path is None:
        output_path = json_path.with_suffix(".md")
    else:
        output_path = Path(output_path)

    lines = []
    lines.append(f"# 《{data.get('book', '未知')}》主题分析")
    lines.append(f"分析日期: {data.get('analysis_date', '')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, theme in enumerate(data.get("themes", []), 1):
        name = theme["name"]
        lines.append(f"## 主题{i}: {name}")
        lines.append("")

        if "definition" in theme:
            lines.append(f"**定义**: {theme['definition']}")
            lines.append("")

        if "development" in theme:
            lines.append(f"**发展脉络**: {theme['development']}")
            lines.append("")

        quotes = theme.get("representative_quotes", [])
        if quotes:
            lines.append(f"**代表段落**:")
            for q in quotes:
                lines.append(f"> {q}")
                lines.append("")

        related = theme.get("related_dimensions", [])
        if related:
            lines.append(f"**关联维度**: {'、'.join(related)}")
            lines.append("")

        ch_indices = theme.get("chapter_indices", [])
        if ch_indices:
            ch_labels = "、".join(f"第{i+1}章" for i in ch_indices)
            lines.append(f"**关联章节**: {ch_labels}")
            lines.append("")

        lines.append("---")
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def keywords_to_md(json_path: str | Path, output_path: str | Path | None = None) -> Path:
    """将 keywords.json 转换为 Markdown 表格。

    参数:
        json_path: keywords.json 路径
        output_path: 输出 .md 路径（默认同目录）

    返回:
        输出的 .md 路径
    """
    json_path = Path(json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if output_path is None:
        output_path = json_path.with_suffix(".md")
    else:
        output_path = Path(output_path)

    lines = []
    lines.append(f"# 关键词分析 — {data.get('title', '未知')}")
    lines.append(f"作者: {data.get('author', '未知')}")
    lines.append(f"总字数: {data.get('total_chars', 0):,}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # TF-IDF Top 50
    lines.append("## TF-IDF 关键词 Top 50")
    lines.append("")
    lines.append("| 排名 | 关键词 | TF-IDF 权重 | TextRank 权重 |")
    lines.append("|------|--------|-------------|---------------|")
    for i, kw in enumerate(data.get("overall_keywords", [])[:50], 1):
        lines.append(
            f"| {i} | {kw['word']} | "
            f"{kw['tfidf_weight']:.4f} | "
            f"{kw['textrank_weight']:.4f} |"
        )
    lines.append("")

    # 高频词 Top 50
    freq_words = data.get("top_frequent_words", {})
    if freq_words:
        lines.append("## 高频词汇 Top 50")
        lines.append("")
        lines.append("| 排名 | 词汇 | 出现次数 |")
        lines.append("|------|------|----------|")
        for i, (word, count) in enumerate(list(freq_words.items())[:50], 1):
            lines.append(f"| {i} | {word} | {count} |")
        lines.append("")

    # 逐章关键词
    chapter_kw = data.get("chapter_keywords", [])
    if chapter_kw:
        lines.append("## 逐章关键词")
        lines.append("")
        for ch in chapter_kw:
            fallback_title = "第" + str(ch["chapter_index"] + 1) + "章"
            title = ch.get("chapter_title", fallback_title)
            lines.append(f"### {title}")
            lines.append(f"*{ch.get('char_count', 0):,} 字*")
            lines.append("")
            kw_list = ch.get("keywords", [])[:15]
            items = ", ".join("**" + k["word"] + "**(" + f"{k['tfidf_weight']:.3f}" + ")" for k in kw_list)
            lines.append(f"Top 15: {items}")
            lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def convert_all(data_dir: str | Path, output_dir: str | Path | None = None, verbose: bool = False) -> list[Path]:
    """将 data/ 目录下所有分析 JSON 转换为 Markdown。

    参数:
        data_dir: 包含 chapters_analysis.json, themes.json, keywords.json 的目录
        output_dir: 输出目录（默认与 data_dir 相同）

    返回:
        生成的 .md 文件路径列表
    """
    data_dir = Path(data_dir)
    if output_dir is None:
        output_dir = data_dir
    else:
        output_dir = Path(output_dir)

    paths = []

    mappings = [
        ("chapters_analysis.json", chapters_to_md),
        ("themes.json", themes_to_md),
        ("keywords.json", keywords_to_md),
    ]

    for filename, converter in mappings:
        json_path = data_dir / filename
        if json_path.exists():
            md_path = output_dir / f"{json_path.stem}.md"
            result = converter(json_path, md_path)
            paths.append(result)
            if verbose:
                print(f"  转换: {json_path.name} → {result.name}")

    return paths
