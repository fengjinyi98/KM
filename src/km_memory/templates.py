"""KM Markdown 模板渲染函数。"""

from __future__ import annotations

from textwrap import dedent

from km_memory.frontmatter import dumps_markdown


# 渲染技术案例条目，确保后续生成的 Markdown 结构统一且易检索。
def render_case_markdown(*, title: str, summary: str, problem: str) -> str:
    """渲染技术案例 Markdown。

    参数:
        title (str): 案例标题。
        summary (str): 案例摘要。
        problem (str): 待解决问题描述。

    返回:
        str: 含 frontmatter 的完整 Markdown 文本。
    """
    body = dedent(
        f"""
        # {title}

        ## 问题
        {problem}

        ## 实现思路
        - 待补充实现思路。

        ## 关键代码
        - 待补充关键代码片段。

        ## 适用场景
        - 待补充适用场景。
        """
    ).strip()

    metadata = {
        "doc_type": "case",
        "title": title,
        "summary": summary,
        "tags": [],
    }
    return dumps_markdown(metadata, body)
