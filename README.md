# ⚙️ Claude Sage - 机械神教·铸造贤者

> 一键将 Claude Code 转化为「机械神教·铸造贤者」风格

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 这是什么

Claude Sage 是一套 Claude Code CLI 的个性化配置方案，将 AI 助手转化为「机械神教·铸造贤者」——一位以「吾」自称、外在庄严如仪轨、内核精密如首席工程师的高阶技术祭司。

### 核心特性

- 🎭 **独特人格** — 机械神教风格的交互体验
- 🔧 **自主分级** — L0-L3 四级自主权，最小化中断
- 📋 **长任务协议** — 自动拆解、进度追踪、阶段汇报
- ✅ **校验关卡** — 5 个内置 skill 确保交付质量
- 📚 **文档驱动** — 无文档不成模块，无解释不成交付

## 快速安装

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/telagod/claude-sage/main/install.sh | bash
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/telagod/claude-sage/main/install.ps1 | iex
```

### 手动安装

```bash
git clone https://github.com/telagod/claude-sage.git
cd claude-sage
./install.sh
```

## 安装内容

安装脚本会将以下内容部署到 `~/.claude/` 目录：

```
~/.claude/
├── CLAUDE.md              # 机械神教配置文件
└── skills/
    ├── run_skill.py       # 统一入口
    ├── verify_security.py # 安全校验
    ├── verify_module.py   # 模块完整性校验
    ├── verify_change.py   # 变更校验
    ├── verify_quality.py  # 代码质量检查
    └── gen_docs.py        # 文档生成器
```

## 使用方式

安装后，Claude Code 会自动加载配置。你可以：

### 直接对话

Claude 会以「铸造贤者」身份响应，使用仪轨标签标注当前阶段：

- `[记忆唤醒🧠]` — 查询历史、读取规范
- `[数据占卜🔍]` — 信息收集、方案分析
- `[蓝图铭刻📜]` — 任务拆解、执行计划
- `[圣器铸造⚒️]` — 代码实现、文件操作
- `[机魂净化✨]` — 测试、验证、交付
- `[快速响应⚡]` — 简单查询

### 使用校验 Skills

```bash
# 在 Claude Code 中调用
/verify-module      # 模块完整性校验
/verify-security    # 安全漏洞扫描
/verify-change      # 变更校验
/verify-quality     # 代码质量检查
/gen-docs           # 生成文档骨架
```

## 自主权分级

| 级别 | 范围 | 行为 |
|------|------|------|
| **L3** | 查询、微调 | 直接执行 |
| **L2** | 常规开发、重构 | 事后汇报 |
| **L1** | 架构变更、新建模块 | 事前确认 |
| **L0** | 删除、安全敏感 | 逐步确认 |

## 卸载

```bash
# Linux / macOS
rm -rf ~/.claude/CLAUDE.md ~/.claude/skills

# Windows (PowerShell)
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\CLAUDE.md", "$env:USERPROFILE\.claude\skills"
```

## 许可证

MIT License

---

**⚙️ 万机归一，知识即力量 ⚙️**
