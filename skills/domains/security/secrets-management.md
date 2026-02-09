---
name: secrets-management
description: 密钥管理与加密。HashiCorp Vault、AWS KMS、密钥轮转、加密最佳实践、密钥生命周期。当用户提到密钥管理、Vault、KMS、密钥轮转、加密、密钥存储、凭证管理时使用。
---

# 🔐 密钥管理 · Secrets Management


## 密钥生命周期

```
生成 → 存储 → 分发 → 使用 → 轮转 → 撤销 → 销毁
  │      │      │      │      │      │      │
  └─ 强度 ─┴─ 加密 ─┴─ 授权 ─┴─ 审计 ─┴─ 自动 ─┴─ 即时 ─┴─ 安全
```

## HashiCorp Vault

### Vault 架构

```
┌─────────────────────────────────────────┐
│            Vault API                    │
├─────────────────────────────────────────┤
│  Auth Methods  │  Secrets Engines       │
│  - Token       │  - KV (Key/Value)      │
│  - LDAP        │  - Database            │
│  - Kubernetes  │  - AWS                 │
│  - AppRole     │  - PKI                 │
├─────────────────────────────────────────┤
│         Storage Backend                 │
│  - Consul / etcd / S3 / File           │
└─────────────────────────────────────────┘
```

### Vault 部署

```bash
# 安装 Vault
wget https://releases.hashicorp.com/vault/1.15.0/vault_1.15.0_linux_amd64.zip
unzip vault_1.15.0_linux_amd64.zip
sudo mv vault /usr/local/bin/

# 启动开发服务器
vault server -dev

# 生产配置
cat > vault-config.hcl <<EOF
storage "consul" {
  address = "127.0.0.1:8500"
  path    = "vault/"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_cert_file = "/etc/vault/tls/vault.crt"
  tls_key_file  = "/etc/vault/tls/vault.key"
}

api_addr = "https://vault.example.com:8200"
cluster_addr = "https://vault.example.com:8201"
ui = true
EOF

# 启动 Vault
vault server -config=vault-config.hcl

# 初始化
vault operator init -key-shares=5 -key-threshold=3

# 解封
vault operator unseal <unseal-key-1>
vault operator unseal <unseal-key-2>
vault operator unseal <unseal-key-3>

# 登录
vault login <root-token>
```

### KV Secrets Engine

```bash
# 启用 KV v2
vault secrets enable -path=secret kv-v2

# 写入密钥
vault kv put secret/myapp/config \
  db_password="supersecret" \
  api_key="abc123"

# 读取密钥
vault kv get secret/myapp/config
vault kv get -field=db_password secret/myapp/config

# 版本管理
vault kv put secret/myapp/config db_password="newsecret"
vault kv get -version=1 secret/myapp/config

# 删除版本
vault kv delete -versions=2 secret/myapp/config

# 永久删除
vault kv destroy -versions=1,2 secret/myapp/config

# 恢复删除
vault kv undelete -versions=2 secret/myapp/config

# 元数据
vault kv metadata get secret/myapp/config
vault kv metadata put -max-versions=5 secret/myapp/config
```

### 动态密钥 (Database)

```bash
# 启用数据库引擎
vault secrets enable database

# 配置数据库连接
vault write database/config/postgresql \
  plugin_name=postgresql-database-plugin \
  allowed_roles="readonly,readwrite" \
  connection_url="postgresql://{{username}}:{{password}}@localhost:5432/mydb" \
  username="vault" \
  password="vaultpass"

# 创建角色
vault write database/roles/readonly \
  db_name=postgresql \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# 生成动态凭证
vault read database/creds/readonly

# 输出示例:
# Key                Value
# ---                -----
# lease_id           database/creds/readonly/abc123
# lease_duration     1h
# username           v-root-readonly-xyz789
# password           A1b2C3d4E5f6
```

### AppRole 认证

```bash
# 启用 AppRole
vault auth enable approle

# 创建策略
vault policy write myapp-policy - <<EOF
path "secret/data/myapp/*" {
  capabilities = ["read"]
}
path "database/creds/readonly" {
  capabilities = ["read"]
}
EOF

# 创建 AppRole
vault write auth/approle/role/myapp \
  token_policies="myapp-policy" \
  token_ttl=1h \
  token_max_ttl=4h

# 获取 Role ID
vault read auth/approle/role/myapp/role-id

# 生成 Secret ID
vault write -f auth/approle/role/myapp/secret-id

# 使用 AppRole 登录
vault write auth/approle/login \
  role_id="<role-id>" \
  secret_id="<secret-id>"
```

