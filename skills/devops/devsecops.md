---
name: devsecops
description: DevSecOps。CI/CD安全、供应链安全、合规自动化。当用户提到 DevSecOps、CI/CD、供应链安全、SAST、DAST时使用。
---

# DevSecOps

> 安全左移，自动化防护

## 安全左移

```
┌─────────────────────────────────────────────────────────────┐
│                    安全左移                                  │
├─────────────────────────────────────────────────────────────┤
│  计划 → 编码 → 构建 → 测试 → 发布 → 部署 → 运维 → 监控     │
│    │      │      │      │      │      │      │      │       │
│  威胁   SAST   SCA   DAST   签名   配置   日志   告警       │
│  建模   IDE    依赖   渗透   验证   加固   审计   响应       │
└─────────────────────────────────────────────────────────────┘
```

## CI/CD 安全

### GitHub Actions
```yaml
name: Security Pipeline

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # SAST - 静态分析
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: p/security-audit

      # SCA - 依赖扫描
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'CRITICAL,HIGH'

      # Secret 扫描
      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2

      # 容器扫描
      - name: Build and scan image
        run: |
          docker build -t myapp:${{ github.sha }} .
          trivy image myapp:${{ github.sha }}
```

### GitLab CI
```yaml
stages:
  - test
  - security
  - build
  - deploy

sast:
  stage: security
  image: semgrep/semgrep
  script:
    - semgrep --config=p/security-audit .

dependency_scan:
  stage: security
  image: aquasec/trivy
  script:
    - trivy fs --severity HIGH,CRITICAL .

container_scan:
  stage: security
  image: aquasec/trivy
  script:
    - trivy image $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

## 安全扫描工具

### SAST (静态分析)
```yaml
工具:
  - Semgrep: 多语言，规则丰富
  - SonarQube: 企业级
  - CodeQL: GitHub 原生
  - Bandit: Python 专用

集成:
  - IDE 插件
  - Pre-commit hooks
  - CI/CD pipeline
```

### SCA (依赖扫描)
```yaml
工具:
  - Trivy: 全能扫描
  - Snyk: 商业方案
  - OWASP Dependency-Check
  - npm audit / pip-audit

检查项:
  - 已知漏洞 (CVE)
  - 许可证合规
  - 过期依赖
```

### DAST (动态分析)
```yaml
工具:
  - OWASP ZAP
  - Nuclei
  - Burp Suite

集成:
  - 部署后自动扫描
  - 定期扫描
  - PR 环境扫描
```

## 供应链安全

### 依赖管理
```yaml
原则:
  - 锁定依赖版本
  - 定期更新
  - 审查新依赖
  - 使用私有仓库

工具:
  - Dependabot
  - Renovate
  - Snyk
```

### 镜像安全
```yaml
原则:
  - 使用官方基础镜像
  - 最小化镜像
  - 扫描漏洞
  - 签名验证

工具:
  - Trivy
  - Cosign (签名)
  - Notary
```

### SBOM (软件物料清单)
```bash
# 生成 SBOM
syft packages dir:. -o spdx-json > sbom.json

# 扫描 SBOM
grype sbom:sbom.json
```

## 安全门禁

```yaml
阻断条件:
  - Critical 漏洞
  - 高危依赖
  - Secret 泄露
  - 许可证违规

警告条件:
  - High 漏洞
  - 中危依赖
  - 代码质量问题
```

## 合规自动化

```yaml
检查项:
  - CIS Benchmark
  - PCI DSS
  - SOC 2
  - GDPR

工具:
  - Open Policy Agent (OPA)
  - Checkov
  - Terrascan
```

---

**安全是每个人的责任，自动化是最好的保障。**
