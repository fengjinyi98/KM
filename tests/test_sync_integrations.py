"""KM 集成同步脚本测试。"""

from pathlib import Path


# 这里先锁定 Claude skill 的仓库源文件位置，确保后续同步脚本有稳定来源。
def test_repo_contains_claude_skill_source() -> None:
    """验证仓库中存在 Claude skill 源文件。"""
    repo_root = Path(__file__).resolve().parents[1]
    source_file = repo_root / "claude-skills" / "km-memory" / "SKILL.md"

    assert source_file.exists()
