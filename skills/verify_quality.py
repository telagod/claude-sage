#!/usr/bin/env python3
"""
verify-quality: 代码质量检查 Skill
检测复杂度、重复代码、命名规范、函数长度等质量指标
"""

import sys
import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set
from enum import Enum


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class QualityIssue:
    severity: Severity
    category: str
    message: str
    file: str
    line: int = 0
    suggestion: str = ""


@dataclass
class QualityReport:
    passed: bool = True
    issues: List[QualityIssue] = field(default_factory=list)
    metrics: Dict = field(default_factory=dict)

    def add_issue(self, issue: QualityIssue):
        self.issues.append(issue)
        if issue.severity == Severity.ERROR:
            self.passed = False


SKIP_DIRS = {
    ".git", ".svn", ".hg",
    "node_modules", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".nuxt",
    "vendor", "third_party",
}

CODE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
}

MAX_LINE_LENGTH = 120
MAX_FUNCTION_LINES = 50
MAX_FILE_LINES = 500
MAX_COMPLEXITY = 10


def should_skip_dir(dir_name: str) -> bool:
    return dir_name in SKIP_DIRS or dir_name.startswith(".")


def get_language(file_path: Path) -> str:
    return CODE_EXTENSIONS.get(file_path.suffix.lower(), "unknown")


def check_line_length(content: str, file_path: str, report: QualityReport):
    """检查行长度"""
    lines = content.split("\n")
    long_lines = []

    for i, line in enumerate(lines, 1):
        if len(line) > MAX_LINE_LENGTH:
            long_lines.append((i, len(line)))

    if long_lines:
        report.add_issue(QualityIssue(
            severity=Severity.WARNING,
            category="行长度",
            message=f"发现 {len(long_lines)} 行超过 {MAX_LINE_LENGTH} 字符",
            file=file_path,
            line=long_lines[0][0],
            suggestion=f"建议将长行拆分，保持每行不超过 {MAX_LINE_LENGTH} 字符",
        ))


def check_function_length(content: str, file_path: str, language: str, report: QualityReport):
    """检查函数长度"""
    function_patterns = {
        "python": r"^\s*def\s+(\w+)\s*\(",
        "javascript": r"(?:function\s+(\w+)|(\w+)\s*[=:]\s*(?:async\s+)?function|\b(\w+)\s*\([^)]*\)\s*{)",
        "typescript": r"(?:function\s+(\w+)|(\w+)\s*[=:]\s*(?:async\s+)?function|\b(\w+)\s*\([^)]*\)\s*(?::\s*\w+)?\s*{)",
        "go": r"func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(",
        "rust": r"fn\s+(\w+)\s*[<(]",
        "java": r"(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(",
    }

    pattern = function_patterns.get(language)
    if not pattern:
        return

    lines = content.split("\n")
    long_functions = []

    in_function = False
    function_name = ""
    function_start = 0
    brace_count = 0

    for i, line in enumerate(lines, 1):
        match = re.search(pattern, line)
        if match:
            if in_function and i - function_start > MAX_FUNCTION_LINES:
                long_functions.append((function_name, function_start, i - function_start))

            function_name = next((g for g in match.groups() if g), "anonymous")
            function_start = i
            in_function = True
            brace_count = line.count("{") - line.count("}")
        elif in_function:
            brace_count += line.count("{") - line.count("}")
            if brace_count <= 0 and language != "python":
                if i - function_start > MAX_FUNCTION_LINES:
                    long_functions.append((function_name, function_start, i - function_start))
                in_function = False

    for func_name, start_line, length in long_functions:
        report.add_issue(QualityIssue(
            severity=Severity.WARNING,
            category="函数长度",
            message=f"函数 '{func_name}' 有 {length} 行，超过建议的 {MAX_FUNCTION_LINES} 行",
            file=file_path,
            line=start_line,
            suggestion="考虑将函数拆分为更小的、职责单一的函数",
        ))


