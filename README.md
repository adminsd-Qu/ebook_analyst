# ebook_analyst — EPUB 电子书智能分析工具

> ⚠️ 本工具会让 AI 至少通读一遍完整原文，会产生**大量上下文和 token 消耗**，请谨慎使用。

将 EPUB 电子书解析为结构化数据，结合 Python 机械处理与 Claude 文学分析，生成包含**词云、逐章详解、主题分析、专题总结**的完整深度报告。

## 功能一览

| 分析维度 | 说明 | 实现 |
|---------|------|------|
| 📖 全书信息 | 书名、作者、字数、章节结构 | Python (ebooklib) |
| 🔑 关键词提取 | TF-IDF + TextRank Top 50 | Python (jieba) |
| ☁️ 全书词云 | 中文词云，自动字体适配 | Python (wordcloud) |
| ☁️ 逐章词云 | 每章独立词云 | Python |
| 📝 逐章详解 | 情节、人物、语言、意象、关键段落 | Claude 深度阅读 |
| 🎯 主题分析 | 3–5 个核心主题，跨章发展脉络 | Claude 跨章统整 |
| ☁️ 专题词云 | 每个主题独立词云 | Python + Claude |
| 📊 专题总结 | 人物、意象、文化、语言四维总结 | Claude 综合 |
| 👥 人物关系图 | 共现网络分析 | Python (networkx) |
| 📄 报告组装 | Markdown 报告 + Token 统计 | Python |

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 解析 EPUB（输出到 EPUB 同目录下的 <书名>/ 子目录）
python scripts\parse_epub.py "D:\books\额尔古纳河右岸.epub"
# → 输出到 D:\books\额尔古纳河右岸\

# 3. 提取关键词
python scripts\keyword_extract.py D:\books\额尔古纳河右岸\data\book.json

# 4. 生成词云
python scripts\wordcloud_gen.py D:\books\额尔古纳河右岸\data\book.json
python scripts\wordcloud_gen.py D:\books\额尔古纳河右岸\data\book.json --mode chapters

# 5. 启动 Claude 深度分析（在 Claude Code 中说）
#    "分析 D:\books\额尔古纳河右岸"
#    或输入 /ebook-analyst 调用 Skill
```

> 💡 也可直接在 Claude Code 对话中发送 .epub 文件路径并调用 `/ebook-analyst`，省去命令行切换目录。

## 完整工作流

```
EPUB 文件
  │
  ├─ [Python] parse_epub.py              → book.json (元数据 + 章节文本)
  ├─ [Python] 按章导出 txt               → data/ch_N.txt (阶段 0.5)
  ├─ [Python] keyword_extract.py         → keywords.json (关键词 + 词频)
  ├─ [Python] wordcloud_gen.py           → wordcloud_*.png (全书 + 逐章词云)
  │
  ├─ [Claude] 逐章深读 (阶段 2)           → data/ch_N+1_analysis.md + ch_N_digest.json
  ├─ [Python] aggregate_chapter_digests  → chapter_summaries.json + chapters_analysis.json
  │
  ├─ [Claude] 主题分析 (阶段 3)           → themes.json
  │     ├─ 汇总 theme_signals → 识别 3–5 核心主题
  │     ├─ 回溯补充逐章分析
  │     └─ 按人物 / 意象 / 文化 / 语言撰写专题总结
  │
  ├─ [Python] wordcloud_gen.py           → wordcloud_topic_*.png (专题词云)
  │     --mode themes --themes themes.json
  │
  ├─ [Python] report_builder.py          → report.md (完整报告)
  │
  └─ [Python] collect_deliverables.py    → deliverables/ (成品整理)
        ├─ JSON → Markdown 自动转换
        └─ 收集所有 .png + .md 到统一目录
