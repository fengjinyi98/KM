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


# 这里做一次 CLI 级别烟雾测试，确保 bootstrap / capture / recall 能串起来工作。
def test_cli_capture_and_recall_smoke(tmp_path: Path, capsys) -> None:
    """验证 CLI 主流程可以完成初始化、写入和召回。"""
    assert main(["bootstrap", "--root", str(tmp_path)]) == 0
    assert (
        main(
            [
                "capture",
                "--root",
                str(tmp_path),
                "--text",
                "把这个丝滑 hover 交互写进 KM，来自项目 Apollo。",
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "recall",
                "--root",
                str(tmp_path),
                "--query",
                "hover 交互",
                "--detail",
                "summary",
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "hover" in output
