---
name: threat-modeling
description: 威胁建模方法论。STRIDE、PASTA、攻击树、威胁矩阵、风险评估。当用户提到威胁建模、STRIDE、PASTA、攻击树、威胁矩阵、风险评估、安全设计时使用。
---

# 🎯 威胁建模 · Threat Modeling


## 威胁建模流程

```
资产识别 → 架构分解 → 威胁枚举 → 风险评级 → 缓解措施 → 验证
    │          │           │          │          │          │
    └─ 数据流 ─┴─ 信任边界 ─┴─ STRIDE ─┴─ CVSS ─┴─ 控制 ─┴─ 测试
```

## STRIDE 方法论

### STRIDE 威胁分类

| 威胁 | 含义 | 目标 | 示例 |
|------|------|------|------|
| **S**poofing | 身份伪造 | 认证 | 伪造 JWT、会话劫持 |
| **T**ampering | 数据篡改 | 完整性 | 修改请求参数、SQL注入 |
| **R**epudiation | 否认 | 不可否认性 | 无审计日志、删除操作记录 |
| **I**nformation Disclosure | 信息泄露 | 机密性 | 敏感数据暴露、目录遍历 |
| **D**enial of Service | 拒绝服务 | 可用性 | DDoS、资源耗尽 |
| **E**levation of Privilege | 权限提升 | 授权 | 越权访问、提权漏洞 |

### STRIDE 威胁建模模板

```yaml
# threat-model.yaml
system:
  name: "用户认证系统"
  version: "1.0"
  owner: "安全团队"

assets:
  - name: "用户凭证"
    classification: "高度机密"
    storage: "数据库加密存储"

  - name: "会话令牌"
    classification: "机密"
    storage: "Redis + HttpOnly Cookie"

components:
  - name: "Web 前端"
    type: "客户端"
    trust_level: "不可信"

  - name: "API 网关"
    type: "服务端"
    trust_level: "可信边界"

  - name: "认证服务"
    type: "服务端"
    trust_level: "可信"

data_flows:
  - id: "DF-01"
    source: "Web 前端"
    destination: "API 网关"
    protocol: "HTTPS"
    data: "用户名/密码"
    trust_boundary: true

threats:
  - id: "T-001"
    category: "Spoofing"
    component: "API 网关"
    description: "攻击者伪造 JWT 令牌"
    impact: "高"
    likelihood: "中"
    risk: "高"
    mitigations:
      - "使用强签名算法 (RS256)"
      - "验证 iss/aud/exp 声明"
      - "密钥轮转策略"
    status: "已缓解"

  - id: "T-002"
    category: "Information Disclosure"
    component: "认证服务"
    description: "错误消息泄露用户存在性"
    impact: "低"
    likelihood: "高"
    risk: "中"
    mitigations:
      - "统一错误消息"
      - "限制登录尝试次数"
    status: "已缓解"
```

### STRIDE 自动化分析

```python
#!/usr/bin/env python3
"""STRIDE 威胁自动枚举"""
import yaml
from typing import List, Dict

STRIDE_RULES = {
    "Spoofing": [
        "是否验证用户身份？",
        "是否使用强认证机制？",
        "是否防护会话劫持？"
    ],
    "Tampering": [
        "数据传输是否加密？",
        "是否验证输入完整性？",
        "是否使用签名/HMAC？"
    ],
    "Repudiation": [
        "是否记录审计日志？",
        "日志是否防篡改？",
        "是否支持不可否认性？"
    ],
    "Information Disclosure": [
        "敏感数据是否加密？",
        "是否存在信息泄露点？",
        "错误消息是否安全？"
    ],
    "Denial of Service": [
        "是否有速率限制？",
        "是否防护资源耗尽？",
        "是否有熔断机制？"
    ],
    "Elevation of Privilege": [
        "是否实施最小权限？",
        "是否验证授权？",
        "是否防护提权攻击？"
    ]
}

def analyze_component(component: Dict) -> List[Dict]:
    """分析组件威胁"""
    threats = []
    trust_level = component.get("trust_level", "不可信")

    for category, questions in STRIDE_RULES.items():
        threat = {
            "component": component["name"],
            "category": category,
            "questions": questions,
            "risk_level": "高" if trust_level == "不可信" else "中"
        }
        threats.append(threat)

    return threats

def generate_report(model_file: str):
    """生成威胁报告"""
    with open(model_file) as f:
        model = yaml.safe_load(f)

    print(f"# 威胁建模报告: {model['system']['name']}\n")

    for component in model.get("components", []):
        print(f"## 组件: {component['name']}")
        threats = analyze_component(component)

        for threat in threats:
            print(f"\n### {threat['category']} (风险: {threat['risk_level']})")
            for q in threat['questions']:
                print(f"  - {q}")

if __name__ == "__main__":
    generate_report("threat-model.yaml")
```

