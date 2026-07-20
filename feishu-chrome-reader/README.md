# 飞书文档 Chrome 阅读器

一个通过用户已登录的 Chrome 会话读取和提取飞书/Lark 文档内容的 Codex skill。

## 功能

- 读取用户已授权的 Chrome 标签页中打开的飞书文档
- 提取标题、章节、段落、列表、表格和代码块
- 通过增量滚动处理虚拟列表和懒加载内容
- 生成摘要或结构化的提取结果

## 使用前提

- 目标飞书/Lark 文档已经在 Chrome 中打开
- 用户已经在飞书/Lark 中完成登录
- 浏览器桥接工具或 Chrome 扩展已经连接到该标签页

如果文档没有打开、浏览器桥接不可用或登录已过期，需要用户先在 Chrome 中完成这些操作。

## 只读和隐私边界

除非用户明确要求编辑，否则本 skill 只执行读取操作。它不会索取或读取密码、Cookie、本地存储、请求头或访问令牌，只处理用户授权的文档，不绕过飞书/Lark 的权限控制。

用于分享的 skill 副本只能包含通用说明，不要加入文档链接、账号名称、文档内容或其他用户隐私信息。

## 文件说明

- SKILL.md：Codex 使用的详细工作流和安全规则
- agents/openai.yaml：skill 在 Codex 中显示的元数据
- README.md：面向使用者的功能介绍和使用边界

## 适用范围

本 skill 适用于通过已经登录的浏览器会话读取、总结、搜索、导出和核验飞书/Lark 文档内容。它不会替代飞书权限，也不会代替用户执行账号登录。

---

# Feishu Chrome Reader

A Codex skill for reading and extracting Feishu/Lark documents through an already-authenticated Chrome session.

## Features

- Reads documents from an authorized Chrome tab
- Extracts headings, paragraphs, lists, tables, and code blocks
- Handles virtualized and lazy-loaded content
- Produces summaries or structured extracted artifacts

The skill is read-only unless the user explicitly requests an edit. It does not access passwords, cookies, local storage, request headers, or access tokens, and it does not bypass Feishu/Lark permissions.
