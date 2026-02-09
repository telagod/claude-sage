#!/usr/bin/env python3
"""
模块结构扫描器
检测模块完整性：目录结构、必需文档、代码组织
"""

import os
import sys
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
    severity: Severity
    message: str
    path: Optional[str] = None


@dataclass
class ScanResult:
    module_path: str
    issues: List[Issue] = field(default_factory=list)
    structure: Dict = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return not any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)


REQUIRED_FILES = {
    "README.md": "模块说明文档",
    "DESIGN.md": "设计决策文档",
}

RECOMMENDED_DIRS = {
    "src": "源代码目录",
    "tests": "测试目录",
}

ALTERNATIVE_SRC_DIRS = ["src", "lib", "pkg", "internal", "cmd", "app"]
ALTERNATIVE_TEST_DIRS = ["tests", "test", "__tests__", "spec"]
ROOT_SCRIPT_FILES = {
    "install.sh",
    "uninstall.sh",
    "install.ps1",
    "uninstall.ps1",
    "Dockerfile",
    "Makefile",
}


def scan_module(path: str) -> ScanResult:
    """扫描模块完整性"""
    module_path = Path(path).resolve()
    result = ScanResult(module_path=str(module_path))

    if not module_path.exists():
        result.issues.append(Issue(
            severity=Severity.ERROR,
            message=f"路径不存在: {module_path}"
        ))
        return result

    if not module_path.is_dir():
        result.issues.append(Issue(
            severity=Severity.ERROR,
            message=f"不是目录: {module_path}"
        ))
        return result

    # 扫描目录结构
    result.structure = scan_structure(module_path)

    # 检查必需文档
    check_required_files(module_path, result)

    # 检查源码目录
    check_source_dirs(module_path, result)

    # 检查测试目录
    check_test_dirs(module_path, result)

    # 检查文档质量
    check_doc_quality(module_path, result)

    return result


def scan_structure(path: Path, depth: int = 3) -> Dict:
    """递归扫描目录结构"""
    structure = {"name": path.name, "type": "dir", "children": []}

    if depth <= 0:
        return structure

    try:
        for item in sorted(path.iterdir()):
            if item.name.startswith('.'):
                continue
            if item.is_file():
                structure["children"].append({
                    "name": item.name,
                    "type": "file",
                    "size": item.stat().st_size
                })
            elif item.is_dir():
                structure["children"].append(
                    scan_structure(item, depth - 1)
                )
    except PermissionError:
        pass

    return structure


def check_required_files(path: Path, result: ScanResult):
    """检查必需文件"""
    for filename, desc in REQUIRED_FILES.items():
        filepath = path / filename
        if not filepath.exists():
            result.issues.append(Issue(
                severity=Severity.ERROR,
                message=f"缺少必需文档: {filename} ({desc})",
                path=str(filepath)
            ))
        elif filepath.stat().st_size < 50:
            result.issues.append(Issue(
                severity=Severity.WARNING,
                message=f"文档内容过少: {filename} (< 50 bytes)",
                path=str(filepath)
            ))


def check_source_dirs(path: Path, result: ScanResult):
    """检查源码目录"""
    found = False
    for dirname in ALTERNATIVE_SRC_DIRS:
        if (path / dirname).is_dir():
            found = True
            break

    # 检查是否有代码文件在根目录
    code_extensions = {'.py', '.go', '.rs', '.ts', '.js', '.java', '.sh', '.ps1'}
    root_code_files = [f for f in path.iterdir()
                       if f.is_file() and f.suffix in code_extensions]
    root_script_files = [f for f in path.iterdir() if f.is_file() and f.name in ROOT_SCRIPT_FILES]

    if root_code_files or root_script_files:
        found = True
        if len(root_code_files) > 5:
            result.issues.append(Issue(
                severity=Severity.WARNING,
                message=f"根目录代码文件过多 ({len(root_code_files)}个)，建议整理到 src/ 目录"
            ))

    if not found:
        result.issues.append(Issue(
            severity=Severity.WARNING,
            message="未找到源码目录或代码文件"
        ))


