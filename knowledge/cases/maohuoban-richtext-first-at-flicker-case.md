---
doc_type: case
title: MaoHuoBan 图文编辑器首次点击 @ 闪烁排查与修复
summary: 图文编辑页首次进入后点击一次 @ 会出现闪烁和位移。最终定位为 UIViewRepresentable + Proton Editor 的程序化文本插入路径不稳定，修复点是局部 replaceCharacters、去掉同帧手动 sync、仅在失焦时恢复 first responder。
tags:
  - case
  - maohuoban
  - swiftui
  - uiviewrepresentable
  - proton
  - richtext
  - mention
  - flicker
---

# MaoHuoBan 图文编辑器首次点击 @ 闪烁排查与修复

## 项目
- 项目目录：`/Users/fengjinyi/Desktop/new-maohuoban/maohuoban`
- 规则文件：`/Users/fengjinyi/Desktop/new-maohuoban/AGENTS.md`

## 现象
- 重启应用后首次进入帖子编辑页，点击一次键盘上的 `@`：
  - 正文首帧会闪烁
  - 某些轮次会伴随视图轻微位移
- 问题只在首次进入页时明显，后续进入会减弱或消失。

## 排除项
- 图片替换链路已单独修好，视觉上能立即切图。
- `@` 重复插入问题已消失。
- 日志已排除这些错误方向：
  - 第二个 `EditorView` / `Coordinator` 被重建
  - 旧 `blocks` 回灌覆盖当前 editor
  - 点击 `@` 后又触发一次 `applyBlocks`

## 根因
根因落在 **`SwiftUI + UIViewRepresentable + Proton Editor` 的程序化纯文本插入路径**：

1. 早期实现为插入一个 `@` 整份回写 `editor.attributedText`
2. 插入后又在同一帧手动调用 `scheduleSyncBlocks`
3. 插入后无条件 `becomeFirstResponder()`

这三件事叠在一起，会把单字符插入放大成一次不必要的布局/焦点刷新，最终表现为首次进入页点击 `@` 闪烁。

## 最终落地代码

### 1. `@` 改成局部字符替换
文件：
`/Users/fengjinyi/Desktop/new-maohuoban/maohuoban/Sources/MHBPublishFeature/Presentation/Views/CreateArticle/MHBArticleRichTextEditor.swift`

```swift
@MainActor
func insertMention(into editor: EditorView) {
    let shouldRestoreFocus = editor.isFirstResponder == false
    let selectionRange = preferredSelectionRange(for: editor)

    isApplyingBlocks = true
    editor.replaceCharacters(in: selectionRange, with: "@")
    let nextRange = NSRange(
        location: min(selectionRange.location + 1, editor.attributedText.length),
        length: 0
    )
    lastKnownSelectionRange = nextRange
    editor.selectedRange = nextRange
    isApplyingBlocks = false
    if shouldRestoreFocus {
        editor.becomeFirstResponder()
    }
}
```

### 2. 同步只走编辑器原生文本回调
文件：
`/Users/fengjinyi/Desktop/new-maohuoban/maohuoban/Sources/MHBPublishFeature/Presentation/Views/CreateArticle/MHBArticleRichTextEditor.swift`

```swift
nonisolated func editor(_ editor: EditorView, didChangeTextAt range: NSRange) {
    if editor.markedTextRange != nil {
        return
    }
    let committedText = editor.attributedText.string
    Task { @MainActor [weak self, weak editor] in
        guard let self, let editor else { return }
        if self.ignoredCommittedTextChangeCount > 0 {
            self.ignoredCommittedTextChangeCount -= 1
            return
        }
        let scheduledSnapshot = self.commitSyncGate.recordCommittedSnapshot(committedText)
        await Task.yield()
        let currentText = editor.attributedText.string
        let isMarked = editor.markedTextRange != nil
        guard self.commitSyncGate.shouldApply(
            scheduledSnapshot: scheduledSnapshot,
            currentText: currentText,
            isMarked: isMarked
        ) else {
            return
        }
        self.commitSyncGate.finish(scheduledSnapshot: scheduledSnapshot)
        self.syncBlocks(from: editor)
    }
}
```

### 3. 本地编辑结果保护，避免外层旧值回灌
文件：
`/Users/fengjinyi/Desktop/new-maohuoban/maohuoban/Sources/MHBPublishFeature/Presentation/Views/CreateArticle/MHBArticleRichTextEditor.swift`

```swift
private func syncBlocks(from editor: EditorView) {
    guard isApplyingBlocks == false else { return }
    if editor.markedTextRange != nil {
        return
    }
    let content = NSMutableAttributedString(attributedString: editor.attributedText)
    let reconcileResult = MHBPublishTopicTokenController.reconcileTopics(in: content)
    activeTopicAnchorLocation = reconcileResult.activeAnchorLocation
    let currentSelection = editor.selectedRange
    if content.isEqual(editor.attributedText) == false {
        isApplyingBlocks = true
        markNextCommittedTextChangeAsProgrammatic()
        editor.attributedText = content
        editor.selectedRange = NSRange(
            location: min(currentSelection.location, content.length),
            length: 0
        )
        isApplyingBlocks = false
    }
    DispatchQueue.main.async { [weak self] in
        self?.parent.onTopicsChange(reconcileResult.topics)
    }
    let nextBlocks = Self.serializeBlocks(from: content, previousBlocks: renderedBlocks)
    renderedBlocks = nextBlocks
    pendingParentBlocks = nextBlocks
    DispatchQueue.main.async { [weak self] in
        guard let self else { return }
        guard editor.attributedText.string == content.string else {
            return
        }
        self.parent.blocks = nextBlocks
    }
    updateHeight(from: editor)
}
```

## 关键结论
- 问题核心不在 SwiftUI 外层 `blocks` 状态机本身。
- 问题核心在 **富文本编辑器程序化插入文本的时机和方式**。
- 单字符插入场景里，**局部替换 + 只走原生文本变更回调 + 避免重复抢焦点** 是稳定写法。

## 应沉淀的工程规则
- 程序化插入纯文本优先使用编辑器局部 API，禁止整份回写 `attributedText`
- 程序化纯文本插入后禁止同帧额外手动 `syncBlocks`
- 只有在编辑器未聚焦时才调用 `becomeFirstResponder()`
- `pending nonce` 必须单调递增，消费条件使用 “>` lastHandled”

## 关联文件
- `/Users/fengjinyi/Desktop/new-maohuoban/maohuoban/Sources/MHBPublishFeature/Presentation/Views/CreateArticle/MHBArticleRichTextEditor.swift`
- `/Users/fengjinyi/Desktop/new-maohuoban/maohuoban/Sources/MHBPublishFeature/Presentation/Views/MHBEditPostScreen.swift`
- `/Users/fengjinyi/Desktop/new-maohuoban/AGENTS.md`
