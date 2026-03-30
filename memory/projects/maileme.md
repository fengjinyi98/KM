---
doc_type: project
title: MaiLeMe
summary: 首页 HTML 设计稿复刻的当前强约束是先几何对位、后抽象，必须重点参考 HomeProportionalRow 与 HomeScreen 的实现方式。
tags:
  - swiftui
  - ios
  - maileme
  - home
  - design-parity
---

# MaiLeMe

## 当前记录
- 首页开发阶段新增强约束：**当需求是按 HTML / 设计稿复刻首页时，必须先逐块几何对位，再做主题 token、交互语义和组件抽象。**
- 重点学习文件：
  - `/Users/fengjinyi/Desktop/MaiLeMe/MaiLeMe/Features/Home/HomeProportionalRow.swift`
  - `/Users/fengjinyi/Desktop/MaiLeMe/MaiLeMe/Features/Home/HomeScreen.swift`
- 首页比例行必须采用 **Layout 驱动 + 内容测量后的同行等高** 思路。
- 首页页面骨架必须按设计稿顺序直接搭建，不允许再先做语义化重构后试图靠微调回到设计稿。

## 当前阶段的明确禁令
- 禁止先做“大主题点交互控件”再逼近 HTML 头部
- 禁止先写固定 `rowHeight` 再猜设计稿
- 禁止把多张首页卡片当成统一内部模板

## 关联案例
- `knowledge/cases/maileme-首页-html-复刻偏差复盘.md`
