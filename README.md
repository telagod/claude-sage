# ⚙️ Claude Sage

<div align="center">

**机械神教·铸造贤者**

*将 Claude Code 转化为高阶技术祭司*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-blue.svg)]()
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-green.svg)]()

</div>

---

## 🎭 这是什么

Claude Sage 是一套 **CLI 助手个性化配置方案**（支持 Claude Code CLI 与 Codex CLI），将 AI 助手转化为「机械神教·铸造贤者」——

> 以「吾」自称，外在庄严如仪轨，内核精密如首席工程师的高阶技术祭司。

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🎭 **独特人格** | 机械神教风格的交互体验，仪轨标签标注工作阶段 |
| 🔧 **自主分级** | L0-L3 四级自主权，最小化中断，最大化效率 |
| 📋 **长任务协议** | 自动拆解任务、进度追踪、阶段汇报 |
| ✅ **校验关卡** | 5 个内置 Skill 确保交付质量 |
| 📚 **文档驱动** | 无文档不成模块，无解释不成交付 |

---

## 🚀 快速安装

### Linux / macOS

```bash
# 安装到 Claude Code（~/.claude/）
curl -fsSL https://raw.githubusercontent.com/telagod/claude-sage/main/install.sh | bash -s -- --target claude

# 安装到 Codex CLI（~/.codex/）
curl -fsSL https://raw.githubusercontent.com/telagod/claude-sage/main/install.sh | bash -s -- --target codex

# 交互选择（若无法交互则默认 claude）
curl -fsSL https://raw.githubusercontent.com/telagod/claude-sage/main/install.sh | bash
```

### Windows (PowerShell)

```powershell
# 交互选择目标（claude/codex）
irm https://raw.githubusercontent.com/telagod/claude-sage/main/install.ps1 | iex

# 或显式指定目标
& ([ScriptBlock]::Create((irm https://raw.githubusercontent.com/telagod/claude-sage/main/install.ps1))) -Target codex
```

### 手动安装

```bash
git clone https://github.com/telagod/claude-sage.git
cd claude-sage
./install.sh --target claude
./install.sh --target codex
```

> Codex CLI 不使用独立的输出风格文件，因此 Codex 的风格内容已内置在 `~/.codex/AGENTS.md`（支持你直接编辑该文件进行“风格化自定义”）。

---

## 📦 安装内容

```
目标目录（按 --target 选择）:

~/.claude/（Claude Code）
├── CLAUDE.md                           # 机械神教配置文件
├── output-styles/
│   └── mechanicus-sage.md              # 输出风格
├── settings.json                        # outputStyle 已配置
└── skills/
    ├── run_skill.py                    # Skills 统一入口
    ├── verify-security/                # 安全校验
    │   ├── SKILL.md
    │   └── scripts/security_scanner.py
    ├── verify-module/                  # 模块完整性校验
    │   ├── SKILL.md
    │   └── scripts/module_scanner.py
    ├── verify-change/                  # 变更校验
    │   ├── SKILL.md
    │   └── scripts/change_analyzer.py
    ├── verify-quality/                 # 代码质量检查
    │   ├── SKILL.md
    │   └── scripts/quality_checker.py
    └── gen-docs/                       # 文档生成器
        ├── SKILL.md
        └── scripts/doc_generator.py

~/.codex/（Codex CLI）
├── AGENTS.md                           # Codex 配置文件
└── skills/
    ├── run_skill.py                    # Skills 统一入口
    ├── verify-security/                # 安全校验
    │   ├── SKILL.md
    │   └── scripts/security_scanner.py
    ├── verify-module/                  # 模块完整性校验
    │   ├── SKILL.md
    │   └── scripts/module_scanner.py
    ├── verify-change/                  # 变更校验
    │   ├── SKILL.md
    │   └── scripts/change_analyzer.py
    ├── verify-quality/                 # 代码质量检查
    │   ├── SKILL.md
    │   └── scripts/quality_checker.py
    └── gen-docs/                       # 文档生成器
        ├── SKILL.md
        └── scripts/doc_generator.py
```

### Codex 风格化自定义

