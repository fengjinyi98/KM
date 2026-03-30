---
doc_type: case
title: MaiLeMe 详情页沉浸式 Hero 下拉拉伸与系统导航栏联显
summary: 记录一套可复用的 SwiftUI 实现模式：单一 Hero 背景源、ScrollView 内容层顶部承载、真实 contentOffset 驱动拉伸、系统导航栏标题槽位联显，以及遇到滚动/头图问题时的日志排障方法。
tags:
  - swiftui
  - ios
  - hero-header
  - scroll
  - navigation-bar
  - immersive-ui
---

# MaiLeMe 详情页沉浸式 Hero 下拉拉伸与系统导航栏联显

## 问题
在实现沉浸式详情页时，常见问题有：

1. 头图没有从手机顶部开始，而是从导航栏下面开始；
2. 下拉时露出纯色背景，而不是头图本身被拉伸；
3. 滚动后导航栏标题不联显，或者联显时机不稳定；
4. 为了“修视觉”不断调阈值、调层级，最后越改越乱。

这类问题的根因通常不是单个参数错误，而是**容器层级、背景来源、滚动偏移来源**三件事同时处理错了。

## 结论
这类沉浸式 Hero 的正确做法是：

1. **Hero 背景只能有一个来源**；
2. **这个背景必须放在 ScrollView 内容层顶部**，而不是放在 ScrollView 背后；
3. **下拉拉伸必须使用真实 ScrollView contentOffset 驱动**；
4. **系统导航栏标题联显不要依赖 `navigationTitle` 硬切**，要用独立 title slot；
5. **方向不明确时先打日志**，禁止盲调。

## 实现思路

### 1. 结构分层
推荐把页面拆成三层：

- `DetailHeroStretchBackground`
  - 唯一顶部背景源；
  - 负责从状态栏顶部开始铺开；
  - 负责下拉拉伸；
- `DetailHeroSection`
  - 只负责徽标、标题、判词、悬浮指标牌；
  - 不再自己绘制背景；
- `ToolbarTitleSlot`
  - 负责滚动后在系统导航栏承接标题；
  - 不和 Hero 内容本身耦合。

也就是说：

**背景层只做背景**，**内容层只做内容**，**导航栏标题只做导航栏标题**。

### 2. 背景层必须放在 ScrollView 内容层顶部
正确结构：

```swift
ScrollView {
    ZStack(alignment: .top) {
        HeroStretchBackground(...)
        VStack(spacing: 0) {
            HeroContent(...)
            ContentSections(...)
        }
    }
}
```

错误结构：

```swift
ZStack {
    HeroStretchBackground(...)
    ScrollView { ... }
}
```

错误原因：
- `ScrollView` 本身常常会有自己的背景或内容遮挡；
- 背景放在它后面时，看起来像“背景消失”或“下拉露黑边”；
- 视觉上就不是“头图在拉伸”，而是“下面有一块别的背景露出来”。

### 3. 下拉拉伸应由真实 `contentOffset` 驱动
应读取：

```swift
scrollGeometry.contentOffset.y + scrollGeometry.contentInsets.top
```

而不是：
- Hero 自己的 `minY` 乱猜；
- 某个子视图的局部坐标。

原因：
- `contentOffset` 才是页面真实滚动值；
- 下拉时它会变成负值；
- 上推时它会变成正值；
- 这是最稳定的驱动源。

### 4. 标题联显不要用 `navigationTitle` 硬切
推荐：

```swift
.navigationTitle("")
.toolbarBackground(.hidden, for: .navigationBar)
.toolbar {
    ToolbarItem(placement: .title) {
        ToolbarTitleSlot(title: toolbarTitle)
    }
}
```

再通过滚动偏移决定：
- `toolbarTitle = nil`
- 或 `toolbarTitle = item.name`

这样：
- 系统导航栏仍然是原生行为；
- 标题显隐更稳定；
- 不会出现 `navigationTitle` 直接切换带来的突兀感。

### 5. 未知根因时先加临时日志
优先打印：
- `safeAreaTop`
- `contentOffset`
- 背景高度
- 标题联显阈值是否命中
- 当前标题状态

这样可以快速判断：
- 是背景层级错了；
- 是偏移源错了；
- 还是阈值错了。

## 关键代码

