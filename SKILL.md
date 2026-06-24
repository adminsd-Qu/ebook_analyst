# ebook-analyst Skill

分析 EPUB 电子书，生成包含词云、逐章详解、主题分析、专题总结等维度的完整深度报告。

## 触发条件

"分析这本电子书" / "分析 EPUB" / "analyze epub" / "分析 {书名}" / "/ebook-analyst"

## 核心规则

**只在阶段 2（逐章深读）结束后暂停一次**，等待用户确认。其余阶段自动推进，不询问。

### 暂停时的交互逻辑

逐章深读全部完成后，输出完整成果汇报 + 主动分析建议：

1. ✅ 已完成: 阶段 0-2 的所有产出（book.json / keywords.json / 词云 / chapters_analysis.json）
2. 💡 主动建议: 根据已读内容，提出 2-3 条可选的额外分析方向（如：人物关系网络、特定意象专题、文化背景考据、跨文本对比等）
3. ❓ 询问: "是否继续生成完整报告？"

用户回复处理：
- **"继续" / "好" / "生成报告"** → 自动依次完成阶段 3→4→5，不再暂停
- **"先做 X"** → 执行用户的额外需求 → 完成后再次询问"是否继续生成完整报告？"
- **"停止" / "整理"** → 跳到阶段 5 收集已完成的成品

### 自动推进规则

以下阶段**不询问用户**，完成时仅一行简要汇报：

| 阶段 | 完成后输出 |
|------|-----------|
| 0 — 启动 | 书名/作者/字数/章节数 + 选定的分析维度 |
| 1 — 机械提取 | 关键词数/高频词数/词云数 |
| 3 — 跨章统整 | 主题数/是否已回溯逐章/专题总结维度 |
| 4 — 报告组装 | report.md 路径 |
| 5 — 整理成品 | 收集文件数 + deliverables 路径 |

## 交互式执行流程

### 阶段 0: 启动（自动）
```bash
python scripts\parse_epub.py <epub_file>
```
阅读 book.json，判断书籍类型，从分析清单选择适用维度。
[自动继续到阶段 1]

### 阶段 1: 机械提取（自动）
```bash
python scripts\keyword_extract.py {book_dir}\data\book.json
python scripts\wordcloud_gen.py {book_dir}\data\book.json --max-words 200
python scripts\wordcloud_gen.py {book_dir}\data\book.json --mode chapters --max-words 150
```
[自动继续到阶段 2]

### 阶段 2: 逐章深读（⭐ 唯一暂停点）
依次阅读各章，按分析维度撰写。每章格式:
```json
{"chapter_index":0,"chapter_title":"","analysis":{"plot_summary":"","character_development":"","language_style":"","imagery_sensory":"","key_passages":[{"text":"","commentary":""}],"theme_signals":[],"cultural_elements":""}}
```
每章完成后追加到 `chapters_analysis.json`，简要汇报（主题线索 + token 消耗），直接继续下一章。
全部章节完成后 → **输出完整成果汇报 + 主动分析建议 + 询问是否继续**

### 阶段 3: 跨章统整（自动，用户确认后）
- 3a. 汇总 theme_signals → 识别 3-5 核心主题 → 写入 `themes.json`
- 3b. 回溯补充逐章分析（根据主题发现补充前文遗漏线索）
- 3c. 按人物/意象/文化/语言四维撰写专题总结
[自动继续到阶段 4]

### 阶段 4: 专题词云 + 报告组装（自动）
```bash
python scripts\wordcloud_gen.py {book_dir}\data\book.json --mode themes --themes {book_dir}\data\themes.json
python -c "from ebook_analyst.report_builder import build_report('{book_dir}', token_stats=[...])"
```
[自动继续到阶段 5]

### 阶段 5: 整理成品（自动）
```bash
python scripts\collect_deliverables.py {book_dir}
```
JSON→MD 自动转换 + 收集所有 .png/.md → `deliverables\` + 生成 README.md 索引。

---

## 分析清单

根据书籍类型动态启用：
- **小说/文学** → A叙事 B人物 C语言 D意象 E主题 F文化 G情感
- **非虚构/社科** → C语言 E主题 F文化 H知识密度
- **诗歌/散文** → C语言 D意象 G情感

暂停时建议的额外分析方向（按需提出 2-3 条）：
- 人物关系网络图（networkx 共现分析）
- 特定意象/符号的跨章追踪
- 历史文化背景考据
- 同类作品对比
- 语言风格量化分析（句长分布、对话密度等）
- 情感曲线绘制（逐章情感极性变化）

## 报告格式

- 交叉引用: 逐章详解末尾 `→ 本章主题线索: [主题A]`，主题分析 `(详见第X章)`
- 引文用 `>` 块引用，报告末尾附 Token 消耗统计表
