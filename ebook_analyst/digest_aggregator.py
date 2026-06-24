"""章节摘要聚合器 — 将单元化分析摘要聚合为合集 JSON。

阶段 2 各章独立产出的 ch_N_digest.json 格式：
{
  "chapter_index": N,
  "chapter_title": "...",
  "char_count": 4567,
  "analysis_md_path": "data/ch_N+1_analysis.md",
  "dimensions": {
    "narrative": {"synopsis": "...", "key_events": [...]},
    "characters": {"appearing": [...], "relationships": [...]},
    "language": {"style_notes": "...", "rhetoric_highlights": [...]},
    "imagery": {"new_elements": [...], "recurring_elements": [...]},
    "culture": {"practices": [...]},
    "theme": {"signals": [...]}
  },
  "key_quotations": [
    {"text": ">=80字原文", "context": "一句话语境", "dimension": "所属维度"}
  ],
  "context_consumption": {
    "chapter_input_estimate": 2300,
    "reference_estimate": 500,
    "output_estimate": 1800,
    "chapter_total": 4600
  }
}

聚合输出:
- chapter_summaries.json: 按维度拆分的章节摘要，供阶段 3 维度索引使用
- chapters_analysis.json: 文学分析合集，供 report_builder.py 和 json_to_md.py 使用
"""

import json
from datetime import datetime
from pathlib import Path


def _load_digests(data_dir: Path) -> list[dict]:
    """加载并排序所有 ch_*_digest.json 文件。"""
    digests = []
    for f in sorted(data_dir.glob("ch_*_digest.json")):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            digests.append(data)
        except (json.JSONDecodeError, KeyError):
            continue
    digests.sort(key=lambda d: d.get("chapter_index", 0))
    return digests


def _load_book_meta(data_dir: Path) -> tuple[str, str]:
    """从 book.json 读取书名和作者。"""
    book_path = data_dir / "book.json"
    if book_path.exists():
        with open(book_path, "r", encoding="utf-8") as f:
            book = json.load(f)
        return book.get("title", ""), book.get("author", "")
    return "", ""


def _render_language_style(dimensions: dict) -> str:
    """将 structured language 渲染为 prose 字符串。"""
    lang = dimensions.get("language", {})
    parts = []
    style_notes = lang.get("style_notes", "")
    if style_notes:
        parts.append(style_notes)
    highlights = lang.get("rhetoric_highlights", [])
    if highlights:
        parts.append("修辞手法：" + "、".join(highlights))
    return "；".join(parts) if parts else ""


def _render_character_development(dimensions: dict) -> str:
    """将 structured characters 渲染为 prose 字符串。"""
    chars = dimensions.get("characters", {})
    parts = []

    appearing = chars.get("appearing", [])
    if appearing:
        items = [f"- {a['name']}（{a.get('status', '出场')}）" for a in appearing]
        parts.append("出场人物：\n" + "\n".join(items))

    relationships = chars.get("relationships", [])
    if relationships:
        items = [f"- {r['from']} → {r['to']}：{r.get('change', '')}" for r in relationships]
        parts.append("人物关系变化：\n" + "\n".join(items))

    return "\n\n".join(parts) if parts else ""


def _render_imagery_sensory(dimensions: dict) -> str:
    """将 structured imagery 渲染为 prose 字符串。"""
    imagery = dimensions.get("imagery", {})
    parts = []

    new_elements = imagery.get("new_elements", [])
    if new_elements:
        items = [f"- **{e['element']}**：{e.get('context', '')}" for e in new_elements]
        parts.append("新意象：\n" + "\n".join(items))

    recurring = imagery.get("recurring_elements", [])
    if recurring:
        names = [r["element"] if isinstance(r, dict) else str(r) for r in recurring]
        parts.append("复现意象：" + "、".join(names))

    return "\n\n".join(parts) if parts else ""


