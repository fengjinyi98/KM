"""Markdown frontmatter 读写测试。"""

from km_memory.frontmatter import dumps_markdown, loads_markdown


# 这里验证 YAML frontmatter 和正文可以双向往返，确保后续写入稳定。
def test_frontmatter_roundtrip() -> None:
    """验证 frontmatter 渲染后仍可无损解析。"""
    text = dumps_markdown({"title": "案例 A", "doc_type": "case"}, "正文")
    metadata, body = loads_markdown(text)

    assert metadata["title"] == "案例 A"
    assert metadata["doc_type"] == "case"
    assert body == "正文"