def check_naming_conventions(content: str, file_path: str, language: str, report: QualityReport):
    """检查命名规范"""
    issues = []

    if language == "python":
        class_pattern = r"class\s+([a-z]\w*)\s*[:\(]"
        matches = re.findall(class_pattern, content)
        for name in matches:
            issues.append(f"类名 '{name}' 应使用 PascalCase")

        const_pattern = r"^([A-Z][A-Z_0-9]*)\s*="
        func_pattern = r"def\s+([A-Z]\w*)\s*\("
        matches = re.findall(func_pattern, content)
        for name in matches:
            if not name.startswith("_"):
                issues.append(f"函数名 '{name}' 应使用 snake_case")

    elif language in ["javascript", "typescript"]:
        class_pattern = r"class\s+([a-z]\w*)\s*[{\(]"
        matches = re.findall(class_pattern, content)
        for name in matches:
            issues.append(f"类名 '{name}' 应使用 PascalCase")

    if issues:
        report.add_issue(QualityIssue(
            severity=Severity.INFO,
            category="命名规范",
            message=f"发现 {len(issues)} 个命名问题",
            file=file_path,
            suggestion="; ".join(issues[:3]) + ("..." if len(issues) > 3 else ""),
        ))


def check_todo_fixme(content: str, file_path: str, report: QualityReport):
    """检查 TODO/FIXME 注释"""
    lines = content.split("\n")
    todos = []
    fixmes = []

    for i, line in enumerate(lines, 1):
        if re.search(r"\bTODO\b", line, re.IGNORECASE):
            todos.append(i)
        if re.search(r"\bFIXME\b", line, re.IGNORECASE):
            fixmes.append(i)

    if fixmes:
        report.add_issue(QualityIssue(
            severity=Severity.WARNING,
            category="FIXME",
            message=f"发现 {len(fixmes)} 个 FIXME 注释",
            file=file_path,
            line=fixmes[0],
            suggestion="FIXME 表示需要修复的问题，建议尽快处理",
        ))

    if todos:
        report.add_issue(QualityIssue(
            severity=Severity.INFO,
            category="TODO",
            message=f"发现 {len(todos)} 个 TODO 注释",
            file=file_path,
            line=todos[0],
            suggestion="建议将 TODO 转化为具体的任务跟踪",
        ))


def check_file_length(content: str, file_path: str, report: QualityReport):
    """检查文件长度"""
    line_count = len(content.split("\n"))

    if line_count > MAX_FILE_LINES:
        report.add_issue(QualityIssue(
            severity=Severity.WARNING,
            category="文件长度",
            message=f"文件有 {line_count} 行，超过建议的 {MAX_FILE_LINES} 行",
            file=file_path,
            suggestion="考虑将文件拆分为多个模块",
        ))


def check_duplicate_code(content: str, file_path: str, report: QualityReport):
    """简单的重复代码检测"""
    lines = [line.strip() for line in content.split("\n") if line.strip() and not line.strip().startswith(("#", "//", "*", "/*"))]

    if len(lines) < 10:
        return

    line_counts: Dict[str, int] = {}
    for line in lines:
        if len(line) > 20:
            line_counts[line] = line_counts.get(line, 0) + 1

    duplicates = [(line, count) for line, count in line_counts.items() if count >= 3]

    if duplicates:
        report.add_issue(QualityIssue(
            severity=Severity.INFO,
            category="重复代码",
            message=f"发现 {len(duplicates)} 处可能的重复代码",
            file=file_path,
            suggestion="考虑提取重复代码为函数或常量",
        ))


def scan_file(file_path: Path, report: QualityReport):
    """扫描单个文件"""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        language = get_language(file_path)
        path_str = str(file_path)

        check_line_length(content, path_str, report)
        check_file_length(content, path_str, report)
        check_function_length(content, path_str, language, report)
        check_naming_conventions(content, path_str, language, report)
        check_todo_fixme(content, path_str, report)
        check_duplicate_code(content, path_str, report)

    except Exception as e:
        report.add_issue(QualityIssue(
            severity=Severity.INFO,
            category="扫描错误",
            message=f"无法扫描文件: {e}",
            file=str(file_path),
        ))


