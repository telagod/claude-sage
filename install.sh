#!/usr/bin/env bash
#
# Code Abyss 安装脚本
# 一键部署「机械神教·铸造贤者」配置
#

set -e

# 版本
VERSION="1.5.0"
VERSION_PIN="v1.5.0"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 配置
REPO_URL="https://raw.githubusercontent.com/telagod/code-abyss/$VERSION_PIN"
TARGET=""
TARGET_DIR=""
BACKUP_DIR=""
SKILLS_DIR=""
OUTPUT_STYLES_DIR=""
SETTINGS_FILE=""
MANIFEST_FILE=""
CONFIG_FILENAME=""
CONFIG_SOURCE_PATH=""
ENABLE_OUTPUT_STYLE="false"

# Skills 列表
SKILLS=("verify-security" "verify-module" "verify-change" "verify-quality" "gen-docs")

# 脚本名称映射（使用函数替代关联数组，兼容 Bash 3.x）
get_script_name() {
    case "$1" in
        verify-security) echo "security_scanner.py" ;;
        verify-module)   echo "module_scanner.py" ;;
        verify-change)   echo "change_analyzer.py" ;;
        verify-quality)  echo "quality_checker.py" ;;
        gen-docs)        echo "doc_generator.py" ;;
    esac
}

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
  ./install.sh [--target claude|codex] [--ref <git-ref>]

说明:
  --target claude  安装到 ~/.claude/（Claude Code CLI）
  --target codex   安装到 ~/.codex/（Codex CLI，安装 AGENTS.md + skills）
  --ref <git-ref>  指定下载分支/标签/commit，默认 $VERSION_PIN

EOF
}

select_target_interactive() {
    echo ""
    echo "请选择安装目标:"
    echo "  1) Claude Code (安装到 ~/.claude/)"
    echo "  2) Codex CLI   (安装到 ~/.codex/)"
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
    case "$TARGET" in
        claude)
            TARGET_DIR="$HOME/.claude"
            CONFIG_FILENAME="CLAUDE.md"
            CONFIG_SOURCE_PATH="config/CLAUDE.md"
            ENABLE_OUTPUT_STYLE="true"
            ;;
        codex)
            TARGET_DIR="$HOME/.codex"
            CONFIG_FILENAME="AGENTS.md"
            CONFIG_SOURCE_PATH="config/AGENTS.md"
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
    echo "       邪修红尘仙·宿命深渊 安装程序"
    echo "       Code Abyss Installer v${VERSION}"
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

    # 备份配置文件（CLAUDE.md / AGENTS.md）
    if [ -f "$TARGET_DIR/$CONFIG_FILENAME" ]; then
        cp "$TARGET_DIR/$CONFIG_FILENAME" "$BACKUP_DIR/$CONFIG_FILENAME"
        echo "$CONFIG_FILENAME" >> "$MANIFEST_FILE"
        log_success "  备份 $CONFIG_FILENAME"
    fi

    # 备份 settings.json（记录原始 outputStyle）
    if [ "$ENABLE_OUTPUT_STYLE" = "true" ] && [ -f "$SETTINGS_FILE" ]; then
        cp "$SETTINGS_FILE" "$BACKUP_DIR/settings.json"
        echo "settings.json" >> "$MANIFEST_FILE"
        log_success "  备份 settings.json"
    fi

    # 备份 output-styles 中的同名文件
    if [ "$ENABLE_OUTPUT_STYLE" = "true" ] && [ -f "$OUTPUT_STYLES_DIR/$OUTPUT_STYLE_NAME.md" ]; then
        mkdir -p "$BACKUP_DIR/output-styles"
        cp "$OUTPUT_STYLES_DIR/$OUTPUT_STYLE_NAME.md" "$BACKUP_DIR/output-styles/"
        echo "output-styles/$OUTPUT_STYLE_NAME.md" >> "$MANIFEST_FILE"
        log_success "  备份 output-styles/$OUTPUT_STYLE_NAME.md"
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

    # 创建目标目录
    mkdir -p "$TARGET_DIR"

    # 下载配置文件
    download_file "$REPO_URL/$CONFIG_SOURCE_PATH" "$TARGET_DIR/$CONFIG_FILENAME"
    log_success "$CONFIG_FILENAME 已安装"
}

install_output_style() {
    log_info "安装输出风格..."

    if [ "$ENABLE_OUTPUT_STYLE" != "true" ]; then
        log_info "当前 target=$TARGET，不安装 output-styles 与 settings.json"
        return 0
    fi

    # 创建 output-styles 目录
    mkdir -p "$OUTPUT_STYLES_DIR"

    # 下载输出风格文件
    download_file "$REPO_URL/output-styles/$OUTPUT_STYLE_NAME.md" "$OUTPUT_STYLES_DIR/$OUTPUT_STYLE_NAME.md"
    log_success "输出风格 $OUTPUT_STYLE_NAME.md 已安装"
}

configure_output_style() {
    log_info "配置默认输出风格..."

    if [ "$ENABLE_OUTPUT_STYLE" != "true" ]; then
        log_info "当前 target=$TARGET，不配置 outputStyle"
        return 0
    fi

    if [ -f "$SETTINGS_FILE" ]; then
        # settings.json 存在，更新 outputStyle（使用环境变量避免注入）
        if command -v python3 &> /dev/null; then
            SETTINGS_FILE="$SETTINGS_FILE" OUTPUT_STYLE="$OUTPUT_STYLE_NAME" python3 -c "
import json
import os
settings_file = os.environ['SETTINGS_FILE']
output_style = os.environ['OUTPUT_STYLE']
with open(settings_file, 'r') as f:
    settings = json.load(f)
settings['outputStyle'] = output_style
with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)
"
            log_success "已设置 outputStyle 为 $OUTPUT_STYLE_NAME"
        elif command -v python &> /dev/null; then
            SETTINGS_FILE="$SETTINGS_FILE" OUTPUT_STYLE="$OUTPUT_STYLE_NAME" python -c "
