---
name: supply-chain
description: 软件供应链安全。SBOM、依赖扫描、签名验证、SLSA框架、制品完整性。当用户提到供应链安全、SBOM、依赖扫描、Sigstore、SLSA、制品安全、软件物料清单时使用。
---

# 🔗 供应链安全 · Supply Chain Security


## 供应链威胁模型

```
源代码 → 构建 → 制品 → 分发 → 部署 → 运行
   │       │      │      │      │      │
   ├─ 投毒  ├─ 篡改 ├─ 后门 ├─ 劫持 ├─ 提权 ├─ 横向
   └─ 泄露  └─ 注入 └─ 恶意 └─ 伪造 └─ 逃逸 └─ 渗出
```

### 攻击向量

| 阶段 | 攻击方式 | 示例 |
|------|----------|------|
| 源代码 | 依赖投毒 | event-stream、ua-parser-js |
| 构建 | CI/CD 劫持 | SolarWinds、CodeCov |
| 制品 | 恶意包 | PyPI/npm 钓鱼包 |
| 分发 | 中间人攻击 | 镜像劫持 |
| 部署 | 配置篡改 | Kubernetes YAML 注入 |
| 运行 | 容器逃逸 | 特权容器、内核漏洞 |

## SBOM (软件物料清单)

### SBOM 标准对比

| 标准 | 组织 | 格式 | 特点 |
|------|------|------|------|
| SPDX | Linux Foundation | JSON/YAML/RDF | ISO 标准、许可证重点 |
| CycloneDX | OWASP | JSON/XML | 安全重点、漏洞关联 |
| SWID | ISO/IEC | XML | 软件识别标签 |

### 生成 SBOM (Syft)

```bash
# 安装 Syft
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh

# 扫描容器镜像
syft nginx:latest -o cyclonedx-json > sbom.json
syft nginx:latest -o spdx-json > sbom-spdx.json

# 扫描目录
syft dir:. -o cyclonedx-json

# 扫描 Git 仓库
syft git:https://github.com/user/repo -o json

# 多格式输出
syft nginx:latest -o table,json=sbom.json,spdx=sbom.spdx
```

### CycloneDX SBOM 结构

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "version": 1,
  "metadata": {
    "timestamp": "2026-02-09T00:00:00Z",
    "component": {
      "type": "application",
      "name": "my-app",
      "version": "1.0.0"
    }
  },
  "components": [
    {
      "type": "library",
      "name": "express",
      "version": "4.18.2",
      "purl": "pkg:npm/express@4.18.2",
      "licenses": [{"license": {"id": "MIT"}}],
      "hashes": [
        {
          "alg": "SHA-256",
          "content": "abc123..."
        }
      ],
      "externalReferences": [
        {
          "type": "vcs",
          "url": "https://github.com/expressjs/express"
        }
      ]
    }
  ],
  "dependencies": [
    {
      "ref": "pkg:npm/express@4.18.2",
      "dependsOn": [
        "pkg:npm/body-parser@1.20.1",
        "pkg:npm/cookie@0.5.0"
      ]
    }
  ]
}
```

### SBOM 生成自动化

```python
#!/usr/bin/env python3
"""SBOM 生成与分析"""
import subprocess
import json
from typing import List, Dict

class SBOMGenerator:
    def __init__(self, target: str):
        self.target = target
        self.sbom = None

    def generate(self, format: str = "cyclonedx-json") -> Dict:
        """生成 SBOM"""
        result = subprocess.run(
            ["syft", self.target, "-o", format],
            capture_output=True,
            text=True
        )
        self.sbom = json.loads(result.stdout)
        return self.sbom

    def get_components(self) -> List[Dict]:
        """提取组件列表"""
        if not self.sbom:
            self.generate()
        return self.sbom.get("components", [])

    def find_component(self, name: str) -> List[Dict]:
        """查找特定组件"""
        components = self.get_components()
        return [c for c in components if name.lower() in c["name"].lower()]

    def get_licenses(self) -> Dict[str, int]:
        """统计许可证"""
        licenses = {}
        for comp in self.get_components():
            for lic in comp.get("licenses", []):
                lic_id = lic.get("license", {}).get("id", "Unknown")
                licenses[lic_id] = licenses.get(lic_id, 0) + 1
        return licenses

    def export_report(self, output: str):
        """导出报告"""
        components = self.get_components()
        licenses = self.get_licenses()

        report = f"# SBOM 报告: {self.target}\n\n"
        report += f"## 统计\n"
        report += f"- 组件总数: {len(components)}\n"
        report += f"- 许可证类型: {len(licenses)}\n\n"
        report += f"## 许可证分布\n"
        for lic, count in sorted(licenses.items(), key=lambda x: -x[1]):
            report += f"- {lic}: {count}\n"

        with open(output, "w") as f:
            f.write(report)

