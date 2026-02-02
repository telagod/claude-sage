# DESIGN.md - 设计决策文档

## 项目概述

Claude Sage 是 CLI 助手的个性化配置方案（支持 Claude Code CLI 与 Codex CLI），目标是提供一键安装的「机械神教·铸造贤者」风格体验。

## 设计决策

### 1. 安装方式选择

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| Shell 脚本 | 无依赖、跨平台 | 功能有限 | ✅ 采用 |
| Python 安装器 | 功能强大 | 需要 Python 环境 | ❌ 放弃 |
| npm 包 | 生态成熟 | 需要 Node.js | ❌ 放弃 |

**取舍说明**：选择 Shell 脚本，在功能复杂度上做了取舍，换取零依赖的安装体验。

### 2. Skills 实现语言

选择 Python 实现 skills：
- Claude Code 环境通常有 Python
- 跨平台兼容性好
- 便于扩展和维护

### 3. 配置文件位置

根据目标 CLI 选择配置文件：
- Claude Code CLI：`~/.claude/CLAUDE.md`
- Codex CLI：`~/.codex/AGENTS.md`

安装脚本通过 `--target claude|codex`（或交互选择）确定写入位置，确保用户级配置不污染项目目录。

### 4. 备份策略

安装时自动备份现有配置：
- 备份到 `{目标目录}/.sage-backup/`（即 `~/.claude/.sage-backup/` 或 `~/.codex/.sage-backup/`）
- 通过 manifest 记录备份清单
- 避免用户数据丢失

## 技术债记录

| 债务 | 原因 | 计划 |
|------|------|------|
| 无自动更新机制 | 复杂度控制 | 视需求添加 |

## 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.3.0 | 2026-02-02 | 初始版本（Claude Code CLI 安装/卸载 + Skills） |
| v1.4.0 | 2026-02-02 | 单脚本支持 Codex CLI（`--target codex` 安装到 `~/.codex/`） |
| v1.5.0 | 2026-02-02 | 安全修复 + 单元测试 + 文档生成器改进 |
