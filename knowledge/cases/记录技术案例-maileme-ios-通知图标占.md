---
doc_type: case
title: 记录技术案例：MaiLeMe iOS 通知图标占
summary: 记录技术案例：MaiLeMe iOS 通知图标占位问题。现象：Home Screen 上 App 图标已正确更新，但本地通知/通知横幅左侧仍显示系统占位图标（网
tags: []
---

# 记录技术案例：MaiLeMe iOS 通知图标占

## 问题
记录技术案例：MaiLeMe iOS 通知图标占位问题。现象：Home Screen 上 App 图标已正确更新，但本地通知/通知横幅左侧仍显示系统占位图标（网格占位），即使已经卸载 App、清理构建缓存、重装也无效。排查证据：1）打包后的 MaiLeMe.app Info.plist 内 CFBundleIcons/CFBundlePrimaryIcon/CFBundleIconName 正常；2）actool 已生成 AppIcon60x60@2x 等系统尺寸图标；3）主图标 PNG 实际不透明，alpha extrema 为 255 到 255；4）通知 API 本身没有可自定义 icon 字段；5）切换为传统完整尺寸 AppIcon 资源集后问题仍可复现。结论：更可能是 iOS 系统层 Notification UI / IconServices 缓存或已知行为，不是项目通知代码或资源配置错误。外部依据：Apple Developer Forums 线程 808387 提到通知图标更新属于 known behavior，设备重启后才会刷新。建议：以后遇到 Home Screen 图标正常但通知里仍是占位图/旧图标的问题，优先验证是否为系统缓存问题，先重启设备再判断；不要继续在通知代码里寻找不存在的 icon 配置项。项目：MaiLeMe。平台：iOS / SwiftUI / UserNotifications。

## 实现思路
- 待补充实现思路。

## 关键代码
- 待补充关键代码片段。

## 适用场景
- 待补充适用场景。
