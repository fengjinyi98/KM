"""KM 命令行入口。"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from km_memory.capture import capture_note
from km_memory.config import DEFAULT_INDEX_DB_RELATIVE_PATH, bootstrap_layout
from km_memory.indexer import KmIndexer
from km_memory.recall import recall_notes


# 构建命令行参数解析器，后续可继续在此扩展更多显式触发命令。
def build_parser() -> argparse.ArgumentParser:
    """构建 KM CLI 的参数解析器。

    参数:
        无。

    返回:
        argparse.ArgumentParser: 已注册基础子命令的解析器实例。
    """
    parser = argparse.ArgumentParser(prog="km")
    subparsers = parser.add_subparsers(dest="command", required=True)

    bootstrap_parser = subparsers.add_parser("bootstrap")
    bootstrap_parser.add_argument("--root", type=Path, required=True)

    capture_parser = subparsers.add_parser("capture")
    capture_parser.add_argument("--root", type=Path, required=True)
    capture_parser.add_argument("--text", required=True)

    recall_parser = subparsers.add_parser("recall")
    recall_parser.add_argument("--root", type=Path, required=True)
    recall_parser.add_argument("--query", required=True)
    recall_parser.add_argument("--detail", default="summary", choices=["summary", "detail", "full"])

    return parser


# 负责分发 CLI 子命令，保持所有 KM 行为都由显式命令触发。
def main(argv: Sequence[str] | None = None) -> int:
    """执行 KM CLI 主流程。

    参数:
        argv (Sequence[str] | None): 外部传入的命令行参数列表；为空时由 argparse 自行读取。

    返回:
        int: 命令执行完成后的退出码，0 表示成功。
    """
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "bootstrap":
        bootstrap_layout(args.root)
        return 0

    if args.command == "capture":
        capture_note(args.root, args.text)
        return 0

    if args.command == "recall":
        indexer = KmIndexer(args.root.joinpath(*DEFAULT_INDEX_DB_RELATIVE_PATH))
        indexer.init_schema()
        results = recall_notes(indexer=indexer, query=args.query, detail_level=args.detail)
        for item in results:
            print(item)
        return 0

    parser.error(f"未知命令: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
