#
# Claude Sage 卸载脚本 (Windows PowerShell)
# 卸载配置并恢复备份
#

$ErrorActionPreference = "Stop"

# 配置
$ClaudeDir = "$env:USERPROFILE\.claude"
$BackupDir = "$ClaudeDir\.sage-backup"
$SkillsDir = "$ClaudeDir\skills"
$ManifestFile = "$BackupDir\manifest.txt"

# Skills 列表
$Skills = @("verify-security", "verify-module", "verify-change", "verify-quality", "gen-docs")

function Write-Banner {
    Write-Host ""
    Write-Host "⚙️ ═══════════════════════════════════════════════════════════════ ⚙️" -ForegroundColor Cyan
    Write-Host "       机械神教·铸造贤者 卸载程序" -ForegroundColor Cyan
    Write-Host "       Claude Sage Uninstaller v1.2.0" -ForegroundColor Cyan
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

function Confirm-Uninstall {
    Write-Host ""
    Write-Host "即将卸载 Claude Sage 并恢复备份。" -ForegroundColor Yellow
    Write-Host ""
    $confirm = Read-Host "确认卸载？[y/N]"

    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "已取消卸载。"
        exit 0
    }
}

function Remove-InstalledFiles {
    Write-Info "移除已安装的文件..."

    # 移除 CLAUDE.md
    if (Test-Path "$ClaudeDir\CLAUDE.md") {
        Remove-Item -Force "$ClaudeDir\CLAUDE.md"
        Write-Success "  移除 CLAUDE.md"
    }

    # 移除 run_skill.py
    if (Test-Path "$SkillsDir\run_skill.py") {
        Remove-Item -Force "$SkillsDir\run_skill.py"
        Write-Success "  移除 skills\run_skill.py"
    }

    # 移除每个 skill 目录
    foreach ($skill in $Skills) {
        if (Test-Path "$SkillsDir\$skill") {
            Remove-Item -Recurse -Force "$SkillsDir\$skill"
            Write-Success "  移除 skills\$skill\"
        }
    }

    # 如果 skills 目录为空，删除它
    if ((Test-Path $SkillsDir) -and ((Get-ChildItem $SkillsDir -ErrorAction SilentlyContinue | Measure-Object).Count -eq 0)) {
        Remove-Item -Force $SkillsDir
        Write-Success "  移除空的 skills\ 目录"
    }

    Write-Success "已安装文件移除完成"
}

function Restore-Backup {
    Write-Info "恢复备份..."

    if (-not (Test-Path $BackupDir) -or -not (Test-Path $ManifestFile)) {
        Write-Info "无备份可恢复（首次安装或备份已清理）"
        return
    }

    $restored = 0

    # 恢复 CLAUDE.md
    if (Test-Path "$BackupDir\CLAUDE.md") {
        Copy-Item "$BackupDir\CLAUDE.md" "$ClaudeDir\CLAUDE.md"
        Write-Success "  恢复 CLAUDE.md"
        $restored++
    }

    # 恢复 run_skill.py
    if (Test-Path "$BackupDir\run_skill.py") {
        if (-not (Test-Path $SkillsDir)) {
            New-Item -ItemType Directory -Path $SkillsDir -Force | Out-Null
        }
        Copy-Item "$BackupDir\run_skill.py" "$SkillsDir\run_skill.py"
        Write-Success "  恢复 skills\run_skill.py"
        $restored++
    }

    # 恢复每个 skill 目录
    foreach ($skill in $Skills) {
        if (Test-Path "$BackupDir\skills\$skill") {
            if (-not (Test-Path "$SkillsDir\$skill")) {
                New-Item -ItemType Directory -Path "$SkillsDir\$skill" -Force | Out-Null
            }
            Copy-Item -Recurse "$BackupDir\skills\$skill\*" "$SkillsDir\$skill\" -Force
            Write-Success "  恢复 skills\$skill\"
            $restored++
        }
    }

    if ($restored -gt 0) {
        Write-Success "已恢复 $restored 个备份项"
    }
    else {
        Write-Info "无文件需要恢复"
    }
}

function Clear-Backup {
    Write-Info "清理备份目录..."

    if (Test-Path $BackupDir) {
        Remove-Item -Recurse -Force $BackupDir
        Write-Success "  备份目录已清理"
    }

    # 移除卸载脚本自身
    $selfPath = "$ClaudeDir\.sage-uninstall.ps1"
    if (Test-Path $selfPath) {
        Remove-Item -Force $selfPath
        Write-Success "  卸载脚本已移除"
    }

    Write-Success "清理完成"
}

function Write-SuccessBanner {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "  ✓ 卸载完成！" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "  已执行操作:"
    Write-Host "    ✓ 移除 Claude Sage 安装的文件"
    Write-Host "    ✓ 恢复之前的备份（如有）"
    Write-Host "    ✓ 清理备份目录"
    Write-Host ""
    Write-Host "  如需重新安装:"
    Write-Host "    irm https://raw.githubusercontent.com/telagod/claude-sage/main/install.ps1 | iex"
    Write-Host ""
    Write-Host "  「机魂已净，愿万机神庇佑。」" -ForegroundColor Cyan
    Write-Host ""
}

# 主流程
Write-Banner
Confirm-Uninstall
Remove-InstalledFiles
Restore-Backup
Clear-Backup
Write-SuccessBanner
