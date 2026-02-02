#!/usr/bin/env python3
"""
verify-quality 单元测试
测试代码质量检查器功能
"""

import unittest
import tempfile
import sys
from pathlib import Path

# 添加 skills 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "verify-quality" / "scripts"))

from quality_checker import (
    Severity, Issue, FileMetrics, QualityResult, PythonAnalyzer,
    analyze_python_file, analyze_generic_file, scan_directory,
    format_report
)


class TestQualityChecker(unittest.TestCase):
    """代码质量检查器测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """测试后清理"""
        self.temp_dir.cleanup()

    def test_analyze_python_file_basic(self):
        """测试基本 Python 文件分析"""
        test_file = self.temp_path / "test.py"
        test_file.write_text('''
def hello():
    """Say hello"""
    print("hello")

class MyClass:
    """A test class"""
    pass
''')

        metrics, issues = analyze_python_file(test_file)

        self.assertEqual(metrics.path, str(test_file))
        self.assertGreater(metrics.lines, 0)
        self.assertGreater(metrics.code_lines, 0)
        self.assertEqual(metrics.functions, 1)
        self.assertEqual(metrics.classes, 1)

    def test_analyze_python_file_with_syntax_error(self):
        """测试语法错误检测"""
        test_file = self.temp_path / "bad.py"
        test_file.write_text('def broken(\n')

        metrics, issues = analyze_python_file(test_file)

        self.assertTrue(any(i.severity == Severity.ERROR for i in issues))
        self.assertTrue(any("语法错误" in i.message for i in issues))

    def test_analyze_python_file_long_function(self):
        """测试长函数检测"""
        test_file = self.temp_path / "long.py"
        lines = ['def long_function():']
        for i in range(60):
            lines.append(f'    x{i} = {i}')
        test_file.write_text('\n'.join(lines))

        metrics, issues = analyze_python_file(test_file)

        self.assertTrue(any("过长" in i.message for i in issues))

    def test_analyze_python_file_high_complexity(self):
        """测试高复杂度检测"""
        test_file = self.temp_path / "complex.py"
        test_file.write_text('''
def complex_function(x):
    if x > 0:
        if x > 10:
            if x > 20:
                if x > 30:
                    if x > 40:
                        if x > 50:
                            if x > 60:
                                if x > 70:
                                    if x > 80:
                                        if x > 90:
                                            return "very high"
    return "low"
''')

        metrics, issues = analyze_python_file(test_file)

        self.assertTrue(any("圈复杂度" in i.message for i in issues))

    def test_analyze_python_file_too_many_parameters(self):
        """测试参数过多检测"""
        test_file = self.temp_path / "params.py"
        test_file.write_text('def func(a, b, c, d, e, f, g):\n    pass')

        metrics, issues = analyze_python_file(test_file)

        self.assertTrue(any("参数过多" in i.message for i in issues))

    def test_analyze_python_file_bad_naming(self):
        """测试命名规范检测"""
        test_file = self.temp_path / "naming.py"
        test_file.write_text('''
class myClass:
    pass

def MyFunction():
    pass
''')

        metrics, issues = analyze_python_file(test_file)

        # 检查是否有命名相关的问题（类名或函数名）
        naming_issues = [i for i in issues if "命名" in i.message or "PascalCase" in i.message or "snake_case" in i.message]
        self.assertTrue(len(naming_issues) > 0)

    def test_analyze_python_file_short_function_name(self):
        """测试函数名过短检测"""
        test_file = self.temp_path / "short.py"
        test_file.write_text('def x():\n    pass')

        metrics, issues = analyze_python_file(test_file)

        self.assertTrue(any("过短" in i.message for i in issues))

    def test_analyze_python_file_long_lines(self):
        """测试长行检测"""
        test_file = self.temp_path / "longline.py"
        long_line = 'x = "' + 'a' * 150 + '"'
        test_file.write_text(long_line)

        metrics, issues = analyze_python_file(test_file)

        self.assertTrue(any("行过长" in i.message for i in issues))

    def test_analyze_python_file_large_file(self):
        """测试大文件检测"""
        test_file = self.temp_path / "large.py"
        lines = []
        for i in range(600):
            lines.append(f'x{i} = {i}')
        test_file.write_text('\n'.join(lines))

        metrics, issues = analyze_python_file(test_file)

        self.assertTrue(any("文件过长" in i.message for i in issues))

    def test_analyze_python_file_comments(self):
        """测试注释行统计"""
        test_file = self.temp_path / "comments.py"
        test_file.write_text('''
# This is a comment
x = 1  # inline comment
"""
Multi-line
comment
"""
y = 2
''')

        metrics, issues = analyze_python_file(test_file)

        self.assertGreater(metrics.comment_lines, 0)

    def test_analyze_generic_file(self):
        """测试通用文件分析"""
        test_file = self.temp_path / "test.js"
        test_file.write_text('''
// Comment
function hello() {
    console.log("hello");
}
''')

        metrics, issues = analyze_generic_file(test_file)

        self.assertEqual(metrics.path, str(test_file))
        self.assertGreater(metrics.lines, 0)

    def test_scan_directory_basic(self):
        """测试目录扫描"""
        (self.temp_path / "file1.py").write_text('x = 1')
        (self.temp_path / "file2.py").write_text('y = 2')

        result = scan_directory(str(self.temp_path))

        self.assertEqual(result.files_scanned, 2)
        self.assertGreater(result.total_lines, 0)

    def test_scan_directory_empty(self):
        """测试空目录扫描"""
        result = scan_directory(str(self.temp_path))

        self.assertEqual(result.files_scanned, 0)

    def test_scan_directory_excludes(self):
        """测试目录排除"""
        (self.temp_path / "src").mkdir()
        (self.temp_path / "src" / "main.py").write_text('x = 1')

        (self.temp_path / "__pycache__").mkdir()
        (self.temp_path / "__pycache__" / "cache.py").write_text('y = 2')

        result = scan_directory(str(self.temp_path), exclude_dirs=['__pycache__'])

        self.assertEqual(result.files_scanned, 1)

    def test_scan_directory_multiple_languages(self):
        """测试多语言扫描"""
        (self.temp_path / "test.py").write_text('x = 1')
        (self.temp_path / "test.js").write_text('var x = 1;')
        (self.temp_path / "test.go").write_text('package main')

        result = scan_directory(str(self.temp_path))

        self.assertEqual(result.files_scanned, 3)

    def test_quality_result_passed_property(self):
        """测试 QualityResult.passed 属性"""
        result = QualityResult(scan_path="/test")

        # 没有错误时应该通过
        self.assertTrue(result.passed)

        # 添加警告
        result.issues.append(Issue(
            severity=Severity.WARNING,
            category="test",
            message="test warning",
            file_path="test.py"
        ))
        self.assertTrue(result.passed)

        # 添加错误
        result.issues.append(Issue(
            severity=Severity.ERROR,
            category="test",
            message="test error",
            file_path="test.py"
        ))
        self.assertFalse(result.passed)

    def test_quality_result_counts(self):
        """测试问题计数"""
        result = QualityResult(scan_path="/test")

        result.issues.append(Issue(
            severity=Severity.ERROR,
            category="test",
            message="error",
            file_path="test.py"
        ))
        result.issues.append(Issue(
            severity=Severity.WARNING,
            category="test",
            message="warning",
            file_path="test.py"
        ))

        self.assertEqual(result.error_count, 1)
        self.assertEqual(result.warning_count, 1)

    def test_file_metrics_dataclass(self):
        """测试 FileMetrics 数据类"""
        metrics = FileMetrics(
            path="/test/file.py",
            lines=100,
            code_lines=80,
            comment_lines=10,
            blank_lines=10,
            functions=5,
            classes=2
        )

        self.assertEqual(metrics.path, "/test/file.py")
        self.assertEqual(metrics.lines, 100)
        self.assertEqual(metrics.functions, 5)

    def test_issue_dataclass(self):
        """测试 Issue 数据类"""
        issue = Issue(
            severity=Severity.WARNING,
            category="复杂度",
            message="函数过长",
            file_path="test.py",
            line_number=10,
            suggestion="拆分函数"
        )

        self.assertEqual(issue.severity, Severity.WARNING)
        self.assertEqual(issue.category, "复杂度")
        self.assertEqual(issue.line_number, 10)

    def test_severity_enum(self):
        """测试 Severity 枚举"""
        self.assertEqual(Severity.ERROR.value, "error")
        self.assertEqual(Severity.WARNING.value, "warning")
        self.assertEqual(Severity.INFO.value, "info")

    def test_format_report_basic(self):
        """测试报告格式化"""
        result = QualityResult(scan_path="/test", files_scanned=5, total_lines=500)

        report = format_report(result)

        self.assertIn("代码质量检查报告", report)
        self.assertIn("/test", report)
        self.assertIn("5", report)

    def test_format_report_with_issues(self):
        """测试包含问题的报告"""
        result = QualityResult(scan_path="/test")
        result.issues.append(Issue(
            severity=Severity.WARNING,
            category="复杂度",
            message="函数过长",
            file_path="test.py",
            line_number=10,
            suggestion="拆分函数"
        ))

        report = format_report(result, verbose=True)

        self.assertIn("函数过长", report)
        self.assertIn("test.py", report)

    def test_python_analyzer_basic(self):
        """测试 Python 分析器"""
        source = '''
def hello():
    """Say hello"""
    print("hello")

class MyClass:
    """A test class"""
    pass
'''

        analyzer = PythonAnalyzer("test.py", source)
        issues, functions, classes, complexity = analyzer.analyze()

        self.assertEqual(len(functions), 1)
        self.assertEqual(len(classes), 1)

    def test_python_analyzer_syntax_error(self):
        """测试语法错误处理"""
        source = 'def broken(\n'

        analyzer = PythonAnalyzer("test.py", source)
        issues, functions, classes, complexity = analyzer.analyze()

        self.assertTrue(any(i.severity == Severity.ERROR for i in issues))


class TestQualityCheckerEdgeCases(unittest.TestCase):
    """代码质量检查器边界条件测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """测试后清理"""
        self.temp_dir.cleanup()

    def test_analyze_empty_file(self):
        """测试空文件分析"""
        test_file = self.temp_path / "empty.py"
        test_file.write_text('')

        metrics, issues = analyze_python_file(test_file)

        self.assertEqual(metrics.lines, 1)  # 空文件有一行

    def test_analyze_file_with_only_comments(self):
        """测试仅包含注释的文件"""
        test_file = self.temp_path / "comments.py"
        test_file.write_text('''
# Comment 1
# Comment 2
# Comment 3
''')

        metrics, issues = analyze_python_file(test_file)

        self.assertEqual(metrics.code_lines, 0)
        self.assertGreater(metrics.comment_lines, 0)

    def test_analyze_file_with_special_characters(self):
        """测试包含特殊字符的文件"""
        test_file = self.temp_path / "special.py"
        test_file.write_text('''
# 中文注释
def 函数():
    """中文文档"""
    pass
''')

        metrics, issues = analyze_python_file(test_file)

        self.assertIsInstance(metrics, FileMetrics)

    def test_scan_deeply_nested(self):
        """测试深层嵌套目录"""
        deep_path = self.temp_path / "a" / "b" / "c" / "d"
        deep_path.mkdir(parents=True)
        (deep_path / "test.py").write_text('x = 1')

        result = scan_directory(str(self.temp_path))

        self.assertEqual(result.files_scanned, 1)

    def test_analyze_file_with_encoding_error(self):
        """测试编码错误处理"""
        test_file = self.temp_path / "binary.bin"
        test_file.write_bytes(b'\x80\x81\x82\x83')

        metrics, issues = analyze_generic_file(test_file)

        # 应该优雅地处理
        self.assertIsInstance(metrics, FileMetrics)

    def test_analyze_very_long_function(self):
        """测试超长函数"""
        test_file = self.temp_path / "very_long.py"
        lines = ['def very_long_function():']
        for i in range(1000):
            lines.append(f'    x{i} = {i}')
        test_file.write_text('\n'.join(lines))

        metrics, issues = analyze_python_file(test_file)

        self.assertTrue(any("过长" in i.message for i in issues))

    def test_analyze_many_functions(self):
        """测试包含多个函数的文件"""
        test_file = self.temp_path / "many.py"
        lines = []
        for i in range(50):
            lines.append(f'def func{i}():\n    pass\n')
        test_file.write_text('\n'.join(lines))

        metrics, issues = analyze_python_file(test_file)

        self.assertEqual(metrics.functions, 50)

    def test_scan_mixed_file_types(self):
        """测试混合文件类型"""
        (self.temp_path / "test.py").write_text('x = 1')
        (self.temp_path / "test.js").write_text('var x = 1;')
        (self.temp_path / "test.txt").write_text('text')
        (self.temp_path / "test.md").write_text('# Markdown')

        result = scan_directory(str(self.temp_path))

        # 只应该扫描代码文件
        self.assertEqual(result.files_scanned, 2)

    def test_format_report_verbose(self):
        """测试详细报告"""
        result = QualityResult(scan_path="/test", files_scanned=1)
        result.file_metrics.append(FileMetrics(
            path="/test/file.py",
            lines=100,
            code_lines=80,
            functions=5,
            max_complexity=8
        ))

        report = format_report(result, verbose=True)

        self.assertIn("复杂度", report)


if __name__ == '__main__':
    unittest.main()