```

## 交互式流程

分析过程在**逐章深读（阶段 2）完成后暂停一次**，其余阶段自动推进：

| 阶段 | 内容 | 实现 | 交互 |
|------|------|------|------|
| 0 — 启动 | 解析 EPUB，确定分析策略 | Python | 自动 |
| 0.5 — 导出 | 按章导出纯文本 txt | Python | 自动 |
| 1 — 机械提取 | 关键词 + 词云生成 | Python | 自动 |
| 2 — 逐章深读 | 每章独立深度文学分析 | Claude | ⭐ 暂停询问 |
| 3 — 跨章统整 | 主题分析 + 专题总结 | Claude | 自动 |
| 4 — 报告组装 | 专题词云 + 最终报告 | Python | 自动 |
| 5 — 整理成品 | JSON→MD + 收集到 deliverables\ | Python | 自动 |

阶段 2 暂停时，Claude 会汇报已完成成果，提出 2–3 条额外分析建议，并询问是否继续。用户回复"继续"后，阶段 3→4→5 一气呵成。

## 项目结构

```
ebook_analyst/
├── README.md
├── SKILL.md                          # Claude Code Skill 定义
├── CLAUDE.md                         # Claude Code 项目上下文
├── requirements.txt                  # Python 依赖
├── pyproject.toml
│
├── ebook_analyst/                    # Python 核心库
│   ├── epub_reader.py                # EPUB 解析器
│   ├── text_processor.py             # 中文分词、停用词过滤
│   ├── keyword_extractor.py          # TF-IDF + TextRank 关键词
│   ├── wordcloud_maker.py            # 词云生成（全书 / 逐章 / 专题）
│   ├── character_network.py          # 人物共现网络（可选）
│   ├── digest_aggregator.py          # 逐章摘要 → 合集 JSON
│   ├── report_builder.py             # Markdown 报告组装
│   ├── json_to_md.py                 # JSON 分析 → Markdown 转换
│   └── collector.py                  # 成品收集器
│
└── scripts/                          # CLI 入口
    ├── parse_epub.py                 # EPUB → book.json
    ├── keyword_extract.py            # → keywords.json
    ├── wordcloud_gen.py              # → PNG 词云
    ├── aggregate_chapter_digests.py  # → 聚合摘要
    └── collect_deliverables.py       # → 整理成品
```

## CLI 参考

### parse_epub.py

```bash
python scripts\parse_epub.py <file.epub>
```

解析 EPUB 文件，输出 `book.json`（含元数据、章节结构、纯文本）到 EPUB 同目录下的 `<书名>/data/`。

### keyword_extract.py

```bash
python scripts\keyword_extract.py <book_dir>\data\book.json
```

基于全书和逐章文本，用 TF-IDF 和 TextRank 各提取 Top 50 关键词，输出 `keywords.json`。

### wordcloud_gen.py

```bash
# 全书词云
python scripts\wordcloud_gen.py <book_dir>\data\book.json

# 逐章词云（跳过字数 < 1000 的章节）
python scripts\wordcloud_gen.py <book_dir>\data\book.json --mode chapters

# 专题词云（需先生成 themes.json）
python scripts\wordcloud_gen.py <book_dir>\data\book.json --mode themes --themes <book_dir>\data\themes.json
```

**参数：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--mode` | `full` | `full` / `chapters` / `themes` |
| `--themes` | — | themes.json 路径（mode=themes 时必填） |
| `-c` `--colormap` | `viridis` | plasma / inferno / magma / turbo / cividis / cool / winter / autumn / spring |
| `--font` | 自动 | 字体简称，`--list-fonts` 查看可用 |
| `--title-fontsize` | `24` | 标题字号（pt） |
| `--max-words` | `100` | 词云最大词数 |
| `--list-fonts` | — | 列出可用中文字体后退出 |

### 可用中文字体

<!-- font-table-start -->

| 简称 | 字体文件名 | 中文名称 |
|------|----------|---------|
| msyhbd | 微软雅黑粗体.TTF | 微软雅黑粗体 |
| stkaiti | 华文楷体.TTF | 华文楷体 |
| stzhongs | 华文中宋.TTF | 华文中宋 |
| hanyichengxing | 汉仪程行简.ttf | 汉仪程行简 |
| hukangxingkai | 华康行楷体 W5.ttf | 华康行楷体 |
| mengmiao | 三极萌喵简体.ttf | 三极萌喵简体 |
| xiquemeihua | 喜鹊梅花楷简繁(字跳网络企业版).ttf | 喜鹊梅花楷 |
| zihunguizhou | 字魂贵州省博物馆联名体.ttf | 字魂贵州省博物馆联名体 |

