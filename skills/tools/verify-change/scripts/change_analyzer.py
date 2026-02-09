#!/usr/bin/env python3
"""
变更分析器
分析代码变更，检测文档同步状态，评估变更影响
"""

import os
import re
import sys
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum


class ChangeType(Enum):
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class FileChange:
    path: str
    change_type: ChangeType
    additions: int = 0
    deletions: int = 0
    is_code: bool = False
    is_doc: bool = False
    is_test: bool = False
    is_config: bool = False


@dataclass
class Issue:
    severity: Severity
    message: str
    related_files: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    changes: List[FileChange] = field(default_factory=list)
    issues: List[Issue] = field(default_factory=list)
    affected_modules: Set[str] = field(default_factory=set)
    doc_sync_status: Dict[str, bool] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return not any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def total_additions(self) -> int:
        return sum(c.additions for c in self.changes)

    @property
    def total_deletions(self) -> int:
        return sum(c.deletions for c in self.changes)


CODE_EXTENSIONS = {'.py', '.go', '.rs', '.ts', '.js', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp'}
DOC_EXTENSIONS = {'.md', '.rst', '.txt', '.adoc'}
TEST_PATTERNS = ['test_', '_test.', '.test.', 'spec_', '_spec.', '/tests/', '/test/', '/__tests__/']
CONFIG_FILES = {'package.json', 'pyproject.toml', 'go.mod', 'Cargo.toml', 'pom.xml', 'Makefile', 'Dockerfile'}


def classify_file(path: str) -> FileChange:
    """分类文件类型"""
    p = Path(path)
    suffix = p.suffix.lower()
    name = p.name.lower()

    change = FileChange(path=path, change_type=ChangeType.MODIFIED)
    change.is_code = suffix in CODE_EXTENSIONS
    change.is_doc = suffix in DOC_EXTENSIONS
    change.is_test = any(pattern in path.lower() for pattern in TEST_PATTERNS)
    change.is_config = name in CONFIG_FILES or suffix in {'.yaml', '.yml', '.json', '.toml', '.ini'}

    return change


def normalize_path(path: str) -> str:
    """规范化相对路径"""
    normalized = path.strip()

    if normalized.startswith('"') and normalized.endswith('"') and len(normalized) >= 2:
        normalized = normalized[1:-1]
        normalized = normalized.replace('\\"', '"').replace('\\\\', '\\')

    if normalized.startswith("./"):
        normalized = normalized[2:]

    return normalized


def parse_name_status_line(line: str) -> Optional[FileChange]:
    """解析 git diff --name-status 输出行"""
    parts = line.split('\t')
    if len(parts) < 2:
        return None

    status_token = parts[0]
    status = status_token[0]
    path = normalize_path(parts[-1])

    if not path:
        return None

    change = classify_file(path)

    if status == 'A':
        change.change_type = ChangeType.ADDED
    elif status == 'M':
        change.change_type = ChangeType.MODIFIED
    elif status == 'D':
        change.change_type = ChangeType.DELETED
    elif status == 'R':
        change.change_type = ChangeType.RENAMED

    return change


def parse_porcelain_line(line: str) -> Optional[FileChange]:
    """解析 git status --porcelain 输出行"""
    if len(line) < 3:
        return None

    status = line[:2]
    raw_path = line[3:] if len(line) > 3 else ""

    if not raw_path:
        return None

    if " -> " in raw_path:
        raw_path = raw_path.split(" -> ", 1)[1]

    path = normalize_path(raw_path)
    if not path:
        return None

    change = classify_file(path)

    if '?' in status or 'A' in status:
        change.change_type = ChangeType.ADDED
    elif 'R' in status:
        change.change_type = ChangeType.RENAMED
    elif 'M' in status:
        change.change_type = ChangeType.MODIFIED
    elif 'D' in status:
        change.change_type = ChangeType.DELETED

    return change


def is_path_in_module(file_path: str, module: str) -> bool:
    """判断文件是否属于模块范围"""
    normalized_path = normalize_path(file_path)

    if module == ".":
        return len(Path(normalized_path).parts) == 1

    module_prefix = f"{module}/"
    return normalized_path == module or normalized_path.startswith(module_prefix)


def get_git_changes(base: str = "HEAD~1", target: str = "HEAD") -> List[FileChange]:
    """获取 Git 变更"""
    changes = []

    try:
        # 获取变更文件列表
        result = subprocess.run(
            ["git", "diff", "--name-status", base, target],
            capture_output=True, text=True, check=True
        )

        for line in result.stdout.splitlines():
            if not line:
                continue

            change = parse_name_status_line(line)
            if change:
                changes.append(change)

        # 获取行数统计
        stat_result = subprocess.run(
            ["git", "diff", "--numstat", base, target],
            capture_output=True, text=True, check=True
        )

        stat_map = {}
        for line in stat_result.stdout.splitlines():
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) >= 3:
                adds = int(parts[0]) if parts[0] != '-' else 0
                dels = int(parts[1]) if parts[1] != '-' else 0
                stat_map[normalize_path(parts[2])] = (adds, dels)

        for change in changes:
            if change.path in stat_map:
                change.additions, change.deletions = stat_map[change.path]

    except subprocess.CalledProcessError:
        pass
    except FileNotFoundError:
        pass

    return changes


