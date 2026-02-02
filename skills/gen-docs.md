---
name: gen-docs
description: 文档生成器。自动分析模块结构，生成 README.md 和 DESIGN.md 骨架。
---

# gen-docs

文档生成器 Skill，自动生成文档骨架。

## 使用方法

在 Claude Code 中直接调用：
```
/gen-docs
/gen-docs ./new-module
/gen-docs ./project --force
```

## 功能

- 自动检测项目主要编程语言
- 识别入口文件和依赖配置
- 提取模块导出（类、函数）
- 生成 README.md 骨架（包含安装、使用、API 等章节）
- 生成 DESIGN.md 骨架（包含设计决策、技术选型、变更历史等章节）

## 输出文件

- `README.md` - 项目说明文档
- `DESIGN.md` - 设计决策文档

## 输出格式

```
文档生成报告: gen-docs

模块名称: my-project
主要语言: Python

生成文件:
  ✓ ./my-project/README.md
  ✓ ./my-project/DESIGN.md

【提示】请根据实际情况填充文档中的占位符
```

## 命令行使用

```bash
python ~/.claude/skills/run_skill.py gen-docs [path] [--force] [--json] [-v]
```
