---
doc_type: case
title: SwiftUI 头像右下角相机图标挖空效果
summary: 沉淀一套可跨项目复用的 SwiftUI 实现：在头像右下角做相机图标“挖空”槽位，再把相机按钮填回去，形成头像可编辑的嵌入式视觉，而不是普通悬浮角标。
tags:
  - swiftui
  - ios
  - avatar
  - camera
  - cutout
  - blendmode
  - compositinggroup
---

# SwiftUI 头像右下角相机图标挖空效果

## 问题
很多“编辑头像”交互都需要在头像右下角放一个相机按钮。

最常见但最容易显得廉价的做法是：

1. 先画头像；
2. 再把一个小相机圆点直接叠在右下角。

这样的问题是：

- 相机图标像“贴片”，不是头像结构的一部分；
- 头像边缘会被小圆点硬压住；
- 一旦外层还有白色边框或卡片交界，视觉会很乱；
- 看起来像“浮在上面”，而不是“嵌进去”。

如果想做成更高级的效果，关键不是“多加一个角标”，而是要先**把头像右下角挖掉一块**，再把相机图标填回去。

## 结论
这类效果的正确做法是：

1. **头像本体和挖空遮罩必须在同一个合成组里处理**；
2. **挖空要用 `blendMode(.destinationOut)`**，而不是直接画一个背景色圆点去遮；
3. **挖空遮罩要比相机图标略大一圈**，这样才会形成“槽位”；
4. **相机图标最后再叠回去**，才能得到“嵌入式编辑入口”；
5. 如果需要更强的“压进内容层”感觉，可以再加一层白色背座和轻微高光/阴影。

一句话总结：

**先挖，再填。**

## 实现思路

### 1. 头像层只负责“头像 + 挖空”
这一步里不要直接放相机图标。

正确结构是：

```swift
ZStack(alignment: .bottomTrailing) {
    AvatarCircle()
    CutoutMask()
}
.compositingGroup()
```

这里的重点是：

- 头像本体和挖空遮罩必须处于同一个 `compositingGroup()` 中；
- 否则 `destinationOut` 不会按你想要的方式把头像挖掉。

### 2. 挖空遮罩必须比相机按钮大一点
如果挖空尺寸和相机按钮完全一样，视觉会显得挤、边缘也会脏。

推荐：

- 相机按钮直径：`24~28`
- 挖空遮罩直径：`相机按钮 + 4`

这样可以留出一圈呼吸间距，看起来像“预留槽位”。

### 3. 相机按钮最后单独叠回去
顺序一定是：

1. 头像本体
2. 挖空遮罩
3. 相机按钮

不能把相机图标直接放进合成组里，否则它也会一起被混掉。

### 4. 如果要更像“嵌入”
可以给头像外层再加一层背座，例如白色圆盘：

- 头像本体深色；
- 外层背座浅色；
- 背座加一层轻微高光和阴影；

这样头像本体像嵌在承托层里，而不是纯粹悬浮。

## 可直接复用的实现代码

### 1. 最小可用版本：头像右下角相机图标挖空

```swift
import SwiftUI

struct AvatarCameraCutoutButton<AvatarContent: View>: View {
    let avatarSize: CGFloat
    let cutoutSize: CGFloat
    let cameraBadgeSize: CGFloat
    let action: () -> Void
    let avatarContent: AvatarContent

    init(
        avatarSize: CGFloat = 96,
        cutoutSize: CGFloat = 30,
        cameraBadgeSize: CGFloat = 26,
        action: @escaping () -> Void,
        @ViewBuilder avatarContent: () -> AvatarContent
    ) {
        self.avatarSize = avatarSize
        self.cutoutSize = cutoutSize
        self.cameraBadgeSize = cameraBadgeSize
        self.action = action
        self.avatarContent = avatarContent()
    }

    var body: some View {
        Button(action: action) {
            ZStack(alignment: .bottomTrailing) {
                ZStack(alignment: .bottomTrailing) {
                    Circle()
                        .fill(Color.black.opacity(0.95))
                        .frame(width: avatarSize, height: avatarSize)
                        .overlay {
                            avatarContent
                                .clipShape(Circle())
                        }

                    Circle()
                        .fill(Color.black)
                        .frame(width: cutoutSize, height: cutoutSize)
                        .offset(x: -2, y: -2)
                        .blendMode(.destinationOut)
                }
                .compositingGroup()

                Circle()
                    .fill(Color.black.opacity(0.72))
                    .frame(width: cameraBadgeSize, height: cameraBadgeSize)
                    .overlay {
                        Image(systemName: "camera.fill")
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundStyle(.white)
                    }
                    .offset(x: -4, y: -4)
            }
        }
        .buttonStyle(.plain)
        .accessibilityLabel("更换头像")
    }
}
```

