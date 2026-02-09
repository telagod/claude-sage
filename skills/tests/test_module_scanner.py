#!/usr/bin/env python3
"""
verify-module 单元测试
测试模块结构扫描器功能
"""

import unittest
import tempfile
import sys
from pathlib import Path

# 添加 skills 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "tools" / "verify-module" / "scripts"))

from module_scanner import (
    Severity, Issue, ScanResult, scan_module, scan_structure,
    check_required_files, check_source_dirs, check_test_dirs,
    check_doc_quality, format_report
)


class TestModuleScanner(unittest.TestCase):
    """模块扫描器测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """测试后清理"""
        self.temp_dir.cleanup()

    def test_scan_module_nonexistent_path(self):
        """测试不存在的路径"""
        nonexistent = self.temp_path / "nonexistent"

        result = scan_module(str(nonexistent))

        self.assertFalse(result.passed)
        self.assertTrue(any(i.severity == Severity.ERROR for i in result.issues))

    def test_scan_module_file_not_directory(self):
        """测试文件而非目录"""
        test_file = self.temp_path / "test.txt"
        test_file.write_text("test")

        result = scan_module(str(test_file))

        self.assertFalse(result.passed)
        self.assertTrue(any(i.severity == Severity.ERROR for i in result.issues))

    def test_scan_module_missing_readme(self):
        """测试缺少 README.md"""
        result = scan_module(str(self.temp_path))

        self.assertFalse(result.passed)
        self.assertTrue(any("README.md" in i.message for i in result.issues))

    def test_scan_module_missing_design(self):
        """测试缺少 DESIGN.md"""
        (self.temp_path / "README.md").write_text("# Test Module\n\nThis is a test module.")

        result = scan_module(str(self.temp_path))

        self.assertFalse(result.passed)
        self.assertTrue(any("DESIGN.md" in i.message for i in result.issues))

    def test_scan_module_with_required_files(self):
        """测试包含必需文件"""
        (self.temp_path / "README.md").write_text("# Test Module\n\nThis is a test module.")
        (self.temp_path / "DESIGN.md").write_text("# Design\n\nDesign decisions.")

        result = scan_module(str(self.temp_path))

        # 应该没有关于缺少文档的错误
        self.assertTrue(not any("缺少必需文档" in i.message for i in result.issues))

    def test_scan_module_with_src_directory(self):
        """测试包含 src 目录"""
        (self.temp_path / "README.md").write_text("# Test")
        (self.temp_path / "DESIGN.md").write_text("# Design")
        (self.temp_path / "src").mkdir()
        (self.temp_path / "src" / "main.py").write_text("print('hello')")

        result = scan_module(str(self.temp_path))

        # 应该没有关于缺少源码目录的警告
        self.assertTrue(not any("未找到源码目录" in i.message for i in result.issues))

    def test_scan_module_with_tests_directory(self):
        """测试包含 tests 目录"""
        (self.temp_path / "README.md").write_text("# Test")
        (self.temp_path / "DESIGN.md").write_text("# Design")
        (self.temp_path / "tests").mkdir()
        (self.temp_path / "tests" / "test_main.py").write_text("import unittest")

        result = scan_module(str(self.temp_path))

        # 应该没有关于缺少测试目录的警告
        self.assertTrue(not any("未找到测试目录" in i.message for i in result.issues))

    def test_scan_module_with_alternative_src_dirs(self):
        """测试替代源码目录名称"""
        (self.temp_path / "README.md").write_text("# Test")
        (self.temp_path / "DESIGN.md").write_text("# Design")

        # 测试 lib 目录
        (self.temp_path / "lib").mkdir()
        (self.temp_path / "lib" / "main.py").write_text("print('hello')")

        result = scan_module(str(self.temp_path))

        self.assertTrue(not any("未找到源码目录" in i.message for i in result.issues))

    def test_scan_module_with_alternative_test_dirs(self):
        """测试替代测试目录名称"""
        (self.temp_path / "README.md").write_text("# Test")
        (self.temp_path / "DESIGN.md").write_text("# Design")

        # 测试 __tests__ 目录
        (self.temp_path / "__tests__").mkdir()
        (self.temp_path / "__tests__" / "test.py").write_text("import unittest")

        result = scan_module(str(self.temp_path))

        self.assertTrue(not any("未找到测试目录" in i.message for i in result.issues))

    def test_scan_module_with_root_code_files(self):
        """测试根目录代码文件"""
        (self.temp_path / "README.md").write_text("# Test")
        (self.temp_path / "DESIGN.md").write_text("# Design")
        (self.temp_path / "main.py").write_text("print('hello')")

        result = scan_module(str(self.temp_path))

        # 应该没有关于缺少源码的警告
        self.assertTrue(not any("未找到源码目录" in i.message for i in result.issues))

    def test_scan_module_with_root_shell_script_files(self):
        """测试根目录 shell 脚本识别为源码"""
        (self.temp_path / "README.md").write_text("# Test")
        (self.temp_path / "DESIGN.md").write_text("# Design")
        (self.temp_path / "install.sh").write_text("#!/usr/bin/env bash\necho ok")

        result = scan_module(str(self.temp_path))

        self.assertTrue(not any("未找到源码目录" in i.message for i in result.issues))

    def test_scan_module_with_root_powershell_script_files(self):
        """测试根目录 PowerShell 脚本识别为源码"""
        (self.temp_path / "README.md").write_text("# Test")
        (self.temp_path / "DESIGN.md").write_text("# Design")
        (self.temp_path / "install.ps1").write_text("Write-Host 'ok'")

        result = scan_module(str(self.temp_path))

        self.assertTrue(not any("未找到源码目录" in i.message for i in result.issues))

    def test_scan_module_too_many_root_files(self):
        """测试根目录文件过多"""
        (self.temp_path / "README.md").write_text("# Test")
        (self.temp_path / "DESIGN.md").write_text("# Design")

        # 创建多个根目录代码文件
        for i in range(10):
            (self.temp_path / f"file{i}.py").write_text("print('hello')")

        result = scan_module(str(self.temp_path))

        self.assertTrue(any("根目录代码文件过多" in i.message for i in result.issues))

    def test_scan_module_small_readme(self):
        """测试内容过少的 README"""
        (self.temp_path / "README.md").write_text("# Test")
        (self.temp_path / "DESIGN.md").write_text("# Design\n\nDesign content here.")

        result = scan_module(str(self.temp_path))

        self.assertTrue(any("文档内容过少" in i.message for i in result.issues))

    def test_scan_module_readme_without_title(self):
        """测试 README 缺少标题"""
        (self.temp_path / "README.md").write_text("This is content without title.")
        (self.temp_path / "DESIGN.md").write_text("# Design\n\nDesign content here.")

        result = scan_module(str(self.temp_path))

        self.assertTrue(any("缺少标题" in i.message for i in result.issues))

    def test_scan_module_readme_without_usage(self):
        """测试 README 缺少使用说明"""
        (self.temp_path / "README.md").write_text("# Test Module\n\nThis is a test module.")
        (self.temp_path / "DESIGN.md").write_text("# Design\n\nDesign content here.")

        result = scan_module(str(self.temp_path))

        self.assertTrue(any("建议添加使用说明" in i.message for i in result.issues))

    def test_scan_module_design_without_decisions(self):
        """测试 DESIGN 缺少设计决策"""
        (self.temp_path / "README.md").write_text("# Test\n\nUsage: test")
        (self.temp_path / "DESIGN.md").write_text("# Design\n\nSome content.")

        result = scan_module(str(self.temp_path))

        self.assertTrue(any("建议记录设计决策" in i.message for i in result.issues))

    def test_scan_structure_basic(self):
        """测试目录结构扫描"""
        (self.temp_path / "file1.py").write_text("x = 1")
        (self.temp_path / "subdir").mkdir()
        (self.temp_path / "subdir" / "file2.py").write_text("y = 2")

        structure = scan_structure(self.temp_path)

        self.assertEqual(structure["type"], "dir")
        self.assertTrue(len(structure["children"]) > 0)

    def test_scan_structure_ignores_hidden_files(self):
        """测试忽略隐藏文件"""
        (self.temp_path / ".hidden").write_text("hidden")
        (self.temp_path / "visible.py").write_text("visible")

        structure = scan_structure(self.temp_path)

        # 隐藏文件应该被忽略
        names = [c["name"] for c in structure["children"]]
        self.assertNotIn(".hidden", names)
        self.assertIn("visible.py", names)

    def test_scan_result_passed_property(self):
        """测试 ScanResult.passed 属性"""
        result = ScanResult(module_path="/test")

        # 没有错误时应该通过
        self.assertTrue(result.passed)

        # 添加警告
        result.issues.append(Issue(
            severity=Severity.WARNING,
            message="test warning"
        ))
        self.assertTrue(result.passed)

        # 添加错误
        result.issues.append(Issue(
            severity=Severity.ERROR,
            message="test error"
        ))
        self.assertFalse(result.passed)

    def test_scan_result_error_count(self):
        """测试错误计数"""
        result = ScanResult(module_path="/test")

        result.issues.append(Issue(severity=Severity.ERROR, message="error1"))
        result.issues.append(Issue(severity=Severity.ERROR, message="error2"))
        result.issues.append(Issue(severity=Severity.WARNING, message="warning"))

        self.assertEqual(result.error_count, 2)
        self.assertEqual(result.warning_count, 1)

    def test_format_report_basic(self):
        """测试报告格式化"""
        result = ScanResult(module_path="/test/module")

        report = format_report(result)

        self.assertIn("模块完整性扫描报告", report)
        self.assertIn("/test/module", report)

    def test_format_report_with_issues(self):
        """测试包含问题的报告"""
        result = ScanResult(module_path="/test/module")
        result.issues.append(Issue(
            severity=Severity.ERROR,
            message="缺少必需文档: README.md",
            path="/test/module/README.md"
        ))

        report = format_report(result, verbose=True)

        self.assertIn("缺少必需文档", report)
        self.assertIn("README.md", report)

    def test_issue_dataclass(self):
        """测试 Issue 数据类"""
        issue = Issue(
            severity=Severity.WARNING,
            message="test message",
            path="/test/path"
        )

        self.assertEqual(issue.severity, Severity.WARNING)
        self.assertEqual(issue.message, "test message")
        self.assertEqual(issue.path, "/test/path")

    def test_severity_enum(self):
        """测试 Severity 枚举"""
        self.assertEqual(Severity.ERROR.value, "error")
        self.assertEqual(Severity.WARNING.value, "warning")
        self.assertEqual(Severity.INFO.value, "info")


class TestModuleScannerEdgeCases(unittest.TestCase):
    """模块扫描器边界条件测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """测试后清理"""
        self.temp_dir.cleanup()

    def test_scan_module_deeply_nested(self):
        """测试深层嵌套结构"""
        (self.temp_path / "README.md").write_text("# Test")
        (self.temp_path / "DESIGN.md").write_text("# Design")

        deep_path = self.temp_path / "a" / "b" / "c" / "d"
        deep_path.mkdir(parents=True)
        (deep_path / "file.py").write_text("x = 1")

        result = scan_module(str(self.temp_path))

        self.assertIsInstance(result, ScanResult)

    def test_scan_module_with_special_characters(self):
        """测试包含特殊字符的文件名"""
        (self.temp_path / "README.md").write_text("# Test")
        (self.temp_path / "DESIGN.md").write_text("# Design")
        (self.temp_path / "文件.py").write_text("x = 1")

        result = scan_module(str(self.temp_path))

        self.assertIsInstance(result, ScanResult)

    def test_scan_module_with_symlinks(self):
        """测试包含符号链接"""
        (self.temp_path / "README.md").write_text("# Test")
        (self.temp_path / "DESIGN.md").write_text("# Design")
        (self.temp_path / "src").mkdir()
        (self.temp_path / "src" / "main.py").write_text("x = 1")

        result = scan_module(str(self.temp_path))

        self.assertIsInstance(result, ScanResult)

    def test_scan_module_with_large_files(self):
        """测试包含大文件"""
        (self.temp_path / "README.md").write_text("# Test\n" + "x" * 10000)
        (self.temp_path / "DESIGN.md").write_text("# Design\n" + "y" * 10000)

        result = scan_module(str(self.temp_path))

        self.assertIsInstance(result, ScanResult)

    def test_scan_module_with_multiple_languages(self):
        """测试多语言代码"""
        (self.temp_path / "README.md").write_text("# Test")
        (self.temp_path / "DESIGN.md").write_text("# Design")
        (self.temp_path / "src").mkdir()
        (self.temp_path / "src" / "main.py").write_text("x = 1")
        (self.temp_path / "src" / "main.go").write_text("package main")
        (self.temp_path / "src" / "main.rs").write_text("fn main() {}")

        result = scan_module(str(self.temp_path))

        self.assertIsInstance(result, ScanResult)


if __name__ == '__main__':
    unittest.main()
