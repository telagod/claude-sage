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
    local timestamp=$(date +%Y%m%d_%H%M%S)

    if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
        log_info "备份现有配置..."
        mkdir -p "$BACKUP_DIR"
        cp "$CLAUDE_DIR/CLAUDE.md" "$BACKUP_DIR/CLAUDE.md.$timestamp"
        log_success "已备份到 $BACKUP_DIR/CLAUDE.md.$timestamp"
    fi

    if [ -d "$SKILLS_DIR" ] && [ "$(ls -A $SKILLS_DIR 2>/dev/null)" ]; then
        log_info "备份现有 skills..."
        mkdir -p "$BACKUP_DIR"
        cp -r "$SKILLS_DIR" "$BACKUP_DIR/skills.$timestamp"
        log_success "已备份到 $BACKUP_DIR/skills.$timestamp"
    fi
}

install_config() {
    log_info "安装配置文件..."

    # 创建 .claude 目录
    mkdir -p "$CLAUDE_DIR"

    # 下载 CLAUDE.md 到 ~/.claude/
    download_file "$REPO_URL/config/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
    log_success "CLAUDE.md 已安装到 $CLAUDE_DIR/"
}

install_skills() {
    log_info "安装 skills..."

    # 创建 skills 目录
    mkdir -p "$SKILLS_DIR"

    # Python 脚本文件
    local py_scripts=(
        "run_skill.py"
        "verify_security.py"
        "verify_module.py"
        "verify_change.py"
        "verify_quality.py"
        "gen_docs.py"
    )

    # Skill 描述文件 (.md) - Claude Code 需要这些文件来识别 skills
    local skill_mds=(
        "verify-security.md"
        "verify-module.md"
        "verify-change.md"
        "verify-quality.md"
        "gen-docs.md"
    )

    log_info "  下载 Python 脚本..."
    for script in "${py_scripts[@]}"; do
        download_file "$REPO_URL/skills/$script" "$SKILLS_DIR/$script"
        chmod +x "$SKILLS_DIR/$script"
        log_success "    $script"
    done

    log_info "  下载 Skill 描述文件..."
    for md in "${skill_mds[@]}"; do
        download_file "$REPO_URL/skills/$md" "$SKILLS_DIR/$md"
        log_success "    $md"
    done

    log_success "Skills 安装完成"
}

verify_installation() {
    log_info "验证安装..."

    local errors=0

    # 检查 CLAUDE.md
    if [ ! -f "$CLAUDE_DIR/CLAUDE.md" ]; then
        log_error "CLAUDE.md 未找到"
        ((errors++))
    else
        log_success "CLAUDE.md ✓"
    fi

    # 检查 skills 目录
    if [ ! -d "$SKILLS_DIR" ]; then
        log_error "skills 目录未找到"
        ((errors++))
    else
        log_success "skills 目录 ✓"
    fi

    # 检查 Python 入口
    if [ ! -f "$SKILLS_DIR/run_skill.py" ]; then
        log_error "run_skill.py 未找到"
        ((errors++))
    else
        log_success "run_skill.py ✓"
    fi

    # 检查 skill 描述文件
    local skill_count=0
    for md in verify-security.md verify-module.md verify-change.md verify-quality.md gen-docs.md; do
        if [ -f "$SKILLS_DIR/$md" ]; then
            ((skill_count++))
        fi
    done

    if [ $skill_count -eq 5 ]; then
        log_success "Skill 描述文件 ($skill_count/5) ✓"
    else
        log_warn "Skill 描述文件不完整 ($skill_count/5)"
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
    echo "  已安装文件:"
    echo "    配置文件: $CLAUDE_DIR/CLAUDE.md"
    echo "    Skills:   $SKILLS_DIR/"
    echo ""
    echo "  已安装的 Skills:"
    echo "    /verify-security  - 安全校验"
    echo "    /verify-module    - 模块完整性校验"
    echo "    /verify-change    - 变更校验"
    echo "    /verify-quality   - 代码质量检查"
    echo "    /gen-docs         - 文档生成器"
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
