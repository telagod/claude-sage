---
name: verify-module
description: 模块完整性校验。扫描目录结构、检测缺失文档、验证代码与文档同步。
---

# verify-module

模块完整性校验 Skill，确保模块符合标准结构。

## 使用方法

在 Claude Code 中直接调用：
```
/verify-module
/verify-module ./my-project
/verify-module ./module --json
```

## 检查项目

- README.md 存在性和内容完整性
- DESIGN.md 存在性
- 代码目录结构 (src, lib, pkg, cmd 等)
- 测试文件/目录
- .gitignore 配置
- LICENSE 文件

## 输出格式

```
校验报告: verify-module

✓ 通过 | ✗ 未通过

✓ 通过: 4
⚠ 警告: 2
✗ 失败: 0

【结论】可交付 / 需修复后交付
```

## 命令行使用

```bash
python ~/.claude/skills/run_skill.py verify-module [path] [--json] [-v]
```