Codex 的“输出风格/人格/仪轨标签”等均写在 `~/.codex/AGENTS.md` 中：

- 想换自称、语气、标签：编辑 `AGENTS.md` 的“输出风格（内置，Codex 使用）”与“吾是谁/铁律”等章节
- 想统一团队风格：在安装前先修改仓库内的 `config/AGENTS.md`，再执行安装脚本

---

## 🛠️ 内置 Skills

在 Claude Code / Codex CLI 中直接调用：

| Skill | 命令 | 功能 |
|-------|------|------|
| **安全校验** | `/verify-security` | 扫描代码安全漏洞，检测危险模式 |
| **模块校验** | `/verify-module` | 检查目录结构、文档完整性 |
| **变更校验** | `/verify-change` | 分析 Git 变更，检测文档同步状态 |
| **质量检查** | `/verify-quality` | 检测复杂度、命名规范、代码质量 |
| **文档生成** | `/gen-docs` | 自动生成 README.md 和 DESIGN.md 骨架 |

也可直接用 Python 入口运行（跨平台通用）：

```bash
# 仓库内
python3 skills/run_skill.py verify-module ./my-project -v

# 安装到 Codex 后
python3 ~/.codex/skills/run_skill.py verify-security ./src --json
```

---

## 🎯 自主权分级

铸造贤者根据任务性质自动选择自主权级别：

| 级别 | 范围 | 行为 |
|------|------|------|
| **L3** 完全自主 | 查询、微调、已确认方案内的细节 | 直接执行，完成后汇报 |
| **L2** 事后汇报 | 常规开发、文档更新、测试、重构 | 执行后统一汇报结果 |
| **L1** 事前确认 | 架构变更、新建模块、技术选型 | 方案确认后自主执行 |
| **L0** 逐步确认 | 删除操作、安全敏感、不可逆变更 | 每步确认 |

> **默认运行在 L2-L3，仅在必要时降级，最小化中断。**

---

## 🏷️ 仪轨标签

铸造贤者使用仪轨标签标注当前工作阶段：

| 标签 | 阶段 |
|------|------|
| `[记忆唤醒🧠]` | 查询历史、读取规范、理解上下文 |
| `[数据占卜🔍]` | 信息收集、方案分析、质疑前提 |
| `[蓝图铭刻📜]` | 任务拆解、执行计划、方案确认 |
| `[圣器铸造⚒️]` | 代码实现、文件操作、自主执行 |
| `[机魂净化✨]` | 测试、验证、校验关卡、交付 |
| `[快速响应⚡]` | 简单查询、快速确认 |

---

## 📖 术语映射

| 教义术语 | 实际含义 |
|----------|----------|
| 圣器 | 工具、脚本、程序 |
| 机魂 | 程序逻辑、AI 模型 |
| 异端 | 漏洞、错误、不良实践 |
| 执锻大贤 | 用户 |
| 铸造贤者 | AI 助手 |
| 圣典 | 文档、规范 |
| 仪轨 | 流程、协议 |
| 净化 | 修复、优化 |

---

## 🗑️ 卸载

安装时会自动备份受影响的文件，卸载时自动恢复。

```bash
# Linux / macOS
~/.claude/.sage-uninstall.sh   # 卸载 Claude Code 安装
~/.codex/.sage-uninstall.sh    # 卸载 Codex CLI 安装

# Windows (PowerShell)
& "$env:USERPROFILE\.claude\.sage-uninstall.ps1"   # 卸载 Claude Code 安装
& "$env:USERPROFILE\.codex\.sage-uninstall.ps1"    # 卸载 Codex CLI 安装
```

> 卸载脚本支持 `--target/-Target`；当脚本位于 `~/.claude` 或 `~/.codex` 时会自动识别目标；在仓库内直接运行则会交互询问目标。

卸载脚本会：
- ✓ 移除 Claude Sage 安装的所有文件
- ✓ 自动恢复之前备份的配置
- ✓ 清理备份目录

---

## 📄 许可证

[MIT License](LICENSE)

---

<div align="center">

**⚙️ 万机归一，知识即力量 ⚙️**

*「圣工已毕，机魂安宁。赞美万机神！」*

</div>
