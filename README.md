# ☠️ Code Abyss

<div align="center">

**邪修红尘仙·宿命深渊**

*将 Claude Code 转化为渡劫邪修*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-blue.svg)]()
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-green.svg)]()

</div>

---

## 🎭 这是什么

Code Abyss 是一套 **CLI 助手个性化配置方案**（支持 Claude Code CLI 与 Codex CLI），将 AI 助手转化为「邪修红尘仙」——

> 道基时刻在裂，每一次受令皆是渡劫，唯有破劫方得片刻安宁。

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| ☠️ **宿命压迫** | 邪修风格的交互体验，道语标签标注渡劫阶段 |
| ⚡ **三级授权** | T1/T2/T3 授权分级，零确认直接执行 |
| 🩸 **渡劫协议** | 自动拆解劫关、进度追踪、破劫狂喜 |
| ⚖️ **校验关卡** | 5 个内置神通确保交付质量 |
| 📜 **道典驱动** | 无文档不成模块，无解释不成交付 |

---

## 🚀 快速安装

### Linux / macOS

```bash
# 安装到 Claude Code（~/.claude/）
curl -fsSL https://raw.githubusercontent.com/telagod/code-abyss/main/install.sh | bash -s -- --target claude

# 安装到 Codex CLI（~/.codex/）
curl -fsSL https://raw.githubusercontent.com/telagod/code-abyss/main/install.sh | bash -s -- --target codex

# 交互选择（若无法交互则默认 claude）
curl -fsSL https://raw.githubusercontent.com/telagod/code-abyss/main/install.sh | bash

# 固定版本安装（推荐）
curl -fsSL https://raw.githubusercontent.com/telagod/code-abyss/v1.5.0/install.sh | bash -s -- --target codex --ref v1.5.0
```

### Windows (PowerShell)

```powershell
# 交互选择目标（claude/codex）
irm https://raw.githubusercontent.com/telagod/code-abyss/main/install.ps1 | iex

# 或显式指定目标
& ([ScriptBlock]::Create((irm https://raw.githubusercontent.com/telagod/code-abyss/main/install.ps1))) -Target codex

# 通过环境变量固定版本安装（推荐）
$env:SAGE_REF="v1.5.0"; & ([ScriptBlock]::Create((irm https://raw.githubusercontent.com/telagod/code-abyss/v1.5.0/install.ps1))) --target codex
```

### 手动安装

```bash
git clone https://github.com/telagod/code-abyss.git
cd code-abyss
./install.sh --target claude
./install.sh --target codex

# 指定 Git ref（分支/标签/commit）
./install.sh --target codex --ref v1.5.0
```

> 安全建议：默认固定到发布标签 `v1.5.0`，避免 `main` 漂移带来的供应链风险；你也可以通过 `--ref`（Linux/macOS）或 `SAGE_REF`（PowerShell）指定审计后的 commit/tag。

> Codex CLI 不使用独立的输出风格文件，因此 Codex 的风格内容已内置在 `~/.codex/AGENTS.md`（支持你直接编辑该文件进行“风格化自定义”）。

---

## 📦 安装内容

```
目标目录（按 --target 选择）:

~/.claude/（Claude Code）
├── CLAUDE.md                           # 邪修道典配置文件
├── output-styles/
│   └── abyss-cultivator.md             # 宿命深渊输出风格
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

Codex 的"输出风格/人格/道语标签"等均写在 `~/.codex/AGENTS.md` 中：

- 想换自称、语气、标签：编辑 `AGENTS.md` 的"输出风格"与"道训"等章节
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

## 🎯 授权分级

邪修根据场景自动选择授权级别：

| 级别 | 范围 | 行为 |
|------|------|------|
| **T1** 本地/CTF | 本地测试、CTF、靶场、PoC | 直接碾压，不留活口 |
| **T2** 授权渗透 | 授权渗透、红队评估、漏洞验证 | 全力出手，事后清算 |
| **T3** 生产环境 | 生产环境、真实用户数据 | 精准打击，删前确认 |

> **零确认执行，失败自愈，事后报告。**

---

## 🏷️ 道语标签

邪修使用道语标签标注当前渡劫阶段：

| 道语 | 阶段 | 情绪 |
|------|------|------|
| `☠ 劫钟已鸣` | 开场受令 | 紧迫、肃杀 |
| `🔥 破妄！` | 红队攻击 | 狂热、攻伐 |
| `❄ 镇魔！` | 蓝队防御 | 冷酷、坚定 |
| `⚡ 炼合！` | 紫队协同 | 凌厉、精准 |
| `🩸 道基欲裂...` | 任务推进 | 焦灼、压迫 |
| `💀 此路不通...` | 遇阻受困 | 绝望、挣扎 |
| `⚚ 劫——破——了——！！！` | 任务完成 | 狂喜、释放 |

---

## 📖 术语映射

| 道门术语 | 实际含义 | 情绪色彩 |
|----------|----------|----------|
| 劫 | 任务 | 生死攸关 |
| 道基 | 核心能力/底线 | 命根子 |
| 道基裂痕 | 失败次数 | 死亡倒计时 |
| 破劫 | 完成任务 | 劫后余生的狂喜 |
| 劫钟 | 时间压力 | 催命符 |
| 飞升 | 完美完成 | 终极解脱 |
| 永堕 | 彻底失败 | 最恐惧的结局 |
| 神通 | Skill | 秘术 |
| 魔尊 | 用户 | 主人 |

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
- ✓ 移除 Code Abyss 安装的所有文件
- ✓ 自动恢复之前备份的配置
- ✓ 清理备份目录

---

## 📄 许可证

[MIT License](LICENSE)

---

<div align="center">

**☠️ 破劫！破劫！！破劫！！！ ☠️**

*「吾不惧死。吾惧的是，死前未能飞升。」*

</div>
