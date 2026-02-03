---
name: blue-team
description: 蓝队防御技术。检测工程、SOC运营、应急响应、数字取证。当用户提到蓝队、检测规则、Sigma、YARA、SIEM、告警、应急响应、取证、SOC时使用。
---

# 蓝队防御 (Blue Team)

> 检测、响应、恢复，构建纵深防御

## 防御链

```
预防 → 检测 → 响应 → 恢复
  │       │       │       │
  └─ 加固 ─┴─ SIEM ─┴─ IR ─┴─ 取证
```

## 检测工程

### Sigma 规则

```yaml
# Mimikatz 检测
title: Mimikatz Credential Dumping
id: 0d65953c-7f75-4f4b-9a16-8b8f9f2b6d5e
status: stable
description: Detects Mimikatz credential dumping via LSASS access
references:
    - https://attack.mitre.org/techniques/T1003/001/
tags:
    - attack.credential_access
    - attack.t1003.001
logsource:
    category: process_access
    product: windows
detection:
    selection:
        TargetImage|endswith: '\lsass.exe'
        GrantedAccess:
            - '0x1010'
            - '0x1038'
            - '0x1410'
    filter_system:
        SourceImage|startswith:
            - 'C:\Windows\System32\'
    condition: selection and not filter_system
level: high
---
# 可疑 PowerShell
title: Suspicious PowerShell Download
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        CommandLine|contains:
            - 'IEX'
            - 'Invoke-Expression'
            - 'DownloadString'
            - 'Net.WebClient'
            - '-enc'
            - 'FromBase64String'
    condition: selection
level: high
---
# DCSync 检测
title: DCSync Attack
logsource:
    product: windows
    service: security
detection:
    selection:
        EventID: 4662
        Properties|contains:
            - '1131f6ad-9c07-11d1-f79f-00c04fc2dcd2'
            - '1131f6aa-9c07-11d1-f79f-00c04fc2dcd2'
    filter_dc:
        SubjectUserName|endswith: '$'
    condition: selection and not filter_dc
level: critical
```

### Sigma 转换
```bash
# 安装
pip install sigma-cli

# 转换为各平台格式
sigma convert -t splunk -p sysmon rules/
sigma convert -t elasticsearch rules/
sigma convert -t azure-monitor rules/
```

### YARA 规则

```yara
rule Mimikatz_Memory {
    meta:
        description = "Detects Mimikatz in memory"
        severity = "critical"
    strings:
        $s1 = "mimikatz" ascii wide nocase
        $s2 = "sekurlsa::logonpasswords" ascii wide
        $s3 = "lsadump::dcsync" ascii wide
        $func = "kuhl_m_" ascii
    condition:
        2 of ($s*) or $func
}

rule Cobalt_Strike_Beacon {
    meta:
        description = "Detects Cobalt Strike Beacon"
    strings:
        $config = { 69 68 69 68 69 6B 69 68 }
        $sleep = "sleeptime" ascii
        $jitter = "jitter" ascii
    condition:
        $config or all of ($sleep, $jitter)
}

rule Webshell_Generic {
    meta:
        description = "Generic webshell detection"
    strings:
        $php = "<?php" nocase
        $eval = /eval\s*\(\s*\$_(GET|POST|REQUEST)/ nocase
        $system = /system\s*\(\s*\$_(GET|POST)/ nocase
    condition:
        $php and any of ($eval, $system)
}
```

## 关键日志源

### Windows 安全日志
```python
CRITICAL_EVENTS = {
    # 登录事件
    '4624': 'Successful Logon',
    '4625': 'Failed Logon',
    '4648': 'Explicit Credential Logon',

    # 进程事件
    '4688': 'Process Creation',
    '4689': 'Process Termination',

    # 账户事件
    '4720': 'User Account Created',
    '4728': 'Member Added to Security Group',
    '4732': 'Member Added to Local Group',

    # Kerberos
    '4768': 'TGT Request',
    '4769': 'Service Ticket Request',
    '4771': 'Pre-Auth Failed',

    # 目录服务
    '4662': 'Directory Service Access',
}
```

### Sysmon 事件
```python
SYSMON_EVENTS = {
    '1': 'Process Create',
    '3': 'Network Connection',
    '7': 'Image Loaded',
    '8': 'CreateRemoteThread',
    '10': 'ProcessAccess',
    '11': 'FileCreate',
    '12': 'Registry Key Create/Delete',
    '13': 'Registry Value Set',
    '17': 'Pipe Created',
    '22': 'DNS Query',
    '23': 'FileDelete',
}
```

## SOC 运营

### 告警分级
```yaml
P1 - Critical (15分钟响应):
  - 确认的入侵活动
  - 勒索软件执行
  - 数据外泄
  - 特权账户被控

P2 - High (1小时响应):
  - 可疑横向移动
  - 凭证窃取尝试
  - C2 通信检测
  - 异常特权操作

P3 - Medium (4小时响应):
  - 可疑进程执行
  - 异常网络连接
  - 策略违规

P4 - Low (24小时响应):
  - 信息性告警
  - 合规检查
```

