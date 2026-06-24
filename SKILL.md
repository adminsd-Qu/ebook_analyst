# ebook-analyst Skill

分析 EPUB 电子书，生成包含词云、逐章详解、主题分析、专题总结等维度的完整深度报告。

## 触发条件

"分析这本电子书" / "分析 EPUB" / "analyze epub" / "分析 {书名}" / "/ebook-analyst"

## 报告规则

每阶段完成后用 3 行汇报:
1. ✅ 已完成项 + 关键数据
2. 🔄 下一步内容 + 预估消耗
3. ❓ 是否继续? (回复"继续"/"下一步"推进，"停止"/"整理"→阶段5收集成品)

## 交互式执行流程

### 阶段 0: 启动
```bash
python scripts/parse_epub.py <epub_file>
```
阅读 book.json，判断书籍类型，从分析清单选择适用维度。
[按报告规则汇报，询问是否继续]

### 阶段 1: 机械提取
等待用户确认后:
```bash
python scripts/keyword_extract.py output/{book}/data/book.json
python scripts/wordcloud_gen.py output/{book}/data/book.json --max-words 200
python scripts/wordcloud_gen.py output/{book}/data/book.json --mode chapters --max-words 150
```
[按报告规则汇报，询问是否继续]

### 阶段 2: 逐章深读
等待用户确认后，依次阅读各章，按分析维度撰写。每章格式:
```json
{"chapter_index":0,"chapter_title":"","analysis":{"plot_summary":"","character_development":"","language_style":"","imagery_sensory":"","key_passages":[{"text":"","commentary":""}],"theme_signals":[],"cultural_elements":""}}
```
每章完成后追加到 `chapters_analysis.json`。每章结束时简要汇报(主题线索 + token消耗)并询问是否继续下一章。
[用户可随时说"跳过"/"停止"]

### 阶段 3: 跨章统整
等待用户确认后:
- 3a. 汇总 theme_signals → 识别 3-5 核心主题 → 写入 `themes.json`
- 3b. 回溯补充逐章分析
- 3c. 按人物/意象/文化/语言四维撰写专题总结
[按报告规则汇报，询问是否继续]

### 阶段 4: 专题词云 + 报告组装
等待用户确认后:
```bash
python scripts/wordcloud_gen.py output/{book}/data/book.json --mode themes --themes output/{book}/data/themes.json
python -c "from ebook_analyst.report_builder import build_report; build_report('output/{book}', token_stats=[...])"
```
[按报告规则汇报，询问是否整理]

### 阶段 5: 整理成品
用户说"停止"/"整理"/"收集"时触发:
```bash
python scripts/collect_deliverables.py output/{book}
```
JSON→MD 自动转换 + 收集所有 .png/.md → `deliverables/` + 生成 README.md 索引。

---

## 分析清单

根据书籍类型动态启用：
- **小说/文学** → A叙事 B人物 C语言 D意象 E主题 F文化 G情感
- **非虚构/社科** → C语言 E主题 F文化 H知识密度
- **诗歌/散文** → C语言 D意象 G情感

完整清单详见 CLAUDE.md。

## 报告格式

- 交叉引用: 逐章详解末尾 `→ 本章主题线索: [主题A]`，主题分析 `(详见第X章)`
- 引文用 `>` 块引用，报告末尾附 Token 消耗统计表
