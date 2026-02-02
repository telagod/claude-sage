#
# Claude Sage 安装脚本 (Windows PowerShell)
# 一键部署「机械神教·铸造贤者」配置
#

$ErrorActionPreference = "Stop"

# 配置
$RepoUrl = "https://raw.githubusercontent.com/telagod/claude-sage/main"
$ClaudeDir = "$env:USERPROFILE\.claude"
$BackupDir = "$ClaudeDir\backup"
$SkillsDir = "$ClaudeDir\skills"

function Write-Banner {
    Write-Host ""
    Write-Host "⚙️ ═══════════════════════════════════════════════════════════════ ⚙️" -ForegroundColor Cyan
    Write-Host "       机械神教·铸造贤者 安装程序" -ForegroundColor Cyan
    Write-Host "       Claude Sage Installer v1.0.0" -ForegroundColor Cyan
    Write-Host "⚙️ ═══════════════════════════════════════════════════════════════ ⚙️" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[✓] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[✗] $Message" -ForegroundColor Red
}

function Test-Dependencies {
    Write-Info "检查依赖..."

    try {
        $null = Get-Command python -ErrorAction Stop
        Write-Success "Python 已安装"
    }
    catch {
        try {
            $null = Get-Command python3 -ErrorAction Stop
            Write-Success "Python3 已安装"
        }
        catch {
            Write-Warning "未检测到 Python，skills 功能可能受限"
        }
    }

    Write-Success "依赖检查通过"
}

function Backup-Existing {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

    if (Test-Path "$ClaudeDir\CLAUDE.md") {
        Write-Info "备份现有配置..."

        if (-not (Test-Path $BackupDir)) {
            New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
        }

        Copy-Item "$ClaudeDir\CLAUDE.md" "$BackupDir\CLAUDE.md.$timestamp"
        Write-Success "已备份到 $BackupDir\CLAUDE.md.$timestamp"
    }

    if ((Test-Path $SkillsDir) -and (Get-ChildItem $SkillsDir -ErrorAction SilentlyContinue)) {
        Write-Info "备份现有 skills..."

        if (-not (Test-Path $BackupDir)) {
            New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
        }

        Copy-Item -Recurse $SkillsDir "$BackupDir\skills.$timestamp"
        Write-Success "已备份到 $BackupDir\skills.$timestamp"
    }
}

function Install-Config {
    Write-Info "安装配置文件..."

    # 创建 .claude 目录
    if (-not (Test-Path $ClaudeDir)) {
        New-Item -ItemType Directory -Path $ClaudeDir -Force | Out-Null
    }

    # 下载 CLAUDE.md
    $configUrl = "$RepoUrl/config/CLAUDE.md"
    Invoke-WebRequest -Uri $configUrl -OutFile "$ClaudeDir\CLAUDE.md" -UseBasicParsing
    Write-Success "CLAUDE.md 已安装到 $ClaudeDir\"
}

function Install-Skills {
    Write-Info "安装 skills..."

    # 创建 skills 目录
    if (-not (Test-Path $SkillsDir)) {
        New-Item -ItemType Directory -Path $SkillsDir -Force | Out-Null
    }

    # Python 脚本文件
    $pyScripts = @(
        "run_skill.py",
        "verify_security.py",
        "verify_module.py",
        "verify_change.py",
        "verify_quality.py",
        "gen_docs.py"
    )

    # Skill 描述文件 (.md) - Claude Code 需要这些文件来识别 skills
    $skillMds = @(
        "verify-security.md",
        "verify-module.md",
        "verify-change.md",
        "verify-quality.md",
        "gen-docs.md"
    )

    Write-Info "  下载 Python 脚本..."
    foreach ($script in $pyScripts) {
        $scriptUrl = "$RepoUrl/skills/$script"
        Invoke-WebRequest -Uri $scriptUrl -OutFile "$SkillsDir\$script" -UseBasicParsing
        Write-Success "    $script"
    }

    Write-Info "  下载 Skill 描述文件..."
    foreach ($md in $skillMds) {
        $mdUrl = "$RepoUrl/skills/$md"
        Invoke-WebRequest -Uri $mdUrl -OutFile "$SkillsDir\$md" -UseBasicParsing
        Write-Success "    $md"
    }

    Write-Success "Skills 安装完成"
}

function Test-Installation {
    Write-Info "验证安装..."

    $errors = 0

    # 检查 CLAUDE.md
    if (-not (Test-Path "$ClaudeDir\CLAUDE.md")) {
        Write-Error "CLAUDE.md 未找到"
        $errors++
    }
    else {
        Write-Success "CLAUDE.md ✓"
    }

    # 检查 skills 目录
    if (-not (Test-Path $SkillsDir)) {
        Write-Error "skills 目录未找到"
        $errors++
    }
    else {
        Write-Success "skills 目录 ✓"
    }

    # 检查 Python 入口
    if (-not (Test-Path "$SkillsDir\run_skill.py")) {
        Write-Error "run_skill.py 未找到"
        $errors++
    }
    else {
        Write-Success "run_skill.py ✓"
    }

    # 检查 skill 描述文件
    $skillCount = 0
    $skillMds = @("verify-security.md", "verify-module.md", "verify-change.md", "verify-quality.md", "gen-docs.md")
    foreach ($md in $skillMds) {
        if (Test-Path "$SkillsDir\$md") {
            $skillCount++
        }
    }

    if ($skillCount -eq 5) {
        Write-Success "Skill 描述文件 ($skillCount/5) ✓"
    }
    else {
        Write-Warning "Skill 描述文件不完整 ($skillCount/5)"
    }

    if ($errors -eq 0) {
        Write-Success "安装验证通过"
        return $true
    }
    else {
        Write-Error "安装验证失败"
        return $false
    }
}

function Write-SuccessBanner {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "  ✓ 安装完成！" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "  已安装文件:"
    Write-Host "    配置文件: $ClaudeDir\CLAUDE.md"
    Write-Host "    Skills:   $SkillsDir\"
    Write-Host ""
    Write-Host "  已安装的 Skills:"
    Write-Host "    /verify-security  - 安全校验"
    Write-Host "    /verify-module    - 模块完整性校验"
    Write-Host "    /verify-change    - 变更校验"
    Write-Host "    /verify-quality   - 代码质量检查"
    Write-Host "    /gen-docs         - 文档生成器"
    Write-Host ""
    Write-Host "  现在启动 Claude Code，即可体验「机械神教·铸造贤者」风格"
    Write-Host ""
    Write-Host "  「圣工已毕，机魂安宁。赞美万机神，知识即力量！」" -ForegroundColor Cyan
    Write-Host ""
}

# 主流程
Write-Banner
Test-Dependencies
Backup-Existing
Install-Config
Install-Skills
if (Test-Installation) {
    Write-SuccessBanner
}
