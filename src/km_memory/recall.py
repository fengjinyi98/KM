"""Recall 检索与渐进式披露。"""

from __future__ import annotations

from km_memory.indexer import KmIndexer


# 根据 detail_level 控制返回层级，默认只返回摘要层，避免正文过度注入上下文。
def recall_notes(indexer: KmIndexer, query: str, detail_level: str = "summary") -> list[dict[str, object]]:
    """从索引中检索条目，并按披露级别裁剪返回内容。

    参数:
        indexer (KmIndexer): 已初始化的索引器实例。
        query (str): 用户查询词。
        detail_level (str): 返回层级，支持 summary / detail / full。

    返回:
        list[dict[str, object]]: 面向上层调用方的检索结果列表。
    """
    rows = indexer.search(query)
    results: list[dict[str, object]] = []
    for row in rows:
        item = {
            "doc_id": row["doc_id"],
            "doc_type": row["doc_type"],
            "title": row["title"],
            "summary": row["summary"],
            "source_path": row["source_path"],
            "is_inbox": row["is_inbox"],
        }
        if detail_level in {"detail", "full"}:
            item["body"] = row["body"]
        results.append(item)
    return results
