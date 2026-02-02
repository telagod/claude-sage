#!/usr/bin/env python3
"""
gen-docs: 文档生成器 Skill
自动分析模块结构，生成 README.md 和 DESIGN.md 骨架
"""

import sys
import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime


@dataclass
class ModuleInfo:
    name: str
    path: Path
    description: str = ""
    language: str = ""
    entry_points: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)


CODE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "React",
    ".tsx": "React TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".rb": "Ruby",
    ".php": "PHP",
}

SKIP_DIRS = {
    ".git", ".svn", ".hg",
    "node_modules", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".nuxt",
    "vendor", "third_party",
}


def detect_language(target_path: Path) -> str:
    """检测主要编程语言"""
    extension_counts: Dict[str, int] = {}

    for ext in CODE_EXTENSIONS:
        count = len(list(target_path.rglob(f"*{ext}")))
        if count > 0:
            extension_counts[ext] = count

    if not extension_counts:
        return "Unknown"

    main_ext = max(extension_counts, key=extension_counts.get)
    return CODE_EXTENSIONS.get(main_ext, "Unknown")


def detect_entry_points(target_path: Path) -> List[str]:
    """检测入口文件"""
    entry_patterns = [
        "main.py", "app.py", "__main__.py", "cli.py",
        "index.js", "index.ts", "main.js", "main.ts", "app.js", "app.ts",
        "main.go", "cmd/main.go",
        "main.rs", "lib.rs",
        "Main.java", "Application.java",
    ]

    found = []
    for pattern in entry_patterns:
        matches = list(target_path.glob(f"**/{pattern}"))
        for match in matches:
            rel_path = match.relative_to(target_path)
            if not any(part in SKIP_DIRS for part in rel_path.parts):
                found.append(str(rel_path))

    return found[:5]


def detect_dependencies(target_path: Path) -> List[str]:
    """检测依赖文件"""
    dep_files = [
        "requirements.txt", "setup.py", "pyproject.toml", "Pipfile",
        "package.json", "yarn.lock", "pnpm-lock.yaml",
        "go.mod", "go.sum",
        "Cargo.toml", "Cargo.lock",
        "pom.xml", "build.gradle", "build.gradle.kts",
        "Gemfile", "composer.json",
    ]

    found = []
    for dep_file in dep_files:
        if (target_path / dep_file).exists():
            found.append(dep_file)

    return found


def extract_exports_python(file_path: Path) -> List[str]:
    """提取 Python 模块的导出"""
    exports = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        classes = re.findall(r"^class\s+([A-Z]\w*)", content, re.MULTILINE)
        exports.extend([f"class {c}" for c in classes])

        functions = re.findall(r"^def\s+([a-z_]\w*)", content, re.MULTILINE)
        public_funcs = [f for f in functions if not f.startswith("_")]
        exports.extend([f"def {f}()" for f in public_funcs[:10]])

    except Exception:
        pass

    return exports[:15]


def analyze_module(target_path: Path) -> ModuleInfo:
    """分析模块信息"""
    info = ModuleInfo(
        name=target_path.name,
        path=target_path,
        language=detect_language(target_path),
        entry_points=detect_entry_points(target_path),
        dependencies=detect_dependencies(target_path),
    )

    for py_file in target_path.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
        info.exports.extend(extract_exports_python(py_file))

    return info


def generate_readme(info: ModuleInfo) -> str:
    """生成 README.md 内容"""
    template = f"""# {info.name}

> [简短描述：这个模块是什么，解决什么问题]

## 概述

[详细说明模块的用途和功能]

## 安装

```bash
# [安装命令]
```

## 快速开始

```{info.language.lower() if info.language != "Unknown" else "bash"}
# [使用示例]
```

## 功能特性

- [ ] 特性 1
- [ ] 特性 2
- [ ] 特性 3

## API 参考

"""

    if info.exports:
        template += "### 主要导出\n\n"
        for export in info.exports[:10]:
            template += f"- `{export}`\n"
        template += "\n"

    template += """## 配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| | | | |

## 依赖

"""

    if info.dependencies:
        for dep in info.dependencies:
            template += f"- {dep}\n"
    else:
        template += "- [列出主要依赖]\n"

    template += """
## 目录结构

```
"""
    template += f"{info.name}/\n"

    if info.entry_points:
        for entry in info.entry_points[:5]:
            template += f"├── {entry}\n"

    template += """├── README.md
├── DESIGN.md
└── ...
```

## 贡献指南

[如何贡献代码]

## 许可证

[许可证类型]

---

*由 Claude Sage gen-docs 生成*
"""

    return template