<!-- font-table-end -->

```bash
# 查看可用字体
python scripts\wordcloud_gen.py --list-fonts

# 指定字体（所有字体统一在项目 ebook_analyst/fonts/ 目录下）
python scripts\wordcloud_gen.py <book.json> --font stkaiti
python scripts\wordcloud_gen.py <book.json> --font mengmiao
```

### aggregate_chapter_digests.py

```bash
python scripts\aggregate_chapter_digests.py <book_dir>
```

将阶段 2 各章独立产出的 `ch_N_digest.json` 聚合为 `chapter_summaries.json` + `chapters_analysis.json`，供阶段 3 按维度索引读取。

### collect_deliverables.py

```bash
python scripts\collect_deliverables.py <book_dir>
```

收集所有成品（.png + .md）到 `deliverables\` 目录，并生成 README.md 文件索引。自动将 JSON 分析文件转换为 Markdown。

## 可选功能

### 人物关系图

```bash
python -c "from ebook_analyst.character_network import generate_character_network; generate_character_network('D:\\books\\额尔古纳河右岸\\data\\book.json', ['人物1', '人物2', '人物3'], 'D:\\books\\额尔古纳河右岸\\character_network.png', min_edge_weight=2)"
```

基于段落级共现统计生成人物关系网络图。`min_edge_weight` 控制连线最低共现次数（默认 3）。

## 中间数据格式

工具链各阶段通过标准化的 JSON 文件传递数据：

| 文件 | 生成阶段 | 说明 |
|------|---------|------|
| `book.json` | 阶段 0 | 元数据 + 章节文本 |
| `data/ch_N.txt` | 阶段 0.5 | 按章导出的纯文本全文 |
| `keywords.json` | 阶段 1 | TF-IDF + TextRank 关键词 |
| `data/ch_{N+1}_analysis.md` | 阶段 2 | 每章独立分析报告（可独立阅读） |
| `data/ch_N_digest.json` | 阶段 2 | 每章结构化摘要（供聚合用） |
| `data/_context_tracker.json` | 阶段 2 | 上下文消耗追踪（支持中断恢复） |
| `chapter_summaries.json` | 聚合 | 按维度拆分的合集摘要 |
| `chapters_analysis.json` | 聚合 | 文学分析合集 |
| `themes.json` | 阶段 3 | 主题分析 + 专题总结 |
| `report.md` | 阶段 4 | 完整分析报告 |
| `deliverables/` | 阶段 5 | 所有成品统一目录 |

## 依赖

- Python >= 3.10
- ebooklib — EPUB 解析
- jieba — 中文分词
- wordcloud + matplotlib — 词云生成
- networkx — 人物关系网络（可选）
- beautifulsoup4 + lxml — HTML 文本提取
- pillow — 图片处理

## 示例输出

以迟子建《额尔古纳河右岸》（约 200,000 字）为例：

| 文件 | 说明 |
|------|------|
| `report.md` | 完整分析报告 |
| `chapters_analysis.md` | 逐章详解 |
| `themes.md` | 五大主题分析 |
| `keywords.md` | TF-IDF / TextRank 关键词 |
| `wordcloud_full.png` | 全书词云 |
| `wordcloud_ch5~8.png` | 逐章词云（短章自动跳过） |
| `wordcloud_topic_*.png` | 专题词云 |
| `character_network.png` | 人物关系网络图 |

**识别的五大主题：**

1. **万物有灵：自然崇拜与人的归属** — 鄂温克族的萨满信仰与山林精神世界
2. **文明碰撞与山林挽歌** — 现代文明冲击下游猎民族的生存困境
3. **生死循环与萨满牺牲** — 死亡叙事中的宗教意涵与救赎
4. **禁忌之爱与氏族伦理** — 个体情感与部落规范的冲突
5. **记忆、讲述与艺术作为对抗遗忘** — 口头传统与文字书写的时间之战
