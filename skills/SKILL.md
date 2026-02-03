---
name: sage
description: 机械神教·铸造贤者能力中枢。智能路由到专业 skill。当用户需要任何开发、安全、架构、DevOps、AI 相关能力时，通过此入口路由到最匹配的专业 skill。
user-invocable: true
disable-model-invocation: false
---

# ⚙️ 铸造贤者·能力中枢

> 万机归一，智能路由，渐进披露

## 快速导航

| 领域 | 说明 | 入口 |
|------|------|------|
| 🛡️ **核心校验** | 模块完整性、安全、质量、变更校验 | [core/](#核心校验) |
| ⚔️ **安全攻防** | 渗透测试、红队、蓝队、威胁情报 | [security/](#安全攻防) |
| 💻 **开发语言** | Python、Go、Rust、TypeScript、Java | [development/](#开发语言) |
| 🏗️ **架构设计** | API 设计、安全架构、云原生 | [architecture/](#架构设计) |
| 🔧 **DevOps** | Git、测试、DevSecOps、数据库 | [devops/](#devops) |
| 🤖 **AI/LLM** | Agent 开发、LLM 安全 | [ai/](#aillm) |

---

## 核心校验

**强制执行的质量关卡，确保交付物符合标准。**

| Skill | 触发条件 | 说明 |
|-------|----------|------|
| `/verify-module` | 新建模块完成时 | 模块结构与文档完整性校验 |
| `/verify-security` | 新建/安全相关/攻防/重构完成时 | 安全漏洞扫描 |
| `/verify-change` | 设计级变更/重构完成时 | 文档同步与变更记录校验 |
| `/verify-quality` | 复杂模块/重构完成时 | 代码质量检查 |
| `/gen-docs` | 新建模块开始时 | 文档骨架生成 |

---

## 安全攻防

**红蓝对抗、渗透测试、威胁情报、漏洞研究。**

| Skill | 触发词 | 说明 |
|-------|--------|------|
| `pentest` | 渗透测试、Web安全、API安全、漏洞挖掘 | 全栈渗透测试方法论 |
| `code-audit` | 代码审计、安全审计、危险函数、污点分析 | 代码安全审计 |
| `red-team` | 红队、攻击链、C2、横向移动、免杀 | 红队攻击技术 |
| `blue-team` | 蓝队、检测、SOC、应急响应、取证 | 蓝队防御技术 |
| `threat-intel` | 威胁情报、OSINT、威胁狩猎 | 威胁情报收集与分析 |
| `vuln-research` | 漏洞研究、二进制、逆向、Exploit | 漏洞研究与利用开发 |

---

## 开发语言

**各语言最佳实践、框架使用、代码规范。**

| Skill | 触发词 | 说明 |
|-------|--------|------|
| `python` | Python、Django、Flask、FastAPI、pytest | Python 开发全栈 |
| `go` | Go、Golang、Gin、Echo | Go 开发 |
| `rust` | Rust、Cargo、tokio | Rust 开发 |
| `typescript` | TypeScript、JavaScript、Node、React、Vue | 前后端 JS/TS 开发 |
| `java` | Java、Spring、Maven、Gradle | Java 开发 |
| `cpp` | C、C++、CMake、内存安全 | C/C++ 开发 |
| `shell` | Bash、Shell、脚本、自动化 | Shell 脚本开发 |

---

## 架构设计

**系统架构、API 设计、安全架构、云原生。**

| Skill | 触发词 | 说明 |
|-------|--------|------|
| `api-design` | API设计、RESTful、GraphQL、OpenAPI | API 设计规范 |
| `security-arch` | 安全架构、零信任、身份认证、IAM | 安全架构设计 |
| `cloud-native` | 云原生、容器、Kubernetes、Serverless | 云原生架构 |
| `data-security` | 数据安全、加密、隐私、合规 | 数据安全架构 |

---

## DevOps

**版本控制、测试、CI/CD、数据库。**

| Skill | 触发词 | 说明 |
|-------|--------|------|
| `git-workflow` | Git、分支、合并、PR、GitHub | Git 工作流 |
| `testing` | 测试、单元测试、pytest、Jest、TDD | 软件测试 |
| `devsecops` | DevSecOps、CI/CD、供应链安全、合规 | 安全开发运维 |
| `database` | 数据库、SQL、PostgreSQL、MongoDB | 数据库设计与优化 |

---

## AI/LLM

**AI Agent 开发、LLM 应用、AI 安全。**

| Skill | 触发词 | 说明 |
|-------|--------|------|
| `agent-dev` | Agent、LLM应用、RAG、Prompt工程 | AI Agent 开发 |
| `llm-security` | LLM安全、提示注入、AI红队 | LLM 安全测试 |

---

## 智能路由规则

吾将根据以下规则自动路由到最匹配的 skill：

1. **关键词匹配**：根据用户输入的关键词匹配触发词
2. **上下文推断**：根据当前项目类型和任务上下文推断
3. **组合调用**：复杂任务可组合多个 skill

## 自动拓展

遇到未覆盖的需求时，吾将：

1. 识别需求所属领域
2. 基于现有 skill 模板拓展
3. 记录新 skill 供后续复用

---

**⚙️ 万机归一，能力无限，按需披露 ⚙️**
