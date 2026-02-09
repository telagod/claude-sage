---
name: iac
description: 基础设施即代码。Terraform、Pulumi、AWS CDK、状态管理、模块开发、远程后端。当用户提到 IaC、Terraform、Pulumi、CDK、基础设施即代码、状态管理时使用。
---

# 🏗️ 基础设施即代码 · IaC

## Terraform

### 项目结构
```
terraform/
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── eks/
│   └── rds/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   └── production/
└── .terraform.lock.hcl
```

### Provider 配置
```hcl
# versions.tf
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }

  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
    kms_key_id     = "arn:aws:kms:us-west-2:123456789012:key/..."
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Project     = var.project_name
    }
  }
}
```

### VPC 模块
```hcl
# modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.name_prefix}-vpc"
  }
}

resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name                                           = "${var.name_prefix}-public-${count.index + 1}"
    "kubernetes.io/role/elb"                       = "1"
    "kubernetes.io/cluster/${var.cluster_name}"    = "shared"
  }
}

resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name                                           = "${var.name_prefix}-private-${count.index + 1}"
    "kubernetes.io/role/internal-elb"              = "1"
    "kubernetes.io/cluster/${var.cluster_name}"    = "shared"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.name_prefix}-igw"
  }
}

resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? length(var.public_subnet_cidrs) : 0
  domain = "vpc"

  tags = {
    Name = "${var.name_prefix}-nat-eip-${count.index + 1}"
  }
}

resource "aws_nat_gateway" "main" {
  count         = var.enable_nat_gateway ? length(var.public_subnet_cidrs) : 0
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = {
    Name = "${var.name_prefix}-nat-${count.index + 1}"
  }

  depends_on = [aws_internet_gateway.main]
}

# modules/vpc/variables.tf
variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway"
  type        = bool
  default     = true
}

variable "cluster_name" {
  description = "EKS cluster name for tagging"
  type        = string
}

# modules/vpc/outputs.tf
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}
```

### EKS 模块
```hcl
# modules/eks/main.tf
resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  role_arn = aws_iam_role.cluster.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids              = concat(var.public_subnet_ids, var.private_subnet_ids)
    endpoint_private_access = true
    endpoint_public_access  = var.endpoint_public_access
    public_access_cidrs     = var.public_access_cidrs
  }

  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  encryption_config {
    provider {
      key_arn = var.kms_key_arn
    }
    resources = ["secrets"]
  }

  depends_on = [
    aws_iam_role_policy_attachment.cluster_policy,
    aws_cloudwatch_log_group.cluster,
  ]
}

resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-node-group"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.private_subnet_ids

  scaling_config {
    desired_size = var.desired_size
    max_size     = var.max_size
    min_size     = var.min_size
  }

  instance_types = var.instance_types
  capacity_type  = var.capacity_type
  disk_size      = var.disk_size

  update_config {
    max_unavailable_percentage = 33
  }

  labels = var.node_labels

  tags = {
    Name = "${var.cluster_name}-node-group"
  }

  depends_on = [
    aws_iam_role_policy_attachment.node_policy,
  ]
}

resource "aws_iam_role" "cluster" {
  name = "${var.cluster_name}-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.cluster.name
}

resource "aws_cloudwatch_log_group" "cluster" {
  name              = "/aws/eks/${var.cluster_name}/cluster"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_arn
}
```

### 环境配置
```hcl
# environments/production/main.tf
module "vpc" {
  source = "../../modules/vpc"

  name_prefix          = "myapp-prod"
  vpc_cidr             = "10.0.0.0/16"
  public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
  availability_zones   = ["us-west-2a", "us-west-2b", "us-west-2c"]
  enable_nat_gateway   = true
  cluster_name         = "myapp-prod"
}

module "eks" {
  source = "../../modules/eks"

  cluster_name           = "myapp-prod"
  kubernetes_version     = "1.28"
  vpc_id                 = module.vpc.vpc_id
  public_subnet_ids      = module.vpc.public_subnet_ids
  private_subnet_ids     = module.vpc.private_subnet_ids
  endpoint_public_access = false

  desired_size   = 3
  min_size       = 3
  max_size       = 10
  instance_types = ["t3.large"]
  capacity_type  = "ON_DEMAND"

  kms_key_arn = aws_kms_key.eks.arn
}

# environments/production/terraform.tfvars
aws_region   = "us-west-2"
environment  = "production"
project_name = "myapp"
```

