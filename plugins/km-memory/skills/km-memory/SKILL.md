---
name: km-memory
description: 在用户明确要求时，写入、更新或检索本地 KM（Knowledge + Memory）系统。遵循显式触发与渐进式披露原则。
---

# KM Memory

## 适用场景
仅在用户**明确要求**时使用，例如：
- “把这个案例写进我们的 KM”
- “更新我们的项目记忆”
- “更新下我的个人画像”
- “去 KM 里查一下有没有类似案例”

## 核心原则
1. **显式触发**：如果用户没有明确要求，不主动访问 KM。
2. **渐进式披露**：检索时先返回摘要，需要时再展开细节或正文。
3. **Markdown 真相源**：所有真实数据都必须写回本地 Markdown。
4. **索引可重建**：SQLite 只负责检索，不作为主存储。

## 工作目录
默认工作目录：`/Users/fengjinyi/Desktop/KM`

## CLI 用法
如果 KM 仓库根目录存在本地虚拟环境，先启用：

```bash
[ -f .venv/bin/activate ] && . .venv/bin/activate
```

在 KM 仓库根目录执行：

```bash
PYTHONPATH=src python -m km_memory.cli bootstrap --root .
PYTHONPATH=src python -m km_memory.cli capture --root . --text "把这个案例写进我们的 KM"
PYTHONPATH=src python -m km_memory.cli recall --root . --query "hover 交互" --detail summary
```

## 行为约束
- 写入时自动判断 `case / project / profile / inbox`。
- 信息不足时优先落到 `inbox/`，不要污染正式库。
- 项目记忆更新时，优先写回主档案并追加日志。
- 检索时优先输出标题、摘要、来源路径。
- 除非用户继续要求，否则不要直接输出全文正文。
