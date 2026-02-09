#!/usr/bin/env python3
"""
代码质量检查器
检测代码复杂度、重复代码、命名规范、函数长度等
"""

import os
import re
import sys
import json
import ast
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
from collections import defaultdict


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
    severity: Severity
    category: str
    message: str
    file_path: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class FileMetrics:
    path: str
    lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    functions: int = 0
    classes: int = 0
    max_complexity: int = 0
    avg_function_length: float = 0


@dataclass
class QualityResult:
    scan_path: str
    files_scanned: int = 0
    total_lines: int = 0
    total_code_lines: int = 0
    issues: List[Issue] = field(default_factory=list)
    file_metrics: List[FileMetrics] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)


# 质量规则配置
MAX_LINE_LENGTH = 120
MAX_FUNCTION_LENGTH = 50
MAX_FILE_LENGTH = 500
MAX_COMPLEXITY = 10
MAX_PARAMETERS = 5
MIN_FUNCTION_NAME_LENGTH = 2
MAX_FUNCTION_NAME_LENGTH = 40
PYTHON_SPECIAL_METHODS = {"setUp", "tearDown", "setUpClass", "tearDownClass", "setUpModule", "tearDownModule"}


class PythonAnalyzer(ast.NodeVisitor):
    """Python AST 分析器"""

    def __init__(self, file_path: str, source: str):
        self.file_path = file_path
        self.source = source
        self.lines = source.split('\n')
        self.issues: List[Issue] = []
        self.functions: List[Dict] = []
        self.classes: List[Dict] = []
        self.complexity = 0

    def analyze(self) -> Tuple[List[Issue], List[Dict], List[Dict], int]:
        try:
            tree = ast.parse(self.source)
            self.visit(tree)
        except SyntaxError as e:
            self.issues.append(Issue(
                severity=Severity.ERROR,
                category="语法",
                message=f"语法错误: {e.msg}",
                file_path=self.file_path,
                line_number=e.lineno
            ))
        return self.issues, self.functions, self.classes, self.complexity

    def visit_FunctionDef(self, node):
        self._analyze_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self._analyze_function(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.classes.append({
            "name": node.name,
            "line": node.lineno,
            "methods": len([n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))])
        })

        # 检查类名
        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
            self.issues.append(Issue(
                severity=Severity.WARNING,
                category="命名",
                message=f"类名 '{node.name}' 不符合 PascalCase 规范",
                file_path=self.file_path,
                line_number=node.lineno,
                suggestion="类名应使用 PascalCase，如 MyClassName"
            ))

        self.generic_visit(node)

    def _analyze_function(self, node):
        func_info = {
            "name": node.name,
            "line": node.lineno,
            "length": self._get_function_length(node),
            "complexity": self._calculate_complexity(node),
            "parameters": len(node.args.args)
        }
        self.functions.append(func_info)
        self.complexity = max(self.complexity, func_info["complexity"])

        # 检查函数长度
        if func_info["length"] > MAX_FUNCTION_LENGTH:
            self.issues.append(Issue(
                severity=Severity.WARNING,
                category="复杂度",
                message=f"函数 '{node.name}' 过长 ({func_info['length']} 行 > {MAX_FUNCTION_LENGTH})",
                file_path=self.file_path,
                line_number=node.lineno,
                suggestion="考虑拆分为多个小函数"
            ))

        # 检查复杂度
        if func_info["complexity"] > MAX_COMPLEXITY:
            self.issues.append(Issue(
                severity=Severity.WARNING,
                category="复杂度",
                message=f"函数 '{node.name}' 圈复杂度过高 ({func_info['complexity']} > {MAX_COMPLEXITY})",
                file_path=self.file_path,
                line_number=node.lineno,
                suggestion="减少嵌套层级，提取子函数"
            ))

        # 检查参数数量
        if func_info["parameters"] > MAX_PARAMETERS:
            self.issues.append(Issue(
                severity=Severity.WARNING,
                category="设计",
                message=f"函数 '{node.name}' 参数过多 ({func_info['parameters']} > {MAX_PARAMETERS})",
                file_path=self.file_path,
                line_number=node.lineno,
                suggestion="考虑使用配置对象或数据类封装参数"
            ))

        # 检查函数命名
        if not node.name.startswith('_') and node.name not in PYTHON_SPECIAL_METHODS and not node.name.startswith('visit_'):
            if not re.match(r'^[a-z][a-z0-9_]*$', node.name):
                self.issues.append(Issue(
                    severity=Severity.INFO,
                    category="命名",
                    message=f"函数名 '{node.name}' 不符合 snake_case 规范",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    suggestion="函数名应使用 snake_case，如 my_function_name"
                ))

        if len(node.name) < MIN_FUNCTION_NAME_LENGTH:
            self.issues.append(Issue(
                severity=Severity.WARNING,
                category="命名",
                message=f"函数名 '{node.name}' 过短",
                file_path=self.file_path,
                line_number=node.lineno,
                suggestion="使用更具描述性的函数名"
            ))

    def _get_function_length(self, node) -> int:
        if hasattr(node, 'end_lineno'):
            return node.end_lineno - node.lineno + 1
        return len(ast.unparse(node).split('\n'))

    def _calculate_complexity(self, node) -> int:
        """计算圈复杂度"""
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
                if child.ifs:
                    complexity += len(child.ifs)

        return complexity