## PASTA 方法论

### PASTA 七阶段流程

```
阶段 I   → 阶段 II  → 阶段 III → 阶段 IV → 阶段 V  → 阶段 VI → 阶段 VII
定义目标    技术范围    应用分解    威胁分析   漏洞分析   攻击建模   风险管理
   │           │           │          │          │          │          │
业务影响   架构图谱   数据流图   威胁情报   弱点枚举   攻击树    缓解策略
```

### PASTA 阶段实施

```python
#!/usr/bin/env python3
"""PASTA 威胁建模框架"""
from dataclasses import dataclass
from typing import List
from enum import Enum

class PastaStage(Enum):
    OBJECTIVES = 1      # 定义目标
    SCOPE = 2           # 技术范围
    DECOMPOSITION = 3   # 应用分解
    THREAT_ANALYSIS = 4 # 威胁分析
    VULNERABILITY = 5   # 漏洞分析
    ATTACK_MODELING = 6 # 攻击建模
    RISK_MANAGEMENT = 7 # 风险管理

@dataclass
class BusinessObjective:
    """业务目标"""
    name: str
    description: str
    security_requirements: List[str]
    compliance: List[str]

@dataclass
class TechnicalScope:
    """技术范围"""
    components: List[str]
    technologies: List[str]
    trust_boundaries: List[str]
    data_classification: dict

@dataclass
class Threat:
    """威胁"""
    id: str
    name: str
    category: str
    likelihood: str
    impact: str
    attack_vector: str

class PASTAModel:
    def __init__(self, system_name: str):
        self.system_name = system_name
        self.objectives = []
        self.scope = None
        self.threats = []
        self.vulnerabilities = []
        self.attacks = []
        self.risks = []

    def stage1_define_objectives(self, objectives: List[BusinessObjective]):
        """阶段 I: 定义业务目标"""
        self.objectives = objectives
        print(f"[Stage I] 已定义 {len(objectives)} 个业务目标")

    def stage2_define_scope(self, scope: TechnicalScope):
        """阶段 II: 定义技术范围"""
        self.scope = scope
        print(f"[Stage II] 范围包含 {len(scope.components)} 个组件")

    def stage3_decompose_application(self):
        """阶段 III: 应用分解"""
        # 生成数据流图、架构图
        print("[Stage III] 应用分解完成")

    def stage4_analyze_threats(self, threat_intel: List[Threat]):
        """阶段 IV: 威胁分析"""
        self.threats = threat_intel
        print(f"[Stage IV] 识别 {len(threat_intel)} 个威胁")

    def stage5_analyze_vulnerabilities(self):
        """阶段 V: 漏洞分析"""
        # 扫描已知漏洞
        print("[Stage V] 漏洞分析完成")

    def stage6_model_attacks(self):
        """阶段 VI: 攻击建模"""
        # 构建攻击树
        print("[Stage VI] 攻击建模完成")

    def stage7_manage_risks(self):
        """阶段 VII: 风险管理"""
        # 计算风险评分，制定缓解策略
        print("[Stage VII] 风险管理完成")

    def generate_report(self) -> str:
        """生成完整报告"""
        report = f"# PASTA 威胁建模报告: {self.system_name}\n\n"
        report += f"## 业务目标\n"
        for obj in self.objectives:
            report += f"- {obj.name}: {obj.description}\n"
        return report

# 使用示例
model = PASTAModel("电商支付系统")
model.stage1_define_objectives([
    BusinessObjective(
        name="保护支付数据",
        description="确保支付信息机密性和完整性",
        security_requirements=["加密传输", "PCI DSS合规"],
        compliance=["PCI DSS", "GDPR"]
    )
])
```

## 攻击树建模

### 攻击树结构

```
                    [窃取用户资金]
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   [盗取凭证]        [篡改交易]        [社会工程]
        │                 │                 │
    ┌───┴───┐         ┌───┴───┐         ┌───┴───┐
[钓鱼] [暴力破解]  [MITM] [SQL注入]  [钓鱼] [假冒客服]
```

### 攻击树 DSL

