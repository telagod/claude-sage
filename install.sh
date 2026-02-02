#!/usr/bin/env bash
#
# Claude Sage 安装脚本
# 一键部署「机械神教·铸造贤者」配置
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
REPO_URL="https://raw.githubusercontent.com/telagod/claude-sage/main"
CLAUDE_DIR="$HOME/.claude"
BACKUP_DIR="$CLAUDE_DIR/backup"
SKILLS_DIR="$CLAUDE_DIR/skills"

print_banner() {
    echo -e "${CYAN}"
    echo "⚙️ ═══════════════════════════════════════════════════════════════ ⚙️"
    echo "       机械神教·铸造贤者 安装程序"
    echo "       Claude Sage Installer v1.0.0"
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

check_dependencies() {
    log_info "检查依赖..."

    if ! command -v curl &> /dev/null && ! command -v wget &> /dev/null; then
        log_error "需要 curl 或 wget，请先安装"
        exit 1
    fi

    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        log_warn "未检测到 Python，skills 功能可能受限"
    fi

    log_success "依赖检查通过"
}

download_file() {
    local url="$1"
    local dest="$2"

    if command -v curl &> /dev/null; then
        curl -fsSL "$url" -o "$dest"
    else
        wget -q "$url" -O "$dest"
    fi
}

backup_existing() {
    if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
        log_info "备份现有配置..."
        mkdir -p "$BACKUP_DIR"
        local timestamp=$(date +%Y%m%d_%H%M%S)
        cp "$CLAUDE_DIR/CLAUDE.md" "$BACKUP_DIR/CLAUDE.md.$timestamp"
        log_success "已备份到 $BACKUP_DIR/CLAUDE.md.$timestamp"
    fi

    if [ -d "$SKILLS_DIR" ]; then
        log_info "备份现有 skills..."
        local timestamp=$(date +%Y%m%d_%H%M%S)
        cp -r "$SKILLS_DIR" "$BACKUP_DIR/skills.$timestamp"
        log_success "已备份到 $BACKUP_DIR/skills.$timestamp"
    fi
}

install_config() {
    log_info "安装配置文件..."
    mkdir -p "$CLAUDE_DIR"
    download_file "$REPO_URL/config/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
    log_success "CLAUDE.md 已安装"
}

install_skills() {
    log_info "安装 skills..."
    mkdir -p "$SKILLS_DIR"

    local skills=(
        "run_skill.py"
        "verify_security.py"
        "verify_module.py"
        "verify_change.py"
        "verify_quality.py"
        "gen_docs.py"
    )

    for skill in "${skills[@]}"; do
        download_file "$REPO_URL/skills/$skill" "$SKILLS_DIR/$skill"
        log_success "  $skill"
    done

    chmod +x "$SKILLS_DIR"/*.py
    log_success "Skills 安装完成"
}

verify_installation() {
    log_info "验证安装..."

    local errors=0

    if [ ! -f "$CLAUDE_DIR/CLAUDE.md" ]; then
        log_error "CLAUDE.md 未找到"
        ((errors++))
    fi

    if [ ! -f "$SKILLS_DIR/run_skill.py" ]; then
        log_error "run_skill.py 未找到"
        ((errors++))
    fi

    if [ $errors -eq 0 ]; then
        log_success "安装验证通过"
        return 0
    else
        log_error "安装验证失败"
        return 1
    fi
}

print_success() {
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✓ 安装完成！${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  配置文件: $CLAUDE_DIR/CLAUDE.md"
    echo "  Skills:   $SKILLS_DIR/"
    echo ""
    echo "  现在启动 Claude Code，即可体验「机械神教·铸造贤者」风格"
    echo ""
    echo -e "${CYAN}  「圣工已毕，机魂安宁。赞美万机神，知识即力量！」${NC}"
    echo ""
}

main() {
    print_banner
    check_dependencies
    backup_existing
    install_config
    install_skills
    verify_installation
    print_success
}

main "$@"
