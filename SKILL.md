# ebook-analyst Skill

分析 EPUB 电子书，生成包含词云、逐章详解、主题分析、专题总结等维度的完整深度报告。

## 触发条件

"分析这本电子书" / "分析 EPUB" / "analyze epub" / "分析 {书名}" / "/ebook-analyst"

## 核心规则

**只在阶段 2（逐章深读）结束后暂停一次**，等待用户确认。其余阶段自动推进，不询问。

### 暂停时的交互逻辑

逐章深读全部完成后，输出完整成果汇报 + 主动分析建议：

1. ✅ 已完成: 阶段 0-2 的所有产出（book.json / keywords.json / 词云 / 逐章独立报告 / 结构化摘要）
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
| 0.5 — 按章导出 | 导出章节数 / 正文数 / 附录数 |
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
[自动继续到阶段 0.5]

### 阶段 0.5: 按章导出 txt（自动）

```bash
python -c "
import json, os, re
book_dir = r'{book_dir}'
with open(os.path.join(book_dir, 'data', 'book.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)
body_pattern = re.compile(r'简介|序|目录|自荐')
exported = 0
for ch in data['chapters']:
    is_body = ch['char_count'] >= 1000 and not body_pattern.search(ch['title'])
    label = '正文' if is_body else '附录'
    fname = os.path.join(book_dir, 'data', f'ch_{ch[\"index\"]}.txt')
    with open(fname, 'w', encoding='utf-8') as out:
        out.write(f'<!-- {label}: char_count={ch[\"char_count\"]} -->\n')
        out.write(ch['title'] + '\n\n' + ch['text'])
    if is_body:
        exported += 1
print(f'导出 {len(data[\"chapters\"])} 章（正文 {exported} 章，附录 {len(data[\"chapters\"]) - exported} 章）')
"
```

同步完成正文识别：
- 正文：char_count ≥ 1000 且标题不含"简介""序""目录""自荐"
- 附录：其余，跳过深读，报告中一句话标注

阶段 2 逐章深读时，每章只需 `Read data/ch_N.txt`。

[自动继续到阶段 1]

### 阶段 1: 机械提取（自动）
```bash
python scripts\keyword_extract.py {book_dir}\data\book.json
python scripts\wordcloud_gen.py {book_dir}\data\book.json
python scripts\wordcloud_gen.py {book_dir}\data\book.json --mode chapters
```
[自动继续到阶段 2]

---

### 阶段 2: 单元化逐章深读（⭐ 唯一暂停点）

每章作为一个**独立分析单元**，fire-and-forget。每个单元产出一份完整可独立阅读的 `.md` 报告 + 一份结构化 `.json` 摘要。

**核心纪律：**
- 一章进，全部产出出，释放上下文，下一章。
- 每章前后显式报告上下文消耗，引导用户关注容量。
- 上下文追踪文件 `data/_context_tracker.json` 提供会话中断后的连续性。

#### 步骤 2.1: 上下文预检

在处理第 N 章之前：

1. 检查 `data/_context_tracker.json` 是否存在：
   - 不存在 → 创建新追踪文件，`model_context_window` 设为 200000（当前模型上下文窗口）
   - 存在 → 读取累计消耗和剩余可用
2. 报告：

```
━━━ 第{N+1}/{total_chapters}章「{title}」({char_count:,}字，约占全书{percent}%) ━━━
上下文状态: 已用 {cumulative:,} / {window:,} tokens | 剩余 ~{remaining:,} tokens
```

3. 如剩余 < 20%（< 40000 tokens），暂停并建议：

> ⚠️ 上下文已用 {percent}%，剩余不足 20%。建议在此暂停，下次会话从第{N+1}章继续。
> 是否继续当前章节？

#### 步骤 2.2: 读取输入

- `Read data/ch_N.txt`（本章全文。N 为 `chapter_index`，零基）
- 参考 `data/keywords.json` 中 `chapter_keywords[N]` 获取本章 Top 关键词

#### 步骤 2.3: 生成独立分析报告

Write `data/ch_{N+1}_analysis.md`（注意：文件名用 1-based 的 {N+1}），按以下模板：

