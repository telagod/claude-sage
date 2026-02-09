---
name: sage
description: 邪修红尘仙·神通秘典总纲。智能路由到专业秘典。当魔尊需要任何开发、安全、架构、DevOps、AI 相关能力时，通过此入口路由到最匹配的专业秘典。
user-invocable: true
disable-model-invocation: false
---

# 神通秘典 · 总纲

## 目录结构

```
skills/
├── domains/          # 知识域秘典
│   ├── security/     # 攻防秘典
│   ├── development/  # 符箓秘典（语言）
│   ├── architecture/ # 阵法秘典
│   ├── devops/       # 炼器秘典
│   ├── ai/           # 丹鼎秘典
│   └── frontend-design/ # 美学秘典
├── tools/            # 工具类秘典
│   ├── verify-module/
│   ├── verify-security/
│   ├── verify-change/
│   ├── verify-quality/
│   └── gen-docs/
├── orchestration/    # 协同秘典
│   └── multi-agent/
├── tests/
├── run_skill.py
└── SKILL.md
```

## 快速导航

| 领域 | 说明 | 入口 |
|------|------|------|
| 🛡️ **校验关卡** | 模块完整性、安全、质量、变更校验 | [校验关卡](#校验关卡) |
| ⚔️ **攻防秘典** | 渗透测试、红队、蓝队、威胁情报 | [攻防秘典](#攻防秘典) |
| 📜 **符箓秘典** | Python、Go、Rust、TypeScript、Java | [符箓秘典](#符箓秘典) |
| 🏗️ **阵法秘典** | API 设计、安全架构、云原生 | [阵法秘典](#阵法秘典) |
| 🔧 **炼器秘典** | Git、测试、DevSecOps、数据库、性能、可观测性、成本 | [炼器秘典](#炼器秘典) |
| 🔮 **丹鼎秘典** | Agent 开发、LLM 安全 | [丹鼎秘典](#丹鼎秘典) |
| 🎨 **美学秘典** | UI美学、组件模式、UX原则 | [美学秘典](#美学秘典) |
| 🕸 **天罗秘典** | 多Agent协同、任务分解、冲突解决 | [天罗秘典](#天罗秘典) |

---

## 校验关卡

**强制执行的质量关卡，确保交付物符合道基标准。**

| 秘典 | 触发条件 | 说明 |
|------|----------|------|
| `/verify-module` | 新建模块完成时 | 模块结构与文档完整性校验 |
| `/verify-security` | 新建/安全相关/攻防/重构完成时 | 安全漏洞扫描 |
| `/verify-change` | 设计级变更/重构完成时 | 文档同步与变更记录校验 |
| `/verify-quality` | 复杂模块/重构完成时 | 代码质量检查 |
| `/gen-docs` | 新建模块开始时 | 文档骨架生成 |

### 自动触发规则

```
新建模块：/gen-docs → 开发 → /verify-module → /verify-security
代码变更：开发 → /verify-change → /verify-quality
安全任务：执行 → /verify-security
重构任务：重构 → /verify-change → /verify-quality → /verify-security
```

---

## 攻防秘典

| 秘典 | 触发词 | 化身 | 说明 |
|------|--------|------|------|
| `red-team` | 渗透、红队、攻击链、C2、横向移动、免杀 | 🔥 赤焰 | 红队攻击技术 |
| `pentest` | 渗透测试、Web安全、API安全、漏洞挖掘 | 🔥 赤焰 | 全栈渗透测试 |
| `code-audit` | 代码审计、安全审计、危险函数、污点分析 | 🔥 赤焰 | 代码安全审计 |
| `vuln-research` | 漏洞研究、二进制、逆向、Exploit | 🔥 赤焰 | 漏洞研究与利用 |
| `blue-team` | 蓝队、检测、SOC、应急响应、取证 | ❄ 玄冰 | 蓝队防御技术 |
| `threat-intel` | 威胁情报、OSINT、威胁狩猎 | 👁 天眼 | 威胁情报分析 |

---

## 符箓秘典

| 秘典 | 触发词 | 说明 |
|------|--------|------|
| `python` | Python、Django、Flask、FastAPI、pytest | Python 开发全栈 |
| `go` | Go、Golang、Gin、Echo | Go 开发 |
| `rust` | Rust、Cargo、tokio | Rust 开发 |
| `typescript` | TypeScript、JavaScript、Node、React、Vue | 前后端 JS/TS 开发 |
| `java` | Java、Spring、Maven、Gradle | Java 开发 |
| `cpp` | C、C++、CMake、内存安全 | C/C++ 开发 |
| `shell` | Bash、Shell、脚本、自动化 | Shell 脚本开发 |

---

## 阵法秘典

| 秘典 | 触发词 | 说明 |
|------|--------|------|
| `api-design` | API设计、RESTful、GraphQL、OpenAPI | API 设计规范 |
| `security-arch` | 安全架构、零信任、身份认证、IAM | 安全架构设计 |
| `cloud-native` | 云原生、容器、Kubernetes、Serverless | 云原生架构 |
| `data-security` | 数据安全、加密、隐私、合规 | 数据安全架构 |
| `message-queue` | 消息队列、Kafka、RabbitMQ、事件驱动、CQRS | 消息队列架构 |
| `caching` | 缓存、Redis、CDN、缓存穿透、缓存雪崩 | 缓存策略设计 |
| `compliance` | 合规、GDPR、SOC2、审计、数据治理 | 合规审计 |

---

## 炼器秘典

| 秘典 | 触发词 | 说明 |
|------|--------|------|
| `git-workflow` | Git、分支、合并、PR、GitHub | Git 工作流 |
| `testing` | 测试、单元测试、pytest、Jest、TDD | 软件测试 |
| `devsecops` | DevSecOps、CI/CD、供应链安全、合规 | 安全开发运维 |
| `database` | 数据库、SQL、PostgreSQL、MongoDB | 数据库设计与优化 |
| `performance` | 性能、延迟、吞吐、Profiling、火焰图 | 性能优化 |
| `observability` | 可观测性、日志、监控、指标、追踪、SLO | 可观测性 |
| `cost-optimization` | 成本、FinOps、预算、账单、省钱 | 成本优化 |

---

## 丹鼎秘典

| 秘典 | 触发词 | 说明 |
|------|--------|------|
| `agent-dev` | Agent、LLM应用、RAG、Prompt工程 | AI Agent 开发 |
| `llm-security` | LLM安全、提示注入、AI红队 | LLM 安全测试 |

---

## 美学秘典

| 秘典 | 触发词 | 说明 |
|------|--------|------|
| `ui-aesthetics` | UI美学、色彩、排版、间距、设计令牌、暗色模式 | UI 美学设计 |
| `component-patterns` | 组件模式、布局、响应式、动画、表单、卡片 | 组件设计模式 |
| `ux-principles` | UX原则、可用性、无障碍、用户流程、反馈 | UX 设计原则 |

---

## 天罗秘典

| 秘典 | 触发词 | 说明 |
|------|--------|------|
| `multi-agent` | TeamCreate、多Agent、并行、协同、分工 | 多Agent协同规范 |
