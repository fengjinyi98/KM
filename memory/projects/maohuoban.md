---
doc_type: project
title: MaoHuoBan
summary: 图文编辑器当前有一条强约束：SwiftUI + UIViewRepresentable + Proton Editor 的程序化纯文本插入必须使用局部替换、避免同帧手动 sync，并且仅在失焦时恢复 first responder。
tags:
  - ios
  - swiftui
  - maohuoban
  - proton
  - richtext
  - editor
---

# MaoHuoBan

## 当前记录
- 图文编辑器的 mention / topic / token 插入属于高风险路径。
- 重点约束文件：
  - `/Users/fengjinyi/Desktop/new-maohuoban/maohuoban/Sources/MHBPublishFeature/Presentation/Views/CreateArticle/MHBArticleRichTextEditor.swift`
  - `/Users/fengjinyi/Desktop/new-maohuoban/AGENTS.md`
- 对 `UIViewRepresentable + Proton Editor` 做程序化纯文本插入时：
  - 必须优先使用 `replaceCharacters(in:with:)`
  - 禁止插入后同帧额外手动 `syncBlocks`
  - `becomeFirstResponder()` 只在当前未聚焦时调用
  - `pending nonce` 必须单调递增

## 关联案例
- `knowledge/cases/maohuoban-richtext-first-at-flicker-case.md`
