"""KM 命令行入口。"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from km_memory.config import bootstrap_layout


# 构建命令行参数解析器，后续 capture / recall 子命令也会在这里扩展。
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

    return parser


# 负责分发 CLI 子命令，目前仅支持 bootstrap。
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
        # 这里显式执行目录初始化，保持第一版行为简单、可测试。
        bootstrap_layout(args.root)
        return 0

    parser.error(f"未知命令: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