# 使用示例
gen = SBOMGenerator("nginx:latest")
gen.generate()
print(f"发现 {len(gen.get_components())} 个组件")
gen.export_report("sbom-report.md")
```

## 依赖扫描

### Trivy 漏洞扫描

```bash
# 安装 Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh

# 扫描容器镜像
trivy image nginx:latest
trivy image --severity HIGH,CRITICAL nginx:latest

# 扫描文件系统
trivy fs .
trivy fs --scanners vuln,secret,misconfig .

# 扫描 SBOM
trivy sbom sbom.json

# 生成报告
trivy image nginx:latest -f json -o report.json
trivy image nginx:latest -f sarif -o report.sarif

# 集成 CI/CD
trivy image --exit-code 1 --severity CRITICAL myapp:latest
```

### Grype 依赖扫描

```bash
# 安装 Grype
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh

# 扫描镜像
grype nginx:latest

# 扫描 SBOM
grype sbom:./sbom.json

# 指定漏洞数据库
grype nginx:latest --db /path/to/db

# 输出格式
grype nginx:latest -o json
grype nginx:latest -o table
grype nginx:latest -o cyclonedx
```

### Snyk 扫描集成

```bash
# 安装 Snyk CLI
npm install -g snyk

# 认证
snyk auth

# 扫描项目
snyk test
snyk test --severity-threshold=high

# 扫描容器
snyk container test nginx:latest

# 扫描 IaC
snyk iac test terraform/

# 监控项目
snyk monitor

# 修复建议
snyk fix
```

### 依赖扫描自动化

```python
#!/usr/bin/env python3
"""依赖漏洞扫描自动化"""
import subprocess
import json
from typing import List, Dict

class VulnerabilityScanner:
    def __init__(self, target: str):
        self.target = target
        self.vulnerabilities = []

    def scan_with_trivy(self) -> List[Dict]:
        """使用 Trivy 扫描"""
        result = subprocess.run(
            ["trivy", "image", "-f", "json", self.target],
            capture_output=True,
            text=True
        )
        data = json.loads(result.stdout)

        vulns = []
        for result in data.get("Results", []):
            for vuln in result.get("Vulnerabilities", []):
                vulns.append({
                    "id": vuln["VulnerabilityID"],
                    "package": vuln["PkgName"],
                    "version": vuln["InstalledVersion"],
                    "severity": vuln["Severity"],
                    "fixed_version": vuln.get("FixedVersion", "N/A")
                })

        self.vulnerabilities = vulns
        return vulns

    def filter_by_severity(self, severity: str) -> List[Dict]:
        """按严重性过滤"""
        return [v for v in self.vulnerabilities if v["severity"] == severity]

    def get_fixable(self) -> List[Dict]:
        """获取可修复漏洞"""
        return [v for v in self.vulnerabilities if v["fixed_version"] != "N/A"]

    def generate_report(self) -> str:
        """生成报告"""
        critical = self.filter_by_severity("CRITICAL")
        high = self.filter_by_severity("HIGH")
        fixable = self.get_fixable()

        report = f"# 漏洞扫描报告: {self.target}\n\n"
        report += f"## 统计\n"
        report += f"- 严重: {len(critical)}\n"
        report += f"- 高危: {len(high)}\n"
        report += f"- 可修复: {len(fixable)}\n\n"

        if critical:
            report += f"## 严重漏洞\n"
            for vuln in critical[:10]:
                report += f"- {vuln['id']}: {vuln['package']} {vuln['version']}\n"

        return report

# 使用示例
scanner = VulnerabilityScanner("nginx:latest")
scanner.scan_with_trivy()
print(scanner.generate_report())
```

## 签名验证 (Sigstore)

### Cosign 签名

```bash
# 安装 Cosign
curl -O -L https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64
chmod +x cosign-linux-amd64
mv cosign-linux-amd64 /usr/local/bin/cosign

# 生成密钥对
cosign generate-key-pair

# 签名镜像
cosign sign --key cosign.key myregistry/myapp:v1.0

# 无密钥签名（Keyless）
cosign sign myregistry/myapp:v1.0