```yaml
# attack-tree.yaml
attack_tree:
  root:
    goal: "窃取用户资金"
    type: "OR"
    children:
      - goal: "盗取凭证"
        type: "OR"
        cost: "低"
        skill: "中"
        detection: "中"
        children:
          - goal: "钓鱼攻击"
            type: "LEAF"
            cost: "低"
            skill: "低"
            detection: "低"
            success_rate: 0.15
            mitigations:
              - "安全意识培训"
              - "邮件过滤"
              - "2FA"

          - goal: "暴力破解"
            type: "LEAF"
            cost: "低"
            skill: "低"
            detection: "高"
            success_rate: 0.05
            mitigations:
              - "账户锁定策略"
              - "验证码"
              - "速率限制"

      - goal: "篡改交易"
        type: "AND"
        cost: "高"
        skill: "高"
        detection: "高"
        children:
          - goal: "拦截通信"
            type: "LEAF"
            mitigations: ["TLS 1.3", "证书固定"]

          - goal: "绕过签名验证"
            type: "LEAF"
            mitigations: ["HMAC-SHA256", "密钥管理"]
```

### 攻击树分析工具

```python
#!/usr/bin/env python3
"""攻击树风险计算"""
import yaml
from typing import Dict, List

class AttackNode:
    def __init__(self, data: Dict):
        self.goal = data["goal"]
        self.type = data["type"]
        self.cost = data.get("cost", "未知")
        self.skill = data.get("skill", "未知")
        self.detection = data.get("detection", "未知")
        self.success_rate = data.get("success_rate", 0.0)
        self.mitigations = data.get("mitigations", [])
        self.children = [AttackNode(c) for c in data.get("children", [])]

    def calculate_risk(self) -> float:
        """计算攻击成功概率"""
        if self.type == "LEAF":
            return self.success_rate

        if self.type == "OR":
            # OR 节点：至少一个子节点成功
            prob = 0.0
            for child in self.children:
                prob = prob + child.calculate_risk() - prob * child.calculate_risk()
            return prob

        if self.type == "AND":
            # AND 节点：所有子节点都成功
            prob = 1.0
            for child in self.children:
                prob *= child.calculate_risk()
            return prob

        return 0.0

    def get_critical_paths(self, threshold: float = 0.1) -> List[str]:
        """获取高风险路径"""
        paths = []
        risk = self.calculate_risk()

        if risk >= threshold:
            path = f"{self.goal} (风险: {risk:.2%})"
            paths.append(path)

            for child in self.children:
                child_paths = child.get_critical_paths(threshold)
                paths.extend([f"  └─ {p}" for p in child_paths])

        return paths

def analyze_attack_tree(tree_file: str):
    """分析攻击树"""
    with open(tree_file) as f:
        data = yaml.safe_load(f)

    root = AttackNode(data["attack_tree"]["root"])

    print(f"攻击目标: {root.goal}")
    print(f"总体风险: {root.calculate_risk():.2%}\n")
    print("高风险路径:")
    for path in root.get_critical_paths():
        print(path)

if __name__ == "__main__":
    analyze_attack_tree("attack-tree.yaml")
```

## 威胁矩阵 (MITRE ATT&CK)

### ATT&CK 战术映射

```python
#!/usr/bin/env python3
"""MITRE ATT&CK 威胁映射"""
from typing import List, Dict

ATTACK_TACTICS = {
    "TA0001": "初始访问 (Initial Access)",
    "TA0002": "执行 (Execution)",
    "TA0003": "持久化 (Persistence)",
    "TA0004": "权限提升 (Privilege Escalation)",
    "TA0005": "防御规避 (Defense Evasion)",
    "TA0006": "凭证访问 (Credential Access)",
    "TA0007": "发现 (Discovery)",
    "TA0008": "横向移动 (Lateral Movement)",
    "TA0009": "收集 (Collection)",
    "TA0010": "渗出 (Exfiltration)",
    "TA0011": "影响 (Impact)"
}

class ThreatMapping:
    def __init__(self):
        self.mappings = []

    def add_threat(self, threat: Dict):
        """添加威胁映射"""
        self.mappings.append(threat)

    def generate_matrix(self) -> str:
        """生成威胁矩阵"""
        matrix = "# ATT&CK 威胁矩阵\n\n"

        for tactic_id, tactic_name in ATTACK_TACTICS.items():
            threats = [t for t in self.mappings if tactic_id in t.get("tactics", [])]

            if threats:
                matrix += f"## {tactic_name}\n\n"
                matrix += "| 技术 | 检测 | 缓解 |\n"
                matrix += "|------|------|------|\n"

                for threat in threats:
                    matrix += f"| {threat['technique']} | "
                    matrix += f"{threat.get('detection', 'N/A')} | "
                    matrix += f"{threat.get('mitigation', 'N/A')} |\n"

                matrix += "\n"

        return matrix

# 使用示例
mapping = ThreatMapping()
mapping.add_threat({
    "technique": "T1566.001 - 钓鱼邮件",
    "tactics": ["TA0001"],
    "detection": "邮件网关检测",
    "mitigation": "安全意识培训"
})
mapping.add_threat({
    "technique": "T1078 - 有效账户",
    "tactics": ["TA0001", "TA0003", "TA0004"],
    "detection": "异常登录检测",
    "mitigation": "MFA + 最小权限"
})

print(mapping.generate_matrix())
```

