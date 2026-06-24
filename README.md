# ebook_analyst — 本地 EPUB 电子书智能分析工具

[English](README_ENG.md) | 中文

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

## 快速开始（Windows环境）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 解析 EPUB（输出默认到 EPUB 同目录）
python scripts\parse_epub.py "D:\books\山河纪事.epub" # 引用改为你的epub文件地址
# → 输出到 D:\books\山河纪事\

# 3. 提取关键词
python scripts\keyword_extract.py D:\books\山河纪事\data\book.json
#                                 ^^^^^^^^^^^^^^^^^
#                           这是上一条指令创建的输出文件夹的路径，后面添加“\data\book.json”

# 4. 生成词云
python scripts\wordcloud_gen.py D:\books\山河纪事\data\book.json
python scripts\wordcloud_gen.py D:\books\山河纪事\data\book.json --mode chapters
#                                 ^^^^^^^^^^^^^^^^^
#                                       同上

# 5. 启动 Claude 深度分析（在 Claude Code 中说）
#    "分析 D:\books\山河纪事"
#    或 "/ebook-analyst" 调用此 Skill
```

```bash
# 您也可以直接在 Claude Code 中引用本脚本路径，发送您的 .epub 文件路径并调用此功能开始分析（建议，命令行操作改目录比较麻烦）。
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
└── temp/                           # EPUB 解压缓存 (gitignore)
```

## Claude Code Skill 交互式流程

整个分析流程在**逐章深读（阶段 2）完成后暂停一次**，其余阶段自动推进：

1. 阶段 0-1 自动执行（解析 + 关键词 + 词云）
2. 阶段 2 逐章深读完成后暂停，输出成果汇报 + 主动提出 2-3 条额外分析建议
3. 用户回复"继续" → 阶段 3→4→5 一气呵成，不再暂停
4. 用户提出额外需求 → 完成需求后再次询问是否生成报告
5. 随时说"停止"或"整理" → 收集已完成的成品

### 阶段一览

| 阶段 | 内容 | 实现 | 交互 |
|------|------|------|------|
| 0 — 启动 | 解析 EPUB，确定分析策略 | Python | 自动 |
| 1 — 机械提取 | 关键词 + 词云生成 | Python | 自动 |
| 2 — 逐章深读 | 每章深度文学分析 | Claude | ⭐ 暂停询问 |
| 3 — 跨章统整 | 主题分析 + 专题总结 | Claude | 自动 |
| 4 — 报告组装 | 专题词云 + 最终报告 | Python | 自动 |
| 5 — 整理成品 | JSON→MD + 收集到 deliverables\ | Python | 自动 |

## 整理成品

```bash
# 将所有 .png 和 .md 收集到 deliverables\ 目录
# 自动将 JSON 分析文件转换为 Markdown
python scripts\collect_deliverables.py D:\books\山河纪事
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
python -c "from ebook_analyst.character_network import generate_character_network; generate_character_network('D:\\books\\山河纪事\\data\\book.json', ['人物1', '人物2', '人物3'], 'D:\\books\\山河纪事\\character_network.png', min_edge_weight=2)"
```

### 专题词云（需先完成主题分析）

```bash
python scripts\wordcloud_gen.py D:\books\山河纪事\data\book.json --mode themes --themes D:\books\山河纪事\data\themes.json
```

## 依赖

- Python >= 3.10
- ebooklib — EPUB 解析
- jieba — 中文分词
- wordcloud + matplotlib — 词云生成
- networkx — 人物关系网络
- beautifulsoup4 + lxml — HTML 文本提取

## 示例输出

对陈墨《山河纪事》(约 180,000 字) 的分析产出：

| 文件 | 大小 | 说明 |
|------|------|------|
| report.md | 44 KB | 完整分析报告 (约 400 行) |
| chapters_analysis.md | 19 KB | 6 章逐章详解 |
| themes.md | 11 KB | 5 大主题分析 |
| keywords.md | 6 KB | TF-IDF/TextRank 关键词 |
| wordcloud_full.png | 294 KB | 全书词云 |
| wordcloud_ch1~6.png | 280-293 KB | 6 张逐章词云 |
| wordcloud_topic_*.png | 5 张 | 5 张专题词云 |
| character_network.png | 358 KB | 12 人关系网络图 |
| **总计** | **~3 MB** | **15 个成品文件** |

### 识别的五大主题

1. **家族兴衰与历史变迁** — 三代人的命运与百年中国的激荡
2. **个人理想与时代洪流** — 知识分子的坚守与妥协
3. **乡土记忆与文化认同** — 离散、回归与精神家园的重建
4. **爱情与命运的纠缠** — 战乱中的离合悲欢
5. **传统工艺的传承与消亡** — 匠人精神的最后守望

