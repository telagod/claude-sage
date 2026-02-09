---
name: gitops
description: GitOps 持续部署。ArgoCD、Flux、声明式部署、自动同步、多环境管理。当用户提到 GitOps、ArgoCD、Flux、声明式部署、自动同步、Git 为真相源时使用。
---

# 🔄 持续部署 · GitOps

## GitOps 核心原则

```
Git 仓库 (唯一真相源)
    │
    ├─ 声明式配置 (Declarative)
    ├─ 版本控制 (Versioned)
    ├─ 自动同步 (Automated)
    └─ 持续协调 (Reconciliation)
         │
         ▼
    Kubernetes 集群
```

### GitOps 工作流
```
开发者 → Git Push → CI 构建镜像 → 更新 Git 配置 → GitOps 控制器检测变更 → 自动部署到集群
                                                              │
                                                              └─ 持续监控 → 自动修复漂移
```

## ArgoCD

### 安装 ArgoCD
```bash
# 创建命名空间
kubectl create namespace argocd

# 安装 ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 暴露 UI (LoadBalancer)
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'

# 或使用 Port Forward
kubectl port-forward svc/argocd-server -n argocd 8080:443

# 获取初始密码
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# 登录 CLI
argocd login localhost:8080
argocd account update-password
```

### Application 定义
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default

  # Git 仓库配置
  source:
    repoURL: https://github.com/example/myapp-config.git
    targetRevision: main
    path: k8s/overlays/production

    # Helm 配置
    helm:
      valueFiles:
        - values-prod.yaml
      parameters:
        - name: image.tag
          value: v1.2.3

    # Kustomize 配置
    kustomize:
      images:
        - myapp=registry.example.com/myapp:v1.2.3

  # 目标集群
  destination:
    server: https://kubernetes.default.svc
    namespace: production

  # 同步策略
  syncPolicy:
    automated:
      prune: true        # 自动删除不在 Git 中的资源
      selfHeal: true     # 自动修复漂移
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

  # 忽略差异
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas  # 忽略 HPA 修改的副本数
```

### ApplicationSet (多环境)
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: myapp-all-envs
  namespace: argocd
spec:
  generators:
    # Git 目录生成器
    - git:
        repoURL: https://github.com/example/myapp-config.git
        revision: main
        directories:
          - path: k8s/overlays/*

  template:
    metadata:
      name: 'myapp-{{path.basename}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/example/myapp-config.git
        targetRevision: main
        path: '{{path}}'
      destination:
        server: https://kubernetes.default.svc
        namespace: '{{path.basename}}'
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
```

### 多集群管理
```bash
# 添加集群
argocd cluster add prod-cluster --name production

# 列出集群
argocd cluster list

# Application 指向不同集群
```

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-prod
spec:
  destination:
    name: production  # 使用集群名称
    namespace: production
```

### ArgoCD CLI 命令
```bash
# 创建应用
argocd app create myapp \
  --repo https://github.com/example/myapp-config.git \
  --path k8s/overlays/production \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace production \
  --sync-policy automated

# 查看应用状态
argocd app get myapp

# 同步应用
argocd app sync myapp

# 查看差异
argocd app diff myapp

# 回滚
argocd app rollback myapp 1

# 查看历史
argocd app history myapp

# 删除应用
argocd app delete myapp
```

### ArgoCD Notifications
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-notifications-cm
  namespace: argocd
data:
  service.slack: |
    token: $slack-token

  template.app-deployed: |
    message: |
      Application {{.app.metadata.name}} is now running new version.
    slack:
      attachments: |
        [{
          "title": "{{ .app.metadata.name}}",
          "title_link":"{{.context.argocdUrl}}/applications/{{.app.metadata.name}}",
          "color": "#18be52",
          "fields": [
            {
              "title": "Sync Status",
              "value": "{{.app.status.sync.status}}",
              "short": true
            },
            {
              "title": "Repository",
              "value": "{{.app.spec.source.repoURL}}",
              "short": true
            }
          ]
        }]

  trigger.on-deployed: |
    - when: app.status.operationState.phase in ['Succeeded']
      send: [app-deployed]

---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  annotations:
    notifications.argoproj.io/subscribe.on-deployed.slack: my-channel
```

## Flux