### ATT&CK Navigator 配置

```json
{
  "name": "威胁覆盖矩阵",
  "versions": {
    "attack": "14",
    "navigator": "4.9.1",
    "layer": "4.5"
  },
  "domain": "enterprise-attack",
  "description": "组织威胁覆盖情况",
  "techniques": [
    {
      "techniqueID": "T1566.001",
      "tactic": "initial-access",
      "color": "#ff6666",
      "comment": "高风险：钓鱼攻击频繁",
      "enabled": true,
      "score": 90
    },
    {
      "techniqueID": "T1078",
      "tactic": "persistence",
      "color": "#ffcc66",
      "comment": "中风险：凭证管理待加强",
      "enabled": true,
      "score": 60
    }
  ]
}
```

## 风险评估

### CVSS 评分计算

```python
#!/usr/bin/env python3
"""CVSS v3.1 评分计算器"""
from enum import Enum

class AttackVector(Enum):
    NETWORK = 0.85
    ADJACENT = 0.62
    LOCAL = 0.55
    PHYSICAL = 0.2

class AttackComplexity(Enum):
    LOW = 0.77
    HIGH = 0.44

class Impact(Enum):
    HIGH = 0.56
    LOW = 0.22
    NONE = 0.0

def calculate_cvss(av: AttackVector, ac: AttackComplexity,
                   c_impact: Impact, i_impact: Impact, a_impact: Impact) -> float:
    """计算 CVSS 基础分"""
    # 简化计算（实际 CVSS 更复杂）
    exploitability = 8.22 * av.value * ac.value
    impact_score = 1 - ((1 - c_impact.value) * (1 - i_impact.value) * (1 - a_impact.value))

    if impact_score <= 0:
        return 0.0

    base_score = min(10.0, (exploitability + impact_score * 10) * 0.6)
    return round(base_score, 1)

# 示例：远程 SQL 注入
score = calculate_cvss(
    AttackVector.NETWORK,
    AttackComplexity.LOW,
    Impact.HIGH,  # 机密性
    Impact.HIGH,  # 完整性
    Impact.HIGH   # 可用性
)
print(f"CVSS 评分: {score} (严重)")
```

### 风险矩阵

```python
#!/usr/bin/env python3
"""风险评估矩阵"""

LIKELIHOOD = {
    "极低": 1,
    "低": 2,
    "中": 3,
    "高": 4,
    "极高": 5
}

IMPACT = {
    "可忽略": 1,
    "低": 2,
    "中": 3,
    "高": 4,
    "严重": 5
}

def calculate_risk(likelihood: str, impact: str) -> tuple:
    """计算风险等级"""
    score = LIKELIHOOD[likelihood] * IMPACT[impact]

    if score >= 15:
        return (score, "严重", "立即处理")
    elif score >= 10:
        return (score, "高", "优先处理")
    elif score >= 6:
        return (score, "中", "计划处理")
    else:
        return (score, "低", "监控")

# 风险评估示例
threats = [
    {"name": "SQL 注入", "likelihood": "高", "impact": "严重"},
    {"name": "XSS", "likelihood": "中", "impact": "中"},
    {"name": "信息泄露", "likelihood": "低", "impact": "高"}
]

print("风险评估结果:\n")
for threat in threats:
    score, level, action = calculate_risk(threat["likelihood"], threat["impact"])
    print(f"{threat['name']}: {level} (评分: {score}) - {action}")
```

## 数据流图 (DFD)

### DFD 建模

```
外部实体          进程              数据存储
┌─────────┐      ╔═════════╗      ║         ║
│  用户   │ ───> ║ Web服务 ║ ───> ║ 数据库  ║
└─────────┘      ╚═════════╝      ║         ║
                      │
                      v
                 [数据流]
```

### DFD Python 生成

