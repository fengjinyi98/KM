"""Markdown frontmatter 编解码工具。"""

from __future__ import annotations

from typing import Any

import yaml


# 将结构化元数据和正文拼装为 Markdown 文本，统一写盘格式。
def dumps_markdown(metadata: dict[str, Any], body: str) -> str:
    """把元数据与正文渲染成包含 YAML frontmatter 的 Markdown。

    参数:
        metadata (dict[str, Any]): 需要写入 frontmatter 的结构化字段。
        body (str): Markdown 正文内容。

    返回:
        str: 完整 Markdown 文本。
    """
    header = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False).strip()
    normalized_body = body.strip()
    return f"---\n{header}\n---\n\n{normalized_body}\n"


# 解析 Markdown 文本，拆出元数据与正文，供读取与索引层复用。
def loads_markdown(text: str) -> tuple[dict[str, Any], str]:
    """解析带 frontmatter 的 Markdown 文本。

    参数:
        text (str): 原始 Markdown 内容。

    返回:
        tuple[dict[str, Any], str]: 解析后的元数据字典与正文文本。
    """
    if not text.startswith("---\n"):
        return {}, text.strip()

    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return {}, text.strip()

    header_text = parts[0].removeprefix("---\n")
    body = parts[1].strip()
    metadata = yaml.safe_load(header_text) or {}
    return metadata, body
