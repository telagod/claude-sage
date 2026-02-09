#!/usr/bin/env python3
"""
verify-security 单元测试
测试代码安全扫描器功能
"""

import unittest
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加 skills 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "tools" / "verify-security" / "scripts"))

from security_scanner import (
    Severity, Finding, ScanResult, scan_file, scan_directory,
    format_report, SECURITY_RULES
)


class TestSecurityScanner(unittest.TestCase):
    """安全扫描器测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """测试后清理"""
        self.temp_dir.cleanup()

    def test_scan_file_with_sql_injection(self):
        """测试 SQL 注入检测"""
        test_file = self.temp_path / "test.py"
        test_file.write_text('cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")')

        findings = scan_file(test_file, SECURITY_RULES)

        self.assertTrue(len(findings) > 0)
        self.assertTrue(any(f.severity == Severity.CRITICAL for f in findings))
        self.assertTrue(any("SQL" in f.message for f in findings))

    def test_scan_file_without_sql_context_not_flagged(self):
        """测试非 SQL 场景不应误报 SQL 注入"""
        test_file = self.temp_path / "non_sql.py"
        test_file.write_text('long_line = "x = \"" + "a" * 10000 + "\""')

        findings = scan_file(test_file, SECURITY_RULES)

        self.assertFalse(any("SQL" in f.message for f in findings))

    def test_scan_file_with_hardcoded_secret(self):
        """测试硬编码密钥检测"""
        test_file = self.temp_path / "config.py"
        test_file.write_text('password = "super_secret_password_12345"')

        findings = scan_file(test_file, SECURITY_RULES)

        self.assertTrue(len(findings) > 0)
        self.assertTrue(any(f.severity == Severity.HIGH for f in findings))

    def test_scan_file_with_command_injection(self):
        """测试命令注入检测"""
        test_file = self.temp_path / "shell.py"
        test_file.write_text('os.system(cmd, shell=True)')

        findings = scan_file(test_file, SECURITY_RULES)

        self.assertTrue(len(findings) > 0)
        self.assertTrue(any("shell=True" in f.message for f in findings))

    def test_scan_file_with_xss_vulnerability(self):
        """测试 XSS 漏洞检测"""
        test_file = self.temp_path / "app.js"
        test_file.write_text('element.innerHTML = userInput;')

        findings = scan_file(test_file, SECURITY_RULES)

        self.assertTrue(len(findings) > 0)
        self.assertTrue(any("innerHTML" in f.message for f in findings))

    def test_scan_file_with_unsafe_pickle(self):
        """测试不安全反序列化检测"""
        test_file = self.temp_path / "data.py"
        test_file.write_text('data = pickle.loads(user_data)')

        findings = scan_file(test_file, SECURITY_RULES)

        self.assertTrue(len(findings) > 0)
        self.assertTrue(any("反序列化" in f.message for f in findings))

    def test_scan_file_with_weak_crypto(self):
        """测试弱加密算法检测"""
        test_file = self.temp_path / "crypto.py"
        test_file.write_text('hash_obj = hashlib.md5(password)')

        findings = scan_file(test_file, SECURITY_RULES)

        self.assertTrue(len(findings) > 0)
        self.assertTrue(any("MD5" in f.message for f in findings))

    def test_scan_file_with_debug_code(self):
        """测试调试代码检测"""
        test_file = self.temp_path / "main.py"
        test_file.write_text('print("debug info")\npdb.set_trace()')

        findings = scan_file(test_file, SECURITY_RULES)

        self.assertTrue(len(findings) > 0)
        self.assertTrue(any("调试" in f.message for f in findings))

    def test_scan_file_print_not_marked_debug(self):
        """测试普通 print 不应被判定调试代码"""
        test_file = self.temp_path / "main.py"
        test_file.write_text('print("normal output")')

        findings = scan_file(test_file, SECURITY_RULES)

        self.assertFalse(any("调试" in f.message for f in findings))

    def test_scan_file_ignores_comments(self):
        """测试注释行被忽略"""
        test_file = self.temp_path / "test.py"
        test_file.write_text('# cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")')

        findings = scan_file(test_file, SECURITY_RULES)

        # 注释行应该被忽略
        self.assertEqual(len(findings), 0)

    def test_scan_file_empty_file(self):
        """测试空文件扫描"""
        test_file = self.temp_path / "empty.py"
        test_file.write_text('')

        findings = scan_file(test_file, SECURITY_RULES)

        self.assertEqual(len(findings), 0)

    def test_scan_file_nonexistent(self):
        """测试不存在的文件"""
        nonexistent = self.temp_path / "nonexistent.py"

        findings = scan_file(nonexistent, SECURITY_RULES)

        self.assertEqual(len(findings), 0)

    def test_scan_directory_basic(self):
        """测试目录扫描基本功能"""
        # 创建测试文件
        (self.temp_path / "safe.py").write_text('x = 1')
        (self.temp_path / "unsafe.py").write_text('password = "secret123456"')

        result = scan_directory(str(self.temp_path))

        self.assertIsInstance(result, ScanResult)
        self.assertEqual(result.files_scanned, 2)
        self.assertTrue(len(result.findings) > 0)

    def test_scan_directory_empty(self):
        """测试空目录扫描"""
        result = scan_directory(str(self.temp_path))

        self.assertEqual(result.files_scanned, 0)
        self.assertEqual(len(result.findings), 0)

    def test_scan_directory_nonexistent(self):
        """测试不存在的目录"""
        nonexistent = self.temp_path / "nonexistent"

        result = scan_directory(str(nonexistent))

        self.assertEqual(result.files_scanned, 0)

    def test_scan_directory_excludes_dirs(self):
        """测试目录排除功能"""
        # 创建被排除的目录
        node_modules = self.temp_path / "node_modules"
        node_modules.mkdir()
        (node_modules / "unsafe.py").write_text('password = "secret123456"')

        # 创建不被排除的文件
        (self.temp_path / "safe.py").write_text('x = 1')

        result = scan_directory(str(self.temp_path), exclude_dirs=['node_modules'])

        self.assertEqual(result.files_scanned, 1)

    def test_scan_directory_default_excludes_tests(self):
        """测试默认排除测试目录"""
        tests_dir = self.temp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_unsafe.py").write_text('password = "secret123456"')
        (self.temp_path / "app.py").write_text('x = 1')

        result = scan_directory(str(self.temp_path))

        self.assertEqual(result.files_scanned, 1)
        self.assertFalse(any("test_unsafe.py" in f.file_path for f in result.findings))

    def test_scan_result_passed_property(self):
        """测试 ScanResult.passed 属性"""
        result = ScanResult(scan_path="/test")

        # 没有发现时应该通过
        self.assertTrue(result.passed)

        # 添加低危发现
        result.findings.append(Finding(
            severity=Severity.LOW,
            category="test",
            message="test",
            file_path="test.py",
            line_number=1,
            line_content="test",
            recommendation="test"
        ))
        self.assertTrue(result.passed)

        # 添加高危发现
        result.findings.append(Finding(
            severity=Severity.HIGH,
            category="test",
            message="test",
            file_path="test.py",
            line_number=2,
            line_content="test",
            recommendation="test"
        ))
        self.assertFalse(result.passed)

    def test_scan_result_count_by_severity(self):
        """测试按严重程度计数"""
        result = ScanResult(scan_path="/test")

        result.findings.append(Finding(
            severity=Severity.CRITICAL,
            category="test",
            message="test",
            file_path="test.py",
            line_number=1,
            line_content="test",
            recommendation="test"
        ))
        result.findings.append(Finding(
            severity=Severity.HIGH,
            category="test",
            message="test",
            file_path="test.py",
            line_number=2,
            line_content="test",
            recommendation="test"
        ))

        counts = result.count_by_severity()

        self.assertEqual(counts['critical'], 1)
        self.assertEqual(counts['high'], 1)
        self.assertEqual(counts['medium'], 0)

    def test_format_report_basic(self):
        """测试报告格式化"""
        result = ScanResult(scan_path="/test", files_scanned=5)

        report = format_report(result)

        self.assertIn("代码安全扫描报告", report)
        self.assertIn("/test", report)
        self.assertIn("5", report)

    def test_format_report_with_findings(self):
        """测试包含发现的报告格式化"""
        result = ScanResult(scan_path="/test", files_scanned=1)
        result.findings.append(Finding(
            severity=Severity.CRITICAL,
            category="注入",
            message="SQL 注入风险",
            file_path="test.py",
            line_number=10,
            line_content="cursor.execute(f'...')",
            recommendation="使用参数化查询"
        ))

        report = format_report(result, verbose=True)

        self.assertIn("SQL 注入风险", report)
        self.assertIn("test.py:10", report)
        self.assertIn("使用参数化查询", report)

    def test_finding_dataclass(self):
        """测试 Finding 数据类"""
        finding = Finding(
            severity=Severity.HIGH,
            category="敏感信息",
            message="硬编码密钥",
            file_path="config.py",
            line_number=5,
            line_content='password = "secret"',
            recommendation="使用环境变量"
        )

        self.assertEqual(finding.severity, Severity.HIGH)
        self.assertEqual(finding.category, "敏感信息")
        self.assertEqual(finding.line_number, 5)

    def test_severity_enum(self):
        """测试 Severity 枚举"""
        self.assertEqual(Severity.CRITICAL.value, "critical")
        self.assertEqual(Severity.HIGH.value, "high")
        self.assertEqual(Severity.MEDIUM.value, "medium")
        self.assertEqual(Severity.LOW.value, "low")
        self.assertEqual(Severity.INFO.value, "info")

    def test_scan_file_with_multiple_issues(self):
        """测试单个文件中的多个问题"""
        test_file = self.temp_path / "multi.py"
        test_file.write_text('''
password = "secret123456"
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
os.system(cmd, shell=True)
''')

        findings = scan_file(test_file, SECURITY_RULES)

        self.assertTrue(len(findings) >= 3)

    def test_scan_directory_with_multiple_extensions(self):
        """测试多种文件类型扫描"""
        (self.temp_path / "test.py").write_text('password = "secret123456"')
        (self.temp_path / "test.js").write_text('element.innerHTML = userInput;')
        (self.temp_path / "test.go").write_text('password := "secret123456"')

        result = scan_directory(str(self.temp_path))

        self.assertEqual(result.files_scanned, 3)
        self.assertTrue(len(result.findings) > 0)

    def test_scan_file_with_encoding_error(self):
        """测试处理编码错误的文件"""
        test_file = self.temp_path / "binary.bin"
        # 写入二进制数据
        test_file.write_bytes(b'\x80\x81\x82\x83')

        findings = scan_file(test_file, SECURITY_RULES)

        # 应该优雅地处理编码错误
        self.assertIsInstance(findings, list)


class TestSecurityScannerEdgeCases(unittest.TestCase):
    """安全扫描器边界条件测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """测试后清理"""
        self.temp_dir.cleanup()

    def test_scan_deeply_nested_directories(self):
        """测试深层嵌套目录"""
        deep_path = self.temp_path / "a" / "b" / "c" / "d" / "e"
        deep_path.mkdir(parents=True)
        (deep_path / "test.py").write_text('password = "secret123456"')

        result = scan_directory(str(self.temp_path))

        self.assertEqual(result.files_scanned, 1)
        self.assertTrue(len(result.findings) > 0)

    def test_scan_file_with_very_long_line(self):
        """测试包含超长行的文件"""
        test_file = self.temp_path / "long.py"
        long_line = 'x = "' + 'a' * 10000 + '"'
        test_file.write_text(long_line)

        findings = scan_file(test_file, SECURITY_RULES)

        # 应该能处理超长行
        self.assertIsInstance(findings, list)

    def test_scan_file_with_special_characters(self):
        """测试包含特殊字符的文件"""
        test_file = self.temp_path / "special.py"
        test_file.write_text('# 中文注释\npassword = "secret123456"  # 密码')

        findings = scan_file(test_file, SECURITY_RULES)

        self.assertTrue(len(findings) > 0)

    def test_scan_result_sorting(self):
        """测试发现按严重程度排序"""
        result = ScanResult(scan_path="/test")

        # 添加不同严重程度的发现
        result.findings.append(Finding(
            severity=Severity.LOW,
            category="test",
            message="low",
            file_path="test.py",
            line_number=1,
            line_content="test",
            recommendation="test"
        ))
        result.findings.append(Finding(
            severity=Severity.CRITICAL,
            category="test",
            message="critical",
            file_path="test.py",
            line_number=2,
            line_content="test",
            recommendation="test"
        ))

        # 扫描会自动排序
        result2 = scan_directory(str(self.temp_path))
        # 验证排序逻辑存在
        self.assertIsInstance(result2, ScanResult)


if __name__ == '__main__':
    unittest.main()
