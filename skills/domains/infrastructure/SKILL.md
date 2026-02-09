---
name: infrastructure
description: 云原生基础设施。Kubernetes、Helm、Kustomize、Operator、CRD、GitOps、ArgoCD、Flux、IaC、Terraform、Pulumi、CDK、基础设施即代码。当用户提到 K8s、Helm、GitOps、IaC、基础设施即代码时路由到此。
---

# 云原生基础设施 · Infrastructure

## 秘典矩阵

| 秘典 | 核心神通 | 触发词 |
|------|----------|--------|
| [kubernetes](kubernetes.md) | Helm/Kustomize/Operator/CRD | Kubernetes、K8s、Helm、Kustomize、Operator、CRD、部署策略 |
| [gitops](gitops.md) | ArgoCD/Flux/声明式部署 | GitOps、ArgoCD、Flux、声明式部署、自动同步 |
| [iac](iac.md) | Terraform/Pulumi/CDK/状态管理 | IaC、Terraform、Pulumi、CDK、基础设施即代码、状态管理 |

## 云原生架构视角

```
                    GitOps 控制平面
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
    ArgoCD/Flux      Kubernetes         IaC 层
        │                 │                 │
   Git Repo ──────> Helm/Kustomize ──> Terraform/Pulumi
        │                 │                 │
    声明式配置        容器编排          云资源管理
```

## 快速选择

### 容器编排
- **Helm Chart 开发** → `kubernetes.md`
- **Kustomize 配置** → `kubernetes.md`
- **Operator 模式** → `kubernetes.md`
- **部署策略** → `kubernetes.md`

### 持续部署
- **GitOps 流程** → `gitops.md`
- **ArgoCD 配置** → `gitops.md`
- **Flux 自动化** → `gitops.md`
- **多环境管理** → `gitops.md`

### 基础设施即代码
- **Terraform 模块** → `iac.md`
- **Pulumi 开发** → `iac.md`
- **AWS CDK** → `iac.md`
- **状态管理** → `iac.md`

## 最佳实践

| 层级 | 工具选择 | 原则 |
|------|----------|------|
| 应用部署 | Helm + Kustomize | 模板化 + 环境差异 |
| 持续交付 | ArgoCD/Flux | Git 为唯一真相源 |
| 基础设施 | Terraform/Pulumi | 声明式 + 状态管理 |
| 配置管理 | External Secrets | 密钥外部化 |
| 可观测性 | Prometheus + Grafana | 指标 + 可视化 |
