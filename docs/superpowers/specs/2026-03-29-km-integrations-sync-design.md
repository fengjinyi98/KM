# KM 集成同步脚本设计文档

**日期：** 2026-03-29  
**主题：** KM 集成同步脚本（Codex 全局插件 + Claude 全局 Skill）  
**状态：** 已确认，可进入实施阶段

---

## 1. 背景

当前 KM 仓库中已经存在两类可复用集成：

- Codex repo-local 插件：`plugins/km-memory/`
- Claude 全局 skill：当前手工安装在 `~/.claude/skills/km-memory/SKILL.md`

为了避免未来在多个位置重复维护，需要增加一个**单向同步脚本**，以 `/Users/fengjinyi/Desktop/KM` 为唯一真相源，把更新同步到外部安装位置。

---

## 2. 目标

提供一个轻量脚本，统一完成以下动作：

1. 将仓库中的 Codex 插件源同步到 `~/plugins/km-memory`
2. 对 `~/.agents/plugins/marketplace.json` 执行 `km-memory` 条目 upsert
3. 将仓库中的 Claude skill 源同步到 `~/.claude/skills/km-memory/SKILL.md`
4. 支持“只检查不写入”的校验模式

---

## 3. 核心原则

### 3.1 单向同步
- 仅允许从 KM 仓库同步到外部位置；
- 不允许从全局安装位置反向改回仓库。

### 3.2 KM 仓库是唯一真相源
- `plugins/km-memory/` 是 Codex 集成源；
- `claude-skills/km-memory/SKILL.md` 是 Claude 集成源；
- 外部安装目录只是发布目标。

### 3.3 尽量不破坏外部现有配置
- 同步 `~/plugins/km-memory` 时，只覆盖该插件目录；
- 更新 `~/.agents/plugins/marketplace.json` 时，仅 upsert `km-memory` 条目，不删除其他插件。

### 3.4 轻量优先
- 使用 Python 标准库完成主要逻辑；
- 不引入额外依赖；
- 不把同步逻辑塞进 `km_memory.cli`，避免和 KM 业务逻辑耦合。

---

## 4. 建议文件布局

新增：

```text
KM/
  claude-skills/
    km-memory/
      SKILL.md
  scripts/
    sync_km_integrations.py
  tests/
    test_sync_integrations.py
```

说明：
- `claude-skills/km-memory/SKILL.md`：Claude 集成源文件；
- `scripts/sync_km_integrations.py`：同步脚本；
- `tests/test_sync_integrations.py`：同步逻辑测试。

---

## 5. 脚本行为

默认命令：

```bash
python scripts/sync_km_integrations.py
```

默认行为：
- 同步 Codex 全局插件；
- 同步 Claude 全局 skill；
- 更新 home-local marketplace；
- 打印执行结果。

可选参数：
- `--codex-only`：仅同步 Codex 集成；
- `--claude-only`：仅同步 Claude 集成；
- `--check`：只检查源文件和目标状态，不做写入。

---

## 6. 详细同步逻辑

### 6.1 Codex
源：
- `/Users/fengjinyi/Desktop/KM/plugins/km-memory`

目标：
- `~/plugins/km-memory`
- `~/.agents/plugins/marketplace.json`

行为：
- 目录级复制 / 覆盖 `~/plugins/km-memory`
- 若 `~/.agents/plugins/marketplace.json` 不存在，则创建
- 若存在，则保留其他插件条目，仅 upsert `km-memory`

### 6.2 Claude
源：
- `/Users/fengjinyi/Desktop/KM/claude-skills/km-memory/SKILL.md`

目标：
- `~/.claude/skills/km-memory/SKILL.md`

行为：
- 创建目录（如不存在）
- 覆盖目标 skill 文件

---

## 7. 第一版不做的事

- 不做双向同步
- 不做冲突检测或 merge
- 不做自动监听同步
- 不改造 Claude 插件系统，仅使用 Claude skills 目录
- 不把同步逻辑接入 KM 主 CLI

---

## 8. 成功标准

完成后应满足：
1. 仓库中存在 `claude-skills/km-memory/SKILL.md` 作为 Claude 源文件
2. 可通过一条命令同步 Codex 全局插件
3. 可通过一条命令同步 Claude 全局 skill
4. `~/.agents/plugins/marketplace.json` 中 `km-memory` 条目可自动创建或更新
5. 测试可以覆盖：
   - marketplace upsert
   - 同步目标文件生成
   - `--check` 不写入

