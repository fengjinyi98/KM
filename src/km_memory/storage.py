"""KM Markdown 文件存储能力。"""

from __future__ import annotations

import re
from pathlib import Path


# 将任意标题归一化为文件名片段，避免路径包含不安全字符。
def slugify(text: str) -> str:
    """把文本转换为适合文件名使用的 slug。

    参数:
        text (str): 原始标题或摘要文本。

    返回:
        str: 仅包含中文、英文、数字和短横线的简化文件名。
    """
    normalized = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", text).strip("-")
    return normalized.lower() or "untitled"


# 将 Markdown 内容写入任意显式路径，供项目日志等辅助文件复用。
def write_markdown_to_path(path: Path, markdown: str) -> Path:
    """把 Markdown 文本写入指定路径。

    参数:
        path (Path): 目标文件路径。
        markdown (str): 最终写入的 Markdown 内容。

    返回:
        Path: 已写入完成的目标路径。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown)
    return path


# 根据文档类型选择正式库或 inbox 路径，并将 Markdown 内容写盘。
def write_markdown(root: Path, *, doc_type: str, title: str, markdown: str, is_inbox: bool) -> Path:
    """将 Markdown 内容写入目标路径。

    参数:
        root (Path): KM 根目录。
        doc_type (str): 文档类型。
        title (str): 用于生成文件名的标题。
        markdown (str): 最终写入的 Markdown 内容。
        is_inbox (bool): 是否写入 inbox。

    返回:
        Path: 实际写入的文件路径。
    """
    if is_inbox:
        directory = root / "inbox" / "captures"
    elif doc_type == "case":
        directory = root / "knowledge" / "cases"
    elif doc_type == "project":
        directory = root / "memory" / "projects"
    elif doc_type == "profile":
        directory = root / "memory" / "profile"
    else:
        directory = root / "inbox" / "captures"

    path = directory / f"{slugify(title)}.md"
    return write_markdown_to_path(path, markdown)
