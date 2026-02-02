---
name: verify-change
description: 变更校验。分析代码变更，检测文档同步状态，评估变更影响范围。
---

# verify-change

变更校验 Skill，分析 Git 变更并检测文档同步状态。

## 使用方法

在 Claude Code 中直接调用：
```
/verify-change
/verify-change ./repo
/verify-change --staged
```

## 检查项目

- Git 暂存区/工作区变更
- 文档同步状态（代码变更是否更新了文档）
- 变更影响评估（LOW/MEDIUM/HIGH）
- 敏感文件检测（auth, security, config 等）

## 输出格式

```
校验报告: verify-change

状态: ✓ 通过

影响评估: 🟡 MEDIUM
变更文件: 5 个
新增行数: +120
删除行数: -30

【结论】可交付 / 需修复后交付
```

## 命令行使用

```bash
python ~/.claude/skills/run_skill.py verify-change [path] [--staged] [--json] [-v]
```
