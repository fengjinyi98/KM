---
doc_type: case
title: MaiLeMe 首页 HTML 复刻偏差复盘
summary: 记录一次 MaiLeMe 首页 SwiftUI 实现偏离 HTML 设计稿的复盘，核心结论是先几何对位再抽象，尤其要学习 HomeProportionalRow 与 HomeScreen 的实现方式。
tags:
  - maileme
  - swiftui
  - html
  - layout
  - design-parity
  - retrospective
---

# MaiLeMe 首页 HTML 复刻偏差复盘

## 对比对象
- SwiftUI 实现截图：`/Users/fengjinyi/Desktop/截屏2026-03-31 00.43.55.png`
- HTML 实现截图：`/Users/fengjinyi/Desktop/截屏2026-03-31 00.46.30.png`

## 结论
这次不是“差一点点”，而是**实现策略从一开始就偏了**：

> 用户要的是“按 HTML 设计稿逐块复刻”，错误做法却是“先做 SwiftUI 语义化重构，再试图靠微调回到设计稿”。

## 根因

### 1. 先抽象，后对位 —— 顺序错了
错误做法：
- 先抽主题 token
- 先做交互语义
- 先做可复用组件
- 再回头逼近设计稿

正确顺序：
- **先把截图和 HTML 结构逐块对齐**
- 再考虑 token、语义、可复用性

### 2. Header 是最大偏差源
错误点：
- 把主题点做成大号交互控件
- 把主题点单独占一行
- 把头部整体撑高
- 导致后面所有卡片整体下推

经验：
- HTML 里的主题点首先是**小尺寸视觉元素**
- 不是一级大控件
- Header 的高度和重心必须先贴住设计稿

### 3. 不能用固定行高去“猜”设计稿
错误做法是：
- 固定 `rowHeight`
- 再把左右卡片塞进去

正确做法是：
- 先分别测左右卡片在各自宽度下的理想高度
- 再取最大值作为整行高度
- 再按 11:9 / 9:11 摆位

### 4. 卡片内部不是统一模板
错误点：
- 把多张卡片理解成“同一类卡片的不同皮肤”

正确理解：
- `待决定`
- `待打卡`
- `闲置榨干`
- `小黑屋`
- `吃灰榜`
- `MVP`
- `变现总额`

这些卡片虽然属于一套视觉系统，但**内部版式都需要单独控制**。

## 必须学习的代码

### 文件 1
`/Users/fengjinyi/Desktop/MaiLeMe/MaiLeMe/Features/Home/HomeProportionalRow.swift`

这个文件的关键不是“比例”本身，而是：
- 用 `Layout` 协议
- 内容驱动高度
- 同行等高
- 宽度按份额精确分配

关键代码摘录：

```swift
struct HomeProportionalLayout: Layout {
    let leadingShare: CGFloat
    let trailingShare: CGFloat
    let spacing: CGFloat

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        guard subviews.count == 2, let width = proposal.width else { return .zero }

        let totalShare = leadingShare + trailingShare
        let usableWidth = max(width - spacing, 0)
        let leftW = usableWidth * (leadingShare / totalShare)
        let rightW = usableWidth * (trailingShare / totalShare)

        let leftSize = subviews[0].sizeThatFits(ProposedViewSize(width: leftW, height: nil))
        let rightSize = subviews[1].sizeThatFits(ProposedViewSize(width: rightW, height: nil))

        let maxRowHeight = max(leftSize.height, rightSize.height)
        return CGSize(width: width, height: maxRowHeight)
    }
}
```

必须记住：

> **先测内容，再定行高，再按比例摆位。**

---

### 文件 2
`/Users/fengjinyi/Desktop/MaiLeMe/MaiLeMe/Features/Home/HomeScreen.swift`

这个文件要学习的不是某个 modifier，而是**页面搭建顺序**：

```swift
VStack(spacing: MaiLeMeTheme.Layout.sectionSpacing) {
    HomeHeaderView(...)

    VStack(spacing: MaiLeMeTheme.Layout.gridSpacing) {
        heroMetricCard
            .frame(height: 130)

        HomeProportionalRow(leadingShare: 11, trailingShare: 9) {
            decisionsCard
        } trailing: {
            missionsCard
        }

        HomeProportionalRow(leadingShare: 9, trailingShare: 11) {
            extractorCard
        } trailing: {
            darkRoomCard
        }

        HomeProportionalRow(leadingShare: 11, trailingShare: 9) {
            dustRankingCard
        } trailing: {
            championCard
        }

        monetizationCard
            .frame(height: 96)
    }
}
```

必须记住：

> **先按设计稿顺序直接搭页面，而不是先把页面抽象成一套“通用业务壳层”。**

## 后续执行规则
以后在 MaiLeMe 首页这类“给了 HTML / 给了截图 / 要求复刻”的任务里，必须遵守：

1. **先截图对位，不先抽象**
2. **先确认 Header 高度与重心**
3. **比例行必须内容驱动高度**
4. **每张卡内部版式单独控制**
5. **SwiftUI 截图与 HTML 截图逐块一致后，才允许继续抽象**

## 一句话记忆
**MaiLeMe 首页复刻的优先级是：几何对位 > 视觉一致 > 再谈抽象。**
