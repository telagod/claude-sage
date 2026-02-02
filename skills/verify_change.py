#!/usr/bin/env python3
"""
verify-change: 变更校验 Skill
分析代码变更，检测文档同步状态，评估变更影响范围
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Set
from enum import Enum


class ChangeType(Enum):
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


class ImpactLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class FileChange:
    path: str
    change_type: ChangeType
    additions: int = 0
    deletions: int = 0


@dataclass
class ChangeReport:
    passed: bool = True
    changes: List[FileChange] = field(default_factory=list)
    doc_sync_issues: List[str] = field(default_factory=list)
    impact_assessment: dict = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    def add_warning(self, warning: str):
        self.warnings.append(warning)

    def add_doc_issue(self, issue: str):
        self.doc_sync_issues.append(issue)
        self.passed = False


def run_git_command(args: List[str], cwd: Path) -> Optional[str]:
    """执行 git 命令"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None


def is_git_repo(path: Path) -> bool:
    """检查是否是 git 仓库"""
    return run_git_command(["rev-parse", "--git-dir"], path) is not None


def get_staged_changes(target_path: Path) -> List[FileChange]:
    """获取暂存区的变更"""
    changes = []

    output = run_git_command(["diff", "--cached", "--name-status"], target_path)
    if not output:
        return changes

    for line in output.split("\n"):
        if not line.strip():
            continue

        parts = line.split("\t")
        if len(parts) < 2:
            continue

        status = parts[0][0]
        file_path = parts[-1]

        change_type_map = {
            "A": ChangeType.ADDED,
            "M": ChangeType.MODIFIED,
            "D": ChangeType.DELETED,
            "R": ChangeType.RENAMED,
        }

        change_type = change_type_map.get(status, ChangeType.MODIFIED)
        changes.append(FileChange(path=file_path, change_type=change_type))

    numstat = run_git_command(["diff", "--cached", "--numstat"], target_path)
    if numstat:
        for line in numstat.split("\n"):
            parts = line.split("\t")
            if len(parts) >= 3:
                try:
                    additions = int(parts[0]) if parts[0] != "-" else 0
                    deletions = int(parts[1]) if parts[1] != "-" else 0
                    file_path = parts[2]

                    for change in changes:
                        if change.path == file_path:
                            change.additions = additions
                            change.deletions = deletions
                            break
                except ValueError:
                    pass

    return changes


def get_unstaged_changes(target_path: Path) -> List[FileChange]:
    """获取未暂存的变更"""
    changes = []

    output = run_git_command(["diff", "--name-status"], target_path)
    if not output:
        return changes

    for line in output.split("\n"):
        if not line.strip():
            continue

        parts = line.split("\t")
        if len(parts) < 2:
            continue

        status = parts[0][0]
        file_path = parts[-1]

        change_type_map = {
            "A": ChangeType.ADDED,
            "M": ChangeType.MODIFIED,
            "D": ChangeType.DELETED,
        }

        change_type = change_type_map.get(status, ChangeType.MODIFIED)
        changes.append(FileChange(path=file_path, change_type=change_type))

    return changes


def check_doc_sync(changes: List[FileChange], target_path: Path, report: ChangeReport):
    """检查文档同步状态"""
    code_extensions = {".py", ".js", ".ts", ".go", ".rs", ".java", ".kt", ".rb", ".php", ".tsx", ".jsx"}
    doc_extensions = {".md", ".rst", ".txt"}

    code_changes = [c for c in changes if Path(c.path).suffix in code_extensions]
    doc_changes = [c for c in changes if Path(c.path).suffix in doc_extensions]

    significant_code_changes = [
        c for c in code_changes
        if c.additions + c.deletions > 20 or c.change_type in [ChangeType.ADDED, ChangeType.DELETED]
    ]

    if significant_code_changes and not doc_changes:
        report.add_doc_issue(
            f"检测到 {len(significant_code_changes)} 个重要代码变更，但未更新文档"
        )

    for change in code_changes:
        if change.change_type == ChangeType.ADDED:
            dir_path = (target_path / change.path).parent
            readme_path = dir_path / "README.md"

            if not readme_path.exists():
                has_readme_change = any(
                    "README.md" in c.path and str(dir_path) in c.path
                    for c in doc_changes
                )
                if not has_readme_change:
                    report.add_warning(f"新文件 {change.path} 所在目录缺少 README.md")


