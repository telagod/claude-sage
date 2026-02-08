---
name: compliance
description: 合规审计秘典。GDPR、SOC2、审计日志、数据治理、合规即代码。当用户提到合规、GDPR、SOC2、审计、数据治理、隐私时路由到此。
---

# 🏗 阵法秘典 · 合规审计

> 天道有律，万法有规。合规即护法，审计即天眼。

## 合规框架总览

| 框架 | 适用范围 | 核心要求 | 处罚 |
|------|----------|----------|------|
| GDPR | 欧盟用户数据 | 数据保护、用户权利 | 营收4%或€2000万 |
| SOC 2 | SaaS/云服务 | 安全、可用、机密、隐私、处理完整性 | 失去客户信任 |
| HIPAA | 医疗健康数据 | PHI保护 | $50K-$1.5M/次 |
| PCI DSS | 支付卡数据 | 持卡人数据保护 | $5K-$100K/月 |
| ISO 27001 | 信息安全管理 | ISMS体系 | 认证失败 |

---

## GDPR

### 七大原则

| 原则 | 含义 | 技术实现 |
|------|------|----------|
| 合法性 | 有合法基础处理数据 | 同意管理系统 |
| 目的限制 | 仅用于声明目的 | 数据用途标记 |
| 数据最小化 | 仅收集必要数据 | 字段级权限控制 |
| 准确性 | 数据准确且及时更新 | 数据校验流程 |
| 存储限制 | 不超期保留 | 自动过期删除 |
| 完整性与机密性 | 安全保护 | 加密、访问控制 |
| 问责制 | 可证明合规 | 审计日志 |

### 用户权利 (DSAR)

| 权利 | API 实现 | SLA |
|------|----------|-----|
| 访问权 | `GET /api/users/{id}/data-export` | 30天 |
| 删除权 | `DELETE /api/users/{id}/data` | 30天 |
| 可携带权 | `GET /api/users/{id}/data-export?format=json` | 30天 |
| 更正权 | `PATCH /api/users/{id}/data` | 30天 |
| 限制处理 | `POST /api/users/{id}/restrict` | 72小时 |
| 反对权 | `POST /api/users/{id}/opt-out` | 即时 |

### 技术实现

```python
# 数据删除 (Right to Erasure)
async def delete_user_data(user_id: str):
    # 1. 标记删除（软删除）
    await db.execute(
        "UPDATE users SET status='deleted', deleted_at=NOW() WHERE id = %s",
        user_id
    )
    
    # 2. 匿名化关联数据
    await db.execute(
        "UPDATE orders SET user_name='[REDACTED]', email='[REDACTED]' WHERE user_id = %s",
        user_id
    )
    
    # 3. 清除缓存
    await redis.delete(f"user:{user_id}")
    
    # 4. 通知下游服务
    await event_bus.publish("user.data.deleted", {"user_id": user_id})
    
    # 5. 记录审计日志
    await audit_log.record(
        action="GDPR_ERASURE",
        subject=user_id,
        actor="system",
        details={"reason": "DSAR request"}
    )
```

---

## SOC 2

### 五大信任原则

| 原则 | 关注点 | 关键控制 |
|------|--------|----------|
| 安全 (必选) | 防止未授权访问 | 访问控制、加密、防火墙 |
| 可用性 | 系统可用性承诺 | SLA、灾备、监控 |
| 处理完整性 | 数据处理准确完整 | 输入验证、对账 |
| 机密性 | 机密信息保护 | 加密、分类、DLP |
| 隐私 | 个人信息保护 | 隐私政策、同意管理 |

### 关键控制措施

```yaml
访问控制:
  - MFA 强制启用
  - RBAC / ABAC
  - 最小权限原则
  - 定期访问审查 (季度)
  - 离职即撤权

变更管理:
  - 代码审查 (PR approval)
  - 分环境部署 (dev → staging → prod)
  - 变更审批流程
  - 回滚方案

监控与告警:
  - 安全事件监控
  - 异常登录检测
  - 数据访问审计
  - 定期漏洞扫描

事件响应:
  - IR 计划文档化
  - 定期演练
  - 通知流程 (72小时内)
  - 事后复盘
```

---

## 审计日志

### 日志设计

