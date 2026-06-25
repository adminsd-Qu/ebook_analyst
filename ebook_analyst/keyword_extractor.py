"""关键词提取器 — TF-IDF 和 TextRank 两种模式。

基于 jieba 分词，支持整体关键词提取和逐章关键词提取。
"""

import atexit
import json
import os
import tempfile
from pathlib import Path
from typing import Optional

import jieba.analyse

from ebook_analyst.text_processor import segment, segment_with_freq, get_stop_words

# jieba.analyse 使用独立的停用词机制，需将我们的停用词表写入临时文件桥接
_STOP_WORDS_PATH: Optional[str] = None


def _init_jieba_stopwords():
    """将 text_processor 的停用词表桥接到 jieba.analyse。"""
    global _STOP_WORDS_PATH
    if _STOP_WORDS_PATH is not None:
        return  # 已初始化
    fd, path = tempfile.mkstemp(suffix=".txt", prefix="jieba_stop_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(get_stop_words())))
        f.write("\n")  # jieba 要求每行一个词并以换行结尾
    jieba.analyse.set_stop_words(path)
    _STOP_WORDS_PATH = path


def _cleanup_stopwords_file():
    if _STOP_WORDS_PATH and os.path.exists(_STOP_WORDS_PATH):
        try:
            os.unlink(_STOP_WORDS_PATH)
        except OSError:
            pass


atexit.register(_cleanup_stopwords_file)


class KeywordExtractor:
    """中文关键词提取器，封装 jieba TF-IDF 和 TextRank。"""

    def __init__(self, text: str = "", stop_words: Optional[set[str]] = None):
        _init_jieba_stopwords()
        self.text = text
        self._stop_words = stop_words or set()

    def set_text(self, text: str):
        self.text = text

    def extract_tfidf(
        self, top_k: int = 50, with_weight: bool = True
    ) -> list[tuple[str, float]] | list[str]:
        """使用 TF-IDF 算法提取关键词。"""
        keywords = jieba.analyse.extract_tags(
            self.text,
            topK=top_k,
            withWeight=with_weight,
        )
        return keywords

    def extract_textrank(
        self, top_k: int = 50, with_weight: bool = True
    ) -> list[tuple[str, float]] | list[str]:
        """使用 TextRank 算法提取关键词。"""
        keywords = jieba.analyse.textrank(
            self.text,
            topK=top_k,
            withWeight=with_weight,
        )
        return keywords

    def extract_combined(
        self, top_k: int = 50
    ) -> dict:
        """同时使用 TF-IDF 和 TextRank，返回合并结果。"""
        tfidf = self.extract_tfidf(top_k=top_k, with_weight=True)
        textrank = self.extract_textrank(top_k=top_k, with_weight=True)

        # 构建合并数据结构
        tfidf_map = {word: weight for word, weight in tfidf}
        textrank_map = {word: weight for word, weight in textrank}

        all_words = set(tfidf_map.keys()) | set(textrank_map.keys())
        combined = []
        for word in all_words:
            combined.append({
                "word": word,
                "tfidf_weight": tfidf_map.get(word, 0.0),
                "textrank_weight": textrank_map.get(word, 0.0),
            })

        # 按 TF-IDF 权重降序排列
        combined.sort(key=lambda x: x["tfidf_weight"], reverse=True)

        return {
            "top_k": top_k,
            "keywords": combined[:top_k],
        }

    def extract_chapter_keywords(
        self, chapters: list[dict], top_k: int = 30
    ) -> list[dict]:
        """逐章提取关键词。"""
        results = []
        for ch in chapters:
            self.set_text(ch["text"])
            kw = self.extract_combined(top_k=top_k)
            results.append({
                "chapter_index": ch["index"],
                "chapter_title": ch["title"],
                "char_count": ch["char_count"],
                "keywords": kw["keywords"],
            })
        return results


def extract_from_book_json(
    book_json_path: str | Path,
    output_path: str | Path | None = None,
    top_k_overall: int = 50,
    top_k_chapter: int = 30,
) -> dict:
    """从 book.json 提取关键词。

    参数:
        book_json_path: book.json 文件路径
        output_path: 输出 JSON 路径 (None 则自动生成)
        top_k_overall: 整体关键词数量
        top_k_chapter: 每章关键词数量

    返回:
        包含整体和逐章关键词的字典
    """
    book_json_path = Path(book_json_path)
    with open(book_json_path, "r", encoding="utf-8") as f:
        book_data = json.load(f)

    # 桥接停用词到 jieba.analyse（首次调用初始化）
    _init_jieba_stopwords()

    # 拼接全书文本
    full_text = "\n".join(ch["text"] for ch in book_data["chapters"])
    extractor = KeywordExtractor(full_text)

    # 整体关键词
    overall = extractor.extract_combined(top_k=top_k_overall)

    # 分词 + 词频统计
    words = segment(full_text, remove_stopwords=True)
    word_freq = segment_with_freq(words)

    # 逐章关键词
    chapter_kw = extractor.extract_chapter_keywords(
        book_data["chapters"], top_k=top_k_chapter
    )

    result = {
        "title": book_data["title"],
        "author": book_data["author"],
        "total_chars": book_data["total_chars"],
        "overall_keywords": overall["keywords"],
        "top_frequent_words": dict(list(word_freq.items())[:50]),
        "chapter_keywords": chapter_kw,
    }

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    return result
