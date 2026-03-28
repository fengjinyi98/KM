"""Recall 与渐进式披露测试。"""

from pathlib import Path

from km_memory.indexer import KmIndexer
from km_memory.recall import recall_notes


# 这里验证 summary 级检索只返回摘要层，不把正文一股脑塞进结果。
def test_recall_returns_summary_first(tmp_path: Path) -> None:
    """验证 summary 级别不会暴露完整正文。"""
    indexer = KmIndexer(tmp_path / "km.db")
    indexer.init_schema()
    indexer.upsert_document(
        doc_id="case-1",
        doc_type="case",
        title="丝滑 hover 反馈",
        summary="通过阴影和位移动画增强反馈",
        body="详细正文和代码片段",
        tags=["ui"],
        source_path="knowledge/cases/hover.md",
        is_inbox=False,
    )

    results = recall_notes(indexer=indexer, query="hover 反馈", detail_level="summary")
    assert results[0]["title"] == "丝滑 hover 反馈"
    assert "body" not in results[0]


# 这里验证 detail 级检索允许按需展开正文内容，符合渐进式披露。
def test_recall_detail_level_reveals_body(tmp_path: Path) -> None:
    """验证 detail 级别会返回正文内容。"""
    indexer = KmIndexer(tmp_path / "km.db")
    indexer.init_schema()
    indexer.upsert_document(
        doc_id="case-1",
        doc_type="case",
        title="丝滑 hover 反馈",
        summary="通过阴影和位移动画增强反馈",
        body="详细正文和代码片段",
        tags=["ui"],
        source_path="knowledge/cases/hover.md",
        is_inbox=False,
    )

    results = recall_notes(indexer=indexer, query="hover 反馈", detail_level="detail")
    assert results[0]["title"] == "丝滑 hover 反馈"
    assert results[0]["body"] == "详细正文和代码片段"
