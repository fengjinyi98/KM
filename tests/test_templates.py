"""Markdown 模板渲染测试。"""

from km_memory.templates import render_case_markdown


# 这里验证技术案例模板至少包含核心章节，避免后续条目结构松散。
def test_render_case_markdown_includes_sections() -> None:
    """验证案例模板会输出标题和关键章节。"""
    markdown = render_case_markdown(
        title="丝滑卡片交互",
        summary="实现高质量悬浮反馈",
        problem="卡片交互缺乏层次感",
    )

    assert "丝滑卡片交互" in markdown
    assert "## 问题" in markdown
    assert "## 实现思路" in markdown
    assert "## 关键代码" in markdown
