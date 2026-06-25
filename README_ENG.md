# ebook_analyst — Local EPUB Ebook Analysis Tool

[中文](README.md) | English

Automatically parse EPUB ebooks into structured data, combining Python mechanical processing with Claude intelligent analysis to produce comprehensive deep analysis reports covering **word clouds, chapter-by-chapter analysis, theme identification, and thematic summaries**.

## Features

| Dimension | Description | Implementation |
|-----------|-------------|----------------|
| 📖 Book Info | Title, author, word count, chapter structure | Python (ebooklib) |
| 🔑 Keywords | TF-IDF + TextRank Top 50 | Python (jieba) |
| ☁️ Full Word Cloud | Chinese word cloud, auto font detection | Python (wordcloud) |
| ☁️ Chapter Word Clouds | Per-chapter word clouds | Python |
| 📝 Chapter Analysis | Plot, characters, language, imagery, key passages | Claude deep reading |
| 🎯 Theme Analysis | 3-5 core themes with cross-chapter development | Claude synthesis |
| ☁️ Thematic Word Clouds | One word cloud per theme | Python + Claude |
| 📊 Thematic Summary | Character, imagery, culture, language dimensions | Claude synthesis |
| 👥 Character Network | Co-occurrence network analysis | Python (networkx) |
| 📄 Report Assembly | Markdown report + token stats | Python |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Parse EPUB (output defaults to EPUB's directory)
python scripts\parse_epub.py "D:\books\example.epub"
# → Output to D:\books\example\

# 3. Extract keywords
python scripts\keyword_extract.py D:\books\example\data\book.json

# 4. Generate word clouds
python scripts\wordcloud_gen.py D:\books\example\data\book.json
python scripts\wordcloud_gen.py D:\books\example\data\book.json --mode chapters
# Customize: colormap / font
python scripts\wordcloud_gen.py D:\books\example\data\book.json --colormap plasma --font simkai

# 5. Launch Claude deep analysis (say in Claude Code)
#    "Analyze D:\books\example"
#    or "/ebook-analyst" to invoke the Skill
```

## Full Workflow

```
EPUB File
  │
  ├─ [Python] parse_epub.py         → book.json (metadata + chapter text)
  ├─ [Python] keyword_extract.py    → keywords.json (keywords + frequency)
  ├─ [Python] wordcloud_gen.py      → wordcloud_*.png (full + per-chapter)
  │
  ├─ [Claude] Chapter Analysis      → chapters_analysis.json
  │     └─ Per chapter: plot, characters, language, imagery, key passages, theme_signals
  │
  ├─ [Claude] Theme Synthesis       → themes.json
  │     ├─ Aggregate theme_signals → identify 3-5 core themes
  │     ├─ Backfill chapter analysis
  │     └─ Thematic summaries (character/imagery/culture/language)
  │
  ├─ [Python] wordcloud_gen.py      → wordcloud_topic_*.png (thematic word clouds)
  │     --mode themes --themes themes.json
  │
  ├─ [Python] report_builder.py     → report.md (full report)
  │
  └─ [Python] collect_deliverables.py → deliverables\ (collected output)
        ├─ JSON → Markdown auto-conversion
        └─ Gather all .png + .md into one directory
```

## Project Structure

```
ebook_analyst/
├── README.md                       # Chinese documentation
├── README_ENG.md                   # English documentation (this file)
├── SKILL.md                        # Claude Code Skill definition
├── CLAUDE.md                       # Claude Code project context
├── requirements.txt                # Python dependencies
├── pyproject.toml
│
├── ebook_analyst/                  # Python core library
│   ├── epub_reader.py              # EPUB parser
│   ├── text_processor.py           # Chinese tokenization, stopwords
│   ├── keyword_extractor.py        # TF-IDF + TextRank
│   ├── wordcloud_maker.py          # Word clouds (full/chapter/thematic)
│   ├── character_network.py        # Character co-occurrence network (optional)
│   ├── report_builder.py           # Markdown report assembly
│   ├── json_to_md.py               # JSON analysis → Markdown conversion
│   └── collector.py                # Deliverable collector
│
├── scripts/                        # CLI entry points
│   ├── parse_epub.py               # EPUB → book.json
│   ├── keyword_extract.py          # → keywords.json
│   ├── wordcloud_gen.py            # → PNG word clouds
│   └── collect_deliverables.py     # → Gather deliverables
│
└── temp/                           # EPUB extraction cache (gitignore)
```

## Claude Code Skill Interactive Workflow

The analysis flow **pauses once** after chapter-by-chapter deep reading (Stage 2). All other stages run automatically:

1. Stages 0-1 run automatically (parse + keywords + word clouds)
2. Stage 2 pauses after all chapters are analyzed — reports findings + proactively suggests 2-3 extra analysis directions
3. User replies "continue" → Stages 3→4→5 run straight through, no further pauses
4. User makes additional requests → fulfill them, then ask again whether to generate the full report
5. Say "stop" or "整理" at any time → collect completed deliverables

### Stage Overview

| Stage | Content | Implementation | Interaction |
|-------|---------|----------------|-------------|
| 0 — Init | Parse EPUB, determine analysis strategy | Python | Auto |
| 1 — Extract | Keywords + word clouds | Python | Auto |
| 2 — Deep Read | Per-chapter literary analysis | Claude | ⭐ Pause & ask |
| 3 — Synthesis | Theme analysis + thematic summaries | Claude | Auto |
| 4 — Report | Thematic word clouds + final report | Python | Auto |
| 5 — Collect | JSON→MD + gather to deliverables\ | Python | Auto |

## Collect Deliverables

```bash
# Gather all .png and .md into the deliverables\ directory
# Auto-converts JSON analysis files to Markdown
python scripts\collect_deliverables.py D:\books\example
```

The deliverables directory includes:
- `report.md` — Full analysis report
- `chapters_analysis.md` — Chapter-by-chapter analysis
- `themes.md` — Theme analysis
- `keywords.md` — Keyword analysis
- `wordcloud_*.png` — All word cloud images
- `character_network.png` — Character network diagram (optional)
- `README.md` — File index

## Optional Features

### Character Network

```bash
python -c "from ebook_analyst.character_network import generate_character_network; generate_character_network('D:\\books\\example\\data\\book.json', ['Character A', 'Character B', 'Character C'], 'D:\\books\\example\\character_network.png', min_edge_weight=2)"
```

### Thematic Word Clouds (requires completed theme analysis)

```bash
python scripts\wordcloud_gen.py D:\books\example\data\book.json --mode themes --themes D:\books\example\data\themes.json
```

### Word Cloud Customization

`wordcloud_gen.py` supports the following options to customize colors, fonts, and titles:

```bash
# List available Chinese fonts
python scripts\wordcloud_gen.py <book.json> --list-fonts

# Switch color scheme (matplotlib colormap)
python scripts\wordcloud_gen.py <book.json> --colormap plasma    # warm gradient
python scripts\wordcloud_gen.py <book.json> -c turbo             # high-contrast rainbow
python scripts\wordcloud_gen.py <book.json> -c cool              # cool tones

# Switch font
python scripts\wordcloud_gen.py <book.json> --font simkai        # KaiTi
python scripts\wordcloud_gen.py <book.json> --font simhei        # HeiTi

# Adjust title font size (default: 24)
python scripts\wordcloud_gen.py <book.json> --title-fontsize 32

# Combine options
python scripts\wordcloud_gen.py <book.json> --mode chapters \
    --colormap cividis --font simkai --title-fontsize 28
```

| Option | Default | Description |
|--------|---------|-------------|
| `-c` / `--colormap` | `viridis` | plasma / inferno / magma / turbo / cividis / cool / winter / autumn / spring |
| `--font` | auto (Microsoft YaHei) | `--list-fonts` to see all 15 available (simhei/simkai/simsun/simfang/fzstk etc.) |
| `--title-fontsize` | `24` | Title font size (pt) |
| `--max-words` | `100` | Max words in word cloud |

## Dependencies

- Python >= 3.10
- ebooklib — EPUB parsing
- jieba — Chinese tokenization
- wordcloud + matplotlib — Word cloud generation
- networkx — Character network
- beautifulsoup4 + lxml — HTML text extraction

## Example Output

Analysis output for a ~180,000-character novel:

| File | Size | Description |
|------|------|-------------|
| report.md | 44 KB | Full report (~400 lines) |
| chapters_analysis.md | 19 KB | 6 chapters detailed analysis |
| themes.md | 11 KB | 5 major themes |
| keywords.md | 6 KB | TF-IDF/TextRank keywords |
| wordcloud_full.png | 294 KB | Full-book word cloud |
| wordcloud_ch1~6.png | 280-293 KB | 6 chapter word clouds |
| wordcloud_topic_*.png | 5 files | 5 thematic word clouds |
| character_network.png | 358 KB | 12-person network diagram |
| **Total** | **~3 MB** | **15 deliverable files** |

### Five Major Themes Identified

1. **Family Fortunes & Historical Change** — Three generations' fates intertwined with a century of upheaval
2. **Individual Ideals & the Tides of History** — The intellectual's perseverance and compromise
3. **Native Soil Memory & Cultural Identity** — Displacement, return, and rebuilding a spiritual home
4. **Love & Fate Entangled** — Separation and reunion amid war and chaos
5. **Traditional Craft: Inheritance & Extinction** — The last guardians of vanishing artisan traditions
