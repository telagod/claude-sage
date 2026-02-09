---
name: threat-intel
description: 威胁情报。OSINT、威胁狩猎、情报分析、IOC管理。当用户提到威胁情报、OSINT、开源情报、威胁狩猎、IOC、TTP、ATT&CK时使用。
---

# 👁 天眼秘典 · 威胁情报 (Threat Intelligence)


## 情报层次

```
┌─────────────────────────────────────────────────────────────┐
│                    威胁情报金字塔                             │
├─────────────────────────────────────────────────────────────┤
│                      战略情报                                │
│                   (决策层/长期趋势)                          │
│                    ─────────────                             │
│                     战术情报                                 │
│                  (TTP/攻击手法)                              │
│                   ─────────────                              │
│                    运营情报                                  │
│                 (攻击活动/APT)                               │
│                  ─────────────                               │
│                   技术情报                                   │
│                (IOC/IP/域名/Hash)                            │
└─────────────────────────────────────────────────────────────┘
```

## OSINT 信息收集

### 域名/IP 情报
```bash
# DNS 查询
dig +short example.com
dig +short -x 1.2.3.4
host example.com

# WHOIS
whois example.com
whois 1.2.3.4

# 子域名枚举
subfinder -d example.com
amass enum -d example.com
```

### 在线情报平台
```yaml
IP/域名信誉:
  - VirusTotal: https://www.virustotal.com
  - AbuseIPDB: https://www.abuseipdb.com
  - Shodan: https://www.shodan.io
  - Censys: https://search.censys.io
  - GreyNoise: https://www.greynoise.io

恶意软件分析:
  - Any.Run: https://any.run
  - Hybrid Analysis: https://www.hybrid-analysis.com
  - Joe Sandbox: https://www.joesandbox.com
  - MalwareBazaar: https://bazaar.abuse.ch

威胁情报:
  - AlienVault OTX: https://otx.alienvault.com
  - MISP: https://www.misp-project.org
  - ThreatFox: https://threatfox.abuse.ch
```

### 搜索引擎 Dorking
```
# Google Dorks
site:example.com filetype:pdf
site:example.com inurl:admin
site:example.com intitle:"index of"
"password" filetype:log site:example.com

# Shodan
hostname:example.com
org:"Target Company"
ssl.cert.subject.cn:example.com
http.title:"Dashboard"

# Censys
services.http.response.html_title:"Admin"
services.tls.certificates.leaf.subject.common_name:example.com
```

### 社交媒体情报
```yaml
平台:
  - LinkedIn: 员工信息、组织架构
  - GitHub: 代码泄露、API密钥
  - Twitter: 安全事件、漏洞披露
  - Pastebin: 数据泄露

GitHub Dorks:
  - "example.com" password
  - "example.com" api_key
  - "example.com" secret
  - org:example filename:.env
```

## IOC 管理

### IOC 类型
```yaml
网络层:
  - IP 地址
  - 域名
  - URL
  - User-Agent

主机层:
  - 文件 Hash (MD5/SHA1/SHA256)
  - 文件路径
  - 注册表键
  - 进程名

行为层:
  - YARA 规则
  - Sigma 规则
  - Snort 规则
```

### IOC 格式 (STIX/TAXII)
```json
{
  "type": "indicator",
  "id": "indicator--xxx",
  "created": "2024-01-01T00:00:00.000Z",
  "pattern": "[file:hashes.SHA256 = 'abc123...']",
  "pattern_type": "stix",
  "valid_from": "2024-01-01T00:00:00.000Z",
  "labels": ["malicious-activity"],
  "kill_chain_phases": [{
    "kill_chain_name": "mitre-attack",
    "phase_name": "execution"
  }]
}
```

### IOC 自动化查询
```python
#!/usr/bin/env python3
"""IOC 批量查询"""
import requests

class IOCChecker:
    def __init__(self, vt_api_key):
        self.vt_key = vt_api_key

    def check_hash(self, file_hash):
        """VirusTotal Hash 查询"""
        url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
        headers = {"x-apikey": self.vt_key}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            stats = data['data']['attributes']['last_analysis_stats']
            return {
                'malicious': stats['malicious'],
                'suspicious': stats['suspicious'],
                'harmless': stats['harmless']
            }
        return None

    def check_ip(self, ip):
        """AbuseIPDB 查询"""
        url = "https://api.abuseipdb.com/api/v2/check"
        params = {"ipAddress": ip, "maxAgeInDays": 90}
        # 需要 API Key
        pass

    def check_domain(self, domain):
        """域名信誉查询"""
        pass
```

