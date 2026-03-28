"""KM SQLite 索引器。"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path


# 对搜索输入做最小切词，兼容空白分隔查询与后续规则排序。
def _tokenize_query(query: str) -> list[str]:
    """把搜索词拆成非空 token 列表。

    参数:
        query (str): 用户输入的原始搜索字符串。

    返回:
        list[str]: 去除空白后的 token 列表。
    """
    return [token.strip() for token in query.split() if token.strip()]


# 负责维护 SQLite 文档表与 FTS 索引，并提供统一的 upsert / search 能力。
@dataclass(slots=True)
class KmIndexer:
    """KM 的 SQLite 索引访问层。

    参数:
        db_path (Path): SQLite 数据库文件路径。

    返回:
        KmIndexer: 可执行建表、写入与搜索的索引器实例。
    """

    db_path: Path

    def _connect(self) -> sqlite3.Connection:
        """创建数据库连接并设置按列名访问结果。"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def init_schema(self) -> None:
        """初始化业务表与 FTS5 虚拟表。"""
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    doc_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    body TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_inbox INTEGER NOT NULL DEFAULT 0
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                    doc_id UNINDEXED,
                    title,
                    summary,
                    body,
                    tags
                );
                """
            )

    def upsert_document(
        self,
        *,
        doc_id: str,
        doc_type: str,
        title: str,
        summary: str,
        body: str,
        tags: list[str],
        source_path: str,
        is_inbox: bool,
    ) -> None:
        """写入或更新文档记录，并同步刷新 FTS 索引。

        参数:
            doc_id (str): 文档唯一 ID。
            doc_type (str): 文档类型。
            title (str): 文档标题。
            summary (str): 文档摘要。
            body (str): 文档正文。
            tags (list[str]): 标签列表。
            source_path (str): Markdown 相对路径。
            is_inbox (bool): 是否属于 inbox 条目。

        返回:
            None: 仅更新数据库，不返回值。
        """
        tags_text = " ".join(tags)
        updated_at = datetime.now(UTC).isoformat()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    doc_id, doc_type, title, summary, body, tags, source_path, updated_at, is_inbox
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(doc_id) DO UPDATE SET
                    doc_type = excluded.doc_type,
                    title = excluded.title,
                    summary = excluded.summary,
                    body = excluded.body,
                    tags = excluded.tags,
                    source_path = excluded.source_path,
                    updated_at = excluded.updated_at,
                    is_inbox = excluded.is_inbox
                """,
                (
                    doc_id,
                    doc_type,
                    title,
                    summary,
                    body,
                    tags_text,
                    source_path,
                    updated_at,
                    1 if is_inbox else 0,
                ),
            )
            # 先删后插，确保 FTS 虚拟表与主表内容严格同步。
            connection.execute("DELETE FROM documents_fts WHERE doc_id = ?", (doc_id,))
            connection.execute(
                "INSERT INTO documents_fts (doc_id, title, summary, body, tags) VALUES (?, ?, ?, ?, ?)",
                (doc_id, title, summary, body, tags_text),
            )

    def search(self, query: str, limit: int = 10) -> list[dict[str, object]]:
        """执行混合检索：优先 FTS，再辅以 LIKE 回退增强中文稳定性。

        参数:
            query (str): 用户搜索词。
            limit (int): 最多返回结果数量。

        返回:
            list[dict[str, object]]: 按相关性排序后的结果列表。
        """
        tokens = _tokenize_query(query)
        if not tokens:
            return []

        fts_query = " OR ".join(tokens)
        like_clauses: list[str] = []
        like_values: list[str] = []
        score_parts: list[str] = []
        for token in tokens:
            like_value = f"%{token}%"
            # 标题、摘要、正文分别给不同权重，形成轻量规则排序。
            score_parts.extend(
                [
                    "CASE WHEN d.title LIKE ? THEN 5 ELSE 0 END",
                    "CASE WHEN d.summary LIKE ? THEN 3 ELSE 0 END",
                    "CASE WHEN d.body LIKE ? THEN 1 ELSE 0 END",
                ]
            )
            like_values.extend([like_value, like_value, like_value])
            like_clauses.append("(d.title LIKE ? OR d.summary LIKE ? OR d.body LIKE ?)")
            like_values.extend([like_value, like_value, like_value])

        where_sql = " OR ".join(like_clauses)
        score_sql = " + ".join(score_parts)

        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT
                    d.doc_id,
                    d.doc_type,
                    d.title,
                    d.summary,
                    d.body,
                    d.tags,
                    d.source_path,
                    d.updated_at,
                    d.is_inbox,
                    ({score_sql}) AS score
                FROM documents AS d
                WHERE d.doc_id IN (
                    SELECT doc_id FROM documents_fts WHERE documents_fts MATCH ?
                ) OR ({where_sql})
                ORDER BY score DESC, d.updated_at DESC
                LIMIT ?
                """,
                [*like_values[: len(score_parts)], fts_query, *like_values[len(score_parts):], limit],
            ).fetchall()

        return [dict(row) for row in rows]
