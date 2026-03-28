"""KM 系统路径与初始化配置。"""

from pathlib import Path

# 这里集中定义 bootstrap 阶段必须存在的目录，避免 CLI 层重复维护路径列表。
REQUIRED_DIRECTORIES: tuple[tuple[str, ...], ...] = (
    ("inbox", "captures"),
    ("knowledge", "cases"),
    ("knowledge", "patterns"),
    ("memory", "profile"),
    ("memory", "projects"),
    ("memory", "logs"),
    ("assets", "images"),
    ("assets", "attachments"),
    ("index",),
    ("templates",),
)


# 负责创建 KM 的基础目录结构。
def bootstrap_layout(root: Path) -> None:
    """创建 KM 运行所需的最小目录结构。

    参数:
        root (Path): KM 仓库根目录。

    返回:
        None: 仅在文件系统中创建目录，不返回值。
    """
    for parts in REQUIRED_DIRECTORIES:
        # 将分段路径拼接到根目录下，确保每层目录都可自动创建。
        directory = root.joinpath(*parts)
        directory.mkdir(parents=True, exist_ok=True)
