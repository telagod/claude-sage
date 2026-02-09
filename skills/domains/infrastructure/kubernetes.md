---
name: kubernetes
description: Kubernetes 容器编排。Helm Chart 开发、Kustomize 配置管理、Operator 模式、CRD 自定义资源、部署策略。当用户提到 K8s、Helm、Kustomize、Operator、CRD、滚动更新、金丝雀部署时使用。
---

# 🎯 容器编排 · Kubernetes

## Helm Chart 开发

### Chart 标准结构
```
mychart/
├── Chart.yaml          # Chart 元数据
├── values.yaml         # 默认配置
├── templates/          # 模板目录
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── _helpers.tpl   # 模板函数
│   └── NOTES.txt      # 安装提示
├── charts/            # 依赖 Chart
└── .helmignore        # 忽略文件
```

### Chart.yaml
```yaml
apiVersion: v2
name: myapp
description: A Helm chart for MyApp
type: application
version: 1.0.0
appVersion: "2.3.1"

dependencies:
  - name: postgresql
    version: 12.1.0
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
  - name: redis
    version: 17.3.0
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
```

### values.yaml 设计
```yaml
# 镜像配置
image:
  repository: myapp
  tag: "1.0.0"
  pullPolicy: IfNotPresent

# 副本数
replicaCount: 3

# 资源限制
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

# 自动扩缩容
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80

# 服务配置
service:
  type: ClusterIP
  port: 80
  targetPort: 8080

# Ingress 配置
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: myapp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: myapp-tls
      hosts:
        - myapp.example.com

# 健康检查
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5

# 环境变量
env:
  - name: LOG_LEVEL
    value: info
  - name: DB_HOST
    value: postgresql

# 密钥引用
envFrom:
  - secretRef:
      name: myapp-secrets
  - configMapRef:
      name: myapp-config

# 持久化存储
persistence:
  enabled: true
  storageClass: "gp3"
  size: 10Gi
  accessMode: ReadWriteOnce

# 依赖服务
postgresql:
  enabled: true
  auth:
    username: myapp
    database: myapp

redis:
  enabled: true
  architecture: standalone
```