def check_test_dirs(path: Path, result: ScanResult):
    """检查测试目录"""
    found = False
    for dirname in ALTERNATIVE_TEST_DIRS:
        if (path / dirname).is_dir():
            found = True
            break

    # 检查是否有测试文件
    test_patterns = ['test_', '_test.', '.test.', 'spec_', '_spec.']
    for f in path.rglob('*'):
        if f.is_file() and any(p in f.name for p in test_patterns):
            found = True
            break

    if not found:
        result.issues.append(Issue(
            severity=Severity.WARNING,
            message="未找到测试目录或测试文件"
        ))


def check_doc_quality(path: Path, result: ScanResult):
    """检查文档质量"""
    readme = path / "README.md"
    design = path / "DESIGN.md"

    if readme.exists():
        content = readme.read_text(encoding='utf-8', errors='ignore')

        # 检查必要章节
        required_sections = ['#']  # 至少有标题
        if not any(s in content for s in required_sections):
            result.issues.append(Issue(
                severity=Severity.WARNING,
                message="README.md 缺少标题",
                path=str(readme)
            ))

        # 检查使用说明
        usage_keywords = ['usage', 'install', '使用', '安装', 'example', '示例']
        if not any(k in content.lower() for k in usage_keywords):
            result.issues.append(Issue(
                severity=Severity.INFO,
                message="README.md 建议添加使用说明或示例",
                path=str(readme)
            ))

    if design.exists():
        content = design.read_text(encoding='utf-8', errors='ignore')

        # 检查设计决策记录
        decision_keywords = ['决策', 'decision', '选择', 'choice', '权衡', 'trade']
        if not any(k in content.lower() for k in decision_keywords):
            result.issues.append(Issue(
                severity=Severity.INFO,
                message="DESIGN.md 建议记录设计决策和权衡",
                path=str(design)
            ))


def format_report(result: ScanResult, verbose: bool = False) -> str:
    """格式化扫描报告"""
    lines = []
    lines.append("=" * 60)
    lines.append("模块完整性扫描报告")
    lines.append("=" * 60)
    lines.append(f"\n模块路径: {result.module_path}")
    lines.append(f"扫描结果: {'✓ 通过' if result.passed else '✗ 未通过'}")
    lines.append(f"错误: {result.error_count} | 警告: {result.warning_count}")

    if result.issues:
        lines.append("\n" + "-" * 40)
        lines.append("问题列表:")
        lines.append("-" * 40)

        for issue in result.issues:
            icon = {"error": "✗", "warning": "⚠", "info": "ℹ"}[issue.severity.value]
            lines.append(f"  {icon} [{issue.severity.value.upper()}] {issue.message}")
            if issue.path and verbose:
                lines.append(f"    路径: {issue.path}")

    if verbose and result.structure:
        lines.append("\n" + "-" * 40)
        lines.append("目录结构:")
        lines.append("-" * 40)
        lines.append(format_structure(result.structure))

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_structure(structure: Dict, indent: int = 0) -> str:
    """格式化目录结构"""
    lines = []
    prefix = "  " * indent

    if structure["type"] == "dir":
        lines.append(f"{prefix}📁 {structure['name']}/")
        for child in structure.get("children", []):
            lines.append(format_structure(child, indent + 1))
    else:
        size = structure.get("size", 0)
        size_str = f"({size} B)" if size < 1024 else f"({size // 1024} KB)"
        lines.append(f"{prefix}📄 {structure['name']} {size_str}")

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="模块完整性扫描器")
    parser.add_argument("path", nargs="?", default=".", help="模块路径")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    result = scan_module(args.path)

    if args.json:
        output = {
            "module_path": result.module_path,
            "passed": result.passed,
            "error_count": result.error_count,
            "warning_count": result.warning_count,
            "issues": [
                {"severity": i.severity.value, "message": i.message, "path": i.path}
                for i in result.issues
            ]
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(format_report(result, args.verbose))

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
