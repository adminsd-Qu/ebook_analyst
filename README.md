# ebook_analyst — 本地 EPUB 电子书智能分析工具

[English](#english) | 中文

将 EPUB 电子书自动解析为结构化数据，结合 Python 机械处理与 Claude 智能分析，生成包含**词云、逐章详解、主题分析、专题总结**等维度的完整深度分析报告。

## 功能

| 维度 | 说明 | 实现 |
|------|------|------|
| 📖 全书信息 | 书名、作者、字数、章节结构 | Python (ebooklib) |
| 🔑 关键词提取 | TF-IDF + TextRank Top 50 | Python (jieba) |
| ☁️ 全书词云 | 中文词云，自动字体检测 | Python (wordcloud) |
| ☁️ 逐章词云 | 每章独立词云 | Python |
| 📝 逐章详解 | 情节、人物、语言、意象、关键段落 | Claude 深度阅读 |
| 🎯 主题分析 | 3-5 个核心主题，跨章发展脉络 | Claude 跨章统整 |
| ☁️ 专题词云 | 每个主题独立词云 | Python + Claude |
| 📊 专题总结 | 人物、意象、文化、语言四维总结 | Claude 综合 |
| 👥 人物关系图 | 共现网络分析 | Python (networkx) |
| 📄 报告组装 | Markdown 报告 + Token 统计 | Python |

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 解析 EPUB
python scripts/parse_epub.py "path of name.epub"

# 3. 提取关键词
python scripts/keyword_extract.py output/<书名>/data/book.json

# 4. 生成词云
python scripts/wordcloud_gen.py output/<书名>/data/book.json
python scripts/wordcloud_gen.py output/<书名>/data/book.json --mode chapters

# 5. 启动 Claude 深度分析（在 Claude Code 中说）
#    "分析 output/<书名>"
#    或 "/ebook-analyst"调用这个skill。
```

```bash
# 您也可以直接在claude code中引用本脚本路径，发送您的.epub文件路径并调用此功能开始分析。
```

## 完整工作流

```
EPUB 文件
  │
  ├─ [Python] parse_epub.py        → book.json (元数据 + 章节文本)
  ├─ [Python] keyword_extract.py   → keywords.json (关键词 + 词频)
  ├─ [Python] wordcloud_gen.py     → wordcloud_*.png (全书 + 逐章词云)
  │
  ├─ [Claude] 逐章详解 (第一轮)    → chapters_analysis.json
  │     └─ 每章: 情节、人物、语言、意象、关键段落、theme_signals
  │
  ├─ [Claude] 主题分析 (第二轮)    → themes.json
  │     ├─ 汇总 theme_signals → 识别 3-5 核心主题
  │     ├─ 回溯补充逐章分析
  │     └─ 按人物/意象/文化/语言撰写专题总结
  │
  ├─ [Python] wordcloud_gen.py     → wordcloud_topic_*.png (专题词云)
  │     --mode themes --themes themes.json
  │
  ├─ [Python] report_builder.py    → report.md (完整报告)
  │
  └─ [Python] collect_deliverables.py → deliverables/ (成品整理)
        ├─ JSON → Markdown 自动转换
        └─ 收集所有 .png + .md 到统一目录
```

## 项目结构

```
ebook_analyst/
├── README.md                       # 本文件
├── SKILL.md                        # Claude Code Skill 定义
├── CLAUDE.md                       # Claude Code 项目上下文
├── requirements.txt                # Python 依赖
├── pyproject.toml
│
├── ebook_analyst/                  # Python 核心库
│   ├── epub_reader.py              # EPUB 解析器
│   ├── text_processor.py           # 中文分词、停用词
│   ├── keyword_extractor.py        # TF-IDF + TextRank
│   ├── wordcloud_maker.py          # 词云 (全书/逐章/专题)
│   ├── character_network.py        # 人物共现网络 (可选)
│   ├── report_builder.py           # Markdown 报告组装
│   ├── json_to_md.py               # JSON 分析 → Markdown 转换
│   └── collector.py                # 成品收集器
│
├── scripts/                        # CLI 入口
│   ├── parse_epub.py               # EPUB → book.json
│   ├── keyword_extract.py          # → keywords.json
│   ├── wordcloud_gen.py            # → PNG 词云
│   └── collect_deliverables.py     # → 收集成品
│
├── output/                         # 分析输出 (gitignore)
│   └── <书名>/
│       ├── report.md
│       ├── wordcloud_*.png
│       ├── data/ (book.json, keywords.json, themes.json...)
│       └── deliverables/ (整理后的成品目录)
│
└── temp/                           # EPUB 解压缓存 (gitignore)
```

## Claude Code Skill 交互式流程

整个分析流程设计为**交互式、逐步推进**。每阶段完成后，Skill 会：

1. 报告已完成的操作和输出文件
2. 说明下一步将做什么
3. **询问用户是否继续**（"继续"/"下一步"推进，"停止"/"整理"收集成品）

### 阶段一览

| 阶段 | 内容 | 实现 |
|------|------|------|
| 0 — 启动 | 解析 EPUB，确定分析策略 | Python |
| 1 — 机械提取 | 关键词 + 词云生成 | Python |
| 2 — 逐章深读 | 每章深度文学分析 | Claude |
| 3 — 跨章统整 | 主题分析 + 专题总结 | Claude |
| 4 — 报告组装 | 专题词云 + 最终报告 | Python |
| 5 — 整理成品 | JSON→MD + 收集到 deliverables/ | Python |

随时说"停止"或"整理"，即可将已完成的分析产物收集到统一目录。

## 整理成品

```bash
# 将所有 .png 和 .md 收集到 deliverables/ 目录
# 自动将 JSON 分析文件转换为 Markdown
python scripts/collect_deliverables.py output/<书名>
```

成品目录包含：
- `report.md` — 完整分析报告
- `chapters_analysis.md` — 逐章详解
- `themes.md` — 主题分析
- `keywords.md` — 关键词分析
- `wordcloud_*.png` — 所有词云图
- `character_network.png` — 人物关系图 (可选)
- `README.md` — 文件索引

## 可选功能

### 人物关系图

```bash
python -c "
from ebook_analyst.character_network import generate_character_network
generate_character_network(
    'output/<书名>/data/book.json',
    ['人物1', '人物2', '人物3', ...],
    'output/<书名>/character_network.png',
    min_edge_weight=2
)
"
```

### 专题词云（需先完成主题分析）

```bash
python scripts/wordcloud_gen.py output/<书名>/data/book.json \
    --mode themes \
    --themes output/<书名>/data/themes.json
```

## 依赖

- Python >= 3.10
- ebooklib — EPUB 解析
- jieba — 中文分词
- wordcloud + matplotlib — 词云生成
- networkx — 人物关系网络
- beautifulsoup4 + lxml — HTML 文本提取

## 示例输出

对迟子建《额尔古纳河右岸》(169,696 字) 的分析产出：

| 文件 | 大小 | 说明 |
|------|------|------|
| report.md | 44 KB | 完整分析报告 (386 行) |
| chapters_analysis.md | 19 KB | 4 章逐章详解 |
| themes.md | 11 KB | 5 大主题分析 |
| keywords.md | 6 KB | TF-IDF/TextRank 关键词 |
| wordcloud_full.png | 294 KB | 全书词云 |
| wordcloud_ch5~8.png | 280-293 KB | 4 张逐章词云 |
| wordcloud_topic_*.png | 5 张 | 5 张专题词云 |
| character_network.png | 358 KB | 16 人关系网络图 |
| **总计** | **~3 MB** | **15 个成品文件** |

### 识别的五大主题

1. **生死循环与萨满信仰** — 妮浩以命换命的牺牲
2. **传统文明与现代性的冲突** — 百年挤压下的文化消散
3. **记忆、讲述与文学救赎** — 故事作为抵抗遗忘的容器
4. **女性命运与民族史诗** — 以女性声音讲述的哀歌式民族志
5. **人与自然：鄂温克式的生态伦理** — 与驯鹿、河流、森林的共生哲学

---

## English

A local EPUB ebook analysis tool. Python handles mechanical tasks (EPUB parsing, jieba tokenization, word cloud generation), while Claude performs deep literary analysis (chapter-by-chapter close reading, theme identification, thematic synthesis). Output is a comprehensive Markdown report with embedded PNG figures.

**Quick start**: `pip install -r requirements.txt` → `python scripts/parse_epub.py <file.epub>` → say "analyze this book" in Claude Code.

**Interactive workflow**: Each stage completes with a prompt asking whether to continue. Say "stop" or "整理" at any point to collect all deliverables (.png + .md) into a single directory.
