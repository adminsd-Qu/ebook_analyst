# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

EPUB ebook analysis tool. Python scripts handle mechanical tasks (EPUB parsing, jieba tokenization, word cloud generation, character co-occurrence). Claude handles literary analysis (chapter summaries, theme identification, thematic synthesis). Output is a Markdown report with embedded PNG figures.

## Architecture: three layers

scripts/ (CLI) → ebook_analyst/ (library) → <epub_dir>/<book>/ (artifacts + data + deliverables)

- **`ebook_analyst/`**: importable library. Core logic lives here.
- **`scripts/`**: CLI entry points. Each starts with `sys.path.insert(0, _PROJECT_ROOT)` so they can import `ebook_analyst` without `pip install`.
- **`<epub_dir>/<book>/`**: output directory. Defaults to EPUB 文件所在目录下的 `<书名>/` 子目录。

## 数据流与中间格式

1. parse_epub.py → book.json
2. keyword_extract.py → keywords.json
3. 阶段 0.5：按章导出 → data/ch_N.txt（全文，供阶段 2 读取 + 阶段 3 回退）
4. Claude 分析（按 SKILL.md 流程）:
   2.  单元化逐章深读 → data/ch_N+1_analysis.md（独立章节报告）+ data/ch_N_digest.json（结构化摘要）
   聚合: aggregate_chapter_digests.py → chapter_summaries.json + chapters_analysis.json
   3.  按维度汇总 summaries + analyses → themes.json
5. report_builder.py → report.md
6. collect_deliverables.py → deliverables/

### 新增文件

data/ch_N.txt — 阶段 0.5 从 book.json 按章导出的纯文本全文。
N 为 chapter_index。阶段 2 逐章读取后释放。阶段 3 回退时重读。

data/ch_{N+1}_analysis.md — 阶段 2 每章产出的独立完整分析报告。
可独立阅读，含情节概要、人物分析、语言叙事、意象感官、关键段落、
文化元素、主题线索、关键词 Top 10、上下文消耗记录。

data/ch_N_digest.json — 阶段 2 每章产出的结构化摘要。
按维度拆分（narrative/characters/language/imagery/culture/theme），
供 aggregate_chapter_digests.py 聚合为合集 JSON，阶段 3 按维度索引。

data/_context_tracker.json — 阶段 2 上下文消耗追踪文件。
记录每章估算 token 消耗 + 累计统计 + 剩余可用。
提供会话中断后的连续性（恢复时跳过已处理章节）。

chapter_summaries.json — 聚合脚本从 ch_N_digest.json 生成。
按分析维度拆分，阶段 3 按维度索引读取，无需遍历全文。

chapters_analysis.json — 聚合脚本从 ch_N_digest.json 生成。
文学分析合集，供 report_builder.py 和 json_to_md.py 使用。

## Common commands

All commands and the interactive analysis workflow are in SKILL.md. Quick reference:

```bash
pip install -r requirements.txt
python scripts\parse_epub.py <file.epub>                         # 输出到 EPUB 同目录
python scripts\keyword_extract.py <book_dir>\data\book.json
python scripts\wordcloud_gen.py <book_dir>\data\book.json [--mode chapters|themes]
python scripts\aggregate_chapter_digests.py <book_dir>           # 聚合逐章摘要为合集 JSON
python scripts\collect_deliverables.py <book_dir>
```

## Module quick reference

- **epub_reader**: ebooklib + BS4, auto chapter title detection, suppresses XML warnings
- **text_processor**: jieba exact mode, ~80 hardcoded stopwords, filters punctuation/numbers/single-char
- **keyword_extractor**: TF-IDF + TextRank dual mode, `extract_from_book_json()` is main entry
- **wordcloud_maker**: Chinese font auto-detect chain (msyhbd→stkaiti→stzhongs), matplotlib Agg backend, `char_count < 1000` chapter filter
- **report_builder**: `build_report(output_dir, token_stats)`, `_load_json` returns `{}` on missing files, token stats passed in not read from file
- **character_network**: paragraph-level co-occurrence, spring_layout seed=42, min_edge_weight default 3
- **json_to_md**: `convert_all(data_dir)` batch converts JSON analysis to standalone .md
- **collector**: `collect_deliverables(output_dir)` gathers .png+.md into single directory with README index
- **digest_aggregator**: `aggregate_all(data_dir)` combines per-chapter ch_N_digest.json into chapter_summaries.json + chapters_analysis.json

## SKILL.md

When users ask to analyze a book, follow the interactive workflow in SKILL.md. The two-pass design is intentional: chapter-by-chapter reading with `theme_signals` first, then cross-chapter synthesis from those signals. This prevents themes from being pre-imposed before chapters are read.