### 告警质量指标
```python
class AlertMetrics:
    def calculate(self, alerts):
        total = len(alerts)
        tp = sum(1 for a in alerts if a['verified'] == 'true_positive')
        fp = sum(1 for a in alerts if a['verified'] == 'false_positive')

        return {
            'true_positive_rate': tp / total * 100,
            'false_positive_rate': fp / total * 100,
            'mean_time_to_detect': self._mttd(alerts),
            'mean_time_to_respond': self._mttr(alerts),
        }
```

## 应急响应

### IR 流程
```
┌─────────────────────────────────────────────────────────────┐
│                    应急响应流程                               │
├─────────────────────────────────────────────────────────────┤
│  1. 准备 (Preparation)                                       │
│  └─ 工具准备、流程文档、联系人清单                           │
│                        ↓                                     │
│  2. 识别 (Identification)                                    │
│  └─ 确认事件、评估范围、初步分类                             │
│                        ↓                                     │
│  3. 遏制 (Containment)                                       │
│  └─ 隔离系统、阻断通信、保护证据                             │
│                        ↓                                     │
│  4. 根除 (Eradication)                                       │
│  └─ 清除恶意软件、修复漏洞、重置凭证                         │
│                        ↓                                     │
│  5. 恢复 (Recovery)                                          │
│  └─ 系统恢复、监控加强、业务恢复                             │
│                        ↓                                     │
│  6. 总结 (Lessons Learned)                                   │
│  └─ 事件报告、改进措施、知识沉淀                             │
└─────────────────────────────────────────────────────────────┘
```

### 快速遏制
```bash
# Windows - 隔离主机
netsh advfirewall set allprofiles state on
netsh advfirewall firewall add rule name="Block All" dir=out action=block

# Linux - 隔离主机
iptables -P INPUT DROP
iptables -P OUTPUT DROP
iptables -A INPUT -s TRUSTED_IP -j ACCEPT

# 禁用账户
net user compromised_user /active:no
passwd -l compromised_user

# 终止恶意进程
taskkill /F /PID <pid>
kill -9 <pid>
```

### 证据收集
```bash
# Windows
wmic process list full > processes.txt
netstat -ano > netstat.txt
reg export HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run run.reg
wevtutil epl Security security.evtx

# Linux
ps auxf > processes.txt
netstat -tulpn > netstat.txt
cat /etc/passwd > passwd.txt
last > logins.txt
cp /var/log/auth.log .
```

## 数字取证

### 内存取证
```bash
# 内存获取
# Windows - WinPMEM
winpmem_mini_x64.exe memory.raw

# Linux - LiME
insmod lime.ko "path=/tmp/memory.lime format=lime"

# 分析 - Volatility
vol.py -f memory.raw imageinfo
vol.py -f memory.raw --profile=Win10x64 pslist
vol.py -f memory.raw --profile=Win10x64 netscan
vol.py -f memory.raw --profile=Win10x64 malfind
vol.py -f memory.raw --profile=Win10x64 dlllist
```

### 磁盘取证
```bash
# 镜像获取
dd if=/dev/sda of=disk.img bs=4M status=progress

# 挂载分析
mount -o ro,loop disk.img /mnt/evidence

# 时间线分析
log2timeline.py timeline.plaso disk.img
psort.py -o l2tcsv timeline.plaso -w timeline.csv

# 文件恢复
foremost -i disk.img -o recovered/
photorec disk.img
```

### 日志分析
```bash
# Windows 事件日志
# 使用 EvtxECmd 解析
EvtxECmd.exe -f Security.evtx --csv output/

# Linux 日志
grep "Failed password" /var/log/auth.log
grep "Accepted" /var/log/auth.log | awk '{print $1,$2,$3,$9,$11}'
zcat /var/log/auth.log.*.gz | grep "sudo"
```

## 威胁狩猎

### 狩猎假设
```yaml
# 基于 ATT&CK 的狩猎假设
hypothesis: "攻击者可能使用 PowerShell 下载并执行恶意代码"
technique: T1059.001
data_sources:
  - Windows PowerShell 日志
  - Sysmon 进程创建
query: |
  EventID=4104 AND ScriptBlockText CONTAINS ("IEX" OR "DownloadString")
```

### 狩猎查询示例
```sql
-- 异常父子进程关系
SELECT parent_name, process_name, command_line
FROM processes
WHERE parent_name = 'winword.exe'
  AND process_name IN ('cmd.exe', 'powershell.exe', 'wscript.exe')

-- 异常网络连接
SELECT process_name, remote_address, remote_port
FROM network_connections
WHERE remote_port NOT IN (80, 443, 53)
  AND process_name NOT IN ('chrome.exe', 'firefox.exe')

-- 可疑计划任务
SELECT name, command, trigger
FROM scheduled_tasks
WHERE command LIKE '%powershell%' OR command LIKE '%cmd%'
```

## 工具清单

| 工具 | 用途 |
|------|------|
| Sigma | 通用检测规则 |
| YARA | 恶意软件检测 |
| Splunk/Elastic | SIEM 平台 |
| Volatility | 内存取证 |
| Autopsy | 磁盘取证 |
| Velociraptor | 端点响应 |
| TheHive | 事件管理 |
| MISP | 威胁情报 |

---

**检测是防御的眼睛，响应是防御的拳头。**
