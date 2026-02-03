---
name: development
description: 开发语言能力索引。Python、Go、Rust、TypeScript、Java、C++、Shell。当用户提到编程、开发、代码、语言时路由到此。
---

# 💻 开发语言能力中枢

> 多语言精通，最佳实践

## 能力矩阵

| Skill | 语言 | 核心能力 |
|-------|------|----------|
| [python](python.md) | Python | Web框架、数据处理、自动化 |
| [go](go.md) | Go | 高并发、微服务、云原生 |
| [rust](rust.md) | Rust | 系统编程、内存安全、高性能 |
| [typescript](typescript.md) | TS/JS | 前后端、Node.js、React/Vue |
| [java](java.md) | Java | 企业级、Spring、微服务 |
| [cpp](cpp.md) | C/C++ | 系统底层、性能优化 |
| [shell](shell.md) | Bash | 脚本自动化、系统管理 |

## 语言选型指南

```yaml
Web 后端:
  - 快速开发: Python (FastAPI/Django)
  - 高性能: Go (Gin/Echo)
  - 企业级: Java (Spring Boot)

Web 前端:
  - SPA: TypeScript + React/Vue
  - SSR: Next.js/Nuxt.js

系统编程:
  - 内存安全: Rust
  - 传统: C/C++

脚本自动化:
  - 通用: Python
  - 系统: Bash/Shell

微服务:
  - 云原生: Go
  - 企业: Java (Spring Cloud)

安全工具:
  - 快速原型: Python
  - 高性能: Go/Rust
```

## 通用最佳实践

### 代码规范
```yaml
命名:
  - 类名: PascalCase
  - 函数/方法: snake_case 或 camelCase
  - 常量: UPPER_SNAKE_CASE
  - 变量: snake_case 或 camelCase

结构:
  - 单一职责原则
  - 函数不超过 50 行
  - 文件不超过 500 行
  - 嵌套不超过 3 层
```

### 错误处理
```yaml
原则:
  - 显式处理错误，不忽略
  - 提供有意义的错误信息
  - 在边界处验证输入
  - 使用类型系统防止错误
```

### 测试
```yaml
测试金字塔:
  - 单元测试: 70%
  - 集成测试: 20%
  - E2E测试: 10%

原则:
  - 测试行为，不测试实现
  - 每个测试只验证一件事
  - 测试边界条件
```

---

**选择合适的语言，写出优雅的代码。**