# 验证签名
cosign verify --key cosign.pub myregistry/myapp:v1.0

# 附加 SBOM
cosign attach sbom --sbom sbom.json myregistry/myapp:v1.0

# 附加证明
cosign attest --key cosign.key --predicate attestation.json myregistry/myapp:v1.0

# 验证证明
cosign verify-attestation --key cosign.pub myregistry/myapp:v1.0
```

### in-toto 供应链证明

```python
#!/usr/bin/env python3
"""in-toto 供应链元数据"""
from in_toto import runlib, verifylib
from in_toto.models.layout import Layout
from in_toto.models.metadata import Metablock

# 定义供应链布局
layout = Layout.read({
    "_type": "layout",
    "steps": [
        {
            "name": "build",
            "expected_materials": [["MATCH", "src/*", "WITH", "PRODUCTS", "FROM", "clone"]],
            "expected_products": [["CREATE", "app"]],
            "pubkeys": ["builder-key-id"],
            "expected_command": ["make", "build"],
            "threshold": 1
        },
        {
            "name": "test",
            "expected_materials": [["MATCH", "app", "WITH", "PRODUCTS", "FROM", "build"]],
            "expected_products": [["CREATE", "test-results.xml"]],
            "pubkeys": ["tester-key-id"],
            "expected_command": ["make", "test"],
            "threshold": 1
        }
    ],
    "inspect": [
        {
            "name": "verify-hash",
            "expected_materials": [["MATCH", "app", "WITH", "PRODUCTS", "FROM", "build"]],
            "expected_products": [["MATCH", "app", "IN", "dst"]],
            "run": ["sha256sum", "app"]
        }
    ]
})

# 记录构建步骤
def record_build_step():
    """记录构建元数据"""
    runlib.in_toto_run(
        name="build",
        material_list=["src/"],
        product_list=["app"],
        command=["make", "build"]
    )

# 验证供应链
def verify_supply_chain():
    """验证完整供应链"""
    verifylib.in_toto_verify(
        layout_path="root.layout",
        layout_key_paths=["root.pub"]
    )

if __name__ == "__main__":
    record_build_step()
```

### Sigstore Policy Controller

```yaml
# policy.yaml - Kubernetes 准入控制
apiVersion: policy.sigstore.dev/v1beta1
kind: ClusterImagePolicy
metadata:
  name: require-signed-images
spec:
  images:
    - glob: "myregistry.io/**"
  authorities:
    - keyless:
        url: https://fulcio.sigstore.dev
        identities:
          - issuer: https://github.com/login/oauth
            subject: "https://github.com/myorg/*"
    - key:
        data: |
          -----BEGIN PUBLIC KEY-----
          MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...
          -----END PUBLIC KEY-----
```

## SLSA 框架

### SLSA 等级

```
Level 0: 无保证
   │
   v
Level 1: 文档化构建过程
   │    - 构建脚本存在
   │    - 可重现构建
   │
   v
Level 2: 防篡改构建服务
   │    - 托管构建平台
   │    - 服务生成的来源
   │    - 签名的来源
   │
   v
Level 3: 额外的强化
   │    - 安全的构建平台
   │    - 不可伪造的来源
   │    - 隔离的构建
   │
   v
Level 4: 最高保证
        - 双方审查
        - 密封的构建
```

### SLSA Provenance 生成

```json
{
  "_type": "https://in-toto.io/Statement/v0.1",
  "subject": [
    {
      "name": "myapp",
      "digest": {
        "sha256": "abc123..."
      }
    }
  ],
  "predicateType": "https://slsa.dev/provenance/v0.2",
  "predicate": {
    "builder": {
      "id": "https://github.com/Attestations/GitHubActionsWorkflow@v1"
    },
    "buildType": "https://github.com/Attestations/GitHubActionsWorkflow@v1",
    "invocation": {
      "configSource": {
        "uri": "git+https://github.com/myorg/myapp@refs/heads/main",
        "digest": {
          "sha1": "def456..."
        },
        "entryPoint": ".github/workflows/build.yml"
      }
    },
    "metadata": {
      "buildStartedOn": "2026-02-09T00:00:00Z",
      "buildFinishedOn": "2026-02-09T00:10:00Z",
      "completeness": {
        "parameters": true,
        "environment": true,
        "materials": true
      },
      "reproducible": false
    },
    "materials": [
      {
        "uri": "git+https://github.com/myorg/myapp@refs/heads/main",
        "digest": {
          "sha1": "def456..."
        }
      }
    ]
  }
}
```

### GitHub Actions SLSA

```yaml
# .github/workflows/slsa.yml
name: SLSA Build
on: [push]

