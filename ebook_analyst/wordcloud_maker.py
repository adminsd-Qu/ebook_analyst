"""词云生成器 — 支持全书、逐章、专题三种模式。

自动检测并配置中文字体，确保中文渲染正常。
"""

import json
from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")  # 非交互式后端
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from wordcloud import WordCloud

from ebook_analyst.text_processor import segment


def _find_chinese_font() -> str:
    """自动检测系统中可用的中文字体路径。"""
    # Windows 字体路径和优先级
    font_dir = Path("C:/Windows/Fonts")
    candidates = [
        font_dir / "msyhbd.ttc",    # 微软雅黑粗体
        font_dir / "STKAITI.TTF",   # 华文楷体
        font_dir / "STZHONGS.TTF",  # 华文中宋
    ]

    for font_path in candidates:
        if font_path.exists():
            return str(font_path)

    # Linux / macOS 回退
    import matplotlib.font_manager as fm

    for f in fm.fontManager.ttflist:
        if any(
            keyword in f.name.lower()
            for keyword in ["hei", "song", "ming", "kai", "cjk", "noto sans"]
        ):
            return f.fname

    # 最终回退
    print("警告: 未找到任何中文字体，词云可能无法正常显示中文。")
    return str(font_dir / "msyhbd.ttc")


_FONT_PATH: Optional[str] = None


def get_font_path() -> str:
    """获取缓存的字体路径。"""
    global _FONT_PATH
    if _FONT_PATH is None:
        _FONT_PATH = _find_chinese_font()
    return _FONT_PATH


# 字体简称 → 文件名映射（优先从 README.md 解析，失败时回退硬编码）
def _load_font_map() -> dict[str, dict[str, str]]:
    """从 README.md 解析字体映射表。

    返回: {简称: {"filename": 文件名, "name_zh": 中文名}}
    解析失败时返回空 dict，调用方回退到硬编码默认值。
    """
    readme_path = Path(__file__).resolve().parent.parent / "README.md"
    if not readme_path.exists():
        return {}

    try:
        content = readme_path.read_text(encoding="utf-8")
    except Exception:
        return {}

    font_map = {}
    in_table = False

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("<!-- font-table-start"):
            in_table = True
            continue
        if stripped.startswith("<!-- font-table-end"):
            break

        if not in_table:
            continue

        # 跳过表头和分隔行
        if "简称" in stripped or stripped.startswith("|---") or stripped.startswith("|--"):
            continue

        # 解析: | 简称 | 文件名 | 中文名 |
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 4:
            short_name = parts[1]
            filename = parts[2]
            name_zh = parts[3]
            if short_name and filename:
                font_map[short_name] = {"filename": filename, "name_zh": name_zh}

    return font_map


_FONT_NAME_MAP_FALLBACK = {
    "msyhbd":    "msyhbd.ttc",
    "stkaiti":   "STKAITI.TTF",
    "stzhongs":  "STZHONGS.TTF",
}

# 字体完整信息（优先从 README 解析，回退硬编码）
_FONT_MAP_DATA = _load_font_map()

# 简称 → 文件名映射
_FONT_NAME_MAP: dict[str, str] = (
    {k: v["filename"] for k, v in _FONT_MAP_DATA.items()}
    if _FONT_MAP_DATA
    else _FONT_NAME_MAP_FALLBACK
)


def resolve_font_path(name: str) -> str:
    """根据字体简称解析为完整路径。

    参数:
        name: 字体简称（如 "msyhbd", "stkaiti", "stzhongs"）

    返回:
        字体文件的绝对路径，找不到时回退到默认字体
    """
    font_dir = Path("C:/Windows/Fonts")
    filename = _FONT_NAME_MAP.get(name.lower())
    if filename:
        path = font_dir / filename
        if path.exists():
            return str(path)
    # 也尝试将 name 直接作为文件名
    direct = font_dir / name
    if direct.exists():
        return str(direct)
    # 回退到自动检测
    print(f"警告: 字体 '{name}' 未找到，使用默认字体")
    return get_font_path()


def list_available_fonts() -> dict[str, tuple[str, str]]:
    """列出当前系统可用的中文字体。

    返回: {简称: (完整路径, 中文名)}
    """
    font_dir = Path("C:/Windows/Fonts")
    # 优先用 README 解析结果（含中文名），回退硬编码
    font_map = _FONT_MAP_DATA if _FONT_MAP_DATA else {
        k: {"filename": v, "name_zh": ""} for k, v in _FONT_NAME_MAP_FALLBACK.items()
    }
    available = {}
    for short_name, info in sorted(font_map.items()):
        path = font_dir / info["filename"]
        if path.exists():
            available[short_name] = (str(path), info.get("name_zh", ""))
    return available


