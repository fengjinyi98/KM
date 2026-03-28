"""KM bootstrap 命令测试。"""

from pathlib import Path

from km_memory.cli import main


# 这里验证 bootstrap 命令会创建 KM 所需的基础目录结构。
def test_bootstrap_creates_km_layout(tmp_path: Path) -> None:
    """验证 bootstrap 命令能够创建知识库与记忆系统的基础目录。"""
    exit_code = main([
        "bootstrap",
        "--root",
        str(tmp_path),
    ])

    assert exit_code == 0
    assert (tmp_path / "knowledge" / "cases").exists()
    assert (tmp_path / "memory" / "profile").exists()
    assert (tmp_path / "index").exists()
