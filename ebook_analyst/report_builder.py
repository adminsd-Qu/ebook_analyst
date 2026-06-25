"""Markdown 报告组装器 — 将各阶段分析结果组装为完整报告。"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


def build_report(
    output_dir: str | Path,
    token_stats: Optional[list[dict]] = None,
) -> Path:
    """组装最终的 Markdown 分析报告。

    参数:
        output_dir: 分析输出目录 (如 /path/to/山河纪事/)
        token_stats: Token 消耗统计列表 [{"stage": "解析", "input": 0, "output": 0}, ...]

    返回:
        生成的 report.md 路径
    """
    output_dir = Path(output_dir)
    data_dir = output_dir / "data"

    # 读取各阶段数据
    book = _load_json(data_dir / "book.json")
    keywords = _load_json(data_dir / "keywords.json")
    themes = _load_json(data_dir / "themes.json")  # 可能不存在
    chapters_analysis = _load_json(data_dir / "chapters_analysis.json")  # 可能不存在

    lines = []

    # ============================================================
    # 1. 封面信息
    # ============================================================
    lines.append(f"# 《{book['title']}》深度分析报告")
    lines.append("")
    lines.append("| 项目 | 内容 |")
    lines.append("|------|------|")
    lines.append(f"| 书名 | {book['title']} |")
    lines.append(f"| 作者 | {book['author']} |")
    lines.append(f"| 语言 | {book.get('language', 'zh')} |")
    lines.append(f"| 总字数 | {book['total_chars']:,} |")
    lines.append(f"| 章节数 | {book['chapter_count']} |")
    lines.append(f"| 分析日期 | {datetime.now().strftime('%Y-%m-%d')} |")
    lines.append("")

    # 分析维度概览
    if chapters_analysis or themes:
        lines.append("### 分析维度概览")
        dims = []
        if chapters_analysis:
            dims.append("逐章详解")
        if keywords:
            dims.append("关键词提取")
        dims.append("全书词云 + 逐章词云")
        if themes:
            dims.append(f"主题分析 ({len(themes.get('themes', []))} 个主题)")
            dims.append("专题词云")
            dims.append("专题总结")
        dims.append("全书总结")
        lines.append("本报告涵盖以下分析维度：" + "、".join(dims) + "。")
        lines.append("")

    # ============================================================
    # 2. 全书词云
    # ============================================================
    wc_full = output_dir / "wordcloud_full.png"
    if wc_full.exists():
        lines.append("---")
        lines.append("## 全书词云")
        lines.append("")
        lines.append(f"![全书词云](wordcloud_full.png)")
        lines.append("")

    # ============================================================
    # 3. 整体关键词
    # ============================================================
    if keywords:
        lines.append("---")
        lines.append("## 关键词分析")
        lines.append("")

        # TF-IDF Top 30 表格
        lines.append("### TF-IDF 关键词 Top 30")
        lines.append("")
        lines.append("| 排名 | 关键词 | TF-IDF 权重 | TextRank 权重 |")
        lines.append("|------|--------|-------------|---------------|")
        for i, kw in enumerate(keywords.get("overall_keywords", [])[:30], 1):
            lines.append(
                f"| {i} | {kw['word']} | "
                f"{kw['tfidf_weight']:.4f} | "
                f"{kw['textrank_weight']:.4f} |"
            )
        lines.append("")

        # 高频词 Top 20
        freq_words = keywords.get("top_frequent_words", {})
        if freq_words:
            lines.append("### 高频词汇 Top 20")
            lines.append("")
            lines.append("| 排名 | 词汇 | 出现次数 |")
            lines.append("|------|------|----------|")
            for i, (word, count) in enumerate(
                list(freq_words.items())[:20], 1
            ):
                lines.append(f"| {i} | {word} | {count} |")
            lines.append("")

    # ============================================================
    # 4. 逐章详解
    # ============================================================
    if chapters_analysis:
        lines.append("---")
        lines.append("## 逐章详解")
        lines.append("")

        for ch_analysis in chapters_analysis.get("chapters", []):
            ch_idx = ch_analysis["chapter_index"]
            ch_title = ch_analysis.get("chapter_title", f"第{ch_idx + 1}章")
            analysis = ch_analysis.get("analysis", {})

            lines.append(f"### 第{ch_idx + 1}章: {ch_title}")
            lines.append("")

            # 词云
            wc_ch = output_dir / f"wordcloud_ch{ch_idx + 1}.png"
            if wc_ch.exists():
                lines.append(f"![第{ch_idx + 1}章词云](wordcloud_ch{ch_idx + 1}.png)")
                lines.append("")

            # 情节概要
            if "plot_summary" in analysis:
                lines.append(f"**情节概要**: {analysis['plot_summary']}")
                lines.append("")

            # 人物发展
            if "character_development" in analysis:
                lines.append(f"**人物发展**: {analysis['character_development']}")
                lines.append("")

            # 语言风格
            if "language_style" in analysis:
                lines.append(f"**语言与叙事**: {analysis['language_style']}")
                lines.append("")

            # 意象描写
            if "imagery_sensory" in analysis:
                lines.append(f"**意象与感官**: {analysis['imagery_sensory']}")
                lines.append("")

            # 关键段落
            key_passages = analysis.get("key_passages", [])
            if key_passages:
                lines.append("**关键段落**:")
                lines.append("")
                for kp in key_passages:
                    lines.append(f"> {kp['text']}")
                    lines.append(f"> *— {kp.get('commentary', '')}*")
                    lines.append("")

            # 文化元素
            if "cultural_elements" in analysis:
                lines.append(f"**文化元素**: {analysis['cultural_elements']}")
                lines.append("")

            # 主题线索
            theme_signals = analysis.get("theme_signals", [])
            if theme_signals:
                labels = "、".join(f"[{t}]" for t in theme_signals)
                lines.append(f"→ **本章主题线索**: {labels}")
                lines.append("")

            lines.append("---")
            lines.append("")

    # ============================================================
    # 5. 主题分析
    # ============================================================
    if themes:
        lines.append("---")
        lines.append("## 主题分析")
        lines.append("")

        for theme in themes.get("themes", []):
            name = theme["name"]
            lines.append(f"### 主题: {name}")
            lines.append("")

            if "definition" in theme:
                lines.append(f"**定义**: {theme['definition']}")
                lines.append("")

            # 专题词云
            safe_name = name.replace("/", "_").replace(" ", "_")
            wc_topic = output_dir / f"wordcloud_topic_{safe_name}.png"
            if wc_topic.exists():
                lines.append(f"![专题词云: {name}](wordcloud_topic_{safe_name}.png)")
                lines.append("")

            # 关联章节
            ch_indices = theme.get("chapter_indices", [])
            if ch_indices:
                ch_labels = "、".join(
                    f"[第{i + 1}章](#第{i + 1}章-{name})" for i in ch_indices
                )
                lines.append(f"**关联章节**: {ch_labels}")
                lines.append("")

            # 发展脉络
            if "development" in theme:
                lines.append(f"**发展脉络**: {theme['development']}")
                lines.append("")

            # 代表段落
            quotes = theme.get("representative_quotes", [])
            if quotes:
                lines.append("**代表段落**:")
                for q in quotes:
                    lines.append(f"> {q}")
                    lines.append("")
            lines.append("")

            # 关联维度
            related = theme.get("related_dimensions", [])
            if related:
                lines.append(f"**关联维度**: {'、'.join(related)}")
                lines.append("")

            lines.append("---")
            lines.append("")

    # ============================================================
    # 6. 专题总结
    # ============================================================
    if chapters_analysis:
        lines.append("---")
        lines.append("## 专题总结")
        lines.append("")

        # 从 chapters_analysis 中汇总各维度
        _append_thematic_summary(lines, chapters_analysis, "人物", "character_development")
        _append_thematic_summary(lines, chapters_analysis, "意象与象征", "imagery_sensory")
        _append_thematic_summary(lines, chapters_analysis, "文化与历史", "cultural_elements")
        _append_thematic_summary(lines, chapters_analysis, "语言与风格", "language_style")

    # ============================================================
    # 7. 全书总结
    # ============================================================
    lines.append("---")
    lines.append("## 全书总结")
    lines.append("")

    lines.append("*[此部分由 Claude 阅读全书后在分析阶段撰写，综合所有维度的最终评述。]*")
    lines.append("")

    # ============================================================
    # 8. Token 消耗统计
    # ============================================================
    if token_stats:
        # 类型校验：必须是 list[dict]，每个元素需含 stage/input/output
        if not isinstance(token_stats, list) or not all(
            isinstance(ts, dict) and {"stage", "input", "output"}.issubset(ts)
            for ts in token_stats
        ):
            print(
                "[build_report] ⚠️ token_stats 类型错误：预期 "
                f"list[dict]（每条含 stage/input/output），"
                f"实际收到 {type(token_stats).__name__}"
            )
        else:
            lines.append("---")
            lines.append("## 分析成本")
            lines.append("")
            lines.append("| 阶段 | 输入 Token | 输出 Token | 合计 |")
            lines.append("|------|-----------|-----------|------|")
            total_input = 0
            total_output = 0
            for ts in token_stats:
                stage = ts.get("stage", "未知")
                inp = ts.get("input", 0)
                out = ts.get("output", 0)
                total_input += inp
                total_output += out
                lines.append(f"| {stage} | {inp:,} | {out:,} | {inp + out:,} |")

            lines.append(
                f"| **总计** | **{total_input:,}** | **{total_output:,}** | "
                f"**{total_input + total_output:,}** |"
            )
            lines.append("")
            lines.append(f"*注: 以上仅统计 Claude API 调用消耗的 Token，不包含 Python 脚本运行成本。*")

    # ============================================================
    # 写入文件
    # ============================================================
    report_path = output_dir / "report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")

    # 后置校验：检查关键内容块是否为空
    _validate_report(lines, report_path)

    return report_path


def _validate_report(lines: list[str], report_path: Path) -> None:
    """校验报告关键区域是否包含有效内容，打印警告。"""
    section_checks = {
        "逐章详解": ("## 逐章详解", "**情节概要**"),
        "主题分析": ("## 主题分析", "### 主题:"),
        "专题总结": ("## 专题总结", "### "),
    }
    issues = []
    for section_name, (header_mark, content_mark) in section_checks.items():
        in_section = False
        has_content = False
        for line in lines:
            if header_mark in line:
                in_section = True
                continue
            if in_section and line.startswith("## ") and header_mark not in line:
                break  # 进入下一节
            if in_section and content_mark in line:
                has_content = True
                break
        if not has_content:
            issues.append(section_name)

    if issues:
        print(
            f"[报告校验] ⚠️  以下区域内容为空：{', '.join(issues)}。"
            f"可能原因：源数据缺失或 digest 格式不匹配。"
        )
    else:
        print(f"[报告校验] ✅ 所有关键内容块均非空")


def _load_json(path: Path) -> dict:
    """安全加载 JSON 文件，不存在则返回空字典。"""
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _append_thematic_summary(
    lines: list[str],
    chapters_analysis: dict,
    label: str,
    field: str,
):
    """从逐章分析中提取某专题维度的总结。"""
    summary_parts = []
    for ch in chapters_analysis.get("chapters", []):
        analysis = ch.get("analysis", {})
        content = analysis.get(field, "")
        if content:
            ch_title = ch.get("chapter_title", f"第{ch['chapter_index'] + 1}章")
            summary_parts.append(f"- **{ch_title}**: {content}")

    if summary_parts:
        lines.append(f"### {label}专题")
        lines.extend(summary_parts)
        lines.append("")
