# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

EPUB ebook analysis tool. Python scripts handle mechanical tasks (EPUB parsing, jieba tokenization, word cloud generation, character co-occurrence). Claude handles literary analysis (chapter summaries, theme identification, thematic synthesis). Output is a Markdown report with embedded PNG figures.

## Architecture: three layers

scripts/ (CLI) → ebook_analyst/ (library) → <epub_dir>/<book>/ (artifacts + data + deliverables)

- **`ebook_analyst/`**: importable library. Core logic lives here.
- **`scripts/`**: CLI entry points. Each starts with `sys.path.insert(0, _PROJECT_ROOT)` so they can import `ebook_analyst` without `pip install`.
- **`<epub_dir>/<book>/`**: output directory. Defaults to EPUB 文件所在目录下的 `<书名>/` 子目录。

## Data flow and intermediate formats

1. **parse_epub.py** → `book.json`: `{title, author, total_chars, chapter_count, chapters: [{index, title, text, char_count}]}`
2. **keyword_extract.py** → `keywords.json`: `{overall_keywords: [{word, tfidf_weight, textrank_weight}], top_frequent_words: {word: count}, chapter_keywords: [...]}`
3. **Claude analysis** (per SKILL.md) → `chapters_analysis.json` and `themes.json`
4. **report_builder.py** → reads all JSON files (gracefully skips missing ones) + wordcloud PNGs → `report.md`
5. **collect_deliverables.py** → JSON→MD auto-convert + gather .png/.md → `deliverables/`

## Common commands

All commands and the interactive analysis workflow are in SKILL.md. Quick reference:

```bash
pip install -r requirements.txt
python scripts\parse_epub.py <file.epub>                         # 输出到 EPUB 同目录
python scripts\keyword_extract.py <book_dir>\data\book.json
python scripts\wordcloud_gen.py <book_dir>\data\book.json [--mode chapters|themes]
python scripts\collect_deliverables.py <book_dir>
```

## Module quick reference

- **epub_reader**: ebooklib + BS4, auto chapter title detection, suppresses XML warnings, skips <1000 char front matter
- **text_processor**: jieba exact mode, ~80 hardcoded stopwords, filters punctuation/numbers/single-char
- **keyword_extractor**: TF-IDF + TextRank dual mode, `extract_from_book_json()` is main entry
- **wordcloud_maker**: Chinese font auto-detect chain (msyh→simhei→simsun→...), matplotlib Agg backend, `char_count < 1000` chapter filter
- **report_builder**: `build_report(output_dir, token_stats)`, `_load_json` returns `{}` on missing files, token stats passed in not read from file
- **character_network**: paragraph-level co-occurrence, spring_layout seed=42, min_edge_weight default 3
- **json_to_md**: `convert_all(data_dir)` batch converts JSON analysis to standalone .md
- **collector**: `collect_deliverables(output_dir)` gathers .png+.md into single directory with README index

## SKILL.md

When users ask to analyze a book, follow the interactive workflow in SKILL.md. The two-pass design is intentional: chapter-by-chapter reading with `theme_signals` first, then cross-chapter synthesis from those signals. This prevents themes from being pre-imposed before chapters are read.