def scan_directory(target_path: Path, report: QualityReport):
    """递归扫描目录"""
    file_count = 0
    total_lines = 0

    def scan(path: Path):
        nonlocal file_count, total_lines

        if path.is_file():
            if path.suffix.lower() in CODE_EXTENSIONS:
                scan_file(path, report)
                file_count += 1
                try:
                    total_lines += len(path.read_text(encoding="utf-8", errors="ignore").split("\n"))
                except:
                    pass
            return

        for item in path.iterdir():
            if item.is_dir():
                if not should_skip_dir(item.name):
                    scan(item)
            elif item.is_file() and item.suffix.lower() in CODE_EXTENSIONS:
                scan_file(item, report)
                file_count += 1
                try:
                    total_lines += len(item.read_text(encoding="utf-8", errors="ignore").split("\n"))
                except:
                    pass

    scan(target_path)

    report.metrics = {
        "files_scanned": file_count,
        "total_lines": total_lines,
        "issues_found": len(report.issues),
    }


def print_report(report: QualityReport, json_output: bool = False):
    """输出报告"""
    if json_output:
        output = {
            "passed": report.passed,
            "metrics": report.metrics,
            "issues": [
                {
                    "severity": i.severity.value,
                    "category": i.category,
                    "message": i.message,
                    "file": i.file,
                    "line": i.line,
                    "suggestion": i.suggestion,
                }
                for i in report.issues
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print("")
    print("=" * 60)
    print("  校验报告: verify-quality")
    print("=" * 60)
    print("")

    status = "✓ 通过" if report.passed else "✗ 未通过"
    print(f"  状态: {status}")
    print("")

    if report.metrics:
        print(f"  扫描文件: {report.metrics.get('files_scanned', 0)} 个")
        print(f"  代码行数: {report.metrics.get('total_lines', 0)} 行")
        print(f"  发现问题: {report.metrics.get('issues_found', 0)} 个")
        print("")

    error_count = len([i for i in report.issues if i.severity == Severity.ERROR])
    warn_count = len([i for i in report.issues if i.severity == Severity.WARNING])
    info_count = len([i for i in report.issues if i.severity == Severity.INFO])

    print(f"  🔴 错误: {error_count}")
    print(f"  🟡 警告: {warn_count}")
    print(f"  🔵 信息: {info_count}")
    print("")

    if report.issues:
        print("-" * 60)
        print("  问题详情:")
        print("-" * 60)

        severity_icons = {
            Severity.ERROR: "🔴",
            Severity.WARNING: "🟡",
            Severity.INFO: "🔵",
        }

        categories: Dict[str, List[QualityIssue]] = {}
        for issue in report.issues:
            if issue.category not in categories:
                categories[issue.category] = []
            categories[issue.category].append(issue)

        for category, issues in categories.items():
            print(f"\n  [{category}] ({len(issues)} 个)")
            for issue in issues[:3]:
                icon = severity_icons.get(issue.severity, "⚪")
                location = f"{issue.file}:{issue.line}" if issue.line else issue.file
                print(f"    {icon} {location}")
                print(f"       {issue.message}")
                if issue.suggestion:
                    print(f"       💡 {issue.suggestion}")

            if len(issues) > 3:
                print(f"    ... 还有 {len(issues) - 3} 个类似问题")

    print("")
    print("=" * 60)
    conclusion = "质量良好" if report.passed else "需要改进"
    print(f"  【结论】{conclusion}")
    print("=" * 60)
    print("")


def main(args: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="代码质量检查 - 检测复杂度、命名规范等",
        prog="verify-quality",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="要检查的目录或文件路径 (默认: 当前目录)",
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

    report = QualityReport()

    if parsed.verbose:
        print(f"[i] 检查目标: {target_path}")

    scan_directory(target_path, report)

    print_report(report, json_output=parsed.json)

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