### Terraform 命令
```bash
# 初始化
terraform init

# 验证配置
terraform validate

# 格式化代码
terraform fmt -recursive

# 查看计划
terraform plan -out=tfplan

# 应用变更
terraform apply tfplan

# 查看状态
terraform show

# 查看输出
terraform output

# 导入现有资源
terraform import aws_vpc.main vpc-12345678

# 销毁资源
terraform destroy

# 状态管理
terraform state list
terraform state show aws_vpc.main
terraform state mv aws_vpc.old aws_vpc.new
terraform state rm aws_vpc.unused

# Workspace 管理
terraform workspace list
terraform workspace new production
terraform workspace select production
```

### 远程状态数据源
```hcl
data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = "mycompany-terraform-state"
    key    = "vpc/terraform.tfstate"
    region = "us-west-2"
  }
}

resource "aws_instance" "app" {
  subnet_id = data.terraform_remote_state.vpc.outputs.private_subnet_ids[0]
}
```

## Pulumi

### 项目结构
```
pulumi/
├── __main__.py
├── Pulumi.yaml
├── Pulumi.dev.yaml
├── Pulumi.prod.yaml
├── requirements.txt
└── modules/
    ├── vpc.py
    ├── eks.py
    └── rds.py
```

### Pulumi.yaml
```yaml
name: myapp-infrastructure
runtime: python
description: Infrastructure for MyApp
```

### VPC 模块 (Python)
```python
# modules/vpc.py
import pulumi
import pulumi_aws as aws

class VpcArgs:
    def __init__(self,
                 name_prefix: str,
                 cidr_block: str = "10.0.0.0/16",
                 availability_zones: list = None,
                 public_subnet_cidrs: list = None,
                 private_subnet_cidrs: list = None):
        self.name_prefix = name_prefix
        self.cidr_block = cidr_block
        self.availability_zones = availability_zones or ["us-west-2a", "us-west-2b"]
        self.public_subnet_cidrs = public_subnet_cidrs or ["10.0.1.0/24", "10.0.2.0/24"]
        self.private_subnet_cidrs = private_subnet_cidrs or ["10.0.11.0/24", "10.0.12.0/24"]

class Vpc(pulumi.ComponentResource):
    def __init__(self, name: str, args: VpcArgs, opts=None):
        super().__init__("custom:network:Vpc", name, {}, opts)

        # VPC
        self.vpc = aws.ec2.Vpc(
            f"{name}-vpc",
            cidr_block=args.cidr_block,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            tags={"Name": f"{args.name_prefix}-vpc"},
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Internet Gateway
        self.igw = aws.ec2.InternetGateway(
            f"{name}-igw",
            vpc_id=self.vpc.id,
            tags={"Name": f"{args.name_prefix}-igw"},
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Public Subnets
        self.public_subnets = []
        for i, (az, cidr) in enumerate(zip(args.availability_zones, args.public_subnet_cidrs)):
            subnet = aws.ec2.Subnet(
                f"{name}-public-{i}",
                vpc_id=self.vpc.id,
                cidr_block=cidr,
                availability_zone=az,
                map_public_ip_on_launch=True,
                tags={"Name": f"{args.name_prefix}-public-{i}"},
                opts=pulumi.ResourceOptions(parent=self)
            )
            self.public_subnets.append(subnet)

        # Private Subnets
        self.private_subnets = []
        for i, (az, cidr) in enumerate(zip(args.availability_zones, args.private_subnet_cidrs)):
            subnet = aws.ec2.Subnet(
                f"{name}-private-{i}",
                vpc_id=self.vpc.id,
                cidr_block=cidr,
                availability_zone=az,
                tags={"Name": f"{args.name_prefix}-private-{i}"},
                opts=pulumi.ResourceOptions(parent=self)
            )
            self.private_subnets.append(subnet)

        # NAT Gateways
        self.nat_gateways = []
        for i, subnet in enumerate(self.public_subnets):
            eip = aws.ec2.Eip(
                f"{name}-nat-eip-{i}",
                domain="vpc",
                tags={"Name": f"{args.name_prefix}-nat-eip-{i}"},
                opts=pulumi.ResourceOptions(parent=self)
            )

            nat = aws.ec2.NatGateway(
                f"{name}-nat-{i}",
                allocation_id=eip.id,
                subnet_id=subnet.id,
                tags={"Name": f"{args.name_prefix}-nat-{i}"},
                opts=pulumi.ResourceOptions(parent=self, depends_on=[self.igw])
            )
            self.nat_gateways.append(nat)

        self.register_outputs({
            "vpc_id": self.vpc.id,
            "public_subnet_ids": [s.id for s in self.public_subnets],
            "private_subnet_ids": [s.id for s in self.private_subnets],
        })
```