```markdown
# 第{N+1}章: {title} — 深度分析

| 属性 | 值 |
|------|-----|
| 章节序号 | {N+1} / {total_chapters} |
| 字数 | {char_count:,} |
| 全书占比 | {percent}% |
| 分析日期 | YYYY-MM-DD |

---

## 情节概要
[2-3段完整的情节概述，含关键事件及其在章节中的位置（开头/中部/结尾）]

## 人物分析
### 出场人物
- **{name}**: {状态 — 出场/退场/死亡/结婚/生育/冲突/离开}

### 人物关系变化
- {from} → {to}: {关系变化的描述}

## 语言与叙事
[语言风格、叙事技巧、修辞手法的分析]

## 意象与感官
### 新出现的意象
- **{element}**: {语境与象征意义}

### 重复出现的意象
- **{element}**: 已在第X、Y章出现

## 关键段落
> {≥80字原文引用}
> *-- {一句话语境说明} [维度: {所属维度}]*

*(保留4-6条关键段落)*

## 文化元素
[本章涉及的文化习俗、历史参照、社会背景分析]

## 主题线索
→ 本章主题信号: [{theme_A}] [{theme_B}] [{theme_C}]

## 本章关键词 (Top 10)
| 排名 | 关键词 | TF-IDF 权重 |
|------|--------|-------------|
| 1 | {word} | {weight:.4f} |

---

## 上下文消耗

| 项目 | 估算 Token |
|------|-----------|
| 原文输入 | {input_estimate:,} |
| 参考数据 | {ref_estimate:,} |
| 分析输出 | {output_estimate:,} |
| **本章合计** | **{chapter_total:,}** |
| 累计已消耗 | {cumulative:,} / {window:,} |
| 剩余可用 | ~{remaining:,} |

---
*独立报告: `data/ch_{N+1}_analysis.md`*
```

#### 步骤 2.4: 生成结构化摘要

Write `data/ch_N_digest.json`（注意：文件名用 0-based 的 {N}），维度拆分格式：

```json
{
  "chapter_index": {N},
  "chapter_title": "{title}",
  "char_count": {char_count},
  "analysis_md_path": "data/ch_{N+1}_analysis.md",
  "dimensions": {
    "narrative": {
      "synopsis": "",
      "key_events": [{"event": "", "location": "开头/中部/结尾"}]
    },
    "characters": {
      "appearing": [{"name": "", "status": "出场/退场/死亡/结婚/生育/冲突/离开"}],
      "relationships": [{"from": "", "to": "", "change": ""}]
    },
    "language": {
      "style_notes": "",
      "rhetoric_highlights": []
    },
    "imagery": {
      "new_elements": [{"element": "", "context": ""}],
      "recurring_elements": []
    },
    "culture": {
      "practices": [{"practice": "", "description": ""}]
    },
    "theme": {
      "signals": []
    }
  },
  "key_quotations": [
    {"text": "≥80 字原文", "context": "一句话语境", "dimension": "所属维度"}
  ],
  "context_consumption": {
    "chapter_input_estimate": 0,
    "reference_estimate": 0,
    "output_estimate": 0,
    "chapter_total": 0
  }
}
```

**设计意图：** `.md` 给人读（独立完整报告），`.json` 给阶段 3 按维度索引（narrative / characters / language / imagery / culture / theme），无需遍历全文章节报告。

每章保留 4-6 条 `key_quotations`，每条 ≥80 字原文，附语境和所属维度。

#### 步骤 2.5: 上下文后检

1. 估算本章消耗：
   - 原文输入 tokens ≈ `char_count × 2`（中文保守上界）
   - 参考数据 tokens ≈ 500（keywords.json 片段）
   - 分析输出 tokens ≈ 生成的 `.md` 文件字符数 × 1
2. 更新 `data/_context_tracker.json`：

```json
{
  "model_context_window": 200000,
  "chapters_processed": [
    {
      "chapter_index": 0,
      "chapter_title": "...",
      "input_estimate": 3400,
      "output_estimate": 2100,
      "chapter_total": 5500
    }
  ],
  "cumulative_input": 3400,
  "cumulative_output": 2100,
  "cumulative_total": 5500,
  "remaining_estimate": 194500
}
```

3. 报告：

```
✅ 第{N+1}章「{title}」处理完毕
   本章消耗: ~{chapter_total:,} tokens（输入 ~{input:,} + 输出 ~{output:,}）
   累计消耗: {cumulative:,} / {window:,} tokens
   剩余可用: ~{remaining:,} tokens
```

4. 释放本章原文上下文，进入下一章。

