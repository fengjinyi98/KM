"""KM 集成同步脚本测试。"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType


# 统一从 scripts 目录加载同步脚本模块，避免要求它必须是安装包。
def load_sync_module() -> ModuleType:
    """按文件路径加载同步脚本模块。"""
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "sync_km_integrations.py"
    spec = importlib.util.spec_from_file_location("sync_km_integrations", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# 这里先锁定 Claude skill 的仓库源文件位置，确保后续同步脚本有稳定来源。
def test_repo_contains_claude_skill_source() -> None:
    """验证仓库中存在 Claude skill 源文件。"""
    repo_root = Path(__file__).resolve().parents[1]
    source_file = repo_root / "claude-skills" / "km-memory" / "SKILL.md"

    assert source_file.exists()


# 这里验证 marketplace 更新时只 upsert km-memory，不应破坏已有其他插件条目。
def test_upsert_marketplace_entry_preserves_existing_plugins(tmp_path: Path) -> None:
    """验证 marketplace upsert 会保留其他插件，仅更新 km-memory。"""
    module = load_sync_module()
    marketplace_path = tmp_path / "marketplace.json"
    marketplace_path.write_text(
        json.dumps(
            {
                "name": "local-plugins",
                "interface": {"displayName": "Local Plugins"},
                "plugins": [
                    {
                        "name": "other-plugin",
                        "source": {"source": "local", "path": "./plugins/other-plugin"},
                        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                        "category": "Productivity",
                    }
                ],
            }
        )
    )

    module.upsert_codex_marketplace_entry(marketplace_path)

    payload = json.loads(marketplace_path.read_text())
    plugin_names = [item["name"] for item in payload["plugins"]]
    assert "other-plugin" in plugin_names
    assert "km-memory" in plugin_names


# 这里验证 check 模式只检查状态，不会真的向目标目录写入文件。
def test_sync_integrations_check_mode_does_not_write_targets(tmp_path: Path) -> None:
    """验证 --check 模式不会写入 Codex 或 Claude 目标目录。"""
    module = load_sync_module()
    repo_root = tmp_path / "repo"
    (repo_root / "plugins" / "km-memory" / ".codex-plugin").mkdir(parents=True)
    (repo_root / "plugins" / "km-memory" / ".codex-plugin" / "plugin.json").write_text("{}")
    (repo_root / "claude-skills" / "km-memory").mkdir(parents=True)
    (repo_root / "claude-skills" / "km-memory" / "SKILL.md").write_text("# skill")

    home_dir = tmp_path / "home"
    claude_dir = home_dir / ".claude"

    result = module.sync_integrations(
        repo_root=repo_root,
        home_dir=home_dir,
        claude_dir=claude_dir,
        check=True,
    )

    assert result["check"] is True
    assert not (home_dir / "plugins" / "km-memory").exists()
    assert not (claude_dir / "skills" / "km-memory" / "SKILL.md").exists()


# 这里验证默认同步会把 Codex 插件、marketplace 和 Claude skill 一次性写入目标位置。
def test_sync_integrations_writes_codex_and_claude_targets(tmp_path: Path) -> None:
    """验证默认同步会写入两侧目标文件。"""
    module = load_sync_module()
    repo_root = tmp_path / "repo"
    (repo_root / "plugins" / "km-memory" / ".codex-plugin").mkdir(parents=True)
    (repo_root / "plugins" / "km-memory" / ".codex-plugin" / "plugin.json").write_text('{"name": "km-memory"}')
    (repo_root / "claude-skills" / "km-memory").mkdir(parents=True)
    (repo_root / "claude-skills" / "km-memory" / "SKILL.md").write_text("# skill")

    home_dir = tmp_path / "home"
    claude_dir = home_dir / ".claude"

    result = module.sync_integrations(
        repo_root=repo_root,
        home_dir=home_dir,
        claude_dir=claude_dir,
        check=False,
    )

    assert result["check"] is False
    assert (home_dir / "plugins" / "km-memory" / ".codex-plugin" / "plugin.json").exists()
    assert (home_dir / ".agents" / "plugins" / "marketplace.json").exists()
    assert (claude_dir / "skills" / "km-memory" / "SKILL.md").exists()