```python
#!/usr/bin/env python3
"""数据流图生成器"""
from dataclasses import dataclass
from typing import List

@dataclass
class Entity:
    """外部实体"""
    id: str
    name: str
    type: str  # external/process/datastore

@dataclass
class DataFlow:
    """数据流"""
    id: str
    source: str
    destination: str
    data: str
    protocol: str
    encrypted: bool

class DFDModel:
    def __init__(self):
        self.entities = []
        self.flows = []

    def add_entity(self, entity: Entity):
        self.entities.append(entity)

    def add_flow(self, flow: DataFlow):
        self.flows.append(flow)

    def identify_trust_boundaries(self) -> List[DataFlow]:
        """识别信任边界"""
        boundaries = []
        for flow in self.flows:
            src = next(e for e in self.entities if e.id == flow.source)
            dst = next(e for e in self.entities if e.id == flow.destination)

            if src.type == "external" or dst.type == "external":
                boundaries.append(flow)

        return boundaries

    def generate_threats(self) -> List[dict]:
        """基于 DFD 生成威胁"""
        threats = []
        boundaries = self.identify_trust_boundaries()

        for flow in boundaries:
            if not flow.encrypted:
                threats.append({
                    "flow": flow.id,
                    "threat": "数据传输未加密",
                    "category": "Information Disclosure",
                    "severity": "高"
                })

        return threats

# 使用示例
dfd = DFDModel()
dfd.add_entity(Entity("E1", "用户", "external"))
dfd.add_entity(Entity("P1", "Web服务", "process"))
dfd.add_entity(Entity("D1", "数据库", "datastore"))

dfd.add_flow(DataFlow("F1", "E1", "P1", "登录凭证", "HTTPS", True))
dfd.add_flow(DataFlow("F2", "P1", "D1", "SQL查询", "TCP", False))

threats = dfd.generate_threats()
for threat in threats:
    print(f"[{threat['severity']}] {threat['flow']}: {threat['threat']}")
```

## 缓解措施库

### 安全控制映射

```yaml
# security-controls.yaml
controls:
  - id: "AC-01"
    name: "访问控制策略"
    category: "访问控制"
    mitigates:
      - "Spoofing"
      - "Elevation of Privilege"
    implementation:
      - "实施 RBAC"
      - "最小权限原则"
      - "定期权限审计"

  - id: "SC-08"
    name: "传输机密性"
    category: "系统通信"
    mitigates:
      - "Information Disclosure"
      - "Tampering"
    implementation:
      - "强制 TLS 1.3"
      - "证书固定"
      - "禁用弱加密套件"

  - id: "AU-02"
    name: "审计事件"
    category: "审计与问责"
    mitigates:
      - "Repudiation"
    implementation:
      - "记录所有安全事件"
      - "集中日志管理"
      - "日志完整性保护"
```

## 威胁建模工具

| 工具 | 类型 | 特点 |
|------|------|------|
| Microsoft Threat Modeling Tool | 桌面应用 | STRIDE 自动化 |
| OWASP Threat Dragon | Web/桌面 | 开源、DFD 支持 |
| IriusRisk | 商业平台 | 自动化威胁库 |
| Threagile | CLI | 代码化威胁建模 |
| PyTM | Python 库 | 编程式建模 |

## 最佳实践

### 威胁建模检查清单

```markdown
## 前期准备
- [ ] 识别关键资产和数据
- [ ] 定义安全目标和合规要求
- [ ] 组建跨职能团队

## 建模过程
- [ ] 绘制架构图和数据流图
- [ ] 标识信任边界
- [ ] 枚举威胁（STRIDE/PASTA）
- [ ] 评估风险等级
- [ ] 制定缓解措施

## 验证与维护
- [ ] 安全测试验证
- [ ] 定期更新模型
- [ ] 跟踪缓解措施实施
- [ ] 事件后复盘更新
```

### 持续威胁建模

```python
#!/usr/bin/env python3
"""持续威胁建模集成"""
import subprocess
import json

def threat_model_as_code():
    """威胁建模即代码"""
    # 1. 从架构代码生成模型
    subprocess.run(["terraform", "graph", "-type=plan"],
                   stdout=open("arch.dot", "w"))

    # 2. 自动威胁分析
    subprocess.run(["threagile", "analyze", "-model", "threat-model.yaml"])

    # 3. 生成报告
    with open("risks.json") as f:
        risks = json.load(f)

    # 4. 质量门禁
    critical_risks = [r for r in risks if r["severity"] == "critical"]
    if critical_risks:
        print(f"发现 {len(critical_risks)} 个严重风险，阻止部署")
        exit(1)

if __name__ == "__main__":
    threat_model_as_code()
```

---
