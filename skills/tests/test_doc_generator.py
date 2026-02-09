#!/usr/bin/env python3
"""
gen-docs 单元测试
测试文档生成器功能
"""

import unittest
import tempfile
import sys
from pathlib import Path

# 添加 skills 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "tools" / "gen-docs" / "scripts"))

from doc_generator import (
    ModuleInfo, detect_language, analyze_python_module, analyze_module,
    generate_readme, generate_design, generate_docs
)


class TestDocGenerator(unittest.TestCase):
    """文档生成器测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """测试后清理"""
        self.temp_dir.cleanup()

    def test_detect_language_python(self):
        """测试 Python 语言检测"""
        (self.temp_path / "main.py").write_text("print('hello')")
        (self.temp_path / "utils.py").write_text("def util(): pass")

        language = detect_language(self.temp_path)

        self.assertEqual(language, "Python")

    def test_detect_language_go(self):
        """测试 Go 语言检测"""
        (self.temp_path / "main.go").write_text("package main")
        (self.temp_path / "utils.go").write_text("package main")

        language = detect_language(self.temp_path)

        self.assertEqual(language, "Go")

    def test_detect_language_rust(self):
        """测试 Rust 语言检测"""
        (self.temp_path / "main.rs").write_text("fn main() {}")
        (self.temp_path / "lib.rs").write_text("pub fn util() {}")

        language = detect_language(self.temp_path)

        self.assertEqual(language, "Rust")

    def test_detect_language_typescript(self):
        """测试 TypeScript 语言检测"""
        (self.temp_path / "main.ts").write_text("console.log('hello')")
        (self.temp_path / "utils.ts").write_text("export function util() {}")

        language = detect_language(self.temp_path)

        self.assertEqual(language, "TypeScript")

    def test_detect_language_javascript(self):
        """测试 JavaScript 语言检测"""
        (self.temp_path / "main.js").write_text("console.log('hello')")

        language = detect_language(self.temp_path)

        self.assertEqual(language, "JavaScript")

    def test_detect_language_java(self):
        """测试 Java 语言检测"""
        (self.temp_path / "Main.java").write_text("public class Main {}")

        language = detect_language(self.temp_path)

        self.assertEqual(language, "Java")

    def test_detect_language_empty_directory(self):
        """测试空目录语言检测"""
        language = detect_language(self.temp_path)

        self.assertEqual(language, "Unknown")

    def test_analyze_python_module_basic(self):
        """测试基本 Python 模块分析"""
        (self.temp_path / "main.py").write_text('''
"""Module docstring"""

def hello():
    """Say hello"""
    pass

class MyClass:
    """A test class"""
    pass
''')

        info = analyze_python_module(self.temp_path)

        self.assertEqual(info.name, self.temp_path.name)
        self.assertEqual(info.language, "Python")
        self.assertGreater(len(info.files), 0)
        self.assertEqual(len(info.functions), 1)
        self.assertEqual(len(info.classes), 1)

    def test_analyze_python_module_with_dependencies(self):
        """测试 Python 模块依赖检测"""
        (self.temp_path / "main.py").write_text("import requests")
        (self.temp_path / "requirements.txt").write_text('''
requests==2.28.0
numpy>=1.20.0
pandas
''')

        info = analyze_python_module(self.temp_path)

        self.assertGreater(len(info.dependencies), 0)
        self.assertIn("requests", info.dependencies)

    def test_analyze_python_module_entry_points(self):
        """测试 Python 模块入口点检测"""
        (self.temp_path / "main.py").write_text("if __name__ == '__main__': pass")
        (self.temp_path / "__main__.py").write_text("print('hello')")

        info = analyze_python_module(self.temp_path)

        self.assertGreater(len(info.entry_points), 0)

    def test_analyze_python_module_ignores_tests(self):
        """测试忽略测试文件"""
        (self.temp_path / "main.py").write_text('''
def hello():
    pass
''')
        (self.temp_path / "test_main.py").write_text('''
def test_hello():
    pass
''')

        info = analyze_python_module(self.temp_path)

        # 应该只有 main.py 中的函数
        self.assertEqual(len(info.functions), 1)

    def test_analyze_python_module_with_pyproject(self):
        """测试 pyproject.toml 依赖检测"""
        (self.temp_path / "main.py").write_text("x = 1")
        (self.temp_path / "pyproject.toml").write_text('''
[project]
dependencies = [
    "requests",
    "numpy"
]
''')

        info = analyze_python_module(self.temp_path)

        # pyproject.toml 应该被识别
        self.assertIsInstance(info, ModuleInfo)

    def test_analyze_module_python(self):
        """测试通用模块分析 - Python"""
        (self.temp_path / "main.py").write_text("x = 1")

        info = analyze_module(self.temp_path)

        self.assertEqual(info.language, "Python")

    def test_analyze_module_go(self):
        """测试通用模块分析 - Go"""
        (self.temp_path / "main.go").write_text("package main")

        info = analyze_module(self.temp_path)

        self.assertEqual(info.language, "Go")

    def test_analyze_module_mixed_languages(self):
        """测试混合语言模块"""
        (self.temp_path / "main.py").write_text("x = 1")
        (self.temp_path / "main.go").write_text("package main")
        (self.temp_path / "main.rs").write_text("fn main() {}")

        info = analyze_module(self.temp_path)

        # 应该检测到主要语言
        self.assertIn(info.language, ["Python", "Go", "Rust"])

    def test_generate_readme_basic(self):
        """测试基本 README 生成"""
        info = ModuleInfo(
            name="TestModule",
            path=str(self.temp_path),
            description="A test module",
            language="Python"
        )

        readme = generate_readme(info)

        self.assertIn("# TestModule", readme)
        self.assertIn("A test module", readme)
        self.assertIn("## 概述", readme)
        self.assertIn("## 使用方法", readme)

    def test_generate_readme_with_dependencies(self):
        """测试包含依赖的 README 生成"""
        info = ModuleInfo(
            name="TestModule",
            path=str(self.temp_path),
            language="Python",
            dependencies=["requests", "numpy", "pandas"]
        )

        readme = generate_readme(info)

        self.assertIn("## 依赖", readme)
        self.assertIn("requests", readme)

    def test_generate_readme_with_api(self):
        """测试包含 API 的 README 生成"""
        info = ModuleInfo(
            name="TestModule",
            path=str(self.temp_path),
            language="Python",
            classes=[{"name": "MyClass", "doc": "A test class"}],
            functions=[{"name": "my_func", "doc": "A test function"}]
        )

        readme = generate_readme(info)

        self.assertIn("## API 概览", readme)
        self.assertIn("MyClass", readme)
        self.assertIn("my_func", readme)

    def test_generate_readme_with_files(self):
        """测试包含文件列表的 README 生成"""
        info = ModuleInfo(
            name="TestModule",
            path=str(self.temp_path),
            language="Python",
            files=["main.py", "utils.py", "config.py"]
        )

        readme = generate_readme(info)

        self.assertIn("## 目录结构", readme)
        self.assertIn("main.py", readme)

    def test_generate_design_basic(self):
        """测试基本 DESIGN 生成"""
        info = ModuleInfo(
            name="TestModule",
            path=str(self.temp_path),
            language="Python"
        )

        design = generate_design(info)

        self.assertIn("# TestModule 设计文档", design)
        self.assertIn("## 设计概述", design)
        self.assertIn("## 架构设计", design)
        self.assertIn("## 设计决策", design)
        self.assertIn("## 权衡取舍", design)
        self.assertIn("## 安全考量", design)
        self.assertIn("## 变更历史", design)

    def test_generate_design_with_components(self):
        """测试包含组件的 DESIGN 生成"""
        info = ModuleInfo(
            name="TestModule",
            path=str(self.temp_path),
            language="Python",
            classes=[
                {"name": "Parser", "doc": "Parse input"},
                {"name": "Processor", "doc": "Process data"}
            ]
        )

        design = generate_design(info)

        self.assertIn("### 核心组件", design)
        self.assertIn("Parser", design)
        self.assertIn("Processor", design)

    def test_generate_design_with_dependencies(self):
        """测试包含依赖的 DESIGN 生成"""
        info = ModuleInfo(
            name="TestModule",
            path=str(self.temp_path),
            language="Python",
            dependencies=["requests", "numpy"]
        )

        design = generate_design(info)

        self.assertIn("### 技术选型", design)
        self.assertIn("requests", design)

    def test_generate_docs_nonexistent_path(self):
        """测试不存在的路径"""
        nonexistent = self.temp_path / "nonexistent"

        result = generate_docs(str(nonexistent))

        self.assertEqual(result["status"], "error")
        self.assertTrue(any("不存在" in msg for msg in result["messages"]))

    def test_generate_docs_creates_files(self):
        """测试文档文件创建"""
        (self.temp_path / "main.py").write_text("x = 1")

        result = generate_docs(str(self.temp_path), force=True)

        self.assertEqual(result["status"], "success")
        self.assertTrue((self.temp_path / "README.md").exists())
        self.assertTrue((self.temp_path / "DESIGN.md").exists())

    def test_generate_docs_respects_existing_files(self):
        """测试尊重已存在的文件"""
        (self.temp_path / "main.py").write_text("x = 1")
        (self.temp_path / "README.md").write_text("# Existing README")

        result = generate_docs(str(self.temp_path), force=False)

        # 不应该覆盖
        content = (self.temp_path / "README.md").read_text()
        self.assertEqual(content, "# Existing README")

    def test_generate_docs_force_overwrite(self):
        """测试强制覆盖"""
        (self.temp_path / "main.py").write_text("x = 1")
        (self.temp_path / "README.md").write_text("# Old README")

        result = generate_docs(str(self.temp_path), force=True)

        # 应该被覆盖
        content = (self.temp_path / "README.md").read_text()
        self.assertNotEqual(content, "# Old README")

    def test_module_info_dataclass(self):
        """测试 ModuleInfo 数据类"""
        info = ModuleInfo(
            name="TestModule",
            path="/test/path",
            description="Test description",
            language="Python",
            files=["main.py"],
            dependencies=["requests"]
        )

        self.assertEqual(info.name, "TestModule")
        self.assertEqual(info.language, "Python")
        self.assertEqual(len(info.files), 1)
        self.assertEqual(len(info.dependencies), 1)

    def test_generate_readme_structure(self):
        """测试 README 结构完整性"""
        info = ModuleInfo(
            name="TestModule",
            path=str(self.temp_path),
            language="Python"
        )

        readme = generate_readme(info)

        # 检查必要的章节
        sections = [
            "# TestModule",
            "## 概述",
            "## 特性",
            "## 使用方法",
            "## 目录结构",
            "## 相关文档"
        ]

        for section in sections:
            self.assertIn(section, readme)

    def test_generate_design_structure(self):
        """测试 DESIGN 结构完整性"""
        info = ModuleInfo(
            name="TestModule",
            path=str(self.temp_path),
            language="Python"
        )

        design = generate_design(info)

        # 检查必要的章节
        sections = [
            "# TestModule 设计文档",
            "## 设计概述",
            "## 架构设计",
            "## 设计决策",
            "## 权衡取舍",
            "## 安全考量",
            "## 变更历史"
        ]

        for section in sections:
            self.assertIn(section, design)


class TestDocGeneratorEdgeCases(unittest.TestCase):
    """文档生成器边界条件测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """测试后清理"""
        self.temp_dir.cleanup()

    def test_analyze_module_deeply_nested(self):
        """测试深层嵌套模块"""
        deep_path = self.temp_path / "a" / "b" / "c"
        deep_path.mkdir(parents=True)
        (deep_path / "main.py").write_text("x = 1")

        info = analyze_module(deep_path)

        self.assertIsInstance(info, ModuleInfo)

    def test_analyze_module_with_special_characters(self):
        """测试包含特殊字符的模块"""
        (self.temp_path / "文件.py").write_text("x = 1")

        info = analyze_module(self.temp_path)

        self.assertIsInstance(info, ModuleInfo)

    def test_generate_readme_empty_module(self):
        """测试空模块的 README 生成"""
        info = ModuleInfo(
            name="EmptyModule",
            path=str(self.temp_path),
            language="Unknown"
        )

        readme = generate_readme(info)

        self.assertIn("# EmptyModule", readme)
        # 检查是否包含占位符或说明
        self.assertTrue(any(keyword in readme for keyword in ["请", "TODO", "示例", "特性"]))

    def test_generate_design_empty_module(self):
        """测试空模块的 DESIGN 生成"""
        info = ModuleInfo(
            name="EmptyModule",
            path=str(self.temp_path),
            language="Unknown"
        )

        design = generate_design(info)

        self.assertIn("# EmptyModule 设计文档", design)
        # 检查是否包含占位符或说明
        self.assertTrue(any(keyword in design for keyword in ["请", "TODO", "设计", "决策"]))

    def test_analyze_python_module_with_syntax_error(self):
        """测试包含语法错误的 Python 模块"""
        (self.temp_path / "bad.py").write_text("def broken(\n")
        (self.temp_path / "good.py").write_text("def hello(): pass")

        info = analyze_python_module(self.temp_path)

        # 应该优雅地处理语法错误
        self.assertIsInstance(info, ModuleInfo)

    def test_analyze_python_module_large_file(self):
        """测试包含大文件的 Python 模块"""
        lines = []
        for i in range(1000):
            lines.append(f"def func{i}(): pass")
        (self.temp_path / "large.py").write_text("\n".join(lines))

        info = analyze_python_module(self.temp_path)

        self.assertGreater(len(info.functions), 0)

    def test_generate_docs_with_many_files(self):
        """测试包含多个文件的模块"""
        for i in range(50):
            (self.temp_path / f"file{i}.py").write_text(f"x{i} = {i}")

        result = generate_docs(str(self.temp_path), force=True)

        self.assertEqual(result["status"], "success")

    def test_detect_language_mixed_extensions(self):
        """测试混合扩展名检测"""
        (self.temp_path / "main.py").write_text("x = 1")
        (self.temp_path / "main.txt").write_text("text")
        (self.temp_path / "main.md").write_text("# Markdown")

        language = detect_language(self.temp_path)

        self.assertEqual(language, "Python")

    def test_generate_readme_with_long_description(self):
        """测试长描述的 README 生成"""
        long_desc = "This is a very long description. " * 100
        info = ModuleInfo(
            name="TestModule",
            path=str(self.temp_path),
            description=long_desc,
            language="Python"
        )

        readme = generate_readme(info)

        self.assertIn(long_desc[:50], readme)

    def test_generate_design_with_many_dependencies(self):
        """测试包含多个依赖的 DESIGN 生成"""
        deps = [f"package{i}" for i in range(20)]
        info = ModuleInfo(
            name="TestModule",
            path=str(self.temp_path),
            language="Python",
            dependencies=deps
        )

        design = generate_design(info)

        self.assertIn("package0", design)


if __name__ == '__main__':
    unittest.main()