#### 全部章节完成后

1. 运行聚合脚本：
```bash
python scripts\aggregate_chapter_digests.py {book_dir}
```
这将所有 `ch_N_digest.json` 合并为 `chapter_summaries.json` + `chapters_analysis.json`（兼容阶段 3 和阶段 4 的格式）。

2. **输出完整成果汇报 + 主动分析建议 + 询问是否继续**

---

### 阶段 3: 跨章统整（自动，用户确认后）

输入源：`chapter_summaries.json` + `chapters_analysis.json`（由聚合脚本生成）

读取方式：按维度索引读取 summaries 对应区块，不加载原文。

回退原文的判定——仅当同时满足以下任一条件时，才 Read 对应 ch_N.txt 的对应段落：

1. 引文不足：某章涉及目标主题的 key_quotations 少于 2 条
2. 状态矛盾：同一人物在相邻两章 characters.appearing 的状态有逻辑冲突
   （如"第 N 章死亡，第 N+1 章出场"）
3. 意象断链：某意象在 ≥3 章的 imagery 中出现，但某章的 imagery 未记录
4. 引文过短：需要引用的 key_quotation 的 text < 50 字

回退时操作：直接 Read 对应章节的 data/ch_N.txt，定位到相关段落。
仅读取必要片段，读后不保留在上下文。

不满足以上条件时，禁止回读原文。

- 3a. 遍历各章 dimensions.theme.signals → 识别 3-5 核心主题 → 写入 `themes.json`
- 3b. 回溯补充：根据识别出的主题，按维度索引查 summaries，补充前文遗漏线索
- 3c. 专题总结：按人物/意象/文化/语言四维撰写
       - 人物专题 → 汇总各章 dimensions.characters
       - 意象专题 → 汇总各章 dimensions.imagery
       - 文化专题 → 汇总各章 dimensions.culture
       - 语言专题 → 汇总各章 dimensions.language
[自动继续到阶段 4]

### 阶段 4: 专题词云 + 报告组装（自动）
```bash
python scripts\wordcloud_gen.py {book_dir}\data\book.json --mode themes --themes {book_dir}\data\themes.json
python -c "from ebook_analyst.report_builder import build_report; build_report(r'{book_dir}', token_stats=[...])"
```
[自动继续到阶段 5]

### 阶段 5: 整理成品（自动）
```bash
python scripts\collect_deliverables.py {book_dir}
```
自动收集所有成品：JSON→MD 转换、逐章独立报告、词云图、完整报告 → `deliverables\` + 生成 README.md 索引。

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

## 词云个性化

`wordcloud_gen.py` 支持以下参数定制词云外观：

```bash
# 查看可用中文字体
python scripts\wordcloud_gen.py <book.json> --list-fonts

# 切换配色方案 (matplotlib colormap)
python scripts\wordcloud_gen.py <book.json> --colormap plasma    # 暖色渐变
python scripts\wordcloud_gen.py <book.json> --colormap turbo     # 高对比彩虹
python scripts\wordcloud_gen.py <book.json> --colormap cool      # 冷色系
python scripts\wordcloud_gen.py <book.json> -c viridis           # 默认 (短选项 -c)

# 切换字体
python scripts\wordcloud_gen.py <book.json> --font stkaiti       # 华文楷体
python scripts\wordcloud_gen.py <book.json> --font msyhbd        # 微软雅黑粗体
python scripts\wordcloud_gen.py <book.json> --font stzhongs      # 华文中宋

# 调整标题字号（默认 24）
python scripts\wordcloud_gen.py <book.json> --title-fontsize 32

# 组合使用
python scripts\wordcloud_gen.py <book.json> --mode chapters \
    --colormap cividis --font stkaiti --title-fontsize 28
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-c` / `--colormap` | `viridis` | matplotlib 配色：plasma / inferno / magma / turbo / cividis / cool / winter / autumn / spring |
| `--font` | 自动（微软雅黑粗体） | 字体简称，`--list-fonts` 查看全部可用 |
| `--title-fontsize` | `24` | 标题字号（pt） |
| `--max-words` | `100` | 词云最大词数 |

## 报告格式

- 交叉引用: 逐章详解末尾 `→ 本章主题线索: [主题A]`，主题分析 `(详见第X章)`
- 引文用 `>` 块引用，报告末尾附 Token 消耗统计表