def analyze_python_file(file_path: Path) -> Tuple[FileMetrics, List[Issue]]:
    """分析 Python 文件"""
    metrics = FileMetrics(path=str(file_path))
    issues = []

    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
    except Exception as e:
        issues.append(Issue(
            severity=Severity.ERROR,
            category="文件",
            message=f"无法读取文件: {e}",
            file_path=str(file_path)
        ))
        return metrics, issues

    # 基础行数统计
    metrics.lines = len(lines)
    in_multiline_string = False

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if not stripped:
            metrics.blank_lines += 1
        elif stripped.startswith('#'):
            metrics.comment_lines += 1
        elif '"""' in stripped or "'''" in stripped:
            if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                metrics.comment_lines += 1
            else:
                in_multiline_string = not in_multiline_string
                metrics.comment_lines += 1
        elif in_multiline_string:
            metrics.comment_lines += 1
        else:
            metrics.code_lines += 1

        # 检查行长度
        if len(line) > MAX_LINE_LENGTH:
            issues.append(Issue(
                severity=Severity.INFO,
                category="格式",
                message=f"行过长 ({len(line)} > {MAX_LINE_LENGTH})",
                file_path=str(file_path),
                line_number=i
            ))

    # 检查文件长度
    if metrics.code_lines > MAX_FILE_LENGTH:
        issues.append(Issue(
            severity=Severity.WARNING,
            category="复杂度",
            message=f"文件过长 ({metrics.code_lines} 行代码 > {MAX_FILE_LENGTH})",
            file_path=str(file_path),
            suggestion="考虑拆分为多个模块"
        ))

    # AST 分析
    analyzer = PythonAnalyzer(str(file_path), content)
    ast_issues, functions, classes, complexity = analyzer.analyze()
    issues.extend(ast_issues)

    metrics.functions = len(functions)
    metrics.classes = len(classes)
    metrics.max_complexity = complexity

    if functions:
        metrics.avg_function_length = sum(f["length"] for f in functions) / len(functions)

    return metrics, issues


def analyze_generic_file(file_path: Path) -> Tuple[FileMetrics, List[Issue]]:
    """分析通用代码文件"""
    metrics = FileMetrics(path=str(file_path))
    issues = []

    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
    except Exception:
        return metrics, issues

    metrics.lines = len(lines)

    comment_patterns = {
        '.js': '//',
        '.ts': '//',
        '.go': '//',
        '.java': '//',
        '.c': '//',
        '.cpp': '//',
        '.rs': '//',
    }

    suffix = file_path.suffix.lower()
    comment_prefix = comment_patterns.get(suffix, '//')

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if not stripped:
            metrics.blank_lines += 1
        elif stripped.startswith(comment_prefix) or stripped.startswith('/*') or stripped.startswith('*'):
            metrics.comment_lines += 1
        else:
            metrics.code_lines += 1

        if len(line) > MAX_LINE_LENGTH:
            issues.append(Issue(
                severity=Severity.INFO,
                category="格式",
                message=f"行过长 ({len(line)} > {MAX_LINE_LENGTH})",
                file_path=str(file_path),
                line_number=i
            ))

    if metrics.code_lines > MAX_FILE_LENGTH:
        issues.append(Issue(
            severity=Severity.WARNING,
            category="复杂度",
            message=f"文件过长 ({metrics.code_lines} 行代码 > {MAX_FILE_LENGTH})",
            file_path=str(file_path),
            suggestion="考虑拆分为多个模块"
        ))

    return metrics, issues


