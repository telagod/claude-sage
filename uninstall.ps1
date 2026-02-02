#
# Claude Sage 卸载脚本 (Windows PowerShell)
# 卸载配置并恢复备份
#

param(
    [ValidateSet("claude", "codex")]
    [string]$Target
)

$ErrorActionPreference = "Stop"

# 版本
$Version = "1.5.0"

# 配置
$BaseDir = $null
$BackupDir = $null
$SkillsDir = $null
$OutputStylesDir = $null
$SettingsFile = $null
$ManifestFile = $null
$ConfigFilename = $null
$EnableOutputStyle = $false

# Skills 列表
$Skills = @("verify-security", "verify-module", "verify-change", "verify-quality", "gen-docs")

# 输出风格
$OutputStyleName = "mechanicus-sage"

function Select-Target {
    if ($script:Target) { return }

    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $claudeDir = Join-Path $env:USERPROFILE ".claude"
    $codexDir = Join-Path $env:USERPROFILE ".codex"

    if ($scriptDir -eq $claudeDir) {
        $script:Target = "claude"
        return
    }
    if ($scriptDir -eq $codexDir) {
        $script:Target = "codex"
        return
    }

    Write-Host ""
    Write-Host "请选择卸载目标:" -ForegroundColor Yellow
    Write-Host "  1) Claude Code (卸载 %USERPROFILE%\\.claude\\)"
    Write-Host "  2) Codex CLI   (卸载 %USERPROFILE%\\.codex\\)"
    Write-Host ""
    $choice = Read-Host "输入序号 [1/2] (默认 1)"

    if (-not $choice -or $choice -eq "1") {
        $script:Target = "claude"
    }
    elseif ($choice -eq "2") {
        $script:Target = "codex"
    }
    else {
        $script:Target = "claude"
    }
}

function Init-TargetVars {
    switch ($script:Target) {
        "claude" {
            $script:BaseDir = Join-Path $env:USERPROFILE ".claude"
            $script:ConfigFilename = "CLAUDE.md"
            $script:EnableOutputStyle = $true
        }
        "codex" {
            $script:BaseDir = Join-Path $env:USERPROFILE ".codex"
            $script:ConfigFilename = "AGENTS.md"
            $script:EnableOutputStyle = $false
        }
    }

    $script:BackupDir = Join-Path $script:BaseDir ".sage-backup"
    $script:SkillsDir = Join-Path $script:BaseDir "skills"
    $script:OutputStylesDir = Join-Path $script:BaseDir "output-styles"
    $script:SettingsFile = Join-Path $script:BaseDir "settings.json"
    $script:ManifestFile = Join-Path $script:BackupDir "manifest.txt"
}

function Write-Banner {
    Write-Host ""
    Write-Host "⚙️ ═══════════════════════════════════════════════════════════════ ⚙️" -ForegroundColor Cyan
    Write-Host "       机械神教·铸造贤者 卸载程序" -ForegroundColor Cyan
    Write-Host "       Claude Sage Uninstaller v$Version" -ForegroundColor Cyan
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
    Write-Host "即将卸载 Claude Sage（Target=$Target）并恢复备份。" -ForegroundColor Yellow
    Write-Host ""
    $confirm = Read-Host "确认卸载？[y/N]"

    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "已取消卸载。"
        exit 0
    }
}