### 安装 Flux
```bash
# 安装 Flux CLI
curl -s https://fluxcd.io/install.sh | sudo bash

# 检查集群兼容性
flux check --pre

# Bootstrap Flux (GitHub)
export GITHUB_TOKEN=<your-token>
flux bootstrap github \
  --owner=example \
  --repository=fleet-infra \
  --branch=main \
  --path=clusters/production \
  --personal

# Bootstrap Flux (GitLab)
flux bootstrap gitlab \
  --owner=example \
  --repository=fleet-infra \
  --branch=main \
  --path=clusters/production \
  --token-auth
```

### GitRepository
```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/example/myapp-config
  ref:
    branch: main
  secretRef:
    name: git-credentials
  ignore: |
    # exclude all
    /*
    # include deploy dir
    !/k8s/
```

### Kustomization
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 5m
  path: ./k8s/overlays/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: myapp
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: myapp
      namespace: production
  timeout: 2m
  wait: true
  postBuild:
    substitute:
      CLUSTER_NAME: production
      REGION: us-west-2
    substituteFrom:
      - kind: ConfigMap
        name: cluster-vars
```

### HelmRepository
```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: HelmRepository
metadata:
  name: bitnami
  namespace: flux-system
spec:
  interval: 1h
  url: https://charts.bitnami.com/bitnami
```

### HelmRelease
```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: myapp
  namespace: production
spec:
  interval: 5m
  chart:
    spec:
      chart: myapp
      version: '1.x'
      sourceRef:
        kind: HelmRepository
        name: myapp-charts
        namespace: flux-system
  values:
    replicaCount: 3
    image:
      tag: v1.2.3
  valuesFrom:
    - kind: ConfigMap
      name: myapp-values
  install:
    remediation:
      retries: 3
  upgrade:
    remediation:
      retries: 3
      remediateLastFailure: true
    cleanupOnFail: true
  rollback:
    cleanupOnFail: true
  test:
    enable: true
```

### ImageRepository & ImagePolicy
```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageRepository
metadata:
  name: myapp
  namespace: flux-system
spec:
  image: registry.example.com/myapp
  interval: 1m
  secretRef:
    name: registry-credentials

---
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata:
  name: myapp
  namespace: flux-system
spec:
  imageRepositoryRef:
    name: myapp
  policy:
    semver:
      range: 1.x.x
  filterTags:
    pattern: '^v[0-9]+\.[0-9]+\.[0-9]+$'
    extract: '$1'

---
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImageUpdateAutomation
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 1m
  sourceRef:
    kind: GitRepository
    name: myapp
  git:
    checkout:
      ref:
        branch: main
    commit:
      author:
        email: fluxcdbot@example.com
        name: fluxcdbot
      messageTemplate: |
        Update image to {{range .Updated.Images}}{{println .}}{{end}}
    push:
      branch: main
  update:
    path: ./k8s/overlays/production
    strategy: Setters
```

### Flux CLI 命令
```bash
# 查看所有资源
flux get all

# 查看 GitRepository
flux get sources git

# 查看 Kustomization
flux get kustomizations

# 查看 HelmRelease
flux get helmreleases

# 手动同步
flux reconcile source git myapp
flux reconcile kustomization myapp

# 暂停/恢复
flux suspend kustomization myapp
flux resume kustomization myapp

# 导出配置
flux export source git myapp > myapp-source.yaml

# 卸载 Flux
flux uninstall
```

## 多环境管理

### 目录结构
```
fleet-infra/
├── clusters/
│   ├── dev/
│   │   ├── flux-system/
│   │   └── apps.yaml
│   ├── staging/
│   │   ├── flux-system/
│   │   └── apps.yaml
│   └── production/
│       ├── flux-system/
│       └── apps.yaml
├── infrastructure/
│   ├── base/
│   │   ├── ingress-nginx/
│   │   ├── cert-manager/
│   │   └── external-secrets/
│   └── overlays/
│       ├── dev/
│       ├── staging/
│       └── production/
└── apps/
    ├── base/
    │   └── myapp/
    │       ├── kustomization.yaml
    │       ├── deployment.yaml
    │       └── service.yaml
    └── overlays/
        ├── dev/
        │   ├── kustomization.yaml
        │   └── patch.yaml
        ├── staging/
        └── production/
```

### 环境配置 (ArgoCD)
```yaml
# clusters/production/apps.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-prod
  namespace: argocd
spec:
  project: production
  source:
    repoURL: https://github.com/example/myapp-config.git
    targetRevision: main
    path: apps/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### 环境配置 (Flux)
