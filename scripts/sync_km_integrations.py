"""同步 KM 外部集成到 Codex 与 Claude 的安装位置。"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


# 构建默认 marketplace 顶层结构，供首次创建全局 marketplace 使用。
def _default_marketplace_payload() -> dict[str, Any]:
    """返回默认的 home-local marketplace 结构。

    返回:
        dict[str, Any]: 包含 name、interface 和 plugins 的基础 marketplace 对象。
    """
    return {
        "name": "local-plugins",
        "interface": {"displayName": "Local Plugins"},
        "plugins": [],
    }


# 生成 km-memory 在 home-local marketplace 中的标准条目。
def _km_memory_marketplace_entry() -> dict[str, Any]:
    """返回 km-memory 的标准 marketplace 条目。"""
    return {
        "name": "km-memory",
        "source": {
            "source": "local",
            "path": "./plugins/km-memory",
        },
        "policy": {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        },
        "category": "Productivity",
    }


# 对 marketplace 执行 upsert，仅更新 km-memory 条目，不破坏其他插件配置。
def upsert_codex_marketplace_entry(marketplace_path: Path, check: bool = False) -> dict[str, Any]:
    """创建或更新 home-local marketplace 中的 km-memory 条目。

    参数:
        marketplace_path (Path): `~/.agents/plugins/marketplace.json` 路径。
        check (bool): 为 True 时只计算结果，不实际写入。

    返回:
        dict[str, Any]: 包含 marketplace 路径与是否写入的结果描述。
    """
    if marketplace_path.exists():
        payload = json.loads(marketplace_path.read_text())
    else:
        payload = _default_marketplace_payload()

    plugins = payload.setdefault("plugins", [])
    entry = _km_memory_marketplace_entry()

    replaced = False
    for index, plugin in enumerate(plugins):
        # 只替换同名条目，其余插件保持原样。
        if plugin.get("name") == "km-memory":
            plugins[index] = entry
            replaced = True
            break

    if not replaced:
        plugins.append(entry)

    if not check:
        marketplace_path.parent.mkdir(parents=True, exist_ok=True)
        marketplace_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

    return {
        "path": str(marketplace_path),
        "written": not check,
        "replaced": replaced,
    }


# 负责把单个文件同步到目标位置；check 模式下只返回状态不写盘。
def sync_file(source_path: Path, target_path: Path, check: bool = False) -> dict[str, Any]:
    """同步单个文件到目标路径。

    参数:
        source_path (Path): 源文件路径。
        target_path (Path): 目标文件路径。
        check (bool): 为 True 时不执行写入。

    返回:
        dict[str, Any]: 描述本次同步动作的状态。
    """
    if not check:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)

    return {
        "source": str(source_path),
        "target": str(target_path),
        "written": not check,
    }


# 负责把整个插件目录同步到目标位置；check 模式下只做状态计算。
def sync_directory(source_dir: Path, target_dir: Path, check: bool = False) -> dict[str, Any]:
    """同步目录树到目标位置。

    参数:
        source_dir (Path): 源目录路径。
        target_dir (Path): 目标目录路径。
        check (bool): 为 True 时不执行写入。

    返回:
        dict[str, Any]: 描述目录同步状态。
    """
    if not check:
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)

    return {
        "source": str(source_dir),
        "target": str(target_dir),
        "written": not check,
    }


# 执行 Codex 与 Claude 的单向同步，默认同时处理两种集成。
def sync_integrations(
    *,
    repo_root: Path,
    home_dir: Path,
    claude_dir: Path,
    codex_only: bool = False,
    claude_only: bool = False,
    check: bool = False,
) -> dict[str, Any]:
    """执行 KM 外部集成同步。

    参数:
        repo_root (Path): KM 仓库根目录。
        home_dir (Path): 用户主目录，例如 `~`。
        claude_dir (Path): Claude 根目录，例如 `~/.claude`。
        codex_only (bool): 是否仅同步 Codex。
        claude_only (bool): 是否仅同步 Claude。
        check (bool): 是否只检查不写入。

    返回:
        dict[str, Any]: 本次同步结果摘要。
    """
    if codex_only and claude_only:
        raise ValueError("--codex-only 与 --claude-only 不能同时使用")

    should_sync_codex = not claude_only
    should_sync_claude = not codex_only

    result: dict[str, Any] = {"check": check, "codex": None, "claude": None}

    if should_sync_codex:
        source_plugin_dir = repo_root / "plugins" / "km-memory"
        target_plugin_dir = home_dir / "plugins" / "km-memory"
        marketplace_path = home_dir / ".agents" / "plugins" / "marketplace.json"

        result["codex"] = {
            "plugin": sync_directory(source_plugin_dir, target_plugin_dir, check=check),
            "marketplace": upsert_codex_marketplace_entry(marketplace_path, check=check),
        }

    if should_sync_claude:
        source_skill_file = repo_root / "claude-skills" / "km-memory" / "SKILL.md"
        target_skill_file = claude_dir / "skills" / "km-memory" / "SKILL.md"
        result["claude"] = sync_file(source_skill_file, target_skill_file, check=check)

    return result


# 构建脚本 CLI，支持全量同步、单侧同步和 check 模式。
def build_parser() -> argparse.ArgumentParser:
    """构建同步脚本参数解析器。"""
    parser = argparse.ArgumentParser(prog="sync_km_integrations")
    parser.add_argument("--codex-only", action="store_true")
    parser.add_argument("--claude-only", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser


# 解析 CLI 参数并执行同步；输出 JSON 方便人和脚本同时读取。
def main() -> int:
    """执行同步脚本主流程。

    返回:
        int: 进程退出码，0 表示成功。
    """
    args = build_parser().parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    result = sync_integrations(
        repo_root=repo_root,
        home_dir=Path.home(),
        claude_dir=Path.home() / ".claude",
        codex_only=args.codex_only,
        claude_only=args.claude_only,
        check=args.check,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
