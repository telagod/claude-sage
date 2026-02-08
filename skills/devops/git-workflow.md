---
name: git-workflow
description: Git 版本控制。分支管理、合并策略、GitHub工作流。当用户提到 Git、分支、merge、rebase、PR、GitHub时使用。
---

# 🔧 炼器秘典 · Git 工作流


## 基础命令

```bash
# 初始化
git init
git clone <url>

# 日常操作
git add <file>
git commit -m "message"
git push origin main
git pull origin main

# 状态查看
git status
git log --oneline -10
git diff
git diff --staged
```

## 分支管理

```bash
# 创建切换
git branch feature-x
git checkout feature-x
git checkout -b feature-x  # 创建并切换

# 查看
git branch -a   # 所有分支
git branch -vv  # 详细信息

# 删除
git branch -d feature-x     # 已合并
git branch -D feature-x     # 强制删除
git push origin --delete feature-x  # 远程
```

## 分支策略

### Git Flow
```
main ─────────────────────────────────────────
  │                                    ↑
  └─ develop ─────────────────────────┬─
       │         ↑         ↑          │
       └─ feature/xxx ─────┘          │
       └─ release/1.0 ────────────────┘
       └─ hotfix/xxx ─────────────────┘
```

### GitHub Flow
```
main ─────────────────────────────────────────
  │              ↑
  └─ feature ────┘ (PR + Review + Merge)
```

### Trunk Based
```
main ─────────────────────────────────────────
  │    ↑    ↑    ↑
  └────┴────┴────┘ (短生命周期分支)
```

## 合并策略

```bash
# Merge (保留历史)
git checkout main
git merge feature-x

# Rebase (线性历史)
git checkout feature-x
git rebase main
git checkout main
git merge feature-x

# Squash (压缩提交)
git merge --squash feature-x
git commit -m "Feature X"
```

## 冲突解决

```bash
# 1. 拉取最新
git fetch origin
git rebase origin/main

# 2. 解决冲突
# 编辑冲突文件，删除 <<<< ==== >>>> 标记

# 3. 继续
git add .
git rebase --continue

# 放弃
git rebase --abort
```

## 撤销操作

```bash
# 撤销工作区修改
git checkout -- <file>
git restore <file>

# 撤销暂存
git reset HEAD <file>
git restore --staged <file>

# 撤销提交
git reset --soft HEAD~1   # 保留修改
git reset --hard HEAD~1   # 丢弃修改
git revert <commit>       # 新提交撤销

# 修改最后提交
git commit --amend
```

## Commit 规范

```yaml
格式: <type>(<scope>): <subject>

类型:
  - feat: 新功能
  - fix: 修复
  - docs: 文档
  - style: 格式
  - refactor: 重构
  - test: 测试
  - chore: 构建/工具

示例:
  - feat(auth): add JWT authentication
  - fix(api): handle null response
  - docs(readme): update installation guide
```

## GitHub 工作流

```bash
# Fork 工作流
1. Fork 仓库
2. git clone <your-fork>
3. git remote add upstream <original>
4. git checkout -b feature
5. 开发 & 提交
6. git push origin feature
7. 创建 PR

# 同步上游
git fetch upstream
git rebase upstream/main
git push origin main
```

## 安全规范

```yaml
禁止:
  - git push --force (除非明确要求)
  - git reset --hard (除非明确要求)
  - git clean -f

必须:
  - commit 前 git status 确认
  - 使用具体文件名 add
  - 每次 commit 聚焦单一变更
```