def get_staged_changes() -> List[FileChange]:
    """获取暂存区变更"""
    changes = []

    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-status"],
            capture_output=True, text=True, check=True
        )

        for line in result.stdout.splitlines():
            if not line:
                continue

            change = parse_name_status_line(line)
            if change:
                changes.append(change)

    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return changes


def get_working_changes() -> List[FileChange]:
    """获取工作区变更"""
    changes = []

    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, check=True
        )

        for line in result.stdout.splitlines():
            if not line:
                continue

            change = parse_porcelain_line(line)
            if change:
                changes.append(change)

    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return changes


def identify_affected_modules(changes: List[FileChange]) -> Set[str]:
    """识别受影响的模块"""
    modules = set()

    for change in changes:
        normalized_path = normalize_path(change.path)
        parts = Path(normalized_path).parts

        if len(parts) == 1:
            modules.add(".")
            continue

        # 查找模块边界（包含 README.md 或 DESIGN.md 的目录）
        for i in range(len(parts)):
            potential_module = Path(*parts[:i+1])
            if (potential_module / "README.md").exists() or (potential_module / "DESIGN.md").exists():
                modules.add(str(potential_module))
                break
        else:
            # 使用顶层目录作为模块
            if len(parts) > 1:
                modules.add(parts[0])

    return modules


def check_doc_sync(changes: List[FileChange], modules: Set[str]) -> tuple[Dict[str, bool], List[Issue]]:
    """检查文档同步状态"""
    doc_status = {}
    issues = []

    code_changes = [c for c in changes if c.is_code and c.change_type != ChangeType.DELETED]
    doc_changes = {normalize_path(c.path) for c in changes if c.is_doc}

    # 检查每个模块
    for module in modules:
        module_path = Path(module)
        readme = normalize_path(str(module_path / "README.md"))
        design = normalize_path(str(module_path / "DESIGN.md"))

        # 检查模块内是否有代码变更
        module_code_changes = [c for c in code_changes if is_path_in_module(c.path, module)]

        if module_code_changes:
            # 检查是否有对应的文档更新
            readme_updated = readme in doc_changes
            design_updated = design in doc_changes

            # 计算变更规模
            total_changes = sum(c.additions + c.deletions for c in module_code_changes)

            if total_changes > 50 and not design_updated:
                issues.append(Issue(
                    severity=Severity.WARNING,
                    message=f"模块 {module} 有较大代码变更 ({total_changes} 行)，但 DESIGN.md 未更新",
                    related_files=[c.path for c in module_code_changes]
                ))
                doc_status[f"{module}/DESIGN.md"] = False
            else:
                doc_status[f"{module}/DESIGN.md"] = True

            # 新增文件检查
            new_files = [c for c in module_code_changes if c.change_type == ChangeType.ADDED]
            if new_files and not readme_updated:
                issues.append(Issue(
                    severity=Severity.INFO,
                    message=f"模块 {module} 新增了文件，建议更新 README.md",
                    related_files=[c.path for c in new_files]
                ))

    return doc_status, issues


def analyze_impact(changes: List[FileChange]) -> List[Issue]:
    """分析变更影响"""
    issues = []

    # 检查是否只改代码不改测试
    code_changes = [c for c in changes if c.is_code and not c.is_test]
    test_changes = [c for c in changes if c.is_test]

    if code_changes and not test_changes:
        total_code_changes = sum(c.additions + c.deletions for c in code_changes)
        if total_code_changes > 30:
            issues.append(Issue(
                severity=Severity.WARNING,
                message=f"代码变更 {total_code_changes} 行，但没有对应的测试更新",
                related_files=[c.path for c in code_changes]
            ))

    # 检查配置文件变更
    config_changes = [c for c in changes if c.is_config]
    if config_changes:
        issues.append(Issue(
            severity=Severity.INFO,
            message="配置文件有变更，请确认是否需要更新文档",
            related_files=[c.path for c in config_changes]
        ))

    # 检查删除操作
    deleted = [c for c in changes if c.change_type == ChangeType.DELETED]
    if deleted:
        issues.append(Issue(
            severity=Severity.INFO,
            message=f"删除了 {len(deleted)} 个文件，请确认相关引用已清理",
            related_files=[c.path for c in deleted]
        ))

    return issues