def scan_directory(path: str, exclude_dirs: List[str] = None) -> QualityResult:
    """扫描目录"""
    scan_path = Path(path).resolve()
    result = QualityResult(scan_path=str(scan_path))

    if exclude_dirs is None:
        exclude_dirs = ['.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build', '.tox']

    code_extensions = {'.py', '.js', '.ts', '.go', '.java', '.rs', '.c', '.cpp'}

    for file_path in scan_path.rglob('*'):
        if any(ex in file_path.parts for ex in exclude_dirs):
            continue

        if file_path.is_file() and file_path.suffix.lower() in code_extensions:
            result.files_scanned += 1

            if file_path.suffix.lower() == '.py':
                metrics, issues = analyze_python_file(file_path)
            else:
                metrics, issues = analyze_generic_file(file_path)

            result.file_metrics.append(metrics)
            result.issues.extend(issues)
            result.total_lines += metrics.lines
            result.total_code_lines += metrics.code_lines

    return result


def format_report(result: QualityResult, verbose: bool = False) -> str:
    """格式化报告"""
    lines = []
    lines.append("=" * 60)
    lines.append("代码质量检查报告")
    lines.append("=" * 60)

    lines.append(f"\n扫描路径: {result.scan_path}")
    lines.append(f"扫描文件: {result.files_scanned}")
    lines.append(f"总行数: {result.total_lines}")
    lines.append(f"代码行数: {result.total_code_lines}")
    lines.append(f"检查结果: {'✓ 通过' if result.passed else '✗ 需要关注'}")
    lines.append(f"错误: {result.error_count} | 警告: {result.warning_count}")

    if result.issues:
        lines.append("\n" + "-" * 40)
        lines.append("问题列表:")
        lines.append("-" * 40)

        # 按类别分组
        by_category = defaultdict(list)
        for issue in result.issues:
            by_category[issue.category].append(issue)

        severity_icons = {"error": "✗", "warning": "⚠", "info": "ℹ"}

        for category, issues in sorted(by_category.items()):
            lines.append(f"\n【{category}】({len(issues)} 个)")
            for issue in issues[:10]:  # 每类最多显示 10 个
                icon = severity_icons[issue.severity.value]
                loc = f":{issue.line_number}" if issue.line_number else ""
                lines.append(f"  {icon} {issue.file_path}{loc}")
                lines.append(f"    {issue.message}")
                if verbose and issue.suggestion:
                    lines.append(f"    💡 {issue.suggestion}")

            if len(issues) > 10:
                lines.append(f"  ... 及其他 {len(issues) - 10} 个问题")

    if verbose and result.file_metrics:
        # 找出最复杂的文件
        complex_files = sorted(result.file_metrics, key=lambda m: m.max_complexity, reverse=True)[:5]
        if complex_files and complex_files[0].max_complexity > 0:
            lines.append("\n" + "-" * 40)
            lines.append("复杂度最高的文件:")
            lines.append("-" * 40)
            for m in complex_files:
                if m.max_complexity > 0:
                    lines.append(f"  {m.path}: 复杂度 {m.max_complexity}, {m.functions} 个函数")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="代码质量检查器")
    parser.add_argument("path", nargs="?", default=".", help="扫描路径")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    result = scan_directory(args.path)

    if args.json:
        output = {
            "scan_path": result.scan_path,
            "files_scanned": result.files_scanned,
            "total_lines": result.total_lines,
            "total_code_lines": result.total_code_lines,
            "passed": result.passed,
            "error_count": result.error_count,
            "warning_count": result.warning_count,
            "issues": [
                {
                    "severity": i.severity.value,
                    "category": i.category,
                    "message": i.message,
                    "file_path": i.file_path,
                    "line_number": i.line_number,
                    "suggestion": i.suggestion
                }
                for i in result.issues
            ]
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(format_report(result, args.verbose))

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