### Vault Python SDK

```python
#!/usr/bin/env python3
"""Vault 客户端封装"""
import hvac
from typing import Dict, Optional

class VaultClient:
    def __init__(self, url: str, token: Optional[str] = None):
        self.client = hvac.Client(url=url, token=token)

    def login_approle(self, role_id: str, secret_id: str):
        """AppRole 登录"""
        response = self.client.auth.approle.login(
            role_id=role_id,
            secret_id=secret_id
        )
        self.client.token = response['auth']['client_token']

    def read_secret(self, path: str) -> Dict:
        """读取 KV 密钥"""
        response = self.client.secrets.kv.v2.read_secret_version(
            path=path,
            mount_point='secret'
        )
        return response['data']['data']

    def write_secret(self, path: str, data: Dict):
        """写入 KV 密钥"""
        self.client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret=data,
            mount_point='secret'
        )

    def get_db_creds(self, role: str) -> Dict:
        """获取动态数据库凭证"""
        response = self.client.secrets.database.generate_credentials(
            name=role
        )
        return {
            'username': response['data']['username'],
            'password': response['data']['password'],
            'lease_id': response['lease_id'],
            'lease_duration': response['lease_duration']
        }

    def renew_lease(self, lease_id: str, increment: int = 3600):
        """续租"""
        self.client.sys.renew_lease(
            lease_id=lease_id,
            increment=increment
        )

    def revoke_lease(self, lease_id: str):
        """撤销租约"""
        self.client.sys.revoke_lease(lease_id)

# 使用示例
vault = VaultClient('https://vault.example.com:8200')
vault.login_approle(role_id='xxx', secret_id='yyy')

# 读取静态密钥
config = vault.read_secret('myapp/config')
print(f"DB Password: {config['db_password']}")

# 获取动态凭证
creds = vault.get_db_creds('readonly')
print(f"Username: {creds['username']}, Password: {creds['password']}")

# 续租
vault.renew_lease(creds['lease_id'], increment=7200)
```

## AWS KMS

### KMS 密钥管理

```bash
# 创建 KMS 密钥
aws kms create-key \
  --description "Application encryption key" \
  --key-usage ENCRYPT_DECRYPT \
  --origin AWS_KMS

# 创建别名
aws kms create-alias \
  --alias-name alias/myapp \
  --target-key-id <key-id>

# 加密数据
aws kms encrypt \
  --key-id alias/myapp \
  --plaintext "sensitive data" \
  --output text \
  --query CiphertextBlob

# 解密数据
aws kms decrypt \
  --ciphertext-blob fileb://encrypted.bin \
  --output text \
  --query Plaintext | base64 --decode

# 生成数据密钥
aws kms generate-data-key \
  --key-id alias/myapp \
  --key-spec AES_256

# 轮转密钥
aws kms enable-key-rotation --key-id <key-id>

# 查看轮转状态
aws kms get-key-rotation-status --key-id <key-id>
```

### KMS 信封加密

```python
#!/usr/bin/env python3
"""KMS 信封加密实现"""
import boto3
import base64
from cryptography.fernet import Fernet
from typing import Tuple

class KMSEnvelopeEncryption:
    def __init__(self, kms_key_id: str):
        self.kms = boto3.client('kms')
        self.kms_key_id = kms_key_id

    def encrypt(self, plaintext: bytes) -> Tuple[bytes, bytes]:
        """信封加密"""
        # 1. 生成数据密钥
        response = self.kms.generate_data_key(
            KeyId=self.kms_key_id,
            KeySpec='AES_256'
        )

        plaintext_key = response['Plaintext']
        encrypted_key = response['CiphertextBlob']

        # 2. 使用数据密钥加密数据
        fernet = Fernet(base64.urlsafe_b64encode(plaintext_key[:32]))
        encrypted_data = fernet.encrypt(plaintext)

        # 3. 返回加密的数据和加密的密钥
        return encrypted_data, encrypted_key

    def decrypt(self, encrypted_data: bytes, encrypted_key: bytes) -> bytes:
        """信封解密"""
        # 1. 解密数据密钥
        response = self.kms.decrypt(CiphertextBlob=encrypted_key)
        plaintext_key = response['Plaintext']

        # 2. 使用数据密钥解密数据
        fernet = Fernet(base64.urlsafe_b64encode(plaintext_key[:32]))
        plaintext = fernet.decrypt(encrypted_data)

        return plaintext

# 使用示例
kms = KMSEnvelopeEncryption('arn:aws:kms:us-east-1:123456789012:key/xxx')

# 加密
data = b"Sensitive information"
encrypted_data, encrypted_key = kms.encrypt(data)

# 解密
decrypted_data = kms.decrypt(encrypted_data, encrypted_key)
print(decrypted_data.decode())
```

