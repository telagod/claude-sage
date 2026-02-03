---
name: data-security
description: 数据安全。加密、隐私保护、合规。当用户提到数据安全、加密、隐私、GDPR、合规时使用。
---

# 数据安全

> 数据是资产，安全是底线

## 数据分类

```yaml
公开数据:
  - 公开信息
  - 营销材料

内部数据:
  - 内部文档
  - 业务数据

机密数据:
  - 客户信息
  - 财务数据
  - 商业秘密

敏感数据:
  - PII (个人身份信息)
  - PHI (健康信息)
  - 支付卡数据
```

## 加密

### 传输加密
```yaml
TLS 配置:
  - TLS 1.2+ (禁用 1.0/1.1)
  - 强密码套件
  - 证书管理
  - HSTS

推荐密码套件:
  - TLS_AES_256_GCM_SHA384
  - TLS_CHACHA20_POLY1305_SHA256
  - ECDHE-RSA-AES256-GCM-SHA384
```

### 存储加密
```python
# 对称加密 (AES-256-GCM)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key = os.urandom(32)  # 256-bit key
nonce = os.urandom(12)
aesgcm = AESGCM(key)

ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data)
```

### 密钥管理
```yaml
原则:
  - 密钥与数据分离
  - 定期轮换
  - 最小权限访问
  - 审计日志

方案:
  - AWS KMS
  - HashiCorp Vault
  - Azure Key Vault
```

### 密码存储
```python
# 使用 bcrypt 或 argon2
import bcrypt

# 哈希
password = b"user_password"
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password, salt)

# 验证
bcrypt.checkpw(password, hashed)
```

## 隐私保护

### 数据脱敏
```python
# 姓名脱敏
def mask_name(name):
    if len(name) <= 1:
        return "*"
    return name[0] + "*" * (len(name) - 1)

# 手机号脱敏
def mask_phone(phone):
    return phone[:3] + "****" + phone[-4:]

# 邮箱脱敏
def mask_email(email):
    local, domain = email.split("@")
    return local[0] + "***@" + domain

# 身份证脱敏
def mask_id_card(id_card):
    return id_card[:6] + "********" + id_card[-4:]
```

### 数据最小化
```yaml
原则:
  - 只收集必要数据
  - 限制保留期限
  - 定期清理
  - 匿名化/假名化
```

## 合规要求

### GDPR
```yaml
核心要求:
  - 合法性、公平性、透明性
  - 目的限制
  - 数据最小化
  - 准确性
  - 存储限制
  - 完整性和保密性
  - 问责制

数据主体权利:
  - 知情权
  - 访问权
  - 更正权
  - 删除权 (被遗忘权)
  - 限制处理权
  - 数据可携带权
  - 反对权
```

### 安全控制
```yaml
技术措施:
  - 加密
  - 访问控制
  - 日志审计
  - 数据备份

组织措施:
  - 安全政策
  - 员工培训
  - 事件响应
  - 供应商管理
```

## 数据安全检查清单

```yaml
分类与发现:
  - [ ] 数据资产清单
  - [ ] 敏感数据识别
  - [ ] 数据流映射

保护:
  - [ ] 传输加密
  - [ ] 存储加密
  - [ ] 访问控制
  - [ ] 数据脱敏

监控:
  - [ ] 访问日志
  - [ ] 异常检测
  - [ ] DLP

合规:
  - [ ] 隐私政策
  - [ ] 数据处理协议
  - [ ] 事件响应计划
```

---

**数据安全：保护用户，保护业务。**