### Deployment 模板
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
      labels:
        {{- include "myapp.selectorLabels" . | nindent 8 }}
    spec:
      serviceAccountName: {{ include "myapp.serviceAccountName" . }}
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: {{ .Values.service.targetPort }}
          protocol: TCP
        {{- if .Values.livenessProbe }}
        livenessProbe:
          {{- toYaml .Values.livenessProbe | nindent 10 }}
        {{- end }}
        {{- if .Values.readinessProbe }}
        readinessProbe:
          {{- toYaml .Values.readinessProbe | nindent 10 }}
        {{- end }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
        {{- if .Values.env }}
        env:
          {{- toYaml .Values.env | nindent 10 }}
        {{- end }}
        {{- if .Values.envFrom }}
        envFrom:
          {{- toYaml .Values.envFrom | nindent 10 }}
        {{- end }}
        {{- if .Values.persistence.enabled }}
        volumeMounts:
        - name: data
          mountPath: /data
        {{- end }}
      {{- if .Values.persistence.enabled }}
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: {{ include "myapp.fullname" . }}
      {{- end }}
```

### _helpers.tpl 模板函数
```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "myapp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "myapp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "myapp.labels" -}}
helm.sh/chart: {{ include "myapp.chart" . }}
{{ include "myapp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "myapp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "myapp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

### Helm 命令
```bash
# 创建 Chart
helm create myapp

# 验证模板
helm lint myapp/
helm template myapp myapp/ --debug

# 安装
helm install myapp myapp/ -n production --create-namespace

# 使用自定义 values
helm install myapp myapp/ -f values-prod.yaml

# 升级
helm upgrade myapp myapp/ --reuse-values

# 回滚
helm rollback myapp 1

# 查看历史
helm history myapp

# 卸载
helm uninstall myapp

# 打包
helm package myapp/

# 推送到 OCI Registry
helm push myapp-1.0.0.tgz oci://registry.example.com/charts
```

## Kustomize 配置管理

### 目录结构
```
kustomize/
├── base/                    # 基础配置
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
└── overlays/                # 环境差异
    ├── dev/
    │   ├── kustomization.yaml
    │   └── patch-replicas.yaml
    ├── staging/
    │   ├── kustomization.yaml
    │   └── patch-resources.yaml
    └── production/
        ├── kustomization.yaml
        ├── patch-replicas.yaml
        └── patch-hpa.yaml
```

### base/kustomization.yaml
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - deployment.yaml
  - service.yaml
  - configmap.yaml

commonLabels:
  app: myapp
  managed-by: kustomize

commonAnnotations:
  version: "1.0.0"

images:
  - name: myapp
    newName: registry.example.com/myapp
    newTag: latest

configMapGenerator:
  - name: myapp-config
    literals:
      - LOG_LEVEL=info
      - MAX_CONNECTIONS=100

secretGenerator:
  - name: myapp-secrets
    literals:
      - DB_PASSWORD=changeme
    type: Opaque
```

### overlays/production/kustomization.yaml
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: production

bases:
  - ../../base

patchesStrategicMerge:
  - patch-replicas.yaml

patchesJson6902:
  - target:
      group: apps
      version: v1
      kind: Deployment
      name: myapp
    path: patch-resources.json

images:
  - name: myapp
    newTag: v1.2.3

replicas:
  - name: myapp
    count: 5

configMapGenerator:
  - name: myapp-config
    behavior: merge
    literals:
      - LOG_LEVEL=warn
      - MAX_CONNECTIONS=500

resources:
  - hpa.yaml
  - pdb.yaml
```

### patch-replicas.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 5
  template:
    spec:
      containers:
      - name: myapp
        resources:
          limits:
            cpu: 2000m
            memory: 2Gi
          requests:
            cpu: 1000m
            memory: 1Gi
```

### patch-resources.json
```json
[
  {
    "op": "replace",
    "path": "/spec/template/spec/containers/0/resources/limits/cpu",
    "value": "2000m"
  },
  {
    "op": "add",
    "path": "/spec/template/spec/containers/0/env/-",
    "value": {
      "name": "ENVIRONMENT",
      "value": "production"
    }
  }
]
```

### Kustomize 命令
```bash
# 查看生成的 YAML
kustomize build overlays/production

# 应用配置
kubectl apply -k overlays/production

# 查看差异
kubectl diff -k overlays/production

# 删除资源
kubectl delete -k overlays/production
```

## Operator 模式

### CRD 定义
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: myapps.example.com
spec:
  group: example.com
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                replicas:
                  type: integer
                  minimum: 1
                  maximum: 10
                version:
                  type: string
                  pattern: '^v[0-9]+\.[0-9]+\.[0-9]+$'
                database:
                  type: object
                  properties:
                    enabled:
                      type: boolean
                    size:
                      type: string
                      enum: [small, medium, large]
              required:
                - replicas
                - version
            status:
              type: object
              properties:
                phase:
                  type: string
                  enum: [Pending, Running, Failed]
                conditions:
                  type: array
                  items:
                    type: object
                    properties:
                      type:
                        type: string
                      status:
                        type: string
                      lastTransitionTime:
                        type: string
                        format: date-time
      subresources:
        status: {}
        scale:
          specReplicasPath: .spec.replicas
          statusReplicasPath: .status.replicas
  scope: Namespaced
  names:
    plural: myapps
    singular: myapp
    kind: MyApp
    shortNames:
      - ma
```

### 自定义资源实例
```yaml
apiVersion: example.com/v1
kind: MyApp
metadata:
  name: myapp-sample
  namespace: default
spec:
  replicas: 3
  version: v1.2.3
  database:
    enabled: true
    size: medium
```

### Operator Controller (Go)
```go
package controllers

import (
    "context"
    appsv1 "k8s.io/api/apps/v1"
    corev1 "k8s.io/api/core/v1"
    "k8s.io/apimachinery/pkg/api/errors"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/apimachinery/pkg/runtime"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"

    examplev1 "example.com/myapp-operator/api/v1"
)

type MyAppReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

// +kubebuilder:rbac:groups=example.com,resources=myapps,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=example.com,resources=myapps/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update;patch;delete

func (r *MyAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    // 获取 MyApp 实例
    myapp := &examplev1.MyApp{}
    if err := r.Get(ctx, req.NamespacedName, myapp); err != nil {
        if errors.IsNotFound(err) {
            return ctrl.Result{}, nil
        }
        return ctrl.Result{}, err
    }

    // 构建期望的 Deployment
    deployment := r.deploymentForMyApp(myapp)

    // 检查 Deployment 是否存在
    found := &appsv1.Deployment{}
    err := r.Get(ctx, client.ObjectKeyFromObject(deployment), found)
    if err != nil && errors.IsNotFound(err) {
        // 创建 Deployment
        if err := r.Create(ctx, deployment); err != nil {
            return ctrl.Result{}, err
        }
        return ctrl.Result{Requeue: true}, nil
    } else if err != nil {
        return ctrl.Result{}, err
    }

    // 更新 Deployment
    if found.Spec.Replicas != myapp.Spec.Replicas {
        found.Spec.Replicas = myapp.Spec.Replicas
        if err := r.Update(ctx, found); err != nil {
            return ctrl.Result{}, err
        }
    }

    // 更新状态
    myapp.Status.Phase = "Running"
    myapp.Status.Replicas = found.Status.ReadyReplicas
    if err := r.Status().Update(ctx, myapp); err != nil {
        return ctrl.Result{}, err
    }

    return ctrl.Result{}, nil
}

func (r *MyAppReconciler) deploymentForMyApp(m *examplev1.MyApp) *appsv1.Deployment {
    labels := map[string]string{
        "app": m.Name,
    }

    return &appsv1.Deployment{
        ObjectMeta: metav1.ObjectMeta{
            Name:      m.Name,
            Namespace: m.Namespace,
            OwnerReferences: []metav1.OwnerReference{
                *metav1.NewControllerRef(m, examplev1.GroupVersion.WithKind("MyApp")),
            },
        },
        Spec: appsv1.DeploymentSpec{
            Replicas: m.Spec.Replicas,
            Selector: &metav1.LabelSelector{
                MatchLabels: labels,
            },
            Template: corev1.PodTemplateSpec{
                ObjectMeta: metav1.ObjectMeta{
                    Labels: labels,
                },
                Spec: corev1.PodSpec{
                    Containers: []corev1.Container{{
                        Name:  "myapp",
                        Image: "myapp:" + m.Spec.Version,
                        Ports: []corev1.ContainerPort{{
                            ContainerPort: 8080,
                        }},
                    }},
                },
            },
        },
    }
}

func (r *MyAppReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&examplev1.MyApp{}).
        Owns(&appsv1.Deployment{}).
        Complete(r)
}
```

### Operator 初始化
```bash
# 使用 Operator SDK
operator-sdk init --domain example.com --repo example.com/myapp-operator

# 创建 API
operator-sdk create api --group example --version v1 --kind MyApp --resource --controller

# 生成 CRD
make manifests

# 安装 CRD
make install

# 运行 Operator
make run

# 构建镜像
make docker-build docker-push IMG=myapp-operator:v1.0.0

# 部署
make deploy IMG=myapp-operator:v1.0.0
```

## 部署策略

### 滚动更新 (Rolling Update)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2          # 最多超出期望副本数
      maxUnavailable: 1    # 最多不可用副本数
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:v2
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 蓝绿部署 (Blue-Green)
```yaml
# Blue (当前版本)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-blue
  labels:
    version: blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: myapp
        image: myapp:v1

---
# Green (新版本)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-green
  labels:
    version: green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: myapp
        image: myapp:v2

---
# Service 切换
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
    version: blue  # 切换到 green 实现蓝绿部署
  ports:
  - port: 80
    targetPort: 8080
```

### 金丝雀部署 (Canary)
```yaml
# 稳定版本
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: myapp
      track: stable
  template:
    metadata:
      labels:
        app: myapp
        track: stable
    spec:
      containers:
      - name: myapp
        image: myapp:v1

---
# 金丝雀版本 (10% 流量)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
      track: canary
  template:
    metadata:
      labels:
        app: myapp
        track: canary
    spec:
      containers:
      - name: myapp
        image: myapp:v2

---
# Service 同时指向两个版本
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp  # 匹配 stable 和 canary
  ports:
  - port: 80
    targetPort: 8080
```

### Flagger 自动金丝雀
```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: myapp
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  service:
    port: 80
    targetPort: 8080
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m
    webhooks:
    - name: load-test
      url: http://flagger-loadtester/
      timeout: 5s
      metadata:
        cmd: "hey -z 1m -q 10 -c 2 http://myapp-canary/"
```

## HPA 自动扩缩容

### 基于 CPU/内存
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 4
        periodSeconds: 30
      selectPolicy: Max
```

### 基于自定义指标
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa-custom
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
  - type: External
    external:
      metric:
        name: queue_messages_ready
        selector:
          matchLabels:
            queue: myapp-queue
      target:
        type: AverageValue
        averageValue: "30"
```

## PDB 防止中断

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  minAvailable: 2  # 或 maxUnavailable: 1
  selector:
    matchLabels:
      app: myapp
```

## 资源配额与限制

### ResourceQuota
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: production
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    limits.cpu: "200"
    limits.memory: 400Gi
    persistentvolumeclaims: "10"
    requests.storage: 500Gi
```

### LimitRange
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: limit-range
  namespace: production
spec:
  limits:
  - max:
      cpu: "4"
      memory: 8Gi
    min:
      cpu: 100m
      memory: 128Mi
    default:
      cpu: 500m
      memory: 512Mi
    defaultRequest:
      cpu: 200m
      memory: 256Mi
    type: Container
  - max:
      storage: 10Gi
    min:
      storage: 1Gi
    type: PersistentVolumeClaim
```

## 最佳实践

| 实践 | 说明 |
|------|------|
| 使用 Helm 模板化 | 复用配置，多环境部署 |
| Kustomize 管理差异 | Base + Overlay 分离基础和环境配置 |
| 健康检查必配 | Liveness + Readiness 保证服务可用性 |
| 资源限制必设 | Requests + Limits 防止资源耗尽 |
| 使用 HPA | 自动扩缩容应对流量波动 |
| 配置 PDB | 防止滚动更新时服务中断 |
| 密钥外部化 | 使用 External Secrets Operator |
| 镜像使用 Digest | 确保部署一致性 |
| 多副本部署 | 至少 2 个副本保证高可用 |
| 亲和性配置 | Pod 反亲和性分散到不同节点 |

## 工具对比

| 工具 | 优势 | 劣势 | 适用场景 |
|------|------|------|----------|
| Helm | 模板强大、生态丰富 | 学习曲线陡峭 | 复杂应用、多环境 |
| Kustomize | 原生支持、无模板 | 功能相对简单 | 简单应用、环境差异 |
| Operator | 自动化运维、领域知识 | 开发复杂 | 有状态应用、复杂生命周期 |
| Flagger | 自动金丝雀、渐进式交付 | 依赖 Service Mesh | 生产环境渐进式发布 |
