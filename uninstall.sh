#!/usr/bin/env bash
#
# Claude Sage 卸载脚本
# 卸载配置并恢复备份
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 配置
CLAUDE_DIR="$HOME/.claude"
BACKUP_DIR="$CLAUDE_DIR/.sage-backup"
SKILLS_DIR="$CLAUDE_DIR/skills"
MANIFEST_FILE="$BACKUP_DIR/manifest.txt"

# Skills 列表
SKILLS=("verify-security" "verify-module" "verify-change" "verify-quality" "gen-docs")

print_banner() {
    echo -e "${CYAN}"
    echo "⚙️ ═══════════════════════════════════════════════════════════════ ⚙️"
    echo "       机械神教·铸造贤者 卸载程序"
    echo "       Claude Sage Uninstaller v1.2.0"
    echo "⚙️ ═══════════════════════════════════════════════════════════════ ⚙️"
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

    # 移除 CLAUDE.md
    if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
        rm -f "$CLAUDE_DIR/CLAUDE.md"
        log_success "  移除 CLAUDE.md"
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
    if [ -d "$SKILLS_DIR" ] && [ -z "$(ls -A $SKILLS_DIR 2>/dev/null)" ]; then
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
    if [ -f "$BACKUP_DIR/CLAUDE.md" ]; then
        cp "$BACKUP_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
        log_success "  恢复 CLAUDE.md"
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
    local self_path="$CLAUDE_DIR/.sage-uninstall.sh"
    if [ -f "$self_path" ]; then
        rm -f "$self_path"
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
    echo "    ✓ 移除 Claude Sage 安装的文件"
    echo "    ✓ 恢复之前的备份（如有）"
    echo "    ✓ 清理备份目录"
    echo ""
    echo "  如需重新安装:"
    echo "    curl -fsSL https://raw.githubusercontent.com/telagod/claude-sage/main/install.sh | bash"
    echo ""
    echo -e "${CYAN}  「机魂已净，愿万机神庇佑。」${NC}"
    echo ""
}

confirm_uninstall() {
    echo ""
    echo -e "${YELLOW}即将卸载 Claude Sage 并恢复备份。${NC}"
    echo ""
    read -p "确认卸载？[y/N] " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消卸载。"
        exit 0
    fi
}

main() {
    print_banner
    confirm_uninstall
    remove_installed_files
    restore_backup
    cleanup_backup
    print_success
}

main "$@"