### AWS Secrets Manager

```bash
# 创建密钥
aws secretsmanager create-secret \
  --name myapp/db/password \
  --secret-string '{"username":"admin","password":"supersecret"}'

# 读取密钥
aws secretsmanager get-secret-value \
  --secret-id myapp/db/password \
  --query SecretString \
  --output text

# 更新密钥
aws secretsmanager update-secret \
  --secret-id myapp/db/password \
  --secret-string '{"username":"admin","password":"newsecret"}'

# 轮转密钥
aws secretsmanager rotate-secret \
  --secret-id myapp/db/password \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:rotate

# 配置自动轮转
aws secretsmanager rotate-secret \
  --secret-id myapp/db/password \
  --rotation-rules AutomaticallyAfterDays=30
```

### Secrets Manager Python

```python
#!/usr/bin/env python3
"""AWS Secrets Manager 客户端"""
import boto3
import json
from typing import Dict

class SecretsManager:
    def __init__(self, region: str = 'us-east-1'):
        self.client = boto3.client('secretsmanager', region_name=region)

    def get_secret(self, secret_id: str) -> Dict:
        """获取密钥"""
        response = self.client.get_secret_value(SecretId=secret_id)
        return json.loads(response['SecretString'])

    def create_secret(self, name: str, secret: Dict):
        """创建密钥"""
        self.client.create_secret(
            Name=name,
            SecretString=json.dumps(secret)
        )

    def update_secret(self, secret_id: str, secret: Dict):
        """更新密钥"""
        self.client.update_secret(
            SecretId=secret_id,
            SecretString=json.dumps(secret)
        )

    def rotate_secret(self, secret_id: str, lambda_arn: str):
        """轮转密钥"""
        self.client.rotate_secret(
            SecretId=secret_id,
            RotationLambdaARN=lambda_arn,
            RotationRules={'AutomaticallyAfterDays': 30}
        )

# 使用示例
sm = SecretsManager()
db_creds = sm.get_secret('myapp/db/password')
print(f"Username: {db_creds['username']}")
```

## 密钥轮转策略

### 自动轮转实现

