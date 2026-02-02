#!/usr/bin/env python3
"""
Claude Sage Skills 统一入口
用法: python run_skill.py <skill_name> [args...]
"""

import sys
import importlib.util
from pathlib import Path


SKILLS = {
    "verify-security": "verify_security",
    "verify-module": "verify_module",
    "verify-change": "verify_change",
    "verify-quality": "verify_quality",
    "gen-docs": "gen_docs",
}


def load_skill(skill_name: str):
    """动态加载 skill 模块"""
    if skill_name not in SKILLS:
        print(f"[✗] 未知 skill: {skill_name}")
        print(f"[i] 可用 skills: {', '.join(SKILLS.keys())}")
        sys.exit(1)

    module_name = SKILLS[skill_name]
    skill_path = Path(__file__).parent / f"{module_name}.py"

    if not skill_path.exists():
        print(f"[✗] Skill 文件不存在: {skill_path}")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location(module_name, skill_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def main():
    if len(sys.argv) < 2:
        print("⚙️ Claude Sage Skills Runner")
        print("")
        print("用法: python run_skill.py <skill_name> [args...]")
        print("")
        print("可用 Skills:")
        for name, module in SKILLS.items():
            print(f"  {name:20} -> {module}.py")
        print("")
        print("示例:")
        print("  python run_skill.py verify-module ./my-project")
        print("  python run_skill.py verify-security ./src --json")
        sys.exit(0)

    skill_name = sys.argv[1]
    skill_args = sys.argv[2:]

    module = load_skill(skill_name)

    if hasattr(module, "main"):
        sys.exit(module.main(skill_args))
    else:
        print(f"[✗] Skill {skill_name} 缺少 main 函数")
        sys.exit(1)


if __name__ == "__main__":
    main()