## ATT&CK 映射

### TTP 分析
```yaml
# 攻击者画像
APT_Profile:
  name: "APT-XX"
  aliases: ["Group A", "Group B"]
  targets:
    - 金融行业
    - 政府机构
  techniques:
    initial_access:
      - T1566.001: Spearphishing Attachment
      - T1566.002: Spearphishing Link
    execution:
      - T1059.001: PowerShell
      - T1059.003: Windows Command Shell
    persistence:
      - T1547.001: Registry Run Keys
      - T1053.005: Scheduled Task
    c2:
      - T1071.001: Web Protocols
      - T1573.001: Encrypted Channel
  tools:
    - Cobalt Strike
    - Mimikatz
    - Custom Malware
```

### ATT&CK Navigator
```python
# 生成 ATT&CK Navigator 层
def generate_navigator_layer(techniques):
    layer = {
        "name": "Threat Actor Coverage",
        "versions": {"attack": "13", "navigator": "4.8"},
        "domain": "enterprise-attack",
        "techniques": []
    }

    for tech_id, score in techniques.items():
        layer["techniques"].append({
            "techniqueID": tech_id,
            "score": score,
            "color": "#ff6666" if score > 50 else "#ffcc66"
        })

    return layer
```

## 威胁狩猎

### 狩猎流程
```
假设生成 → 数据收集 → 分析调查 → 发现验证 → 知识沉淀
    │           │           │           │           │
    └─ ATT&CK ──┴─ SIEM ────┴─ 查询 ────┴─ IOC ────┴─ 规则
```

### 狩猎假设模板
```yaml
hypothesis: "攻击者可能通过 PowerShell 下载执行恶意代码"
technique: T1059.001
data_sources:
  - Windows PowerShell 日志 (4103, 4104)
  - Sysmon 进程创建 (Event ID 1)
query: |
  EventID=4104 AND ScriptBlockText CONTAINS
  ("IEX" OR "Invoke-Expression" OR "DownloadString" OR "Net.WebClient")
expected_results:
  - 可疑脚本块
  - 外部 URL 下载
  - 编码命令
response:
  - 隔离主机
  - 提取样本
  - 扩展狩猎
```

### 狩猎查询库
```sql
-- 异常 PowerShell 执行
SELECT timestamp, hostname, user, command_line
FROM process_events
WHERE process_name = 'powershell.exe'
  AND (command_line LIKE '%IEX%'
       OR command_line LIKE '%DownloadString%'
       OR command_line LIKE '%-enc%')

-- 异常网络连接
SELECT timestamp, process_name, remote_address, remote_port
FROM network_events
WHERE remote_port NOT IN (80, 443, 53, 22)
  AND remote_address NOT LIKE '10.%'
  AND remote_address NOT LIKE '192.168.%'

-- 可疑文件创建
SELECT timestamp, process_name, file_path
FROM file_events
WHERE file_path LIKE '%\Temp\%'
  AND file_path LIKE '%.exe'
  AND process_name IN ('powershell.exe', 'cmd.exe', 'wscript.exe')
```

## 情报共享

### MISP 集成
```python
from pymisp import PyMISP

misp = PyMISP(url, key, ssl=False)

# 创建事件
event = misp.new_event(
    distribution=0,
    info="Phishing Campaign 2024-01",
    analysis=2,
    threat_level_id=2
)

# 添加 IOC
misp.add_attribute(event, type='ip-dst', value='1.2.3.4')
misp.add_attribute(event, type='domain', value='malicious.com')
misp.add_attribute(event, type='sha256', value='abc123...')

# 添加标签
misp.tag(event, 'tlp:amber')
misp.tag(event, 'misp-galaxy:mitre-attack-pattern="T1566"')
```

## 工具清单

| 工具 | 用途 |
|------|------|
| MISP | 威胁情报平台 |
| OpenCTI | 威胁情报管理 |
| TheHive | 事件响应平台 |
| Maltego | 关系分析 |
| Shodan | 网络空间搜索 |
| VirusTotal | 恶意软件分析 |
| ATT&CK Navigator | TTP 可视化 |

---

