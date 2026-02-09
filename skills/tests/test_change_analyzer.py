#!/usr/bin/env python3
"""
verify-change 单元测试
测试变更分析器功能
"""

import unittest
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加 skills 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "tools" / "verify-change" / "scripts"))

from change_analyzer import (
    ChangeType, Severity, FileChange, Issue, AnalysisResult,
    classify_file, identify_affected_modules, check_doc_sync,
    analyze_impact, analyze_changes, format_report,
    get_working_changes, get_staged_changes, get_git_changes
)


class TestChangeAnalyzer(unittest.TestCase):
    """变更分析器测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """测试后清理"""
        self.temp_dir.cleanup()

    def test_classify_file_python_code(self):
        """测试 Python 代码文件分类"""
        change = classify_file("src/main.py")

        self.assertTrue(change.is_code)
        self.assertFalse(change.is_doc)
        self.assertFalse(change.is_test)

    def test_classify_file_test(self):
        """测试测试文件分类"""
        change = classify_file("tests/test_main.py")

        self.assertTrue(change.is_code)
        self.assertTrue(change.is_test)

    def test_classify_file_documentation(self):
        """测试文档文件分类"""
        change = classify_file("docs/README.md")

        self.assertTrue(change.is_doc)
        self.assertFalse(change.is_code)

    def test_classify_file_config(self):
        """测试配置文件分类"""
        change = classify_file("package.json")

        self.assertTrue(change.is_config)

    def test_classify_file_yaml_config(self):
        """测试 YAML 配置文件"""
        change = classify_file("config.yaml")

        self.assertTrue(change.is_config)

    def test_classify_file_multiple_patterns(self):
        """测试多个模式匹配"""
        change = classify_file("tests/test_utils.py")

        self.assertTrue(change.is_code)
        self.assertTrue(change.is_test)

    def test_classify_file_underscore_test(self):
        """测试 _test 模式"""
        change = classify_file("src/utils_test.go")

        self.assertTrue(change.is_test)

    def test_classify_file_spec_pattern(self):
        """测试 spec 模式"""
        change = classify_file("spec/main_spec.js")

        self.assertTrue(change.is_test)

    @patch('change_analyzer.subprocess.run')
    def test_get_working_changes_keeps_dotfile_prefix(self, mock_run):
        """测试工作区变更保留 dotfile 前缀"""
        mock_run.return_value = MagicMock(stdout=' M .gitignore\n')

        changes = get_working_changes()

        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].path, '.gitignore')
        self.assertEqual(changes[0].change_type, ChangeType.MODIFIED)

    @patch('change_analyzer.subprocess.run')
    def test_get_staged_changes_parses_status(self, mock_run):
        """测试暂存区变更解析"""
        mock_run.return_value = MagicMock(stdout='A\tsrc/new.py\nM\tREADME.md\n')

        changes = get_staged_changes()

        self.assertEqual(len(changes), 2)
        self.assertEqual(changes[0].change_type, ChangeType.ADDED)
        self.assertEqual(changes[0].path, 'src/new.py')
        self.assertEqual(changes[1].change_type, ChangeType.MODIFIED)

    @patch('change_analyzer.subprocess.run')
    def test_get_git_changes_maps_numstat(self, mock_run):
        """测试提交变更行数映射"""
        mock_run.side_effect = [
            MagicMock(stdout='M\tsrc/main.py\n'),
            MagicMock(stdout='10\t2\tsrc/main.py\n')
        ]

        changes = get_git_changes('HEAD~1', 'HEAD')

        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].path, 'src/main.py')
        self.assertEqual(changes[0].additions, 10)
        self.assertEqual(changes[0].deletions, 2)

    @patch('change_analyzer.subprocess.run')
    def test_get_working_changes_parses_rename(self, mock_run):
        """测试工作区重命名解析"""
        mock_run.return_value = MagicMock(stdout='R  old_name.py -> new_name.py\n')

        changes = get_working_changes()

        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].path, 'new_name.py')
        self.assertEqual(changes[0].change_type, ChangeType.RENAMED)

    def test_identify_affected_modules_single_file(self):
        """测试识别受影响的模块"""
        # 创建模块结构
        module_path = self.temp_path / "mymodule"
        module_path.mkdir()
        (module_path / "README.md").write_text("# Module")
        (module_path / "src").mkdir()
        (module_path / "src" / "main.py").write_text("x = 1")

        changes = [
            FileChange(path="mymodule/src/main.py", change_type=ChangeType.MODIFIED)
        ]

        modules = identify_affected_modules(changes)

        self.assertIn("mymodule", modules)

    def test_identify_affected_modules_multiple(self):
        """测试识别多个受影响的模块"""
        # 创建多个模块
        for mod in ["module1", "module2"]:
            mod_path = self.temp_path / mod
            mod_path.mkdir()
            (mod_path / "README.md").write_text("# Module")

        changes = [
            FileChange(path="module1/src/main.py", change_type=ChangeType.MODIFIED),
            FileChange(path="module2/src/main.py", change_type=ChangeType.MODIFIED)
        ]

        modules = identify_affected_modules(changes)

        self.assertIn("module1", modules)
        self.assertIn("module2", modules)

    def test_identify_affected_modules_root_file(self):
        """测试根目录文件识别为当前模块"""
        changes = [
            FileChange(path="main.py", change_type=ChangeType.MODIFIED)
        ]

        modules = identify_affected_modules(changes)

        self.assertIn(".", modules)

    def test_check_doc_sync_root_module(self):
        """测试根目录模块文档同步"""
        changes = [
            FileChange(
                path="main.py",
                change_type=ChangeType.MODIFIED,
                is_code=True,
                additions=80,
                deletions=10
            )
        ]

        doc_status, issues = check_doc_sync(changes, {"."})

        self.assertFalse(doc_status.get("./DESIGN.md", True))
        self.assertTrue(any("DESIGN.md" in i.message for i in issues))

    def test_check_doc_sync_no_changes(self):
        """测试无变更时的文档同步检查"""
        doc_status, issues = check_doc_sync([], set())

        self.assertEqual(len(doc_status), 0)
        self.assertEqual(len(issues), 0)

    def test_check_doc_sync_code_without_doc_update(self):
        """测试代码变更但文档未更新"""
        module_path = self.temp_path / "mymodule"
        module_path.mkdir()
        (module_path / "README.md").write_text("# Module")
        (module_path / "DESIGN.md").write_text("# Design")

        changes = [
            FileChange(
                path="mymodule/src/main.py",
                change_type=ChangeType.MODIFIED,
                is_code=True,
                additions=100,
                deletions=50
            )
        ]

        doc_status, issues = check_doc_sync(changes, {"mymodule"})

        # 大规模变更应该有警告
        self.assertTrue(any("DESIGN.md" in i.message for i in issues))

    def test_check_doc_sync_with_doc_update(self):
        """测试代码和文档同时更新"""
        module_path = self.temp_path / "mymodule"
        module_path.mkdir()
        (module_path / "README.md").write_text("# Module")
        (module_path / "DESIGN.md").write_text("# Design")

        changes = [
            FileChange(
                path="mymodule/src/main.py",
                change_type=ChangeType.MODIFIED,
                is_code=True,
                additions=100,
                deletions=50
            ),
            FileChange(
                path="mymodule/DESIGN.md",
                change_type=ChangeType.MODIFIED,
                is_doc=True
            )
        ]

        doc_status, issues = check_doc_sync(changes, {"mymodule"})

        # 文档已更新，不应该有警告
        self.assertFalse(any("DESIGN.md" in i.message for i in issues))

    def test_analyze_impact_code_without_tests(self):
        """测试代码变更但无测试更新"""
        changes = [
            FileChange(
                path="src/main.py",
                change_type=ChangeType.MODIFIED,
                is_code=True,
                additions=50,
                deletions=20
            )
        ]

        issues = analyze_impact(changes)

        # 应该有关于缺少测试的警告
        self.assertTrue(any("测试" in i.message for i in issues))

    def test_analyze_impact_with_tests(self):
        """测试代码和测试同时更新"""
        changes = [
            FileChange(
                path="src/main.py",
                change_type=ChangeType.MODIFIED,
                is_code=True,
                additions=50,
                deletions=20
            ),
            FileChange(
                path="tests/test_main.py",
                change_type=ChangeType.MODIFIED,
                is_code=True,
                is_test=True
            )
        ]

        issues = analyze_impact(changes)

        # 不应该有关于缺少测试的警告
        self.assertFalse(any("测试" in i.message for i in issues))

    def test_analyze_impact_config_changes(self):
        """测试配置文件变更"""
        changes = [
            FileChange(
                path="package.json",
                change_type=ChangeType.MODIFIED,
                is_config=True
            )
        ]

        issues = analyze_impact(changes)

        # 应该有关于配置变更的提示
        self.assertTrue(any("配置文件" in i.message for i in issues))

    def test_analyze_impact_deleted_files(self):
        """测试删除文件"""
        changes = [
            FileChange(
                path="src/old_module.py",
                change_type=ChangeType.DELETED,
                is_code=True
            )
        ]

        issues = analyze_impact(changes)

        # 应该有关于删除的提示
        self.assertTrue(any("删除" in i.message for i in issues))

    def test_analysis_result_passed_property(self):
        """测试 AnalysisResult.passed 属性"""
        result = AnalysisResult()

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

    def test_analysis_result_additions_deletions(self):
        """测试新增和删除行数统计"""
        result = AnalysisResult()

        result.changes.append(FileChange(
            path="file1.py",
            change_type=ChangeType.MODIFIED,
            additions=10,
            deletions=5
        ))
        result.changes.append(FileChange(
            path="file2.py",
            change_type=ChangeType.MODIFIED,
            additions=20,
            deletions=15
        ))

        self.assertEqual(result.total_additions, 30)
        self.assertEqual(result.total_deletions, 20)

    def test_file_change_dataclass(self):
        """测试 FileChange 数据类"""
        change = FileChange(
            path="src/main.py",
            change_type=ChangeType.MODIFIED,
            additions=10,
            deletions=5,
            is_code=True
        )

        self.assertEqual(change.path, "src/main.py")
        self.assertEqual(change.change_type, ChangeType.MODIFIED)
        self.assertEqual(change.additions, 10)
        self.assertTrue(change.is_code)

    def test_change_type_enum(self):
        """测试 ChangeType 枚举"""
        self.assertEqual(ChangeType.ADDED.value, "added")
        self.assertEqual(ChangeType.MODIFIED.value, "modified")
        self.assertEqual(ChangeType.DELETED.value, "deleted")
        self.assertEqual(ChangeType.RENAMED.value, "renamed")

    def test_severity_enum(self):
        """测试 Severity 枚举"""
        self.assertEqual(Severity.ERROR.value, "error")
        self.assertEqual(Severity.WARNING.value, "warning")
        self.assertEqual(Severity.INFO.value, "info")

    def test_format_report_basic(self):
        """测试报告格式化"""
        result = AnalysisResult()
        result.changes.append(FileChange(
            path="src/main.py",
            change_type=ChangeType.MODIFIED,
            additions=10,
            deletions=5
        ))

        report = format_report(result)

        self.assertIn("变更分析报告", report)
        self.assertIn("1", report)  # 1 file changed

    def test_format_report_with_issues(self):
        """测试包含问题的报告"""
        result = AnalysisResult()
        result.issues.append(Issue(
            severity=Severity.WARNING,
            message="代码变更但没有测试更新",
            related_files=["src/main.py"]
        ))

        report = format_report(result, verbose=True)

        self.assertIn("代码变更", report)
        self.assertIn("src/main.py", report)

    def test_format_report_with_modules(self):
        """测试包含模块信息的报告"""
        result = AnalysisResult()
        result.affected_modules.add("module1")
        result.affected_modules.add("module2")

        report = format_report(result)

        self.assertIn("module1", report)
        self.assertIn("module2", report)

    def test_issue_dataclass(self):
        """测试 Issue 数据类"""
        issue = Issue(
            severity=Severity.WARNING,
            message="test message",
            related_files=["file1.py", "file2.py"]
        )

        self.assertEqual(issue.severity, Severity.WARNING)
        self.assertEqual(issue.message, "test message")
        self.assertEqual(len(issue.related_files), 2)


class TestChangeAnalyzerEdgeCases(unittest.TestCase):
    """变更分析器边界条件测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """测试后清理"""
        self.temp_dir.cleanup()

    def test_classify_file_case_insensitive(self):
        """测试文件分类大小写不敏感"""
        change1 = classify_file("src/Main.PY")
        change2 = classify_file("src/main.py")

        self.assertEqual(change1.is_code, change2.is_code)

    def test_identify_modules_with_nested_structure(self):
        """测试嵌套模块识别"""
        changes = [
            FileChange(path="a/b/c/src/main.py", change_type=ChangeType.MODIFIED)
        ]

        modules = identify_affected_modules(changes)

        self.assertIsInstance(modules, set)

    def test_analyze_impact_small_changes(self):
        """测试小规模变更"""
        changes = [
            FileChange(
                path="src/main.py",
                change_type=ChangeType.MODIFIED,
                is_code=True,
                additions=5,
                deletions=2
            )
        ]

        issues = analyze_impact(changes)

        # 小规模变更不应该有测试警告
        self.assertFalse(any("测试" in i.message for i in issues))

    def test_analyze_impact_large_changes(self):
        """测试大规模变更"""
        changes = [
            FileChange(
                path="src/main.py",
                change_type=ChangeType.MODIFIED,
                is_code=True,
                additions=100,
                deletions=50
            )
        ]

        issues = analyze_impact(changes)

        # 大规模变更应该有测试警告
        self.assertTrue(any("测试" in i.message for i in issues))

    def test_check_doc_sync_small_changes(self):
        """测试小规模变更的文档同步检查"""
        module_path = self.temp_path / "mymodule"
        module_path.mkdir()
        (module_path / "README.md").write_text("# Module")
        (module_path / "DESIGN.md").write_text("# Design")

        changes = [
            FileChange(
                path="mymodule/src/main.py",
                change_type=ChangeType.MODIFIED,
                is_code=True,
                additions=10,
                deletions=5
            )
        ]

        doc_status, issues = check_doc_sync(changes, {"mymodule"})

        # 小规模变更不应该有文档警告
        self.assertFalse(any("DESIGN.md" in i.message for i in issues))

    def test_format_report_empty_changes(self):
        """测试空变更报告"""
        result = AnalysisResult()

        report = format_report(result)

        self.assertIn("变更分析报告", report)
        self.assertIn("0", report)

    def test_multiple_file_types(self):
        """测试多种文件类型"""
        changes = [
            FileChange(path="src/main.py", change_type=ChangeType.MODIFIED, is_code=True),
            FileChange(path="README.md", change_type=ChangeType.MODIFIED, is_doc=True),
            FileChange(path="tests/test.py", change_type=ChangeType.MODIFIED, is_code=True, is_test=True),
            FileChange(path="package.json", change_type=ChangeType.MODIFIED, is_config=True),
        ]

        result = AnalysisResult()
        result.changes = changes

        self.assertEqual(len(result.changes), 4)


if __name__ == '__main__':
    unittest.main()
