"""人物关系网络分析 — 基于共现统计的人物关系图生成。

可选模块，仅在分析小说类作品时启用。
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

from ebook_analyst.wordcloud_maker import get_font_path


def build_character_cooccurrence(
    chapters: list[dict],
    character_names: list[str],
    window_size: int = 100,
) -> dict[str, dict[str, int]]:
    """基于共现统计构建人物关系网络。

    在同一段落（约 window_size 字符范围内）共同出现的两个人物，
    记为一次关联。关联次数越多 = 关系越紧密。

    参数:
        chapters: 章节列表
        character_names: 人物名称列表
        window_size: 共现窗口（字符数）

    返回:
        共现矩阵: {name: {other_name: count}}
    """
    matrix = defaultdict(lambda: defaultdict(int))

    full_text = "\n".join(ch["text"] for ch in chapters)

    # 按段落切分
    paragraphs = [p.strip() for p in full_text.split("\n") if p.strip()]

    for para in paragraphs:
        # 找出该段落中出现的所有人物
        present = []
        for name in character_names:
            if name in para:
                present.append(name)

        # 每对人物 +1
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                matrix[present[i]][present[j]] += 1
                matrix[present[j]][present[i]] += 1

    return dict(matrix)


def draw_network(
    matrix: dict[str, dict[str, int]],
    output_path: str | Path,
    min_edge_weight: int = 3,
    figsize: tuple = (12, 10),
):
    """绘制人物关系网络图。

    参数:
        matrix: 共现矩阵
        output_path: 输出图片路径
        min_edge_weight: 最小边权重（过滤弱关联）
        figsize: 图片尺寸
    """
    try:
        import networkx as nx
    except ImportError:
        print("警告: 需要 networkx 库来绘制关系图。跳过。")
        return

    G = nx.Graph()

    # 添加节点和边
    for name, edges in matrix.items():
        G.add_node(name)
        for other, weight in edges.items():
            if weight >= min_edge_weight and name < other:  # 避免重复边
                G.add_edge(name, other, weight=weight)

    if len(G.nodes()) == 0:
        print("警告: 没有足够的人物关系数据来绘制网络图。")
        return

    # 绘图
    fig, ax = plt.subplots(figsize=figsize)

    # 使用 spring layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # 边权重映射到线宽
    edge_weights = [G[u][v]["weight"] for u, v in G.edges()]
    max_weight = max(edge_weights) if edge_weights else 1

    # 绘制边
    for u, v, data in G.edges(data=True):
        width = 0.5 + 3 * (data["weight"] / max_weight)
        alpha = 0.3 + 0.5 * (data["weight"] / max_weight)
        nx.draw_networkx_edges(
            G, pos, edgelist=[(u, v)],
            width=width, alpha=alpha, edge_color="#555555"
        )

    # 节点大小
    font_path = get_font_path()
    font_prop = FontProperties(fname=font_path, size=10)
    degrees = dict(G.degree())
    max_deg = max(degrees.values()) if degrees else 1
    node_sizes = [500 + 1500 * (degrees[n] / max_deg) for n in G.nodes()]

    nx.draw_networkx_nodes(
        G, pos, node_size=node_sizes,
        node_color="#4A90D9", alpha=0.85
    )

    # 标签
    labels = {n: n for n in G.nodes()}
    nx.draw_networkx_labels(
        G, pos, labels,
        font_size=10,
        font_family=font_prop.get_name(),
    )

    ax.axis("off")
    title_font = FontProperties(fname=font_path, size=16)
    ax.set_title("人物关系网络图", fontproperties=title_font, pad=20)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(output_path), bbox_inches="tight", dpi=150)
    plt.close(fig)


def generate_character_network(
    book_json_path: str | Path,
    character_names: list[str],
    output_path: str | Path,
    **kwargs,
) -> Optional[Path]:
    """从 book.json 生成人物关系图。

    参数:
        book_json_path: book.json 路径
        character_names: Claude 识别的人物名称列表
        output_path: 输出 PNG 路径

    返回:
        输出路径，或 None (失败时)
    """
    with open(book_json_path, "r", encoding="utf-8") as f:
        book = json.load(f)

    matrix = build_character_cooccurrence(
        book["chapters"], character_names
    )

    if not matrix:
        return None

    draw_network(matrix, output_path, **kwargs)
    return Path(output_path)