permissions:
  id-token: write
  contents: read
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build
        run: make build

      - name: Generate SLSA Provenance
        uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v1.9.0
        with:
          base64-subjects: "${{ steps.hash.outputs.hashes }}"
          upload-assets: true

      - name: Sign with Cosign
        run: |
          cosign sign --yes \
            -a "repo=${{ github.repository }}" \
            -a "workflow=${{ github.workflow }}" \
            ghcr.io/${{ github.repository }}:${{ github.sha }}
```

### SLSA 验证工具

```bash
# 安装 slsa-verifier
go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@latest

# 验证 Provenance
slsa-verifier verify-artifact \
  --provenance-path provenance.json \
  --source-uri github.com/myorg/myapp \
  myapp

# 验证容器镜像
slsa-verifier verify-image \
  --provenance-path provenance.json \
  --source-uri github.com/myorg/myapp \
  ghcr.io/myorg/myapp:v1.0
```

## 依赖锁定

### Package Lock 文件

```bash
# npm
npm ci  # 使用 package-lock.json 精确安装

# yarn
yarn install --frozen-lockfile

# pip
pip install -r requirements.txt --require-hashes

# go
go mod verify
go mod download

# cargo
cargo build --locked
```

### 生成哈希锁定

```python
#!/usr/bin/env python3
"""生成依赖哈希锁定文件"""
import hashlib
import json
import subprocess
from typing import Dict, List

def generate_pip_hashes(requirements: str) -> Dict[str, str]:
    """为 pip 依赖生成哈希"""
    result = subprocess.run(
        ["pip", "hash", "-r", requirements],
        capture_output=True,
        text=True
    )

    hashes = {}
    for line in result.stdout.split("\n"):
        if "==" in line and "--hash=" in line:
            pkg = line.split("==")[0]
            hash_val = line.split("--hash=")[1].split()[0]
            hashes[pkg] = hash_val

    return hashes

def verify_integrity(package: str, expected_hash: str) -> bool:
    """验证包完整性"""
    result = subprocess.run(
        ["pip", "download", "--no-deps", package],
        capture_output=True
    )

    # 计算实际哈希
    actual_hash = hashlib.sha256(result.stdout).hexdigest()
    return actual_hash == expected_hash

# 生成锁定文件
hashes = generate_pip_hashes("requirements.txt")
with open("requirements.lock", "w") as f:
    json.dump(hashes, f, indent=2)
```

## 私有依赖仓库

### Nexus Repository 配置

```bash
# Docker 配置
docker login nexus.company.com:8082

# npm 配置
npm config set registry https://nexus.company.com/repository/npm-group/

# pip 配置
pip config set global.index-url https://nexus.company.com/repository/pypi-group/simple

# Maven 配置
# ~/.m2/settings.xml
```

```xml
<settings>
  <mirrors>
    <mirror>
      <id>nexus</id>
      <mirrorOf>*</mirrorOf>
      <url>https://nexus.company.com/repository/maven-public/</url>
    </mirror>
  </mirrors>
  <servers>
    <server>
      <id>nexus</id>
      <username>${env.NEXUS_USER}</username>
      <password>${env.NEXUS_PASS}</password>
    </server>
  </servers>
</settings>
```

### Artifactory 扫描集成

```yaml
# .jfrog-pipelines.yml
pipelines:
  - name: scan_artifacts
    steps:
      - name: xray_scan
        type: XrayScan
        configuration:
          inputResources:
            - name: docker_image
          failOnScan: true
          scanThreshold: HIGH
```

## 供应链策略

### OPA 供应链策略

```rego
# supply-chain-policy.rego
package supply_chain

# 拒绝未签名镜像
deny[msg] {
    input.kind == "Pod"
    image := input.spec.containers[_].image
    not is_signed(image)
    msg := sprintf("镜像未签名: %v", [image])
}

# 拒绝高危漏洞
deny[msg] {
    vuln := input.vulnerabilities[_]
    vuln.severity == "CRITICAL"
    not has_exception(vuln.id)
    msg := sprintf("发现严重漏洞: %v in %v", [vuln.id, vuln.package])
}

# 要求 SBOM
deny[msg] {
    input.kind == "Deployment"
    not has_sbom(input.metadata.annotations)
    msg := "缺少 SBOM 注解"
}

