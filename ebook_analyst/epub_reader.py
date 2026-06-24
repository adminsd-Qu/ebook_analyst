"""EPUB 解析器 — 提取元数据、章节结构和纯文本内容。

EPUB 文件是 ZIP 压缩包，包含 XHTML/HTML 格式的章节文件。
本模块按 spine 顺序遍历所有文档，提取干净的纯文本。
"""

import json
import re
import warnings
from pathlib import Path

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from ebooklib import epub

# EPUB 中的 XHTML 文件可能被误检测为 HTML，抑制不必要的警告
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


class EpubReader:
    """解析 EPUB 文件，提取元数据和章节文本。"""

    def __init__(self, epub_path: str | Path):
        self.epub_path = Path(epub_path)
        if not self.epub_path.exists():
            raise FileNotFoundError(f"EPUB 文件不存在: {self.epub_path}")
        self.book = epub.read_epub(str(self.epub_path))

    def get_metadata(self) -> dict:
        """提取书籍元数据。"""
        meta = {}

        # 书名
        titles = self.book.get_metadata("DC", "title")
        if titles:
            meta["title"] = titles[0][0]

        # 作者
        creators = self.book.get_metadata("DC", "creator")
        if creators:
            meta["author"] = creators[0][0]

        # 语言
        languages = self.book.get_metadata("DC", "language")
        if languages:
            meta["language"] = languages[0][0]

        return meta

    def get_chapters(self) -> list[dict]:
        """按 spine 顺序提取所有章节的纯文本内容。

        返回:
            chapters: [{"index": 0, "title": "...", "text": "...", "char_count": 0}, ...]
        """
        chapters = []
        spine_items = list(self.book.spine)

        for index, item in enumerate(spine_items):
            try:
                doc = self.book.get_item_with_id(item[0])
                if doc is None:
                    continue

                content = doc.get_content()
                soup = BeautifulSoup(content, "lxml")

                # 尝试提取章节标题
                title = self._extract_chapter_title(soup, index)

                # 提取纯文本
                text = self._extract_clean_text(soup)

                if not text.strip():
                    continue  # 跳过空章节

                chapters.append(
                    {
                        "index": index,
                        "title": title,
                        "text": text,
                        "char_count": len(text),
                    }
                )
            except Exception as e:
                # 跳过解析失败的文档，但不中断整体流程
                print(f"警告: 第 {index} 个文档解析失败: {e}")
                continue

        return chapters

    def _extract_chapter_title(self, soup: BeautifulSoup, index: int) -> str:
        """从 HTML 中提取章节标题。"""
        # 优先查找标题标签
        for tag_name in ["h1", "h2", "h3", "h4", "title"]:
            tag = soup.find(tag_name)
            if tag and tag.get_text(strip=True):
                return tag.get_text(strip=True)

        # 回退："第X章" 模式匹配
        text = soup.get_text()
        match = re.search(r"(第[一二三四五六七八九十百千\d]+[章节回部篇])", text)
        if match:
            # 取匹配位置前后各 20 字符作为标题
            start = max(0, match.start())
            end = min(len(text), match.end() + 20)
            return text[start:end].strip().split("\n")[0]

        return f"第{index + 1}章"

    def _extract_clean_text(self, soup: BeautifulSoup) -> str:
        """从 BeautifulSoup 对象中提取清洗后的纯文本。"""
        # 移除 script 和 style 标签
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # 获取文本
        text = soup.get_text()

        # 规范化空白
        lines = (line.strip() for line in text.splitlines())
        chunks = (line for line in lines if line)
        text = "\n".join(chunks)

        # 合并多于2个的连续换行
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def extract_all(self) -> dict:
        """提取完整数据：元数据 + 章节列表。"""
        metadata = self.get_metadata()
        chapters = self.get_chapters()

        total_chars = sum(ch["char_count"] for ch in chapters)

        return {
            "title": metadata.get("title", "未知书名"),
            "author": metadata.get("author", "未知作者"),
            "language": metadata.get("language", "zh"),
            "total_chars": total_chars,
            "chapter_count": len(chapters),
            "chapters": chapters,
        }

    def save_json(self, output_path: str | Path) -> Path:
        """提取并保存为 JSON 文件。"""
        output_path = Path(output_path)
        data = self.extract_all()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return output_path
