#!/usr/bin/env python3
"""
verify-module: 模块完整性校验 Skill
扫描目录结构、检测缺失文档、验证代码与文档同步
"""

import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Set
from enum import Enum


class CheckStatus(Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    message: str
    details: List[str] = field(default_factory=list)


@dataclass
class ModuleReport:
    passed: bool = True
    checks: List[CheckResult] = field(default_factory=list)

    def add_check(self, check: CheckResult):
        self.checks.append(check)
        if check.status == CheckStatus.FAIL:
            self.passed = False


REQUIRED_FILES = ["README.md"]
RECOMMENDED_FILES = ["DESIGN.md"]
CODE_DIRS = ["src", "lib", "pkg", "cmd", "internal", "app"]
TEST_PATTERNS = ["tests", "test", "__tests__", "spec", "*_test.go", "*_test.py", "*.test.ts", "*.spec.ts"]


def check_readme(target_path: Path, report: ModuleReport):
    """检查 README.md 存在性和内容"""
    readme_path = target_path / "README.md"

    if not readme_path.exists():
        report.add_check(CheckResult(
            name="README.md 存在性",
            status=CheckStatus.FAIL,
            message="缺少 README.md 文件",
            details=["模块必须包含 README.md 说明文档"],
        ))
        return

    content = readme_path.read_text(encoding="utf-8", errors="ignore")
    issues = []

    if len(content) < 100:
        issues.append("README.md 内容过少（< 100 字符）")

    required_sections = ["#"]
    if not any(section in content for section in required_sections):
        issues.append("README.md 缺少标题")

    if issues:
        report.add_check(CheckResult(
            name="README.md 内容",
            status=CheckStatus.WARN,
            message="README.md 内容不完整",
            details=issues,
        ))
    else:
        report.add_check(CheckResult(
            name="README.md",
            status=CheckStatus.PASS,
            message="README.md 存在且内容充实",
        ))


def check_design_doc(target_path: Path, report: ModuleReport):
    """检查 DESIGN.md 存在性"""
    design_path = target_path / "DESIGN.md"

    if not design_path.exists():
        report.add_check(CheckResult(
            name="DESIGN.md 存在性",
            status=CheckStatus.WARN,
            message="缺少 DESIGN.md 文件",
            details=["建议添加 DESIGN.md 记录设计决策"],
        ))
        return

    content = design_path.read_text(encoding="utf-8", errors="ignore")

    if len(content) < 50:
        report.add_check(CheckResult(
            name="DESIGN.md 内容",
            status=CheckStatus.WARN,
            message="DESIGN.md 内容过少",
            details=["DESIGN.md 应包含设计决策和权衡说明"],
        ))
    else:
        report.add_check(CheckResult(
            name="DESIGN.md",
            status=CheckStatus.PASS,
            message="DESIGN.md 存在且有内容",
        ))


def check_code_structure(target_path: Path, report: ModuleReport):
    """检查代码目录结构"""
    found_code_dirs = []
    code_files = []

    for code_dir in CODE_DIRS:
        dir_path = target_path / code_dir
        if dir_path.exists() and dir_path.is_dir():
            found_code_dirs.append(code_dir)

    code_extensions = {".py", ".js", ".ts", ".go", ".rs", ".java", ".kt", ".rb", ".php"}
    for item in target_path.iterdir():
        if item.is_file() and item.suffix in code_extensions:
            code_files.append(item.name)

    if not found_code_dirs and not code_files:
        report.add_check(CheckResult(
            name="代码结构",
            status=CheckStatus.WARN,
            message="未检测到标准代码目录或代码文件",
            details=[f"建议使用标准目录: {', '.join(CODE_DIRS)}"],
        ))
    else:
        details = []
        if found_code_dirs:
            details.append(f"代码目录: {', '.join(found_code_dirs)}")
        if code_files:
            details.append(f"根目录代码文件: {len(code_files)} 个")

        report.add_check(CheckResult(
            name="代码结构",
            status=CheckStatus.PASS,
            message="检测到代码文件/目录",
            details=details,
        ))


def check_tests(target_path: Path, report: ModuleReport):
    """检查测试目录/文件"""
    has_tests = False
    test_locations = []

    for pattern in ["tests", "test", "__tests__", "spec"]:
        test_dir = target_path / pattern
        if test_dir.exists() and test_dir.is_dir():
            has_tests = True
            test_locations.append(str(test_dir.relative_to(target_path)))

    test_file_patterns = ["*_test.py", "*_test.go", "*.test.ts", "*.test.js", "*.spec.ts", "*.spec.js", "test_*.py"]
    for pattern in test_file_patterns:
        for test_file in target_path.rglob(pattern):
            has_tests = True
            test_locations.append(str(test_file.relative_to(target_path)))
            if len(test_locations) > 5:
                break

    if not has_tests:
        report.add_check(CheckResult(
            name="测试",
            status=CheckStatus.WARN,
            message="未检测到测试文件/目录",
            details=["建议添加测试用例确保代码质量"],
        ))
    else:
        report.add_check(CheckResult(
            name="测试",
            status=CheckStatus.PASS,
            message="检测到测试文件/目录",
            details=test_locations[:5] + (["..."] if len(test_locations) > 5 else []),
        ))


def check_gitignore(target_path: Path, report: ModuleReport):
    """检查 .gitignore"""
    gitignore_path = target_path / ".gitignore"

    if not gitignore_path.exists():
        report.add_check(CheckResult(
            name=".gitignore",
            status=CheckStatus.WARN,
            message="缺少 .gitignore 文件",
            details=["建议添加 .gitignore 避免提交不必要的文件"],
        ))
    else:
        report.add_check(CheckResult(
            name=".gitignore",
            status=CheckStatus.PASS,
            message=".gitignore 存在",
        ))


def check_license(target_path: Path, report: ModuleReport):
    """检查 LICENSE 文件"""
    license_files = ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"]

    has_license = any((target_path / f).exists() for f in license_files)

    if not has_license:
        report.add_check(CheckResult(
            name="LICENSE",
            status=CheckStatus.WARN,
            message="缺少 LICENSE 文件",
            details=["开源项目建议添加许可证文件"],
        ))
    else:
        report.add_check(CheckResult(
            name="LICENSE",
            status=CheckStatus.PASS,
            message="LICENSE 文件存在",
        ))


def print_report(report: ModuleReport, json_output: bool = False):
    """输出报告"""
    if json_output:
        output = {
            "passed": report.passed,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "details": c.details,
                }
                for c in report.checks
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print("")
    print("=" * 60)
    print("  校验报告: verify-module")
    print("=" * 60)
    print("")

    status = "✓ 通过" if report.passed else "✗ 未通过"
    print(f"  状态: {status}")
    print("")

    pass_count = len([c for c in report.checks if c.status == CheckStatus.PASS])
    warn_count = len([c for c in report.checks if c.status == CheckStatus.WARN])
    fail_count = len([c for c in report.checks if c.status == CheckStatus.FAIL])

    print(f"  ✓ 通过: {pass_count}")
    print(f"  ⚠ 警告: {warn_count}")
    print(f"  ✗ 失败: {fail_count}")
    print("")

    print("-" * 60)
    print("  检查详情:")
    print("-" * 60)

    status_icons = {
        CheckStatus.PASS: "✓",
        CheckStatus.WARN: "⚠",
        CheckStatus.FAIL: "✗",
    }

    for check in report.checks:
        icon = status_icons[check.status]
        print(f"\n  [{icon}] {check.name}")
        print(f"      {check.message}")
        for detail in check.details:
            print(f"      - {detail}")

    print("")
    print("=" * 60)
    conclusion = "可交付" if report.passed else "需修复后交付"
    print(f"  【结论】{conclusion}")
    print("=" * 60)
    print("")


def main(args: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="模块完整性校验 - 检查目录结构和文档",
        prog="verify-module",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="要检查的模块路径 (默认: 当前目录)",
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

    if not target_path.is_dir():
        print(f"[✗] 路径不是目录: {target_path}")
        return 1

    report = ModuleReport()

    if parsed.verbose:
        print(f"[i] 检查目标: {target_path}")

    check_readme(target_path, report)
    check_design_doc(target_path, report)
    check_code_structure(target_path, report)
    check_tests(target_path, report)
    check_gitignore(target_path, report)
    check_license(target_path, report)

    print_report(report, json_output=parsed.json)

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