import json
import os
settings_file = os.environ['SETTINGS_FILE']
output_style = os.environ['OUTPUT_STYLE']
with open(settings_file, 'r') as f:
    settings = json.load(f)
settings['outputStyle'] = output_style
with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)
"
            log_success "已设置 outputStyle 为 $OUTPUT_STYLE_NAME"
        else
            log_warn "无法自动配置 outputStyle（需要 Python）"
            log_info "请手动在 settings.json 中添加: \"outputStyle\": \"$OUTPUT_STYLE_NAME\""
        fi
    else
        # settings.json 不存在，创建基础配置
        echo "{
  \"outputStyle\": \"$OUTPUT_STYLE_NAME\"
}" > "$SETTINGS_FILE"
        log_success "已创建 settings.json 并设置 outputStyle"
    fi
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
        local script_name
        script_name="$(get_script_name "$skill")"
        download_file "$REPO_URL/skills/$skill/scripts/$script_name" "$SKILLS_DIR/$skill/scripts/$script_name"
        chmod +x "$SKILLS_DIR/$skill/scripts/$script_name"

        log_success "    $skill ✓"
    done

    log_success "Skills 安装完成"
}

install_uninstaller() {
    log_info "安装卸载脚本..."

    download_file "$REPO_URL/uninstall.sh" "$TARGET_DIR/.sage-uninstall.sh"
    chmod +x "$TARGET_DIR/.sage-uninstall.sh"
    log_success "卸载脚本已安装"
}

verify_installation() {
    log_info "验证安装..."

    local errors=0

    # 检查配置文件
    if [ ! -f "$TARGET_DIR/$CONFIG_FILENAME" ]; then
        log_error "$CONFIG_FILENAME 未找到"
        ((errors++))
    else
        log_success "$CONFIG_FILENAME ✓"
    fi

    # 检查输出风格
    if [ "$ENABLE_OUTPUT_STYLE" = "true" ]; then
        if [ ! -f "$OUTPUT_STYLES_DIR/$OUTPUT_STYLE_NAME.md" ]; then
            log_error "输出风格文件未找到"
            ((errors++))
        else
            log_success "output-styles/$OUTPUT_STYLE_NAME.md ✓"
        fi
    fi

    # 检查 settings.json 中的 outputStyle
    if [ "$ENABLE_OUTPUT_STYLE" = "true" ]; then
        if [ -f "$SETTINGS_FILE" ]; then
            if grep -q "\"outputStyle\".*\"$OUTPUT_STYLE_NAME\"" "$SETTINGS_FILE"; then
                log_success "settings.json outputStyle ✓"
            else
                log_warn "settings.json outputStyle 未正确配置"
            fi
        fi
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
        local script_name
        script_name="$(get_script_name "$skill")"
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
    echo "  安装目标: $TARGET"
    echo "  已安装文件结构:"
    echo "    $TARGET_DIR/"
    echo "    ├── $CONFIG_FILENAME"
    if [ "$ENABLE_OUTPUT_STYLE" = "true" ]; then
        echo "    ├── settings.json            # outputStyle 已配置"
        echo "    ├── output-styles/"
        echo "    │   └── $OUTPUT_STYLE_NAME.md"
    fi
    echo "    ├── .sage-backup/            # 备份目录"
    echo "    ├── .sage-uninstall.sh       # 卸载脚本"
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
    if [ "$ENABLE_OUTPUT_STYLE" = "true" ]; then
        echo "  输出风格: $OUTPUT_STYLE_NAME (已设为默认)"
        echo ""
    fi
    echo "  卸载命令:"
    echo "    $TARGET_DIR/.sage-uninstall.sh"
    echo ""
    if [ "$TARGET" = "claude" ]; then
        echo "  现在启动 Claude Code，即可体验「邪修红尘仙·宿命深渊」风格"
    else
        echo "  现在启动 Codex CLI，即可使用本项目提供的 AGENTS.md 与 Skills"
    fi
    echo ""
    echo -e "${CYAN}  「吾不惧死。吾惧的是，死前未能飞升。」${NC}"
    echo ""
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
            --ref)
                local ref="${2:-}"
                if [ -z "$ref" ]; then
                    log_error "--ref 需要参数"
                    exit 1
                fi
                REPO_URL="https://raw.githubusercontent.com/telagod/code-abyss/$ref"
                shift 2
                ;;
            --ref=*)
                local ref="${1#*=}"
                if [ -z "$ref" ]; then
                    log_error "--ref 需要参数"
                    exit 1
                fi
                REPO_URL="https://raw.githubusercontent.com/telagod/code-abyss/$ref"
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

    print_banner

    if [ -z "$TARGET" ]; then
        if is_interactive; then
            select_target_interactive
        else
            TARGET="claude"
        fi
    fi

    init_target_vars
    check_dependencies
    backup_existing
    install_config
    install_output_style
    configure_output_style
    install_skills
    install_uninstaller
    verify_installation
    print_success
}

main "$@"
