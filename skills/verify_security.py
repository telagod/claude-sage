#!/usr/bin/env python3
"""
verify-security: 安全校验 Skill
扫描代码安全漏洞，检测危险模式，确保安全决策有文档记录
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from enum import Enum


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    severity: Severity
    category: str
    message: str
    file: str
    line: int
    code_snippet: str = ""
    recommendation: str = ""


@dataclass
class SecurityReport:
    passed: bool = True
    findings: List[Finding] = field(default_factory=list)
    summary: dict = field(default_factory=dict)

    def add_finding(self, finding: Finding):
        self.findings.append(finding)
        if finding.severity in [Severity.CRITICAL, Severity.HIGH]:
            self.passed = False

    def generate_summary(self):
        self.summary = {
            "critical": len([f for f in self.findings if f.severity == Severity.CRITICAL]),
            "high": len([f for f in self.findings if f.severity == Severity.HIGH]),
            "medium": len([f for f in self.findings if f.severity == Severity.MEDIUM]),
            "low": len([f for f in self.findings if f.severity == Severity.LOW]),
            "info": len([f for f in self.findings if f.severity == Severity.INFO]),
            "total": len(self.findings),
        }


DANGEROUS_PATTERNS = [
    {
        "pattern": r"eval\s*\(",
        "severity": Severity.HIGH,
        "category": "代码注入",
        "message": "检测到 eval() 使用，可能导致代码注入",
        "recommendation": "避免使用 eval()，使用 ast.literal_eval() 或其他安全替代方案",
    },
    {
        "pattern": r"exec\s*\(",
        "severity": Severity.HIGH,
        "category": "代码注入",
        "message": "检测到 exec() 使用，可能导致代码注入",
        "recommendation": "避免使用 exec()，重构代码逻辑",
    },
    {
        "pattern": r"subprocess\..*shell\s*=\s*True",
        "severity": Severity.HIGH,
        "category": "命令注入",
        "message": "subprocess 使用 shell=True，可能导致命令注入",
        "recommendation": "使用 shell=False 并传递参数列表",
    },
    {
        "pattern": r"os\.system\s*\(",
        "severity": Severity.HIGH,
        "category": "命令注入",
        "message": "检测到 os.system() 使用，可能导致命令注入",
        "recommendation": "使用 subprocess.run() 替代，避免 shell=True",
    },
    {
        "pattern": r"pickle\.loads?\s*\(",
        "severity": Severity.HIGH,
        "category": "反序列化",
        "message": "检测到 pickle 反序列化，可能导致任意代码执行",
        "recommendation": "使用 JSON 或其他安全的序列化格式",
    },
    {
        "pattern": r"yaml\.load\s*\([^)]*\)",
        "severity": Severity.MEDIUM,
        "category": "反序列化",
        "message": "检测到不安全的 YAML 加载",
        "recommendation": "使用 yaml.safe_load() 替代 yaml.load()",
    },
    {
        "pattern": r"(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]",
        "severity": Severity.HIGH,
        "category": "硬编码凭证",
        "message": "检测到硬编码的敏感信息",
        "recommendation": "使用环境变量或密钥管理服务",
    },
    {
        "pattern": r"md5\s*\(|hashlib\.md5",
        "severity": Severity.MEDIUM,
        "category": "弱加密",
        "message": "检测到 MD5 使用，不适合密码哈希",
        "recommendation": "使用 bcrypt、argon2 或 scrypt 进行密码哈希",
    },
    {
        "pattern": r"sha1\s*\(|hashlib\.sha1",
        "severity": Severity.LOW,
        "category": "弱加密",
        "message": "检测到 SHA1 使用，建议使用更强的哈希算法",
        "recommendation": "使用 SHA-256 或更强的哈希算法",
    },
    {
        "pattern": r"verify\s*=\s*False",
        "severity": Severity.HIGH,
        "category": "SSL/TLS",
        "message": "检测到禁用 SSL 证书验证",
        "recommendation": "启用 SSL 证书验证，配置正确的 CA 证书",
    },
    {
        "pattern": r"CORS\s*\(\s*\*|Access-Control-Allow-Origin.*\*",
        "severity": Severity.MEDIUM,
        "category": "CORS",
        "message": "检测到过于宽松的 CORS 配置",
        "recommendation": "限制允许的源，避免使用通配符",
    },
    {
        "pattern": r"innerHTML\s*=|\.html\s*\(",
        "severity": Severity.MEDIUM,
        "category": "XSS",
        "message": "检测到可能的 XSS 风险",
        "recommendation": "使用 textContent 或进行 HTML 转义",
    },
    {
        "pattern": r"SELECT.*\+.*\"|f['\"]SELECT|\.format\(.*SELECT",
        "severity": Severity.HIGH,
        "category": "SQL 注入",
        "message": "检测到可能的 SQL 注入风险",
        "recommendation": "使用参数化查询或 ORM",
    },
    {
        "pattern": r"random\.(random|randint|choice)\s*\(",
        "severity": Severity.LOW,
        "category": "弱随机数",
        "message": "检测到使用非加密安全的随机数生成器",
        "recommendation": "安全场景使用 secrets 模块",
    },
    {
        "pattern": r"DEBUG\s*=\s*True",
        "severity": Severity.MEDIUM,
        "category": "配置",
        "message": "检测到 DEBUG 模式开启",
        "recommendation": "生产环境确保 DEBUG=False",
    },
]

SKIP_DIRS = {
    ".git", ".svn", ".hg",
    "node_modules", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".nuxt",
    "vendor", "third_party",
}

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".go", ".rs", ".java", ".kt",
    ".php", ".rb", ".sh", ".bash",
    ".sql", ".html", ".vue", ".svelte",
}


def should_skip_dir(dir_name: str) -> bool:
    return dir_name in SKIP_DIRS or dir_name.startswith(".")


def should_scan_file(file_path: Path) -> bool:
    return file_path.suffix.lower() in CODE_EXTENSIONS


def scan_file(file_path: Path, report: SecurityReport):
    """扫描单个文件"""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            for pattern_info in DANGEROUS_PATTERNS:
                if re.search(pattern_info["pattern"], line, re.IGNORECASE):
                    finding = Finding(
                        severity=pattern_info["severity"],
                        category=pattern_info["category"],
                        message=pattern_info["message"],
                        file=str(file_path),
                        line=i,
                        code_snippet=line.strip()[:100],
                        recommendation=pattern_info["recommendation"],
                    )
                    report.add_finding(finding)
    except Exception as e:
        report.add_finding(Finding(
            severity=Severity.INFO,
            category="扫描错误",
            message=f"无法扫描文件: {e}",
            file=str(file_path),
            line=0,
        ))


def scan_directory(target_path: Path, report: SecurityReport):
    """递归扫描目录"""
    if target_path.is_file():
        if should_scan_file(target_path):
            scan_file(target_path, report)
        return

    for item in target_path.iterdir():
        if item.is_dir():
            if not should_skip_dir(item.name):
                scan_directory(item, report)
        elif item.is_file() and should_scan_file(item):
            scan_file(item, report)


def check_design_doc(target_path: Path, report: SecurityReport):
    """检查是否有安全决策文档"""
    design_files = list(target_path.glob("**/DESIGN.md"))

    if not design_files:
        report.add_finding(Finding(
            severity=Severity.LOW,
            category="文档",
            message="未找到 DESIGN.md，安全决策可能未记录",
            file=str(target_path),
            line=0,
            recommendation="创建 DESIGN.md 记录安全相关的设计决策",
        ))
        return

    for design_file in design_files:
        content = design_file.read_text(encoding="utf-8", errors="ignore").lower()
        security_keywords = ["security", "安全", "认证", "授权", "加密", "authentication", "authorization"]

        if not any(kw in content for kw in security_keywords):
            report.add_finding(Finding(
                severity=Severity.INFO,
                category="文档",
                message="DESIGN.md 中未发现安全相关章节",
                file=str(design_file),
                line=0,
                recommendation="在 DESIGN.md 中添加安全决策章节",
            ))


def print_report(report: SecurityReport, json_output: bool = False):
    """输出报告"""
    report.generate_summary()

    if json_output:
        output = {
            "passed": report.passed,
            "summary": report.summary,
            "findings": [
                {
                    "severity": f.severity.value,
                    "category": f.category,
                    "message": f.message,
                    "file": f.file,
                    "line": f.line,
                    "code_snippet": f.code_snippet,
                    "recommendation": f.recommendation,
                }
                for f in report.findings
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print("")
    print("=" * 60)
    print("  校验报告: verify-security")
    print("=" * 60)
    print("")

    status = "✓ 通过" if report.passed else "✗ 未通过"
    print(f"  状态: {status}")
    print("")
    print(f"  🔴 Critical: {report.summary['critical']}")
    print(f"  🟠 High:     {report.summary['high']}")
    print(f"  🟡 Medium:   {report.summary['medium']}")
    print(f"  🔵 Low:      {report.summary['low']}")
    print(f"  ⚪ Info:     {report.summary['info']}")
    print("")

    if report.findings:
        print("-" * 60)
        print("  详细发现:")
        print("-" * 60)

        for i, f in enumerate(report.findings, 1):
            severity_icons = {
                Severity.CRITICAL: "🔴",
                Severity.HIGH: "🟠",
                Severity.MEDIUM: "🟡",
                Severity.LOW: "🔵",
                Severity.INFO: "⚪",
            }
            icon = severity_icons.get(f.severity, "⚪")

            print(f"\n  [{i}] {icon} [{f.severity.value.upper()}] {f.category}")
            print(f"      文件: {f.file}:{f.line}")
            print(f"      问题: {f.message}")
            if f.code_snippet:
                print(f"      代码: {f.code_snippet}")
            if f.recommendation:
                print(f"      建议: {f.recommendation}")

    print("")
    print("=" * 60)
    conclusion = "可交付" if report.passed else "需修复后交付"
    print(f"  【结论】{conclusion}")
    print("=" * 60)
    print("")


def main(args: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="安全校验 - 扫描代码安全漏洞",
        prog="verify-security",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="要扫描的目录或文件路径 (默认: 当前目录)",
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

    report = SecurityReport()

    if parsed.verbose:
        print(f"[i] 扫描目标: {target_path}")

    scan_directory(target_path, report)
    check_design_doc(target_path, report)

    print_report(report, json_output=parsed.json)

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