class WordcloudMaker:
    """中文词云生成器。

    支持三种模式:
    - full: 全书词云
    - chapters: 逐章词云
    - themes: 专题词云
    """

    def __init__(self, font_path: Optional[str] = None):
        self.font_path = font_path or get_font_path()
        self._verify_font()

    def _verify_font(self):
        """验证字体文件存在。"""
        if not Path(self.font_path).exists():
            print(f"警告: 字体文件不存在: {self.font_path}")
            print("词云中的中文可能无法正常显示。")

    def generate(
        self,
        text: str,
        output_path: str | Path,
        width: int = 1200,
        height: int = 800,
        max_words: int = 100,
        background_color: str = "white",
        colormap: str = "viridis",
        title: Optional[str] = None,
        title_fontsize: int = 24,
    ) -> Path:
        """从文本生成词云图片。

        参数:
            text: 输入文本
            output_path: 输出 PNG 路径
            width, height: 图片尺寸
            max_words: 最大词数
            background_color: 背景色
            colormap: 颜色映射（matplotlib colormap 名称，如 viridis/plasma/inferno/turbo/cool/winter）
            title: 可选的图片标题
            title_fontsize: 标题字号（默认 24）

        返回:
            输出文件路径
        """
        # 分词
        words = segment(text, remove_stopwords=True)
        word_text = " ".join(words)

        if not word_text.strip():
            raise ValueError("分词后无有效词语，无法生成词云")

        # 生成词云
        wc = WordCloud(
            font_path=self.font_path,
            width=width,
            height=height,
            max_words=max_words,
            background_color=background_color,
            colormap=colormap,
            max_font_size=160,
            min_font_size=16,
            prefer_horizontal=0.85,
            margin=8,
            relative_scaling=0.5,
            collocations=False,
            random_state=42,
        )
        wc.generate(word_text)

        # 渲染并保存
        fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        if title:
            title_font = FontProperties(fname=self.font_path, size=title_fontsize)
            ax.set_title(title, fontproperties=title_font, pad=14)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(
            str(output_path),
            bbox_inches="tight",
            pad_inches=0.2,
            dpi=150,
            facecolor=background_color,
        )
        plt.close(fig)

        return output_path

    def generate_full(
        self,
        chapters: list[dict],
        output_path: str | Path,
        **kwargs,
    ) -> Path:
        """生成全书词云。"""
        full_text = "\n".join(ch["text"] for ch in chapters)
        return self.generate(
            full_text,
            output_path,
            title="全书词云",
            **kwargs,
        )

    def generate_chapters(
        self,
        chapters: list[dict],
        output_dir: str | Path,
        **kwargs,
    ) -> list[Path]:
        """为每章生成独立词云。"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = []
        for ch in chapters:
            # 跳过过短的章节（前言、作者介绍等）
            if ch["char_count"] < 1000:
                continue

            ch_num = ch["index"] + 1
            path = output_dir / f"wordcloud_ch{ch_num}.png"
            self.generate(
                ch["text"],
                path,
                title=f"第{ch_num}章: {ch['title']}",
                **kwargs,
            )
            paths.append(path)

        return paths

    def generate_themes(
        self,
        themes_data: dict,
        chapters: list[dict],
        output_dir: str | Path,
        **kwargs,
    ) -> list[Path]:
        """根据主题分析结果生成专题词云。

        参数:
            themes_data: themes.json 数据，每个主题带 chapter_indices
            chapters: 章节列表
            output_dir: 输出目录
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = []
        themes = themes_data.get("themes", [])
        for theme in themes:
            theme_name = theme["name"]
            # 用主题自身的元文本（引文 + 定义 + 发展脉络）作为词云文本源，
            # 确保不同主题的词云内容有实质性差异
            parts = []
            quotes = theme.get("representative_quotes", [])
            if quotes:
                parts.extend(quotes)
            definition = theme.get("definition", "")
            if definition:
                parts.append(definition)
            development = theme.get("development", "")
            if development:
                parts.append(development)
            theme_text = "\n".join(parts)

            # 元文本过短时（极端情况），回退到关联章节全文
            if len(theme_text) < 200:
                indices = theme.get("chapter_indices", [])
                if not indices:
                    theme_text = "\n".join(ch["text"] for ch in chapters)
                else:
                    theme_text = "\n".join(
                        ch["text"]
                        for ch in chapters
                        if ch["index"] in indices
                    )

            safe_name = theme_name.replace("/", "_").replace(" ", "_")
            path = output_dir / f"wordcloud_topic_{safe_name}.png"
            self.generate(
                theme_text,
                path,
                title=f"专题词云: {theme_name}",
                **kwargs,
            )
            paths.append(path)

        return paths