### 2. 强化版本：带白色背座的嵌入式头像

如果你想让头像看起来不是简单圆形，而是**嵌入在内容层交界处**，可以加一层背座：

```swift
import SwiftUI

struct EmbeddedAvatarCameraButton<AvatarContent: View>: View {
    let action: () -> Void
    let avatarContent: AvatarContent

    init(
        action: @escaping () -> Void,
        @ViewBuilder avatarContent: () -> AvatarContent
    ) {
        self.action = action
        self.avatarContent = avatarContent()
    }

    var body: some View {
        Button(action: action) {
            ZStack(alignment: .bottomTrailing) {
                ZStack(alignment: .bottomTrailing) {
                    Circle()
                        .fill(.white)
                        .frame(width: 104, height: 104)
                        .overlay {
                            Circle()
                                .fill(Color.black.opacity(0.95))
                                .frame(width: 96, height: 96)
                                .overlay {
                                    avatarContent
                                        .clipShape(Circle())
                                }
                        }

                    Circle()
                        .fill(Color.black)
                        .frame(width: 30, height: 30)
                        .offset(x: -2, y: -2)
                        .blendMode(.destinationOut)
                }
                .compositingGroup()
                .background {
                    Circle()
                        .fill(Color.white.opacity(0.92))
                        .frame(width: 104, height: 104)
                        .shadow(color: .white.opacity(0.7), radius: 4, x: -2, y: -2)
                        .shadow(color: Color.black.opacity(0.10), radius: 10, x: 4, y: 6)
                }

                Circle()
                    .fill(Color.black.opacity(0.72))
                    .frame(width: 26, height: 26)
                    .overlay {
                        Image(systemName: "camera.fill")
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundStyle(.white)
                    }
                    .overlay {
                        Circle()
                            .stroke(Color.white.opacity(0.2), lineWidth: 0.5)
                    }
                    .offset(x: -4, y: -4)
            }
        }
        .buttonStyle(.plain)
        .accessibilityLabel("更换头像")
    }
}
```

## 关键点

### 1. 为什么必须用 `compositingGroup()`
因为 `blendMode(.destinationOut)` 不是“删掉某个 view”，而是对当前合成结果做挖空。

如果不加 `compositingGroup()`：

- 遮罩可能只影响局部；
- 或根本不按预期工作；
- 最终看起来像黑色补丁，而不是挖空。

### 2. 为什么挖空遮罩要用纯色
遮罩本质上不是视觉元素，而是“减掉一块”的工具。

所以这里最稳的做法就是：

```swift
Circle()
    .fill(Color.black)
    .blendMode(.destinationOut)
```

颜色本身并不重要，重要的是它参与合成后会把对应区域挖掉。

### 3. 为什么不能直接用背景色去盖
因为页面背景色一变，这个“补丁”就穿帮了：

- 深色背景时看起来不对；
- 毛玻璃背景时边缘发脏；
- 卡片层级变化时会露馅。

挖空方案的优点是：

**它是结构性的，不依赖页面背景色。**

## 适用场景

这套实现适合：

1. 用户头像编辑入口；
2. 社区个人中心；
3. 创作者主页；
4. 带封面图的资料页；
5. 任何需要“头像本体 + 可编辑角标”，但不想做成廉价悬浮贴片的页面。

## 不适用场景

不建议在这些场景用：

1. 头像本身很小（例如 32pt）；
2. 角标只是纯状态提示，不可点击；
3. 设计语言明确要求“角标悬浮”，而不是嵌入。

## 易错点

1. **忘记 `compositingGroup()`**
   - 挖空不会生效或效果错误。

2. **把相机图标也放进同一个合成组**
   - 相机图标可能一起被挖掉。

3. **挖空遮罩和相机按钮一样大**
   - 视觉会显得挤，没有“槽位感”。

4. **直接拿背景色去盖**
   - 页面背景一变就穿帮。

## 适合配合使用的模式

这套头像挖空效果，通常和以下结构一起出现时最自然：

- 沉浸式头图；
- 白色内容层；
- 头像卡在头图与内容层交界处；
- 头像左对齐但略大于页面基础边距；

也就是说，这个效果本身是**头像交界嵌入模式**的一个子问题，
但它应该被单独记录、单独复用，而不是混在某个具体项目页面里。