function Remove-InstalledFiles {
    Write-Info "移除已安装的文件..."

    # 移除配置文件（CLAUDE.md / AGENTS.md）
    $configPath = Join-Path $BaseDir $ConfigFilename
    if (Test-Path $configPath) {
        Remove-Item -Force $configPath
        Write-Success "  移除 $ConfigFilename"
    }

    # 移除输出风格文件
    if ($EnableOutputStyle) {
        $styleFile = Join-Path $OutputStylesDir "$OutputStyleName.md"
        if (Test-Path $styleFile) {
            Remove-Item -Force $styleFile
            Write-Success "  移除 output-styles/$OutputStyleName.md"
        }
    }

    # 如果 output-styles 目录为空，删除它
    if ($EnableOutputStyle) {
        if ((Test-Path $OutputStylesDir) -and ((Get-ChildItem $OutputStylesDir -ErrorAction SilentlyContinue | Measure-Object).Count -eq 0)) {
            Remove-Item -Force $OutputStylesDir
            Write-Success "  移除空的 output-styles\ 目录"
        }
    }

    # 移除 run_skill.py
    $runSkillPath = Join-Path $SkillsDir "run_skill.py"
    if (Test-Path $runSkillPath) {
        Remove-Item -Force $runSkillPath
        Write-Success "  移除 skills/run_skill.py"
    }

    # 移除每个 skill 目录
    foreach ($skill in $Skills) {
        $skillPath = Join-Path $SkillsDir $skill
        if (Test-Path $skillPath) {
            Remove-Item -Recurse -Force $skillPath
            Write-Success "  移除 skills/$skill/"
        }
    }

    # 如果 skills 目录为空，删除它
    if ((Test-Path $SkillsDir) -and ((Get-ChildItem $SkillsDir -ErrorAction SilentlyContinue | Measure-Object).Count -eq 0)) {
        Remove-Item -Force $SkillsDir
        Write-Success "  移除空的 skills/ 目录"
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

    # 恢复配置文件
    $backupConfig = Join-Path $BackupDir $ConfigFilename
    if (Test-Path $backupConfig) {
        $configPath = Join-Path $BaseDir $ConfigFilename
        Copy-Item $backupConfig $configPath
        Write-Success "  恢复 $ConfigFilename"
        $restored++
    }

    # 恢复 settings.json
    if ($EnableOutputStyle) {
        $backupSettings = Join-Path $BackupDir "settings.json"
        if (Test-Path $backupSettings) {
            Copy-Item $backupSettings $SettingsFile
            Write-Success "  恢复 settings.json"
            $restored++
        }
    }

    # 恢复输出风格文件
    if ($EnableOutputStyle) {
        $backupStyleFile = Join-Path $BackupDir "output-styles/$OutputStyleName.md"
        if (Test-Path $backupStyleFile) {
            if (-not (Test-Path $OutputStylesDir)) {
                New-Item -ItemType Directory -Path $OutputStylesDir -Force | Out-Null
            }
            Copy-Item $backupStyleFile $OutputStylesDir
            Write-Success "  恢复 output-styles/$OutputStyleName.md"
            $restored++
        }
    }

    # 恢复 run_skill.py
    $backupRunSkill = Join-Path $BackupDir "run_skill.py"
    if (Test-Path $backupRunSkill) {
        if (-not (Test-Path $SkillsDir)) {
            New-Item -ItemType Directory -Path $SkillsDir -Force | Out-Null
        }
        $runSkillPath = Join-Path $SkillsDir "run_skill.py"
        Copy-Item $backupRunSkill $runSkillPath
        Write-Success "  恢复 skills/run_skill.py"
        $restored++
    }

    # 恢复每个 skill 目录
    foreach ($skill in $Skills) {
        $backupSkillDir = Join-Path $BackupDir "skills/$skill"
        if (Test-Path $backupSkillDir) {
            $skillDir = Join-Path $SkillsDir $skill
            if (-not (Test-Path $skillDir)) {
                New-Item -ItemType Directory -Path $skillDir -Force | Out-Null
            }
            Copy-Item -Recurse "$backupSkillDir/*" $skillDir -Force
            Write-Success "  恢复 skills/$skill/"
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
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    if (($scriptDir -eq $BaseDir) -and ((Split-Path -Leaf $MyInvocation.MyCommand.Path) -eq ".sage-uninstall.ps1")) {
        $selfPath = Join-Path $BaseDir ".sage-uninstall.ps1"
        if (Test-Path $selfPath) {
            Remove-Item -Force $selfPath
            Write-Success "  卸载脚本已移除"
        }
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
Select-Target
Init-TargetVars
Confirm-Uninstall
Remove-InstalledFiles
Restore-Backup
Clear-Backup
Write-SuccessBanner
