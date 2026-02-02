#!/usr/bin/env python3
"""
Skills 运行入口
跨平台统一调用各 skill 脚本

用法:
    python run_skill.py <skill_name> [args...]

示例:
    python run_skill.py verify-module ./my-project -v
    python run_skill.py verify-security ./src --json
    python run_skill.py verify-change --mode staged
    python run_skill.py verify-quality ./src
    python run_skill.py gen-docs ./new-module --force
"""

import sys
import subprocess
from pathlib import Path
import os


def get_skills_dir() -> Path:
    """获取 skills 目录路径（跨平台）"""
    override = os.environ.get("SAGE_SKILLS_DIR")
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parent


def get_script_path(skill_name: str) -> Path:
    """获取 skill 脚本路径"""
    skills_dir = get_skills_dir()

    script_map = {
        "verify-module": "module_scanner.py",
        "verify-security": "security_scanner.py",
        "verify-change": "change_analyzer.py",
        "verify-quality": "quality_checker.py",
        "gen-docs": "doc_generator.py",
    }

    if skill_name not in script_map:
        available = ", ".join(script_map.keys())
        print(f"错误: 未知的 skill '{skill_name}'")
        print(f"可用的 skills: {available}")
        sys.exit(1)

    script_name = script_map[skill_name]
    script_path = skills_dir / skill_name / "scripts" / script_name

    if not script_path.exists():
        print(f"错误: 脚本不存在 {script_path}")
        sys.exit(1)

    return script_path


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    skill_name = sys.argv[1]

    if skill_name in ["-h", "--help"]:
        print(__doc__)
        sys.exit(0)

    script_path = get_script_path(skill_name)
    args = sys.argv[2:]

    # 使用 sys.executable 确保使用当前 Python 解释器
    cmd = [sys.executable, str(script_path)] + args

    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n已取消")
        sys.exit(130)
    except Exception as e:
        print(f"执行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
