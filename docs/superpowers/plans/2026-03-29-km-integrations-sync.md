# KM Integrations Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 KM 仓库增加一个单向同步脚本，把仓库中的 Codex 插件源与 Claude skill 源同步到全局安装位置。

**Architecture:** 采用“仓库源文件 + 独立 Python 同步脚本 + 轻量测试”的实现方式。同步脚本只负责文件复制和 marketplace upsert，不侵入现有 `km_memory` 业务逻辑。

**Tech Stack:** Python 3、argparse、json、shutil、pathlib、pytest

---

## Planned File Structure

**Create:**
- `/Users/fengjinyi/Desktop/KM/claude-skills/km-memory/SKILL.md`
- `/Users/fengjinyi/Desktop/KM/scripts/sync_km_integrations.py`
- `/Users/fengjinyi/Desktop/KM/tests/test_sync_integrations.py`

**Modify:**
- `/Users/fengjinyi/Desktop/KM/README.md`

---

### Task 1: 建立 Claude skill 源文件

**Files:**
- Create: `/Users/fengjinyi/Desktop/KM/claude-skills/km-memory/SKILL.md`
- Test: `/Users/fengjinyi/Desktop/KM/tests/test_sync_integrations.py`

- [ ] **Step 1: 写失败测试，要求仓库存在 Claude skill 源文件**
- [ ] **Step 2: 运行测试确认失败**
- [ ] **Step 3: 创建 `claude-skills/km-memory/SKILL.md`**
- [ ] **Step 4: 运行测试确认通过**
- [ ] **Step 5: 提交**

---

### Task 2: 实现 marketplace upsert 与文件同步函数

**Files:**
- Create: `/Users/fengjinyi/Desktop/KM/scripts/sync_km_integrations.py`
- Test: `/Users/fengjinyi/Desktop/KM/tests/test_sync_integrations.py`

- [ ] **Step 1: 写失败测试，覆盖 marketplace upsert 与 `--check` 不写入**
- [ ] **Step 2: 运行测试确认失败**
- [ ] **Step 3: 实现最小同步函数与 CLI 参数解析**
- [ ] **Step 4: 运行测试确认通过**
- [ ] **Step 5: 提交**

---

### Task 3: 更新文档并做端到端验证

**Files:**
- Modify: `/Users/fengjinyi/Desktop/KM/README.md`
- Modify: `/Users/fengjinyi/Desktop/KM/tests/test_sync_integrations.py`

- [ ] **Step 1: 增加 README 的同步说明**
- [ ] **Step 2: 跑完整测试**
- [ ] **Step 3: 手动执行 `python scripts/sync_km_integrations.py --check` 与默认同步**
- [ ] **Step 4: 提交**

---

## Verification Checklist

- [ ] `. .venv/bin/activate && PYTHONPATH=src python -m pytest -q`
- [ ] `. .venv/bin/activate && python scripts/sync_km_integrations.py --check`
- [ ] `. .venv/bin/activate && python scripts/sync_km_integrations.py`

