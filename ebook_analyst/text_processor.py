"""文本处理器 — 文本清洗、停用词过滤、分词。"""

import re

import jieba


# 常用中文停用词表
_STOP_WORDS = set(
    """
的 了 在 是 我 有 和 就 不 人 都 一 一个 上 也 很 到 说 要 去 你 会 着 没有
看 好 自己 这 他 她 它 们 那 些 什么 而 为 所以 因为 但是 可以 这个 那个
如果 虽然 之后 然而 并且 之 与 及 或 但 被 把 让 从 对 于 还 又 再 更
已经 能 更 还是 不过 等等 的话 啦 吧 呢 啊 嘛 哦 嗯 哈 哟 啰 呗 吶
已经 将 向 以 及 其 等 所 而 且 地 得 着 过 来 去 么 之 已 该
我们 他们 她们 它们 你们 咱们 大家 别人 人家 自个 彼此 各位 诸位
时候 就是 还是 只是 总是 一样 似的 这样 那样 这么 那么 怎么 怎样
多么 什么 为什么 哪里 哪儿 那边 这边 这里 那里 哪个 哪些 每个
然后 接着 之后 以前 以后 刚才 现在 正在 已经 曾经 将要
没有 可以 知道 觉得 认为 看见 听见 起来 出来 下来 过来 回来
上去 进去 出去 过去 进来 起来 起 完 到 会 能 要 想 让
一些 一点 一种 各种 全部 所有 整个 别的 其他 另一个
""".split()
)

# 额外标点和空白
_PUNCTUATION = set("，。！？、；：""''（）【】《》…—·～　 \t\n\r")


def clean_text(text: str) -> str:
    """清洗文本：去除多余空白、规范化标点。"""
    text = re.sub(r"[\s]+", " ", text)
    text = re.sub(r"[_]{3,}", "", text)
    text = re.sub(r"[*]{3,}", "", text)
    return text.strip()


def segment(text: str, remove_stopwords: bool = True) -> list[str]:
    """使用 jieba 对中文文本分词。

    参数:
        text: 输入文本
        remove_stopwords: 是否去除停用词

    返回:
        分词结果列表
    """
    words = jieba.cut(text, cut_all=False)

    result = []
    for w in words:
        w = w.strip()
        if not w or len(w) < 2:
            continue
        if w in _PUNCTUATION:
            continue
        if remove_stopwords and w in _STOP_WORDS:
            continue
        # 过滤纯数字
        if re.match(r"^\d+(\.\d+)?$", w):
            continue
        result.append(w)

    return result


def segment_with_freq(words: list[str]) -> dict[str, int]:
    """统计分词后的词频。"""
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return dict(
        sorted(freq.items(), key=lambda x: x[1], reverse=True)
    )


def get_stop_words() -> set[str]:
    """返回停用词集合。"""
    return _STOP_WORDS.copy()