### 1. 读取真实滚动偏移
```swift
.onScrollGeometryChange(for: CGFloat.self) { scrollGeometry in
    scrollGeometry.contentOffset.y + scrollGeometry.contentInsets.top
} action: { oldValue, newValue in
    updateScrollOffset(oldValue: oldValue, newValue: newValue)
}
```

### 2. 用单一背景源做下拉拉伸
```swift
struct DetailHeroStretchBackground: View {
    let artwork: some View
    let safeAreaTop: CGFloat
    let contentOffsetY: CGFloat

    var body: some View {
        let baseHeight: CGFloat = 420 + safeAreaTop
        let stretchHeight = baseHeight + max(-contentOffsetY, 0)

        artwork
            .frame(height: stretchHeight)
            .frame(maxWidth: .infinity, alignment: .top)
            .offset(y: contentOffsetY < 0 ? contentOffsetY : 0)
            .ignoresSafeArea(edges: .top)
    }
}
```

关键点：
- `max(-contentOffsetY, 0)`：只在下拉时增加高度；
- `offset(y: contentOffsetY)`：在下拉时反向抵消内容整体下移，让背景锚定在屏幕顶部；
- 背景从头到尾只有这一层。

### 3. 正确的页面层级
```swift
ScrollView {
    ZStack(alignment: .top) {
        DetailHeroStretchBackground(...)

        VStack(spacing: 0) {
            DetailHeroSection(...)
            DetailBodySections(...)
        }
    }
}
```

### 4. 导航栏标题联显
```swift
@State private var toolbarTitle: String?
@State private var contentOffsetY: CGFloat = 0

private func syncToolbarTitle() {
    let showThreshold: CGFloat = 120
    let nextTitle: String? = contentOffsetY >= showThreshold ? itemName : nil

    guard nextTitle != toolbarTitle else { return }
    withAnimation(.easeInOut(duration: 0.18)) {
        toolbarTitle = nextTitle
    }
}
```

### 5. 临时日志模板
```swift
logger.debug("scroll offset changed old=\(oldValue, format: .fixed(precision: 2)) new=\(newValue, format: .fixed(precision: 2)) normalized=\(normalized, format: .fixed(precision: 2))")
logger.debug("sync toolbar title contentOffsetY=\(contentOffsetY, format: .fixed(precision: 2)) threshold=\(showThreshold, format: .fixed(precision: 2)) nextTitle=\(nextTitle ?? \"nil\", privacy: .public)")
```

## 适用场景
这套模式适用于：

1. **沉浸式详情页**
   - 商品详情
   - 内容详情
   - 活动详情
   - 个人页头图

2. **需要系统导航栏承接标题的页面**
   - 初始强调视觉头图；
   - 滚动后强调上下文标题。

3. **需要下拉时头图拉伸的页面**
   - 头图从状态栏顶部开始铺开；
   - 用户下拉时希望看到“头图本身被拉伸”，而不是露出额外背景。

4. **有复杂模块内容但首屏必须保留情绪表达的工具页**
   - 上半屏偏情绪封面；
   - 下半屏偏工具操作和内容。

## 不适用场景
不建议在以下情况下用这套：

1. 页面没有 Hero，只是普通列表页；
2. 页面顶部没有沉浸式图片或视觉背景；
3. 页面要求固定导航栏，不需要标题联显；
4. 顶部只是普通卡片，不需要拉伸效果。

## 错误经验
以下做法都已验证会出问题：

1. **双背景源**
   - 一个背景在 Hero 里；
   - 一个背景在页面外层；
   - 结果是下拉时露出错误背景或层次冲突。

2. **把背景放在 ScrollView 背后**
   - 看起来像“背景不见了”；
   - 本质是被 ScrollView 自身内容层遮住。

3. **用 Hero 自己的 `minY` 猜滚动联动**
   - 容易拿到不稳定的局部值；
   - 导致标题联显时机错误。

4. **不打日志直接调阈值**
   - 最容易越改越乱；
   - 无法知道到底是层级问题、偏移源问题，还是阈值问题。

## 对应项目文件（当代码仍存在时）
- `/Users/fengjinyi/Desktop/MaiLeMe/MaiLeMe/Features/Detail/ItemDetailScreen.swift`
- `/Users/fengjinyi/Desktop/MaiLeMe/MaiLeMe/Features/Detail/Sections/DetailHeroSection.swift`

即使未来项目代码被删除，上面的实现思路和关键代码仍可直接复用到新的 SwiftUI 项目中。