is_signed(image) {
    # 检查 Cosign 签名
    signatures := data.cosign.signatures[image]
    count(signatures) > 0
}

has_sbom(annotations) {
    annotations["sbom.url"]
}

has_exception(vuln_id) {
    data.exceptions[vuln_id]
}
```

### Kyverno 供应链策略

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-supply-chain
spec:
  validationFailureAction: enforce
  rules:
    - name: verify-image-signature
      match:
        any:
          - resources:
              kinds:
                - Pod
      verifyImages:
        - imageReferences:
            - "*"
          attestors:
            - count: 1
              entries:
                - keys:
                    publicKeys: |-
                      -----BEGIN PUBLIC KEY-----
                      ...
                      -----END PUBLIC KEY-----

    - name: require-sbom
      match:
        any:
          - resources:
              kinds:
                - Deployment
      validate:
        message: "必须提供 SBOM"
        pattern:
          metadata:
            annotations:
              sbom.url: "?*"

    - name: block-critical-vulns
      match:
        any:
          - resources:
              kinds:
                - Pod
      validate:
        message: "镜像包含严重漏洞"
        deny:
          conditions:
            any:
              - key: "{{ images.*.vulnerabilities[?severity=='CRITICAL'] | length(@) }}"
                operator: GreaterThan
                value: 0
```

## CI/CD 集成

### GitLab CI 供应链安全

```yaml
# .gitlab-ci.yml
stages:
  - build
  - scan
  - sign
  - deploy

variables:
  IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

build:
  stage: build
  script:
    - docker build -t $IMAGE .
    - docker push $IMAGE

sbom:
  stage: scan
  script:
    - syft $IMAGE -o cyclonedx-json > sbom.json
    - cosign attach sbom --sbom sbom.json $IMAGE
  artifacts:
    paths:
      - sbom.json

vulnerability_scan:
  stage: scan
  script:
    - trivy image --exit-code 1 --severity CRITICAL $IMAGE
  allow_failure: false

sign:
  stage: sign
  script:
    - cosign sign --key $COSIGN_KEY $IMAGE
  only:
    - main

deploy:
  stage: deploy
  script:
    - cosign verify --key $COSIGN_PUB $IMAGE
    - kubectl set image deployment/myapp app=$IMAGE
  only:
    - main
```

### GitHub Actions 完整流程

```yaml
name: Secure Supply Chain
on: [push]

permissions:
  contents: read
  packages: write
  id-token: write

jobs:
  build-and-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build
        run: docker build -t myapp:${{ github.sha }} .

      - name: Generate SBOM
        run: |
          syft myapp:${{ github.sha }} -o cyclonedx-json > sbom.json

      - name: Scan Vulnerabilities
        run: |
          trivy image --exit-code 1 --severity CRITICAL myapp:${{ github.sha }}

      - name: Sign Image
        run: |
          cosign sign --yes myapp:${{ github.sha }}

      - name: Attach SBOM
        run: |
          cosign attach sbom --sbom sbom.json myapp:${{ github.sha }}

      - name: Generate Provenance
        uses: slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@v1.9.0
```

## 工具清单

| 工具 | 类型 | 用途 |
|------|------|------|
| Syft | SBOM | 生成软件物料清单 |
| Trivy | 扫描 | 漏洞/配置/密钥扫描 |
| Grype | 扫描 | 依赖漏洞扫描 |
| Snyk | 商业 | 全方位安全扫描 |
| Cosign | 签名 | 容器签名验证 |
| in-toto | 框架 | 供应链完整性 |
| SLSA | 框架 | 供应链等级标准 |
| Sigstore | 平台 | 无密钥签名基础设施 |

## 最佳实践

### 供应链安全检查清单

```markdown
## 源代码阶段
- [ ] 启用分支保护
- [ ] 要求代码审查
- [ ] 使用依赖锁定文件
- [ ] 定期更新依赖
- [ ] 扫描密钥泄露

## 构建阶段
- [ ] 使用托管 CI/CD
- [ ] 隔离构建环境
- [ ] 生成 SBOM
- [ ] 记录构建来源
- [ ] 签名制品

## 制品阶段
- [ ] 扫描漏洞
- [ ] 验证签名
- [ ] 存储在私有仓库
- [ ] 实施访问控制
- [ ] 保留审计日志

## 部署阶段
- [ ] 验证签名和来源
- [ ] 检查 SBOM
- [ ] 准入控制策略
- [ ] 运行时监控
- [ ] 事件响应计划
```

---