def assess_impact(changes: List[FileChange], report: ChangeReport):
    """评估变更影响"""
    total_additions = sum(c.additions for c in changes)
    total_deletions = sum(c.deletions for c in changes)
    total_files = len(changes)

    if total_files > 20 or total_additions + total_deletions > 500:
        impact = ImpactLevel.HIGH
    elif total_files > 5 or total_additions + total_deletions > 100:
        impact = ImpactLevel.MEDIUM
    else:
        impact = ImpactLevel.LOW

    sensitive_patterns = [
        "auth", "security", "password", "token", "secret",
        "config", "settings", "env",
        "migration", "schema", "model",
    ]

    sensitive_files = []
    for change in changes:
        path_lower = change.path.lower()
        if any(pattern in path_lower for pattern in sensitive_patterns):
            sensitive_files.append(change.path)

    if sensitive_files:
        impact = ImpactLevel.HIGH

    report.impact_assessment = {
        "level": impact.value,
        "total_files": total_files,
        "total_additions": total_additions,
        "total_deletions": total_deletions,
        "sensitive_files": sensitive_files,
    }


def print_report(report: ChangeReport, json_output: bool = False):
    """输出报告"""
    if json_output:
        output = {
            "passed": report.passed,
            "changes": [
                {
                    "path": c.path,
                    "type": c.change_type.value,
                    "additions": c.additions,
                    "deletions": c.deletions,
                }
                for c in report.changes
            ],
            "doc_sync_issues": report.doc_sync_issues,
            "impact_assessment": report.impact_assessment,
            "warnings": report.warnings,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print("")
    print("=" * 60)
    print("  校验报告: verify-change")
    print("=" * 60)
    print("")

    status = "✓ 通过" if report.passed else "✗ 未通过"
    print(f"  状态: {status}")
    print("")

    if report.impact_assessment:
        impact = report.impact_assessment
        level_icons = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        icon = level_icons.get(impact["level"], "⚪")

        print(f"  影响评估: {icon} {impact['level'].upper()}")
        print(f"  变更文件: {impact['total_files']} 个")
        print(f"  新增行数: +{impact['total_additions']}")
        print(f"  删除行数: -{impact['total_deletions']}")

        if impact.get("sensitive_files"):
            print(f"  敏感文件: {len(impact['sensitive_files'])} 个")
            for f in impact["sensitive_files"][:5]:
                print(f"    - {f}")

    print("")

    if report.changes:
        print("-" * 60)
        print("  变更文件列表:")
        print("-" * 60)

        type_icons = {
            ChangeType.ADDED: "➕",
            ChangeType.MODIFIED: "📝",
            ChangeType.DELETED: "➖",
            ChangeType.RENAMED: "📋",
        }

        for change in report.changes[:20]:
            icon = type_icons.get(change.change_type, "📄")
            stats = f"+{change.additions}/-{change.deletions}" if change.additions or change.deletions else ""
            print(f"  {icon} {change.path} {stats}")

        if len(report.changes) > 20:
            print(f"  ... 还有 {len(report.changes) - 20} 个文件")

    if report.doc_sync_issues:
        print("")
        print("-" * 60)
        print("  ⚠ 文档同步问题:")
        print("-" * 60)
        for issue in report.doc_sync_issues:
            print(f"  - {issue}")

    if report.warnings:
        print("")
        print("-" * 60)
        print("  ⚠ 警告:")
        print("-" * 60)
        for warning in report.warnings:
            print(f"  - {warning}")

    print("")
    print("=" * 60)
    conclusion = "可交付" if report.passed else "需修复后交付"
    print(f"  【结论】{conclusion}")
    print("=" * 60)
    print("")


def main(args: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="变更校验 - 分析代码变更和文档同步",
        prog="verify-change",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="要检查的仓库路径 (默认: 当前目录)",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="只检查暂存区的变更",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出",
    )

    parsed = parser.parse_args(args)
    target_path = Path(parsed.path).resolve()

    if not target_path.exists():
        print(f"[✗] 路径不存在: {target_path}")
        return 1

    if not is_git_repo(target_path):
        print(f"[✗] 不是 git 仓库: {target_path}")
        return 1

    report = ChangeReport()

    if parsed.verbose:
        print(f"[i] 检查目标: {target_path}")

    if parsed.staged:
        report.changes = get_staged_changes(target_path)
    else:
        staged = get_staged_changes(target_path)
        unstaged = get_unstaged_changes(target_path)

        seen_paths = set()
        for change in staged + unstaged:
            if change.path not in seen_paths:
                report.changes.append(change)
                seen_paths.add(change.path)

    if not report.changes:
        print("[i] 未检测到变更")
        return 0

    check_doc_sync(report.changes, target_path, report)
    assess_impact(report.changes, report)

    print_report(report, json_output=parsed.json)

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
