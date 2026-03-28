# KM

KM 是一个以 **本地 Markdown** 为真相源、以 **SQLite** 为索引层的个人知识库与记忆系统。

它的目标不是做重型笔记软件，而是提供一套更可控的本地方案：

- 用 Markdown 沉淀技术案例
- 用 Markdown 维护项目记忆与个人画像
- 用 Git 管理历史并推送远程仓库备份
- 用 SQLite FTS 做轻量混合检索
- 用 Codex plugin 在**显式触发**时完成写入、更新、召回

## 核心原则

- **本地优先**：Markdown 是唯一真相源
- **显式触发**：只有你明确要求时，才访问 KM
- **渐进式披露**：先返回摘要，需要时再展开正文
- **轻量优先**：第一版不引入向量模型

## 快速开始

### 1. 创建本地虚拟环境

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pytest pyyaml
```

### 2. 初始化 KM 目录结构

```bash
PYTHONPATH=src python -m km_memory.cli bootstrap --root .
```

### 3. 写入一个技术案例

```bash
PYTHONPATH=src python -m km_memory.cli capture --root . --text "把这个丝滑 hover 交互写进 KM，来自项目 Apollo。"
```

### 4. 更新项目记忆

```bash
PYTHONPATH=src python -m km_memory.cli capture --root . --text "更新项目 Apollo：当前阶段是内测，技术栈是 SwiftUI。"
```

### 5. 更新个人画像

```bash
PYTHONPATH=src python -m km_memory.cli capture --root . --text "更新我的个人画像：我偏好简洁、渐进披露、Markdown 优先。"
```

### 6. 按需检索 KM

```bash
PYTHONPATH=src python -m km_memory.cli recall --root . --query "hover 交互" --detail summary
```

## 当前支持的内容类型

### 1. 技术案例
默认保存：
- 问题说明
- 实现思路
- 关键代码片段占位
- 来源上下文

### 2. 项目记忆
当前支持：
- 项目主档案写回
- 项目变更日志追加

### 3. 个人画像
当前支持：
- `memory/profile/me.md` 主档案写回
- 画像变更日志追加

## 目录结构

```text
KM/
  inbox/
    captures/
  knowledge/
    cases/
    patterns/
  memory/
    profile/
    projects/
    logs/
  assets/
    images/
    attachments/
  index/
    km.db
  plugins/
    km-memory/
  src/
    km_memory/
  templates/
```

## Plugin 入口

当前仓库内已包含 repo-local plugin：

- Marketplace：`/Users/fengjinyi/Desktop/KM/.agents/plugins/marketplace.json`
- Plugin：`/Users/fengjinyi/Desktop/KM/plugins/km-memory`

它遵循两条硬规则：
- 只有用户明确要求时才访问 KM
- 检索时优先返回摘要，而不是直接输出全文

## 测试

```bash
. .venv/bin/activate
PYTHONPATH=src python -m pytest -q
```

## Git 备份建议

建议把这个仓库作为一个独立 Git 仓库使用：

```bash
git remote add origin <your-repo-url>
git push -u origin main
```

这样可以同时获得：
- 本地可控的 Markdown 真相源
- Git 历史追踪
- 远程仓库备份

## 后续演进方向

- 完善 profile / project 的字段级合并
- 增加更稳定的 Markdown 模板渲染
- 增加更强的混合排序与过滤
- 视需要再引入 embedding / 向量检索
