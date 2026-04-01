---
doc_type: project
title: OpenAI
summary: OpenAI CTF / Organizer Keepalive 项目当前形成执行面、控制面、注册器三层架构，并明确 organizer 优先、oauth 候补策略。
tags: [project, openai, ctf, organizer, keepalive, control-plane]
---

# OpenAI

## 当前记录
当前主线是三层架构：

1. **CLIProxyAPI** 作为执行面：
   - 管理认证文件
   - 提供推理入口
   - 提供 usage / request-log / management API
   - 为 organizer 账号提供 fallback 保活路径

2. **pool-orchestrator** 作为控制面：
   - 管理账号池分层
   - 执行 warmup / probe / 补池调度
   - 应用 organizer 优先、oauth 候补策略
   - 聚合任务详情与治理状态

3. **codex-register** 作为外部注册器：
   - 默认通过 batch 并发模式出号
   - 支持无 workspace 时保留 organizer_candidate
   - 可向 CPAMC 上传认证文件

## 当前策略
- organizer 号优先 serving。
- oauth_full 号作为候补与长期资产。
- organizer 配额不足或死号直接淘汰。
- oauth_full 配额不足保留，等待恢复。

## 当前关键资产
- 项目文档
- 控制面代码与 git 提交
- 注册器改造代码与 git 提交
- CPAMC 执行面配置与演示版本
