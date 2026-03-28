"""Capture 流程测试。"""

from pathlib import Path

from km_memory.capture import capture_note


# 这里验证具有明显技术案例特征的输入会直接写入正式案例目录。
def test_capture_case_writes_formal_markdown(tmp_path: Path) -> None:
    """验证技术案例输入会被识别并落入正式 case 库。"""
    result = capture_note(
        root=tmp_path,
        text="把这个卡片悬浮交互写进 KM，它解决的是 hover 反馈生硬的问题，来自项目 foo。",
    )

    assert result.doc_type == "case"
    assert result.is_inbox is False
    assert result.path.exists()
    assert "knowledge/cases" in str(result.path)


# 这里验证信息不足的输入不会污染正式库，而是先进入 inbox 等待整理。
def test_capture_unknown_note_goes_to_inbox(tmp_path: Path) -> None:
    """验证模糊输入会回退到 inbox。"""
    result = capture_note(root=tmp_path, text="记一下这个以后可能有用")

    assert result.is_inbox is True
    assert result.path.exists()
    assert "inbox/captures" in str(result.path)


# 这里验证项目更新不会落入 inbox，而是更新主档案并追加变更日志。
def test_capture_project_updates_profile_and_log(tmp_path: Path) -> None:
    """验证项目记忆会更新主档案并生成日志。"""
    first = capture_note(root=tmp_path, text="更新项目 Apollo：当前阶段是内测，技术栈是 SwiftUI。")
    second = capture_note(root=tmp_path, text="更新项目 Apollo：新增约束是要兼容离线场景。")

    project_file = tmp_path / "memory" / "projects" / "apollo.md"
    log_files = sorted((tmp_path / "memory" / "logs").glob("project-apollo-*.md"))

    assert first.doc_type == "project"
    assert first.is_inbox is False
    assert second.path == project_file
    assert project_file.exists()
    assert log_files


# 这里验证个人画像更新会写入正式 profile 主档案，而不是回退到 inbox。
def test_capture_profile_updates_profile_archive(tmp_path: Path) -> None:
    """验证个人画像输入会更新正式 profile 条目。"""
    result = capture_note(root=tmp_path, text="更新我的个人画像：我偏好简洁、渐进披露、Markdown 优先。")

    profile_file = tmp_path / "memory" / "profile" / "me.md"

    assert result.doc_type == "profile"
    assert result.is_inbox is False
    assert result.path == profile_file
    assert profile_file.exists()