```yaml
# clusters/production/apps.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 5m
  path: ./apps/overlays/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: fleet-infra
```

## 渐进式交付

### ArgoCD Rollouts
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp
spec:
  replicas: 10
  strategy:
    canary:
      steps:
      - setWeight: 10
      - pause: {duration: 1m}
      - setWeight: 20
      - pause: {duration: 1m}
      - setWeight: 50
      - pause: {duration: 2m}
      - setWeight: 80
      - pause: {duration: 2m}
      canaryService: myapp-canary
      stableService: myapp-stable
      trafficRouting:
        istio:
          virtualService:
            name: myapp
            routes:
            - primary
      analysis:
        templates:
        - templateName: success-rate
        startingStep: 2
        args:
        - name: service-name
          value: myapp-canary
  revisionHistoryLimit: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:v2
```

### AnalysisTemplate
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
  - name: service-name
  metrics:
  - name: success-rate
    interval: 1m
    successCondition: result >= 0.95
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(
            http_requests_total{service="{{args.service-name}}",status=~"2.."}[1m]
          )) /
          sum(rate(
            http_requests_total{service="{{args.service-name}}"}[1m]
          ))
```

## 密钥管理

### Sealed Secrets
```bash
# 安装 Sealed Secrets
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.18.0/controller.yaml

# 安装 kubeseal CLI
wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.18.0/kubeseal-linux-amd64
sudo install -m 755 kubeseal-linux-amd64 /usr/local/bin/kubeseal

# 创建 Sealed Secret
kubectl create secret generic myapp-secrets \
  --from-literal=db-password=supersecret \
  --dry-run=client -o yaml | \
  kubeseal -o yaml > myapp-sealed-secret.yaml

# 提交到 Git
git add myapp-sealed-secret.yaml
git commit -m "Add sealed secret"
```

```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: myapp-secrets
  namespace: production
spec:
  encryptedData:
    db-password: AgBy3i4OJSWK+PiTySYZZA9rO43cGDEq...
  template:
    metadata:
      name: myapp-secrets
      namespace: production
    type: Opaque
```

### External Secrets Operator
```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: production
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-west-2
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: myapp-secrets
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: myapp-secrets
    creationPolicy: Owner
  data:
  - secretKey: db-password
    remoteRef:
      key: production/myapp/db-password
  - secretKey: api-key
    remoteRef:
      key: production/myapp/api-key
```

## 最佳实践

| 实践 | 说明 |
|------|------|
| Git 为唯一真相源 | 所有配置变更必须通过 Git |
| 分支策略 | main 对应生产，develop 对应开发 |
| 环境隔离 | 不同环境使用不同目录/分支 |
| 自动同步 + 自愈 | 生产环境启用 automated + selfHeal |
| 密钥加密 | 使用 Sealed Secrets 或 External Secrets |
| 渐进式交付 | 使用 Rollouts 实现金丝雀部署 |
| 监控告警 | 集成 Prometheus + Grafana |
| 审计日志 | 记录所有部署变更 |
| 回滚策略 | 保留历史版本，快速回滚 |
| 多集群管理 | 使用 ApplicationSet 统一管理 |

## ArgoCD vs Flux 对比

| 特性 | ArgoCD | Flux |
|------|--------|------|
| UI | ✅ 功能强大的 Web UI | ❌ 无 UI (可用 Weave GitOps) |
| 多租户 | ✅ Projects + RBAC | ⚠️ 需额外配置 |
| 多集群 | ✅ 原生支持 | ✅ 原生支持 |
| Helm 支持 | ✅ 完整支持 | ✅ 完整支持 |
| Kustomize 支持 | ✅ 完整支持 | ✅ 完整支持 |
| 镜像自动更新 | ⚠️ 需 Image Updater | ✅ 原生支持 |
| 渐进式交付 | ✅ Argo Rollouts | ✅ Flagger |
| 通知 | ✅ 内置 | ✅ 内置 |
| 学习曲线 | 中等 | 较陡 |
| CNCF 状态 | Graduated | Graduated |

## 工具清单

| 工具 | 用途 |
|------|------|
| ArgoCD | GitOps 持续部署 |
| Flux | GitOps 持续部署 |
| Argo Rollouts | 渐进式交付 |
| Flagger | 自动金丝雀部署 |
| Sealed Secrets | 密钥加密 |
| External Secrets | 外部密钥同步 |
| Kustomize | 配置管理 |
| Helm | 包管理 |