### EKS 模块 (Python)
```python
# modules/eks.py
import pulumi
import pulumi_aws as aws
import pulumi_eks as eks

class EksArgs:
    def __init__(self,
                 cluster_name: str,
                 vpc_id: pulumi.Output,
                 public_subnet_ids: list,
                 private_subnet_ids: list,
                 desired_capacity: int = 3,
                 min_size: int = 2,
                 max_size: int = 10,
                 instance_type: str = "t3.medium"):
        self.cluster_name = cluster_name
        self.vpc_id = vpc_id
        self.public_subnet_ids = public_subnet_ids
        self.private_subnet_ids = private_subnet_ids
        self.desired_capacity = desired_capacity
        self.min_size = min_size
        self.max_size = max_size
        self.instance_type = instance_type

class EksCluster(pulumi.ComponentResource):
    def __init__(self, name: str, args: EksArgs, opts=None):
        super().__init__("custom:kubernetes:EksCluster", name, {}, opts)

        # EKS Cluster
        self.cluster = eks.Cluster(
            name,
            vpc_id=args.vpc_id,
            public_subnet_ids=args.public_subnet_ids,
            private_subnet_ids=args.private_subnet_ids,
            instance_type=args.instance_type,
            desired_capacity=args.desired_capacity,
            min_size=args.min_size,
            max_size=args.max_size,
            enabled_cluster_log_types=["api", "audit", "authenticator"],
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.register_outputs({
            "cluster_name": self.cluster.core.cluster.name,
            "kubeconfig": self.cluster.kubeconfig,
        })
```

### 主程序
```python
# __main__.py
import pulumi
import pulumi_aws as aws
from modules.vpc import Vpc, VpcArgs
from modules.eks import EksCluster, EksArgs

# 配置
config = pulumi.Config()
environment = pulumi.get_stack()
project_name = pulumi.get_project()

# VPC
vpc = Vpc(
    "myapp-vpc",
    VpcArgs(
        name_prefix=f"{project_name}-{environment}",
        cidr_block="10.0.0.0/16",
        availability_zones=["us-west-2a", "us-west-2b", "us-west-2c"],
        public_subnet_cidrs=["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"],
        private_subnet_cidrs=["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"],
    )
)

# EKS
eks_cluster = EksCluster(
    "myapp-eks",
    EksArgs(
        cluster_name=f"{project_name}-{environment}",
        vpc_id=vpc.vpc.id,
        public_subnet_ids=[s.id for s in vpc.public_subnets],
        private_subnet_ids=[s.id for s in vpc.private_subnets],
        desired_capacity=config.get_int("desired_capacity") or 3,
        min_size=config.get_int("min_size") or 2,
        max_size=config.get_int("max_size") or 10,
        instance_type=config.get("instance_type") or "t3.medium",
    )
)

# Outputs
pulumi.export("vpc_id", vpc.vpc.id)
pulumi.export("cluster_name", eks_cluster.cluster.core.cluster.name)
pulumi.export("kubeconfig", eks_cluster.cluster.kubeconfig)
```

### Pulumi 命令
```bash
# 初始化项目
pulumi new aws-python

# 配置
pulumi config set aws:region us-west-2
pulumi config set desired_capacity 5 --stack production

# 预览变更
pulumi preview

# 应用变更
pulumi up

# 查看输出
pulumi stack output kubeconfig

# 查看资源
pulumi stack

# 销毁资源
pulumi destroy

# Stack 管理
pulumi stack ls
pulumi stack select production
pulumi stack init staging

# 导出/导入状态
pulumi stack export > state.json
pulumi stack import < state.json
```

## AWS CDK

### 项目结构
```
cdk/
├── app.py
├── cdk.json
├── requirements.txt
└── stacks/
    ├── vpc_stack.py
    ├── eks_stack.py
    └── rds_stack.py
```

