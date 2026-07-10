---
name: hermes-knowledge-base
description: '知识库整理规范：Markdown + AAAK 格式，适配 Git/rsync 同步。
  Use when organizing markdown documents, building a knowledge base, migrating notes across devices,
  or standardizing documentation format.
  禁用：代码仓库文档、项目 README、一次性笔记。'
version: 1.0.0
author: Hermes
license: MIT
platforms:
- linux
- macos
- windows
metadata:
  hermes:
    tags:
      trigger:
      - 知识库
      - 笔记整理
      - Markdown 规范
      - AAAK
      - 文档归档
      - git同步文档
      - rsync迁移
      - 知识库格式
      - knowledge base
      - markdown整理
      disable:
      - 项目README
      - 一次性笔记
      - 代码注释
    skill_type: workflow
    priority: normal
---
# 知识库整理规范

## 核心标准

- 格式：Markdown + AAAK 规范
- 同步：适配 Git / rsync 跨设备迁移
- 结构：结论前置，操作步骤居中，补充说明后置
- 标题层级：精简，不堆砌空段落

## AAAK 格式要点

- A（Abstract）：一句话摘要
- A（Architecture）：架构/原理说明
- A（Action）：具体操作步骤
- K（Knowledge）：相关知识链接

## 文件组织

- 按主题分类目录
- 每个主题一个独立 md 文件
- 图片/附件放在同目录 assets/ 下
- 索引文件（README.md）列出所有主题

## 适配要求

- Git：文本文件，无二进制大文件
- rsync：路径统一，无绝对路径引用
- 跨设备：使用相对路径，不依赖特定环境变量
