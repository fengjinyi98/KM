"""SQLite 索引器测试。"""

from pathlib import Path

from km_memory.indexer import KmIndexer


# 这里验证文档写入索引后可以被全文检索命中。
def test_indexer_can_upsert_and_search(tmp_path: Path) -> None:
    """验证索引器支持 upsert 与全文搜索。"""
    indexer = KmIndexer(tmp_path / "km.db")
    indexer.init_schema()
    indexer.upsert_document(
        doc_id="case-1",
        doc_type="case",
        title="卡片悬浮反馈",
        summary="实现更丝滑的卡片交互",
        body="hover motion shadow",
        tags=["interaction", "ui"],
        source_path="knowledge/cases/case-1.md",
        is_inbox=False,
    )

    results = indexer.search("丝滑 交互")
    assert results
    assert results[0]["doc_id"] == "case-1"
