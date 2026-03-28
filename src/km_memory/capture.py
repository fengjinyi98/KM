"""Capture 写入流程。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path

from km_memory.config import DEFAULT_INDEX_DB_RELATIVE_PATH, bootstrap_layout
from km_memory.frontmatter import dumps_markdown
from km_memory.indexer import KmIndexer
from km_memory.intents import classify_intent
from km_memory.storage import slugify, write_markdown, write_markdown_to_path
from km_memory.templates import render_case_markdown


# 表示一次 capture 执行后的结果，供 CLI 与测试共同消费。
@dataclass(slots=True)
class CaptureResult:
    """描述一次 Capture 落盘结果。

    参数:
        doc_type (str): 最终识别出的文档类型。
        is_inbox (bool): 是否进入 inbox。
        path (Path): 实际写入的 Markdown 路径。

    返回:
        CaptureResult: Capture 结果对象。
    """

    doc_type: str
    is_inbox: bool
    path: Path


# 从原始输入中提取一个第一版足够可用的标题，优先保证稳定落盘而非复杂语义理解。
def _infer_title(text: str, doc_type: str) -> str:
    """根据输入文本推断简要标题。"""
    cleaned = text.replace("把这个", "").replace("写进 KM", "").strip("，。 ")
    short = cleaned[:24].strip() or f"{doc_type}-note"
    return short


# 从“更新项目 XXX”一类文本中提取对象名称，用于主档案稳定命名。
def _extract_named_subject(text: str, prefix: str) -> str | None:
    """从带前缀的自然语言中提取主题名称。

    参数:
        text (str): 原始输入文本。
        prefix (str): 主题前缀，例如“项目”或“画像”。

    返回:
        str | None: 解析出的主题名称；若未命中则返回 None。
    """
    match = re.search(rf"{prefix}\s+([A-Za-z0-9_\-\u4e00-\u9fff]+)", text)
    return match.group(1) if match else None


# 生成 inbox 条目，保留原始信息并等待后续整理。
def _render_inbox_markdown(*, title: str, text: str) -> str:
    """渲染 inbox Markdown 内容。"""
    metadata = {
        "doc_type": "inbox",
        "title": title,
        "summary": text[:80],
        "tags": [],
    }
    body = f"# {title}\n\n## 原始记录\n{text}\n\n## 后续整理建议\n- 待补充。"
    return dumps_markdown(metadata, body)


# 生成项目主档案内容，第一版先保存最新状态摘要，后续再演进为字段级合并。
def _render_project_markdown(*, project_name: str, text: str) -> str:
    """渲染项目主档案 Markdown。"""
    metadata = {
        "doc_type": "project",
        "title": project_name,
        "summary": text[:80],
        "tags": [],
    }
    body = (
        f"# {project_name}\n\n"
        f"## 当前记录\n{text}\n\n"
        "## 后续补充\n- 待补充项目目标、阶段、技术栈与约束。"
    )
    return dumps_markdown(metadata, body)


# 生成个人画像主档案内容，第一版先记录当前偏好与工作方式摘要。
def _render_profile_markdown(*, text: str) -> str:
    """渲染个人画像主档案 Markdown。"""
    metadata = {
        "doc_type": "profile",
        "title": "me",
        "summary": text[:80],
        "tags": [],
    }
    body = (
        "# me\n\n"
        f"## 当前画像\n{text}\n\n"
        "## 后续补充\n- 待补充长期偏好、项目版图与工作方式。"
    )
    return dumps_markdown(metadata, body)


# 为项目或画像生成变更日志，保留历史演化轨迹。
def _render_log_markdown(*, title: str, text: str, doc_type: str) -> str:
    """渲染变更日志 Markdown。"""
    metadata = {
        "doc_type": f"{doc_type}-log",
        "title": title,
        "summary": text[:80],
        "tags": [],
    }
    body = f"# {title}\n\n## 变更内容\n{text}"
    return dumps_markdown(metadata, body)


# 执行第一版 Capture：识别类型、决定正式库/Inbox、写盘并同步索引。
def capture_note(root: Path, text: str) -> CaptureResult:
    """将自然语言输入写入 KM。"""
    bootstrap_layout(root)

    doc_type = classify_intent(text)
    is_inbox = doc_type == "inbox"

    if doc_type == "case":
        title = _infer_title(text, doc_type)
        markdown = render_case_markdown(
            title=title,
            summary=text[:80],
            problem=text,
        )
        path = write_markdown(
            root,
            doc_type=doc_type,
            title=title,
            markdown=markdown,
            is_inbox=False,
        )
    elif doc_type == "project":
        project_name = _extract_named_subject(text, "项目") or _infer_title(text, doc_type)
        markdown = _render_project_markdown(project_name=project_name, text=text)
        path = write_markdown(
            root,
            doc_type=doc_type,
            title=project_name,
            markdown=markdown,
            is_inbox=False,
        )
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
        log_path = root / "memory" / "logs" / f"project-{slugify(project_name)}-{timestamp}.md"
        write_markdown_to_path(
            log_path,
            _render_log_markdown(title=f"项目 {project_name} 变更", text=text, doc_type=doc_type),
        )
    elif doc_type == "profile":
        markdown = _render_profile_markdown(text=text)
        path = write_markdown_to_path(root / "memory" / "profile" / "me.md", markdown)
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
        log_path = root / "memory" / "logs" / f"profile-me-{timestamp}.md"
        write_markdown_to_path(
            log_path,
            _render_log_markdown(title="个人画像变更", text=text, doc_type=doc_type),
        )
        is_inbox = False
    else:
        title = _infer_title(text, doc_type)
        markdown = _render_inbox_markdown(title=title, text=text)
        path = write_markdown(
            root,
            doc_type=doc_type,
            title=title,
            markdown=markdown,
            is_inbox=True,
        )
        is_inbox = True

    indexer = KmIndexer(root.joinpath(*DEFAULT_INDEX_DB_RELATIVE_PATH))
    indexer.init_schema()
    indexer.upsert_document(
        doc_id=path.stem,
        doc_type=doc_type,
        title=path.stem,
        summary=text[:80],
        body=markdown,
        tags=[],
        source_path=str(path.relative_to(root)),
        is_inbox=is_inbox,
    )
    return CaptureResult(doc_type=doc_type, is_inbox=is_inbox, path=path)
