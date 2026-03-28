"""KM 领域对象定义。"""

from __future__ import annotations

from dataclasses import dataclass, field


# 表示通用 Markdown 文档的基础元数据，供索引与存储层复用。
@dataclass(slots=True)
class KmDocument:
    """描述 KM 中的一个基础文档对象。

    参数:
        doc_type (str): 文档类型，例如 case / project / profile / inbox。
        title (str): 文档标题。
        summary (str): 文档摘要，用于检索结果展示。
        tags (list[str]): 文档标签列表，便于后续索引与筛选。

    返回:
        KmDocument: 结构化文档对象实例。
    """

    doc_type: str
    title: str
    summary: str = ""
    tags: list[str] = field(default_factory=list)
