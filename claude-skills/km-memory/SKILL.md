---
name: km-memory
description: 在用户明确要求时，写入、更新或检索本地 KM（Knowledge + Memory）系统。适用于“把这个案例写进我们的 KM”“更新项目记忆”“更新个人画像”“去 KM 里查一下有没有类似案例”等场景。遵循显式触发与渐进式披露原则。
---

# KM Memory

在 Claude 中，把这个 skill 当作你的 **本地知识库 / 记忆系统入口**。

## 适用场景
仅在用户**明确要求**时使用，例如：
- “把这个案例写进我们的 KM”
- “更新我们的项目记忆”
- “更新下我的个人画像”
- “去 KM 里查一下有没有类似案例”
- “查一下我们的 KM 里有没有这个交互实现”

## 核心原则
1. **显式触发**：如果用户没有明确要求，不主动访问 KM。
2. **渐进式披露**：检索时先返回摘要，需要时再展开细节或正文。
3. **Markdown 真相源**：所有真实数据都必须写回本地 Markdown。
4. **索引可重建**：SQLite 只负责检索，不作为主存储。

## KM 仓库位置
默认 KM 根目录：

```bash
/Users/fengjinyi/Desktop/KM
```

## 使用方式
如果 KM 仓库根目录存在本地虚拟环境，先启用：

```bash
cd /Users/fengjinyi/Desktop/KM
[ -f .venv/bin/activate ] && . .venv/bin/activate
```

### 初始化 KM 结构

```bash
cd /Users/fengjinyi/Desktop/KM
[ -f .venv/bin/activate ] && . .venv/bin/activate
PYTHONPATH=src python -m km_memory.cli bootstrap --root .
```

### 写入技术案例

```bash
cd /Users/fengjinyi/Desktop/KM
[ -f .venv/bin/activate ] && . .venv/bin/activate
PYTHONPATH=src python -m km_memory.cli capture --root . --text "把这个案例写进我们的 KM"
```

### 更新项目记忆

```bash
cd /Users/fengjinyi/Desktop/KM
[ -f .venv/bin/activate ] && . .venv/bin/activate
PYTHONPATH=src python -m km_memory.cli capture --root . --text "更新项目 Apollo：当前阶段是内测，技术栈是 SwiftUI。"
```

### 更新个人画像

```bash
cd /Users/fengjinyi/Desktop/KM
[ -f .venv/bin/activate ] && . .venv/bin/activate
PYTHONPATH=src python -m km_memory.cli capture --root . --text "更新我的个人画像：我偏好简洁、渐进披露、Markdown 优先。"
```

### 检索 KM

```bash
cd /Users/fengjinyi/Desktop/KM
[ -f .venv/bin/activate ] && . .venv/bin/activate
PYTHONPATH=src python -m km_memory.cli recall --root . --query "hover 交互" --detail summary
```

## 输出约束
- 写入时自动判断 `case / project / profile / inbox`。
- 信息不足时优先落到 `inbox/`，不要污染正式库。
- 项目记忆更新时，优先写回主档案并追加日志。
- 个人画像更新时，优先写回 `memory/profile/me.md` 并追加日志。
- 检索时优先输出标题、摘要、来源路径。
- 除非用户继续要求，否则不要直接输出全文正文。

## 说明
这个 skill 对应的底层系统位于：

- KM 仓库：`/Users/fengjinyi/Desktop/KM`
- CLI 模块：`/Users/fengjinyi/Desktop/KM/src/km_memory`

如果后续 KM 仓库结构发生变化，应同步更新这里的路径说明。