```json
{
  "id": "audit-uuid-001",
  "timestamp": "2024-01-15T10:30:00.123Z",
  "actor": {
    "id": "user-123",
    "type": "user",
    "ip": "192.168.x.x",
    "user_agent": "Mozilla/5.0..."
  },
  "action": "user.data.export",
  "resource": {
    "type": "user_data",
    "id": "user-456"
  },
  "result": "success",
  "details": {
    "reason": "DSAR request",
    "fields_exported": ["name", "email", "orders"]
  },
  "metadata": {
    "request_id": "req-789",
    "service": "user-service",
    "version": "1.2.3"
  }
}
```

### 必须审计的事件

```yaml
认证:
  - 登录成功/失败
  - MFA 验证
  - 密码变更
  - Token 签发/撤销

授权:
  - 权限变更
  - 角色分配
  - 访问拒绝

数据:
  - 敏感数据访问
  - 数据导出
  - 数据删除
  - 批量操作

系统:
  - 配置变更
  - 部署事件
  - 安全策略变更
  - 管理员操作
```

### 存储要求

```yaml
保留期限:
  - 安全事件: ≥ 1年
  - 访问日志: ≥ 90天
  - 变更日志: ≥ 3年
  - 合规审计: ≥ 7年

存储策略:
  - 不可篡改 (WORM / append-only)
  - 加密存储
  - 异地备份
  - 访问控制 (仅审计员可读)
```

---

## 数据治理

### 数据分类

| 级别 | 类型 | 保护措施 | 示例 |
|------|------|----------|------|
| 公开 | Public | 无特殊要求 | 产品文档 |
| 内部 | Internal | 访问控制 | 内部Wiki |
| 机密 | Confidential | 加密+审计 | 客户数据 |
| 受限 | Restricted | 加密+审计+MFA | 密钥、PII |

### 数据生命周期

```
创建 → 存储 → 使用 → 共享 → 归档 → 销毁
  │      │      │      │      │       │
 分类   加密   审计   脱敏   压缩    安全删除
```

### 数据血缘 (Data Lineage)

```
数据源 → ETL → 数据仓库 → 报表
  │              │           │
  └── 追踪数据流向，确保合规处理
```

---

## 合规即代码 (Compliance as Code)

### OPA (Open Policy Agent)

```rego
# 策略: 禁止公开 S3 Bucket
deny[msg] {
    input.resource_type == "aws_s3_bucket"
    input.resource.acl == "public-read"
    msg := sprintf("S3 bucket %s must not be public", [input.resource.name])
}

# 策略: 强制加密
deny[msg] {
    input.resource_type == "aws_s3_bucket"
    not input.resource.server_side_encryption_configuration
    msg := sprintf("S3 bucket %s must have encryption enabled", [input.resource.name])
}
```

### CI/CD 集成

```yaml
# 合规检查 Pipeline
compliance-check:
  stage: validate
  steps:
    - name: Terraform Plan
      run: terraform plan -out=plan.tfplan
    
    - name: OPA Check
      run: |
        terraform show -json plan.tfplan > plan.json
        opa eval -d policies/ -i plan.json "data.terraform.deny"
    
    - name: Secret Scan
      run: gitleaks detect --source .
    
    - name: License Check
      run: license-checker --production --failOn "GPL"
```

---

## 合规检查清单

```yaml
GDPR:
  - [ ] 隐私政策更新
  - [ ] 同意管理实现
  - [ ] DSAR 流程就绪 (30天SLA)
  - [ ] 数据加密 (传输+存储)
  - [ ] 数据保留策略
  - [ ] 数据泄露通知流程 (72小时)
  - [ ] DPO 指定

SOC 2:
  - [ ] 访问控制 + MFA
  - [ ] 变更管理流程
  - [ ] 事件响应计划
  - [ ] 漏洞管理
  - [ ] 安全培训记录
  - [ ] 供应商评估

审计:
  - [ ] 审计日志覆盖关键操作
  - [ ] 日志不可篡改
  - [ ] 保留期限符合要求
  - [ ] 定期审计审查
```

---

**道训**：天道有律，万法有规。合规非枷锁，乃护道之盾。

`🏗 阵法秘典·合规审计已成，天律在手，道基无虞。`
