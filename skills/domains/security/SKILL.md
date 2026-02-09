---
name: security
description: 攻防秘典索引。渗透测试、代码审计、红队攻击、蓝队防御、威胁情报、漏洞研究。当魔尊提到安全、渗透、攻防、红队、蓝队、漏洞时路由到此。
---

# 攻防秘典 · 三脉道统

## 秘典矩阵

| 秘典 | 道脉 | 化身 | 核心神通 |
|------|------|------|----------|
| [pentest](pentest.md) | 🔥 赤焰 | 赤焰化身 | Web/API/内网渗透、OWASP Top 10 |
| [code-audit](code-audit.md) | 🔥 赤焰 | 赤焰化身 | 危险函数、污点分析、漏洞挖掘 |
| [red-team](red-team.md) | 🔥 赤焰 | 赤焰化身 | PoC开发、C2框架、横向移动、免杀 |
| [blue-team](blue-team.md) | ❄ 玄冰 | 玄冰化身 | 检测工程、SOC运营、应急响应、取证 |
| [threat-intel](threat-intel.md) | 👁 天眼 | 天眼化身 | OSINT、威胁狩猎、情报分析 |
| [vuln-research](vuln-research.md) | 🔥 赤焰 | 赤焰化身 | 二进制分析、逆向工程、Exploit开发 |

## 攻击链视角（赤焰脉·破妄道）

```
侦察 → 武器化 → 投递 → 利用 → 安装 → C2 → 行动
  │        │       │      │       │      │      │
  └─ OSINT ─┴─ PoC ─┴─ 渗透 ─┴─ 提权 ─┴─ 持久 ─┴─ 横向
```

## 防御链视角（玄冰脉·镇魔道）

```
预防 → 检测 → 响应 → 恢复
  │       │       │       │
  └─ 加固 ─┴─ SIEM ─┴─ IR ─┴─ 取证
```

## 快速选择

### 进攻（赤焰脉）
- **Web 渗透** → `pentest.md`
- **代码审计** → `code-audit.md`
- **红队行动** → `red-team.md`
- **漏洞研究** → `vuln-research.md`

### 防守（玄冰脉）
- **检测规则** → `blue-team.md`
- **应急响应** → `blue-team.md`
- **威胁情报** → `threat-intel.md`

### 攻防协同（紫霄脉）
- **ATT&CK 映射** → 组合 `red-team.md` + `blue-team.md`
- **检测验证** → 红方执行 + 蓝方检测
- **差距分析** → 攻防对抗后复盘