def generate_design(info: ModuleInfo) -> str:
    """生成 DESIGN.md 内容"""
    today = datetime.now().strftime("%Y-%m-%d")

    template = f"""# DESIGN.md - {info.name}

## 概述

本文档记录 {info.name} 模块的设计决策、架构选择和技术权衡。

## 设计目标

1. [目标 1]
2. [目标 2]
3. [目标 3]

## 架构设计

### 整体架构

```
[架构图或流程图]
```

### 核心组件

| 组件 | 职责 | 依赖 |
|------|------|------|
| | | |

## 技术选型

### 编程语言

- **选择**: {info.language}
- **原因**: [为什么选择这个语言]

### 关键依赖

"""

    if info.dependencies:
        for dep in info.dependencies:
            template += f"""
#### {dep}

- **用途**: [这个依赖的作用]
- **替代方案**: [考虑过的其他选项]
- **选择原因**: [为什么选择它]
"""

    template += """
## 设计决策

### 决策 1: [决策标题]

| 维度 | 方案 A | 方案 B | 选择 |
|------|--------|--------|------|
| 复杂度 | | | |
| 性能 | | | |
| 可维护性 | | | |

**决策**: [选择了哪个方案]

**理由**: [为什么这样选择]

**取舍**: [在哪些维度做了什么取舍]

## 安全考虑

- [ ] 输入验证
- [ ] 认证/授权
- [ ] 数据加密
- [ ] 日志脱敏

## 性能考虑

- [性能目标和约束]
- [优化策略]

## 技术债

| 债务 | 原因 | 影响 | 计划 |
|------|------|------|------|
| | | | |

## 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| v0.1.0 | {today} | 初始设计 | |

## 参考资料

- [相关文档链接]

---

*由 Claude Sage gen-docs 生成*
"""

    return template


def print_result(info: ModuleInfo, readme_path: Path, design_path: Path, json_output: bool = False):
    """输出结果"""
    if json_output:
        output = {
            "module": info.name,
            "language": info.language,
            "generated": {
                "readme": str(readme_path),
                "design": str(design_path),
            },
            "detected": {
                "entry_points": info.entry_points,
                "dependencies": info.dependencies,
                "exports": info.exports[:10],
            },
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print("")
    print("=" * 60)
    print("  文档生成报告: gen-docs")
    print("=" * 60)
    print("")
    print(f"  模块名称: {info.name}")
    print(f"  主要语言: {info.language}")
    print("")
    print("  生成文件:")
    print(f"    ✓ {readme_path}")
    print(f"    ✓ {design_path}")
    print("")

    if info.entry_points:
        print("  检测到的入口文件:")
        for entry in info.entry_points:
            print(f"    - {entry}")
        print("")

    if info.dependencies:
        print("  检测到的依赖文件:")
        for dep in info.dependencies:
            print(f"    - {dep}")
        print("")

    print("=" * 60)
    print("  【提示】请根据实际情况填充文档中的占位符")
    print("=" * 60)
    print("")


def main(args: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="文档生成器 - 生成 README.md 和 DESIGN.md 骨架",
        prog="gen-docs",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="目标模块路径 (默认: 当前目录)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="覆盖已存在的文件",
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

    readme_path = target_path / "README.md"
    design_path = target_path / "DESIGN.md"

    if not parsed.force:
        if readme_path.exists():
            print(f"[!] README.md 已存在，使用 --force 覆盖")
            return 1
        if design_path.exists():
            print(f"[!] DESIGN.md 已存在，使用 --force 覆盖")
            return 1

    if parsed.verbose:
        print(f"[i] 分析目标: {target_path}")

    info = analyze_module(target_path)

    readme_content = generate_readme(info)
    design_content = generate_design(info)

    readme_path.write_text(readme_content, encoding="utf-8")
    design_path.write_text(design_content, encoding="utf-8")

    print_result(info, readme_path, design_path, json_output=parsed.json)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