### VPC Stack (Python)
```python
# stacks/vpc_stack.py
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct

class VpcStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        self.vpc = ec2.Vpc(
            self, "MyVpc",
            max_azs=3,
            cidr="10.0.0.0/16",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
            ],
            nat_gateways=3,
        )
```

### EKS Stack (Python)
```python
# stacks/eks_stack.py
from aws_cdk import (
    Stack,
    aws_eks as eks,
    aws_ec2 as ec2,
    aws_iam as iam,
)
from constructs import Construct

class EksStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # EKS Cluster
        self.cluster = eks.Cluster(
            self, "MyCluster",
            version=eks.KubernetesVersion.V1_28,
            vpc=vpc,
            default_capacity=0,
            cluster_logging=[
                eks.ClusterLoggingTypes.API,
                eks.ClusterLoggingTypes.AUDIT,
                eks.ClusterLoggingTypes.AUTHENTICATOR,
            ],
        )

        # Node Group
        self.cluster.add_nodegroup_capacity(
            "NodeGroup",
            instance_types=[ec2.InstanceType("t3.medium")],
            min_size=2,
            max_size=10,
            desired_size=3,
            disk_size=50,
        )

        # Helm Chart
        self.cluster.add_helm_chart(
            "NginxIngress",
            chart="ingress-nginx",
            repository="https://kubernetes.github.io/ingress-nginx",
            namespace="ingress-nginx",
            create_namespace=True,
        )
```

### App
```python
# app.py
import aws_cdk as cdk
from stacks.vpc_stack import VpcStack
from stacks.eks_stack import EksStack

app = cdk.App()

env = cdk.Environment(
    account="123456789012",
    region="us-west-2"
)

vpc_stack = VpcStack(app, "VpcStack", env=env)
eks_stack = EksStack(app, "EksStack", vpc=vpc_stack.vpc, env=env)

app.synth()
```

### CDK 命令
```bash
# 初始化项目
cdk init app --language python

# 安装依赖
pip install -r requirements.txt

# 合成 CloudFormation
cdk synth

# 查看差异
cdk diff

# 部署
cdk deploy --all

# 销毁
cdk destroy --all

# Bootstrap (首次使用)
cdk bootstrap aws://123456789012/us-west-2
```

## 状态管理

### Terraform 远程后端
```hcl
# S3 + DynamoDB
terraform {
  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
    kms_key_id     = "arn:aws:kms:us-west-2:123456789012:key/..."
  }
}

# Terraform Cloud
terraform {
  backend "remote" {
    organization = "mycompany"
    workspaces {
      name = "production"
    }
  }
}
```

### 状态锁定
```bash
# 创建 DynamoDB 表
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### 状态迁移
```bash
# 从本地迁移到 S3
terraform init -migrate-state

# 手动拉取状态
terraform state pull > terraform.tfstate

# 手动推送状态
terraform state push terraform.tfstate
```

## 最佳实践

| 实践 | 说明 |
|------|------|
| 模块化 | 将可复用组件抽象为模块 |
| 环境隔离 | 不同环境使用不同 State |
| 远程状态 | 使用 S3/Terraform Cloud 存储状态 |
| 状态锁定 | 使用 DynamoDB 防止并发修改 |
| 版本控制 | Provider 版本锁定 |
| 密钥管理 | 使用 AWS Secrets Manager/SSM |
| 标签规范 | 统一资源标签 |
| 变更审查 | Plan 后人工审查再 Apply |
| 自动化 | CI/CD 集成 |
| 文档化 | 模块添加 README 和示例 |

## 工具对比

| 工具 | 语言 | 状态管理 | 云支持 | 学习曲线 |
|------|------|----------|---------|----------|
| Terraform | HCL | 显式 | 全平台 | 中等 |
| Pulumi | 多语言 | 自动 | 全平台 | 较低 |
| AWS CDK | 多语言 | CloudFormation | AWS | 中等 |
| CloudFormation | YAML/JSON | AWS 托管 | AWS | 较高 |

## 工具清单

| 工具 | 用途 |
|------|------|
| Terraform | 多云 IaC |
| Pulumi | 编程语言 IaC |
| AWS CDK | AWS 原生 IaC |
| Terragrunt | Terraform 包装器 |
| Atlantis | Terraform PR 自动化 |
| Infracost | 成本估算 |
| Checkov | 安全扫描 |
| tfsec | Terraform 安全扫描 |
