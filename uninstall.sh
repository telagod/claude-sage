#!/usr/bin/env bash
#
# Code Abyss 卸载脚本
# 卸载配置并恢复备份
#

set -e

# 版本
VERSION="1.5.0"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 配置
TARGET=""
TARGET_DIR=""
BACKUP_DIR=""
SKILLS_DIR=""
OUTPUT_STYLES_DIR=""
SETTINGS_FILE=""
MANIFEST_FILE=""
CONFIG_FILENAME=""
ENABLE_OUTPUT_STYLE="false"

# Skills 列表
SKILLS=("verify-security" "verify-module" "verify-change" "verify-quality" "gen-docs")

# 输出风格
OUTPUT_STYLE_NAME="abyss-cultivator"

is_interactive() {
    [ -t 1 ] && [ -r /dev/tty ]
}

tty_read() {
    local prompt="$1"
    local __var_name="$2"
    local value=""

    if [ -r /dev/tty ]; then
        read -r -p "$prompt" value < /dev/tty || true
    else
        read -r -p "$prompt" value || true
    fi

    printf -v "$__var_name" '%s' "$value"
}

usage() {
    cat <<EOF
用法:
  ./uninstall.sh [--target claude|codex]

说明:
  --target claude  卸载 ~/.claude/（Claude Code CLI）
  --target codex   卸载 ~/.codex/（Codex CLI）

提示:
  若脚本位于 ~/.claude/ 或 ~/.codex/（如 ~/.codex/.sage-uninstall.sh），将自动识别目标。

EOF
}

select_target_interactive() {
    echo ""
    echo "请选择卸载目标:"
    echo "  1) Claude Code (卸载 ~/.claude/)"
    echo "  2) Codex CLI   (卸载 ~/.codex/)"
    echo ""
    local choice=""
    tty_read "输入序号 [1/2] (默认 1): " choice
    case "${choice:-1}" in
        1) TARGET="claude" ;;
        2) TARGET="codex" ;;
        *) TARGET="claude" ;;
    esac
}

init_target_vars() {
    local script_dir
    script_dir="$(cd "$(dirname "$0")" && pwd)"

    if [ -z "$TARGET" ]; then
        if [ "$script_dir" = "$HOME/.claude" ]; then
            TARGET="claude"
        elif [ "$script_dir" = "$HOME/.codex" ]; then
            TARGET="codex"
        fi
    fi

    if [ -z "$TARGET" ]; then
        if is_interactive; then
            select_target_interactive
        else
            TARGET="claude"
        fi
    fi

    case "$TARGET" in
        claude)
            TARGET_DIR="$HOME/.claude"
            CONFIG_FILENAME="CLAUDE.md"
            ENABLE_OUTPUT_STYLE="true"
            ;;
        codex)
            TARGET_DIR="$HOME/.codex"
            CONFIG_FILENAME="AGENTS.md"
            ENABLE_OUTPUT_STYLE="false"
            ;;
        *)
            log_error "未知 target: $TARGET（仅支持 claude|codex）"
            exit 1
            ;;
    esac

    BACKUP_DIR="$TARGET_DIR/.sage-backup"
    SKILLS_DIR="$TARGET_DIR/skills"
    OUTPUT_STYLES_DIR="$TARGET_DIR/output-styles"
    SETTINGS_FILE="$TARGET_DIR/settings.json"
    MANIFEST_FILE="$BACKUP_DIR/manifest.txt"
}