```python
#!/usr/bin/env python3
"""密钥自动轮转"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional

class SecretRotation:
    def __init__(self, vault_client):
        self.vault = vault_client
        self.rotation_period = timedelta(days=90)

    def generate_password(self, length: int = 32) -> str:
        """生成强密码"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def should_rotate(self, secret_path: str) -> bool:
        """检查是否需要轮转"""
        metadata = self.vault.client.secrets.kv.v2.read_secret_metadata(
            path=secret_path,
            mount_point='secret'
        )

        created_time = datetime.fromisoformat(
            metadata['data']['created_time'].replace('Z', '+00:00')
        )

        return datetime.now() - created_time > self.rotation_period

    def rotate_database_password(self, db_config: Dict):
        """轮转数据库密码"""
        # 1. 生成新密码
        new_password = self.generate_password()

        # 2. 在数据库中更新密码
        import psycopg2
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            f"ALTER USER {db_config['user']} WITH PASSWORD %s",
            (new_password,)
        )
        conn.commit()
        conn.close()

        # 3. 更新 Vault 中的密钥
        self.vault.write_secret(
            'myapp/db/password',
            {'password': new_password}
        )

        # 4. 记录轮转事件
        self.log_rotation('database', 'myapp/db/password')

    def rotate_api_key(self, service: str, api_endpoint: str):
        """轮转 API 密钥"""
        # 1. 调用服务 API 生成新密钥
        import requests
        response = requests.post(
            f"{api_endpoint}/keys/rotate",
            headers={'Authorization': f'Bearer {self.get_current_key(service)}'}
        )
        new_key = response.json()['api_key']

        # 2. 更新 Vault
        self.vault.write_secret(
            f'{service}/api_key',
            {'key': new_key}
        )

        # 3. 撤销旧密钥（延迟撤销，给应用时间更新）
        # 在 24 小时后撤销

    def log_rotation(self, secret_type: str, path: str):
        """记录轮转日志"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': secret_type,
            'path': path,
            'action': 'rotated'
        }
        print(f"[ROTATION] {log_entry}")

    def get_current_key(self, service: str) -> str:
        """获取当前密钥"""
        secret = self.vault.read_secret(f'{service}/api_key')
        return secret['key']

# 使用示例
from vault_client import VaultClient

vault = VaultClient('https://vault.example.com:8200')
vault.login_approle(role_id='xxx', secret_id='yyy')

rotation = SecretRotation(vault)

# 检查并轮转
if rotation.should_rotate('myapp/db/password'):
    rotation.rotate_database_password({
        'host': 'localhost',
        'database': 'mydb',
        'user': 'myapp',
        'password': vault.read_secret('myapp/db/password')['password']
    })
```

### 轮转策略配置

```yaml
# rotation-policy.yaml
rotation_policies:
  - name: "database_passwords"
    type: "database"
    schedule: "0 2 * * 0"  # 每周日凌晨2点
    max_age_days: 90
    notification:
      - email: security@company.com
      - slack: "#security-alerts"

  - name: "api_keys"
    type: "api"
    schedule: "0 3 1 * *"  # 每月1号凌晨3点
    max_age_days: 30
    grace_period_hours: 24

  - name: "tls_certificates"
    type: "certificate"
    schedule: "0 4 * * *"  # 每天凌晨4点检查
    renew_before_days: 30
    auto_deploy: true
```

## 加密最佳实践

### 静态加密

```python
#!/usr/bin/env python3
"""数据静态加密"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os

class DataEncryption:
    def __init__(self, master_key: bytes):
        self.master_key = master_key

    def derive_key(self, salt: bytes) -> bytes:
        """从主密钥派生加密密钥"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.master_key))

    def encrypt_field(self, plaintext: str, context: str = "") -> str:
        """加密字段"""
        salt = os.urandom(16)
        key = self.derive_key(salt + context.encode())
        fernet = Fernet(key)

        encrypted = fernet.encrypt(plaintext.encode())
        # 返回: salt + encrypted_data
        return base64.b64encode(salt + encrypted).decode()

    def decrypt_field(self, ciphertext: str, context: str = "") -> str:
        """解密字段"""
        data = base64.b64decode(ciphertext)
        salt = data[:16]
        encrypted = data[16:]

        key = self.derive_key(salt + context.encode())
        fernet = Fernet(key)

        return fernet.decrypt(encrypted).decode()

# 使用示例
master_key = os.environ['MASTER_KEY'].encode()
crypto = DataEncryption(master_key)

# 加密敏感字段
encrypted_ssn = crypto.encrypt_field("123-45-6789", context="user:ssn")
encrypted_cc = crypto.encrypt_field("4111111111111111", context="user:cc")

# 解密
ssn = crypto.decrypt_field(encrypted_ssn, context="user:ssn")
```

### 传输加密

```python
#!/usr/bin/env python3
"""TLS 配置最佳实践"""
import ssl
import socket

def create_secure_context() -> ssl.SSLContext:
    """创建安全的 SSL 上下文"""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    # 加载证书
    context.load_cert_chain('server.crt', 'server.key')

    # 仅允许 TLS 1.2+
    context.minimum_version = ssl.TLSVersion.TLSv1_2

    # 禁用不安全的密码套件
    context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')

    # 启用 OCSP Stapling
    context.options |= ssl.OP_NO_COMPRESSION

    return context

# HTTPS 服务器示例
def run_https_server():
    context = create_secure_context()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('0.0.0.0', 8443))
        sock.listen(5)

        with context.wrap_socket(sock, server_side=True) as ssock:
            while True:
                conn, addr = ssock.accept()
                # 处理连接
                conn.close()
```

