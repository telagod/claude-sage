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
BACKUP_DIR="$CLAUDE_DIR/.sage-backup"
SKILLS_DIR="$CLAUDE_DIR/skills"
MANIFEST_FILE="$BACKUP_DIR/manifest.txt"

# Skills 列表
SKILLS=("verify-security" "verify-module" "verify-change" "verify-quality" "gen-docs")

# 脚本名称映射
declare -A SCRIPT_NAMES=(
    ["verify-security"]="security_scanner.py"
    ["verify-module"]="module_scanner.py"
    ["verify-change"]="change_analyzer.py"
    ["verify-quality"]="quality_checker.py"
    ["gen-docs"]="doc_generator.py"
)

print_banner() {
    echo -e "${CYAN}"
    echo "⚙️ ═══════════════════════════════════════════════════════════════ ⚙️"
    echo "       机械神教·铸造贤者 安装程序"
    echo "       Claude Sage Installer v1.2.0"
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
    else
        log_success "Python 已安装"
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
    log_info "备份现有配置..."

    # 创建备份目录
    mkdir -p "$BACKUP_DIR"

    # 清空旧的 manifest
    > "$MANIFEST_FILE"

    # 备份 CLAUDE.md
    if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
        cp "$CLAUDE_DIR/CLAUDE.md" "$BACKUP_DIR/CLAUDE.md"
        echo "CLAUDE.md" >> "$MANIFEST_FILE"
        log_success "  备份 CLAUDE.md"
    fi

    # 备份 skills 目录中受影响的文件
    if [ -d "$SKILLS_DIR" ]; then
        # 备份 run_skill.py
        if [ -f "$SKILLS_DIR/run_skill.py" ]; then
            cp "$SKILLS_DIR/run_skill.py" "$BACKUP_DIR/run_skill.py"
            echo "skills/run_skill.py" >> "$MANIFEST_FILE"
            log_success "  备份 skills/run_skill.py"
        fi

        # 备份每个 skill 目录
        for skill in "${SKILLS[@]}"; do
            if [ -d "$SKILLS_DIR/$skill" ]; then
                mkdir -p "$BACKUP_DIR/skills/$skill"
                cp -r "$SKILLS_DIR/$skill"/* "$BACKUP_DIR/skills/$skill/" 2>/dev/null || true
                echo "skills/$skill" >> "$MANIFEST_FILE"
                log_success "  备份 skills/$skill/"
            fi
        done
    fi

    # 记录安装时间
    echo "# Installed: $(date)" >> "$MANIFEST_FILE"

    if [ -s "$MANIFEST_FILE" ]; then
        log_success "备份完成，清单保存至 $MANIFEST_FILE"
    else
        log_info "无需备份（首次安装）"
    fi
}

install_config() {
    log_info "安装配置文件..."

    # 创建 .claude 目录
    mkdir -p "$CLAUDE_DIR"

    # 下载 CLAUDE.md 到 ~/.claude/
    download_file "$REPO_URL/config/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
    log_success "CLAUDE.md 已安装"
}

install_skills() {
    log_info "安装 skills..."

    # 创建 skills 目录
    mkdir -p "$SKILLS_DIR"

    # 下载 run_skill.py 入口
    download_file "$REPO_URL/skills/run_skill.py" "$SKILLS_DIR/run_skill.py"
    chmod +x "$SKILLS_DIR/run_skill.py"
    log_success "run_skill.py 入口脚本"

    # 安装每个 skill
    for skill in "${SKILLS[@]}"; do
        log_info "  安装 $skill..."

        # 创建 skill 目录结构
        mkdir -p "$SKILLS_DIR/$skill/scripts"

        # 下载 SKILL.md
        download_file "$REPO_URL/skills/$skill/SKILL.md" "$SKILLS_DIR/$skill/SKILL.md"

        # 下载脚本
        local script_name="${SCRIPT_NAMES[$skill]}"
        download_file "$REPO_URL/skills/$skill/scripts/$script_name" "$SKILLS_DIR/$skill/scripts/$script_name"
        chmod +x "$SKILLS_DIR/$skill/scripts/$script_name"

        log_success "    $skill ✓"
    done

    log_success "Skills 安装完成"
}

install_uninstaller() {
    log_info "安装卸载脚本..."

    download_file "$REPO_URL/uninstall.sh" "$CLAUDE_DIR/.sage-uninstall.sh"
    chmod +x "$CLAUDE_DIR/.sage-uninstall.sh"
    log_success "卸载脚本已安装"
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

    # 检查 run_skill.py
    if [ ! -f "$SKILLS_DIR/run_skill.py" ]; then
        log_error "run_skill.py 未找到"
        ((errors++))
    else
        log_success "run_skill.py ✓"
    fi

    # 检查每个 skill
    local skill_count=0
    for skill in "${SKILLS[@]}"; do
        local script_name="${SCRIPT_NAMES[$skill]}"
        if [ -f "$SKILLS_DIR/$skill/SKILL.md" ] && [ -f "$SKILLS_DIR/$skill/scripts/$script_name" ]; then
            ((skill_count++))
        else
            log_warn "$skill 不完整"
        fi
    done

    if [ $skill_count -eq ${#SKILLS[@]} ]; then
        log_success "Skills ($skill_count/${#SKILLS[@]}) ✓"
    else
        log_warn "Skills 不完整 ($skill_count/${#SKILLS[@]})"
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
    echo "  已安装文件结构:"
    echo "    $CLAUDE_DIR/"
    echo "    ├── CLAUDE.md"
    echo "    ├── .sage-backup/          # 备份目录"
    echo "    ├── .sage-uninstall.sh     # 卸载脚本"
    echo "    └── skills/"
    echo "        ├── run_skill.py"
    echo "        ├── verify-security/"
    echo "        ├── verify-module/"
    echo "        ├── verify-change/"
    echo "        ├── verify-quality/"
    echo "        └── gen-docs/"
    echo ""
    echo "  已安装的 Skills:"
    echo "    /verify-security  - 安全校验"
    echo "    /verify-module    - 模块完整性校验"
    echo "    /verify-change    - 变更校验"
    echo "    /verify-quality   - 代码质量检查"
    echo "    /gen-docs         - 文档生成器"
    echo ""
    echo "  卸载命令:"
    echo "    ~/.claude/.sage-uninstall.sh"
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
    install_uninstaller
    verify_installation
    print_success
}

main "$@"
