---
name: verify-security
description: 安全校验。自动扫描代码安全漏洞，检测危险模式，确保安全决策有文档记录。
---

# verify-security

安全校验 Skill，扫描代码中的安全漏洞和危险模式。

## 使用方法

在 Claude Code 中直接调用：
```
/verify-security
/verify-security ./src
/verify-security ./project --json
```

## 检测项目

- 代码注入 (eval, exec)
- 命令注入 (os.system, subprocess shell=True)
- 反序列化漏洞 (pickle, yaml.load)
- 硬编码凭证 (password, secret, api_key)
- 弱加密算法 (MD5, SHA1)
- SSL/TLS 配置问题
- CORS 配置问题
- XSS 风险
- SQL 注入风险

## 输出格式

```
校验报告: verify-security

✓ 通过 | ✗ 未通过

- 🔴 Critical: 0
- 🟠 High: 0
- 🟡 Medium: 2
- 🔵 Low: 5

【结论】可交付 / 需修复后交付
```

## 命令行使用

```bash
python ~/.claude/skills/run_skill.py verify-security [path] [--json] [-v]
```
