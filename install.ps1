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
    if (Test-Path "$ClaudeDir\CLAUDE.md") {
        Write-Info "备份现有配置..."

        if (-not (Test-Path $BackupDir)) {
            New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
        }

        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        Copy-Item "$ClaudeDir\CLAUDE.md" "$BackupDir\CLAUDE.md.$timestamp"
        Write-Success "已备份到 $BackupDir\CLAUDE.md.$timestamp"
    }

    if (Test-Path $SkillsDir) {
        Write-Info "备份现有 skills..."
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        Copy-Item -Recurse $SkillsDir "$BackupDir\skills.$timestamp"
        Write-Success "已备份到 $BackupDir\skills.$timestamp"
    }
}

function Install-Config {
    Write-Info "安装配置文件..."

    if (-not (Test-Path $ClaudeDir)) {
        New-Item -ItemType Directory -Path $ClaudeDir -Force | Out-Null
    }

    $configUrl = "$RepoUrl/config/CLAUDE.md"
    Invoke-WebRequest -Uri $configUrl -OutFile "$ClaudeDir\CLAUDE.md" -UseBasicParsing
    Write-Success "CLAUDE.md 已安装"
}

function Install-Skills {
    Write-Info "安装 skills..."

    if (-not (Test-Path $SkillsDir)) {
        New-Item -ItemType Directory -Path $SkillsDir -Force | Out-Null
    }

    $skills = @(
        "run_skill.py",
        "verify_security.py",
        "verify_module.py",
        "verify_change.py",
        "verify_quality.py",
        "gen_docs.py"
    )

    foreach ($skill in $skills) {
        $skillUrl = "$RepoUrl/skills/$skill"
        Invoke-WebRequest -Uri $skillUrl -OutFile "$SkillsDir\$skill" -UseBasicParsing
        Write-Success "  $skill"
    }

    Write-Success "Skills 安装完成"
}

function Test-Installation {
    Write-Info "验证安装..."

    $errors = 0

    if (-not (Test-Path "$ClaudeDir\CLAUDE.md")) {
        Write-Error "CLAUDE.md 未找到"
        $errors++
    }

    if (-not (Test-Path "$SkillsDir\run_skill.py")) {
        Write-Error "run_skill.py 未找到"
        $errors++
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
    Write-Host "  配置文件: $ClaudeDir\CLAUDE.md"
    Write-Host "  Skills:   $SkillsDir\"
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