def analyze_changes(mode: str = "working") -> AnalysisResult:
    """分析变更"""
    result = AnalysisResult()

    # 获取变更
    if mode == "staged":
        result.changes = get_staged_changes()
    elif mode == "committed":
        result.changes = get_git_changes()
    else:
        result.changes = get_working_changes()

    if not result.changes:
        return result

    # 识别受影响模块
    result.affected_modules = identify_affected_modules(result.changes)

    # 检查文档同步
    doc_status, doc_issues = check_doc_sync(result.changes, result.affected_modules)
    result.doc_sync_status = doc_status
    result.issues.extend(doc_issues)

    # 分析影响
    impact_issues = analyze_impact(result.changes)
    result.issues.extend(impact_issues)

    return result


def format_report(result: AnalysisResult, verbose: bool = False) -> str:
    """格式化分析报告"""
    lines = []
    lines.append("=" * 60)
    lines.append("变更分析报告")
    lines.append("=" * 60)

    lines.append(f"\n变更文件: {len(result.changes)}")
    lines.append(f"新增行数: +{result.total_additions}")
    lines.append(f"删除行数: -{result.total_deletions}")
    lines.append(f"受影响模块: {', '.join(result.affected_modules) or '无'}")
    lines.append(f"分析结果: {'✓ 通过' if result.passed else '✗ 需要关注'}")

    if result.changes and verbose:
        lines.append("\n" + "-" * 40)
        lines.append("变更文件列表:")
        lines.append("-" * 40)

        type_icons = {
            ChangeType.ADDED: "➕",
            ChangeType.MODIFIED: "📝",
            ChangeType.DELETED: "➖",
            ChangeType.RENAMED: "📋"
        }

        for change in result.changes:
            icon = type_icons[change.change_type]
            tags = []
            if change.is_code:
                tags.append("代码")
            if change.is_doc:
                tags.append("文档")
            if change.is_test:
                tags.append("测试")
            if change.is_config:
                tags.append("配置")

            tag_str = f" [{', '.join(tags)}]" if tags else ""
            lines.append(f"  {icon} {change.path}{tag_str} (+{change.additions}/-{change.deletions})")

    if result.issues:
        lines.append("\n" + "-" * 40)
        lines.append("问题与建议:")
        lines.append("-" * 40)

        severity_icons = {"error": "✗", "warning": "⚠", "info": "ℹ"}

        for issue in result.issues:
            icon = severity_icons[issue.severity.value]
            lines.append(f"\n  {icon} [{issue.severity.value.upper()}] {issue.message}")
            if verbose and issue.related_files:
                for f in issue.related_files[:5]:
                    lines.append(f"      - {f}")
                if len(issue.related_files) > 5:
                    lines.append(f"      ... 及其他 {len(issue.related_files) - 5} 个文件")

    if result.doc_sync_status:
        lines.append("\n" + "-" * 40)
        lines.append("文档同步状态:")
        lines.append("-" * 40)

        for doc, synced in result.doc_sync_status.items():
            icon = "✓" if synced else "✗"
            lines.append(f"  {icon} {doc}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="变更分析器")
    parser.add_argument("--mode", choices=["working", "staged", "committed"],
                        default="working", help="分析模式")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    result = analyze_changes(args.mode)

    if args.json:
        output = {
            "passed": result.passed,
            "total_additions": result.total_additions,
            "total_deletions": result.total_deletions,
            "affected_modules": list(result.affected_modules),
            "changes": [
                {
                    "path": c.path,
                    "type": c.change_type.value,
                    "additions": c.additions,
                    "deletions": c.deletions,
                    "is_code": c.is_code,
                    "is_doc": c.is_doc,
                    "is_test": c.is_test
                }
                for c in result.changes
            ],
            "issues": [
                {
                    "severity": i.severity.value,
                    "message": i.message,
                    "related_files": i.related_files
                }
                for i in result.issues
            ],
            "doc_sync_status": result.doc_sync_status
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(format_report(result, args.verbose))

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