print_banner() {
    echo -e "${CYAN}"
    echo "☠️ ═══════════════════════════════════════════════════════════════ ☠️"
    echo "       邪修红尘仙·宿命深渊 卸载程序"
    echo "       Code Abyss Uninstaller v${VERSION}"
    echo "☠️ ═══════════════════════════════════════════════════════════════ ☠️"
    echo -e "${NC}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

remove_installed_files() {
    log_info "移除已安装的文件..."

    # 移除配置文件（CLAUDE.md / AGENTS.md）
    if [ -f "$TARGET_DIR/$CONFIG_FILENAME" ]; then
        rm -f "$TARGET_DIR/$CONFIG_FILENAME"
        log_success "  移除 $CONFIG_FILENAME"
    fi

    # 移除输出风格文件
    if [ "$ENABLE_OUTPUT_STYLE" = "true" ] && [ -f "$OUTPUT_STYLES_DIR/$OUTPUT_STYLE_NAME.md" ]; then
        rm -f "$OUTPUT_STYLES_DIR/$OUTPUT_STYLE_NAME.md"
        log_success "  移除 output-styles/$OUTPUT_STYLE_NAME.md"
    fi

    # 如果 output-styles 目录为空，删除它
    if [ "$ENABLE_OUTPUT_STYLE" = "true" ] && [ -d "$OUTPUT_STYLES_DIR" ] && [ -z "$(ls -A "$OUTPUT_STYLES_DIR" 2>/dev/null)" ]; then
        rmdir "$OUTPUT_STYLES_DIR"
        log_success "  移除空的 output-styles/ 目录"
    fi

    # 移除 run_skill.py
    if [ -f "$SKILLS_DIR/run_skill.py" ]; then
        rm -f "$SKILLS_DIR/run_skill.py"
        log_success "  移除 skills/run_skill.py"
    fi

    # 移除每个 skill 目录
    for skill in "${SKILLS[@]}"; do
        if [ -d "$SKILLS_DIR/$skill" ]; then
            rm -rf "$SKILLS_DIR/$skill"
            log_success "  移除 skills/$skill/"
        fi
    done

    # 如果 skills 目录为空，删除它
    if [ -d "$SKILLS_DIR" ] && [ -z "$(ls -A "$SKILLS_DIR" 2>/dev/null)" ]; then
        rmdir "$SKILLS_DIR"
        log_success "  移除空的 skills/ 目录"
    fi

    log_success "已安装文件移除完成"
}

restore_backup() {
    log_info "恢复备份..."

    if [ ! -d "$BACKUP_DIR" ] || [ ! -f "$MANIFEST_FILE" ]; then
        log_info "无备份可恢复（首次安装或备份已清理）"
        return 0
    fi

    local restored=0

    # 恢复 CLAUDE.md
    if [ -f "$BACKUP_DIR/$CONFIG_FILENAME" ]; then
        cp "$BACKUP_DIR/$CONFIG_FILENAME" "$TARGET_DIR/$CONFIG_FILENAME"
        log_success "  恢复 $CONFIG_FILENAME"
        ((restored++))
    fi

    # 恢复 settings.json
    if [ "$ENABLE_OUTPUT_STYLE" = "true" ] && [ -f "$BACKUP_DIR/settings.json" ]; then
        cp "$BACKUP_DIR/settings.json" "$SETTINGS_FILE"
        log_success "  恢复 settings.json"
        ((restored++))
    fi

    # 恢复输出风格文件
    if [ "$ENABLE_OUTPUT_STYLE" = "true" ] && [ -f "$BACKUP_DIR/output-styles/$OUTPUT_STYLE_NAME.md" ]; then
        mkdir -p "$OUTPUT_STYLES_DIR"
        cp "$BACKUP_DIR/output-styles/$OUTPUT_STYLE_NAME.md" "$OUTPUT_STYLES_DIR/"
        log_success "  恢复 output-styles/$OUTPUT_STYLE_NAME.md"
        ((restored++))
    fi

    # 恢复 run_skill.py
    if [ -f "$BACKUP_DIR/run_skill.py" ]; then
        mkdir -p "$SKILLS_DIR"
        cp "$BACKUP_DIR/run_skill.py" "$SKILLS_DIR/run_skill.py"
        log_success "  恢复 skills/run_skill.py"
        ((restored++))
    fi

    # 恢复每个 skill 目录
    for skill in "${SKILLS[@]}"; do
        if [ -d "$BACKUP_DIR/skills/$skill" ]; then
            mkdir -p "$SKILLS_DIR/$skill"
            cp -r "$BACKUP_DIR/skills/$skill"/* "$SKILLS_DIR/$skill/"
            log_success "  恢复 skills/$skill/"
            ((restored++))
        fi
    done

    if [ $restored -gt 0 ]; then
        log_success "已恢复 $restored 个备份项"
    else
        log_info "无文件需要恢复"
    fi
}

cleanup_backup() {
    log_info "清理备份目录..."

    if [ -d "$BACKUP_DIR" ]; then
        rm -rf "$BACKUP_DIR"
        log_success "  备份目录已清理"
    fi

    # 移除卸载脚本自身
    local script_dir
    script_dir="$(cd "$(dirname "$0")" && pwd)"
    if [ "$script_dir" = "$TARGET_DIR" ] && [ "$(basename "$0")" = ".sage-uninstall.sh" ]; then
        rm -f "$TARGET_DIR/.sage-uninstall.sh"
        log_success "  卸载脚本已移除"
    fi

    log_success "清理完成"
}

print_success() {
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✓ 卸载完成！${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  已执行操作:"
    echo "    ✓ 移除 Code Abyss 安装的文件"
    echo "    ✓ 恢复之前的备份（如有）"
    echo "    ✓ 清理备份目录"
    echo ""
    echo "  如需重新安装:"
    echo "    curl -fsSL https://raw.githubusercontent.com/telagod/code-abyss/main/install.sh | bash"
    echo ""
    echo -e "${CYAN}  「道基已净，愿来世再渡此劫。」${NC}"
    echo ""
}

confirm_uninstall() {
    echo ""
    echo -e "${YELLOW}即将卸载 Code Abyss（target=$TARGET）并恢复备份。${NC}"
    echo ""
    local reply=""
    if [ -r /dev/tty ]; then
        read -r -p "确认卸载？[y/N] " -n 1 reply < /dev/tty || true
    else
        read -r -p "确认卸载？[y/N] " -n 1 reply || true
    fi
    echo ""

    if [[ ! $reply =~ ^[Yy]$ ]]; then
        echo "已取消卸载。"
        exit 0
    fi
}

main() {
    while [ $# -gt 0 ]; do
        case "$1" in
            --target)
                TARGET="${2:-}"
                shift 2
                ;;
            --target=*)
                TARGET="${1#*=}"
                shift 1
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                usage
                exit 1
                ;;
        esac
    done

    init_target_vars

    print_banner
    confirm_uninstall
    remove_installed_files
    restore_backup
    cleanup_backup
    print_success
}

main "$@"