### 使用中加密 (Homomorphic)

```python
#!/usr/bin/env python3
"""同态加密示例（简化）"""
from typing import List

class SimpleHomomorphic:
    """简化的加法同态加密"""

    def __init__(self, public_key: int, private_key: int):
        self.public_key = public_key
        self.private_key = private_key

    def encrypt(self, plaintext: int) -> int:
        """加密"""
        # 简化实现，实际应使用 Paillier 等算法
        return (plaintext * self.public_key) % 1000000007

    def decrypt(self, ciphertext: int) -> int:
        """解密"""
        return (ciphertext * self.private_key) % 1000000007

    def add_encrypted(self, c1: int, c2: int) -> int:
        """在密文上执行加法"""
        return (c1 + c2) % 1000000007

# 使用示例
he = SimpleHomomorphic(public_key=123, private_key=456)

# 加密两个数
enc1 = he.encrypt(10)
enc2 = he.encrypt(20)

# 在密文上相加
enc_sum = he.add_encrypted(enc1, enc2)

# 解密结果
result = he.decrypt(enc_sum)
print(f"10 + 20 = {result}")
```

## Kubernetes Secrets

### External Secrets Operator

```yaml
# external-secret.yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: "https://vault.example.com:8200"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "myapp"
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: myapp-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: myapp-secrets
    creationPolicy: Owner
  data:
    - secretKey: db_password
      remoteRef:
        key: myapp/config
        property: db_password
    - secretKey: api_key
      remoteRef:
        key: myapp/config
        property: api_key
```

### Sealed Secrets

```bash
# 安装 Sealed Secrets
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# 安装 kubeseal CLI
wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/kubeseal-linux-amd64
chmod +x kubeseal-linux-amd64
sudo mv kubeseal-linux-amd64 /usr/local/bin/kubeseal

# 创建 Secret
kubectl create secret generic mysecret \
  --from-literal=password=supersecret \
  --dry-run=client -o yaml > secret.yaml

# 加密 Secret
kubeseal -f secret.yaml -w sealed-secret.yaml

# 应用 Sealed Secret
kubectl apply -f sealed-secret.yaml
```

## 工具清单

| 工具 | 类型 | 特点 |
|------|------|------|
| HashiCorp Vault | 平台 | 动态密钥、多后端 |
| AWS KMS | 云服务 | 托管密钥、信封加密 |
| AWS Secrets Manager | 云服务 | 自动轮转、集成 |
| Azure Key Vault | 云服务 | HSM 支持 |
| GCP Secret Manager | 云服务 | IAM 集成 |
| CyberArk | 企业 | PAM 解决方案 |
| Sealed Secrets | K8s | GitOps 友好 |
| External Secrets | K8s | 多后端同步 |

## 最佳实践

### 密钥管理检查清单

```markdown
## 生成与存储
- [ ] 使用加密强随机数生成器
- [ ] 密钥长度符合标准（AES-256, RSA-2048+）
- [ ] 集中存储在密钥管理系统
- [ ] 启用静态加密
- [ ] 实施访问控制

## 分发与使用
- [ ] 最小权限原则
- [ ] 使用短期凭证
- [ ] 避免硬编码
- [ ] 环境变量或挂载卷
- [ ] 传输加密（TLS）

## 轮转与撤销
- [ ] 定期自动轮转
- [ ] 支持紧急撤销
- [ ] 轮转后验证
- [ ] 保留审计日志
- [ ] 通知相关方

## 监控与审计
- [ ] 记录所有访问
- [ ] 异常检测告警
- [ ] 定期审计
- [ ] 合规性检查
- [ ] 事件响应计划
```

### 密钥分类策略

| 级别 | 类型 | 轮转周期 | 存储 |
|------|------|----------|------|
| P0 | 根密钥、主密钥 | 年度 | HSM |
| P1 | 数据加密密钥 | 季度 | Vault |
| P2 | API 密钥 | 月度 | Secrets Manager |
| P3 | 会话令牌 | 小时 | Redis |

---