def _render_cultural_elements(dimensions: dict) -> str:
    """将 structured culture 渲染为 prose 字符串。"""
    culture = dimensions.get("culture", {})
    practices = culture.get("practices", [])
    if practices:
        items = [f"- {p['practice']}：{p.get('description', '')}" for p in practices]
        return "\n".join(items)
    return ""


def aggregate_to_summaries(data_dir: str | Path) -> dict:
    """各章 ch_*_digest.json → chapter_summaries.json 格式。

    返回数据结构与现有 chapter_summaries.json 兼容:
    {
      "book": "...",
      "author": "...",
      "chapters": [
        {chapter_index, chapter_title, char_count, dimensions, key_quotations}
      ]
    }
    """
    data_dir = Path(data_dir)
    book_title, book_author = _load_book_meta(data_dir)
    digests = _load_digests(data_dir)

    chapters = []
    for d in digests:
        chapters.append({
            "chapter_index": d["chapter_index"],
            "chapter_title": d.get("chapter_title", ""),
            "char_count": d.get("char_count", 0),
            "dimensions": d.get("dimensions", {}),
            "key_quotations": d.get("key_quotations", []),
        })

    return {
        "book": book_title,
        "author": book_author,
        "chapters": chapters,
    }


def aggregate_to_analysis(data_dir: str | Path) -> dict:
    """各章 ch_*_digest.json → chapters_analysis.json 格式。

    从结构化 dimensions 渲染 prose 字段，兼容 report_builder.py 和 json_to_md.py:
    {
      "book": "...",
      "author": "...",
      "analysis_date": "...",
      "chapters": [
        {chapter_index, chapter_title, char_count, analysis: {
          plot_summary, character_development, language_style,
          imagery_sensory, key_passages, theme_signals, cultural_elements
        }}
      ]
    }
    """
    data_dir = Path(data_dir)
    book_title, book_author = _load_book_meta(data_dir)
    digests = _load_digests(data_dir)

    chapters = []
    for d in digests:
        dims = d.get("dimensions", {})
        key_quotations = d.get("key_quotations", [])

        # 将 key_quotations 映射为 key_passages 格式
        key_passages = []
        for kq in key_quotations:
            key_passages.append({
                "text": kq.get("text", ""),
                "commentary": f"{kq.get('context', '')} [{kq.get('dimension', '')}]".strip(),
            })

        chapters.append({
            "chapter_index": d["chapter_index"],
            "chapter_title": d.get("chapter_title", ""),
            "char_count": d.get("char_count", 0),
            "analysis": {
                "plot_summary": dims.get("narrative", {}).get("synopsis", ""),
                "character_development": _render_character_development(dims),
                "language_style": _render_language_style(dims),
                "imagery_sensory": _render_imagery_sensory(dims),
                "key_passages": key_passages,
                "theme_signals": dims.get("theme", {}).get("signals", []),
                "cultural_elements": _render_cultural_elements(dims),
            },
        })

    return {
        "book": book_title,
        "author": book_author,
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "chapters": chapters,
    }


def aggregate_all(
    data_dir: str | Path,
    verbose: bool = False,
) -> tuple[Path, Path]:
    """执行两个聚合，写入 chapter_summaries.json + chapters_analysis.json。

    参数:
        data_dir: data/ 目录路径（含 book.json 和 ch_*_digest.json）
        verbose: 是否打印进度信息

    返回:
        (summaries_path, analysis_path) 两个输出文件路径
    """
    data_dir = Path(data_dir)

    summaries = aggregate_to_summaries(data_dir)
    summaries_path = data_dir / "chapter_summaries.json"
    summaries_path.write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if verbose:
        print(f"  → chapter_summaries.json ({len(summaries['chapters'])} 章)")

    analysis = aggregate_to_analysis(data_dir)
    analysis_path = data_dir / "chapters_analysis.json"
    analysis_path.write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if verbose:
        print(f"  → chapters_analysis.json ({len(analysis['chapters'])} 章)")

    return summaries_path, analysis_path
