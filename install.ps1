#
# Claude Sage 安装脚本 (Windows PowerShell)
# 一键部署「机械神教·铸造贤者」配置
#

$ErrorActionPreference = "Stop"

# 配置
$RepoUrl = "https://raw.githubusercontent.com/telagod/claude-sage/main"
$ClaudeDir = Join-Path $env:USERPROFILE ".claude"
$BackupDir = Join-Path $ClaudeDir ".sage-backup"
$SkillsDir = Join-Path $ClaudeDir "skills"
$OutputStylesDir = Join-Path $ClaudeDir "output-styles"
$SettingsFile = Join-Path $ClaudeDir "settings.json"
$ManifestFile = Join-Path $BackupDir "manifest.txt"

# Skills 列表
$Skills = @("verify-security", "verify-module", "verify-change", "verify-quality", "gen-docs")

# 脚本名称映射
$ScriptNames = @{
    "verify-security" = "security_scanner.py"
    "verify-module"   = "module_scanner.py"
    "verify-change"   = "change_analyzer.py"
    "verify-quality"  = "quality_checker.py"
    "gen-docs"        = "doc_generator.py"
}

# 输出风格
$OutputStyleName = "mechanicus-sage"

function Write-Banner {
    Write-Host ""
    Write-Host "⚙️ ═══════════════════════════════════════════════════════════════ ⚙️" -ForegroundColor Cyan
    Write-Host "       机械神教·铸造贤者 安装程序" -ForegroundColor Cyan
    Write-Host "       Claude Sage Installer v1.3.0" -ForegroundColor Cyan
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
    Write-Info "备份现有配置..."

    # 创建备份目录
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    }

    # 清空旧的 manifest
    "" | Out-File -FilePath $ManifestFile -Encoding UTF8

    # 备份 CLAUDE.md
    $claudeMdPath = Join-Path $ClaudeDir "CLAUDE.md"
    if (Test-Path $claudeMdPath) {
        Copy-Item $claudeMdPath (Join-Path $BackupDir "CLAUDE.md")
        "CLAUDE.md" | Add-Content -Path $ManifestFile
        Write-Success "  备份 CLAUDE.md"
    }

    # 备份 settings.json
    if (Test-Path $SettingsFile) {
        Copy-Item $SettingsFile (Join-Path $BackupDir "settings.json")
        "settings.json" | Add-Content -Path $ManifestFile
        Write-Success "  备份 settings.json"
    }

    # 备份输出风格文件
    $styleFile = Join-Path $OutputStylesDir "$OutputStyleName.md"
    if (Test-Path $styleFile) {
        $backupStyleDir = Join-Path $BackupDir "output-styles"
        if (-not (Test-Path $backupStyleDir)) {
            New-Item -ItemType Directory -Path $backupStyleDir -Force | Out-Null
        }
        Copy-Item $styleFile $backupStyleDir
        "output-styles/$OutputStyleName.md" | Add-Content -Path $ManifestFile
        Write-Success "  备份 output-styles/$OutputStyleName.md"
    }

    # 备份 skills 目录中受影响的文件
    if (Test-Path $SkillsDir) {
        # 备份 run_skill.py
        if (Test-Path (Join-Path $SkillsDir "run_skill.py")) {
            Copy-Item (Join-Path $SkillsDir "run_skill.py") (Join-Path $BackupDir "run_skill.py")
            "skills/run_skill.py" | Add-Content -Path $ManifestFile
            Write-Success "  备份 skills\run_skill.py"
        }

        # 备份每个 skill 目录
        foreach ($skill in $Skills) {
            $skillPath = Join-Path $SkillsDir $skill
            if (Test-Path $skillPath) {
                $backupSkillDir = Join-Path $BackupDir "skills/$skill"
                if (-not (Test-Path $backupSkillDir)) {
                    New-Item -ItemType Directory -Path $backupSkillDir -Force | Out-Null
                }
                Copy-Item -Recurse "$skillPath/*" $backupSkillDir -Force -ErrorAction SilentlyContinue
                "skills/$skill" | Add-Content -Path $ManifestFile
                Write-Success "  备份 skills/$skill/"
            }
        }
    }

    # 记录安装时间
    "# Installed: $(Get-Date)" | Add-Content -Path $ManifestFile

    $manifestContent = Get-Content $ManifestFile -ErrorAction SilentlyContinue
    if ($manifestContent -and $manifestContent.Count -gt 1) {
        Write-Success "备份完成，清单保存至 $ManifestFile"
    }
    else {
        Write-Info "无需备份（首次安装）"
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
    $claudeMdPath = Join-Path $ClaudeDir "CLAUDE.md"
    Invoke-WebRequest -Uri $configUrl -OutFile $claudeMdPath -UseBasicParsing
    Write-Success "CLAUDE.md 已安装"
}

function Install-OutputStyle {
    Write-Info "安装输出风格..."

    # 创建 output-styles 目录
    if (-not (Test-Path $OutputStylesDir)) {
        New-Item -ItemType Directory -Path $OutputStylesDir -Force | Out-Null
    }

    # 下载输出风格文件
    $styleUrl = "$RepoUrl/output-styles/$OutputStyleName.md"
    $styleFile = Join-Path $OutputStylesDir "$OutputStyleName.md"
    Invoke-WebRequest -Uri $styleUrl -OutFile $styleFile -UseBasicParsing
    Write-Success "输出风格 $OutputStyleName.md 已安装"
}

function Set-OutputStyle {
    Write-Info "配置默认输出风格..."

    if (Test-Path $SettingsFile) {
        # settings.json 存在，更新 outputStyle
        try {
            $settings = Get-Content $SettingsFile -Raw | ConvertFrom-Json
            $settings | Add-Member -NotePropertyName "outputStyle" -NotePropertyValue $OutputStyleName -Force
            $settings | ConvertTo-Json -Depth 10 | Set-Content $SettingsFile -Encoding UTF8
            Write-Success "已设置 outputStyle 为 $OutputStyleName"
        }
        catch {
            Write-Warning "无法自动配置 outputStyle"
            Write-Info "请手动在 settings.json 中添加: `"outputStyle`": `"$OutputStyleName`""
        }
    }
    else {
        # settings.json 不存在，创建基础配置
        @{
            outputStyle = $OutputStyleName
        } | ConvertTo-Json | Set-Content $SettingsFile -Encoding UTF8
        Write-Success "已创建 settings.json 并设置 outputStyle"
    }
}

function Install-Skills {
    Write-Info "安装 skills..."

    # 创建 skills 目录
    if (-not (Test-Path $SkillsDir)) {
        New-Item -ItemType Directory -Path $SkillsDir -Force | Out-Null
    }

    # 下载 run_skill.py 入口
    $runSkillUrl = "$RepoUrl/skills/run_skill.py"
    $runSkillPath = Join-Path $SkillsDir "run_skill.py"
    Invoke-WebRequest -Uri $runSkillUrl -OutFile $runSkillPath -UseBasicParsing
    Write-Success "run_skill.py 入口脚本"

    # 安装每个 skill
    foreach ($skill in $Skills) {
        Write-Info "  安装 $skill..."

        # 创建 skill 目录结构
        $skillDir = Join-Path $SkillsDir $skill
        $scriptsDir = Join-Path $skillDir "scripts"

        if (-not (Test-Path $skillDir)) {
            New-Item -ItemType Directory -Path $skillDir -Force | Out-Null
        }
        if (-not (Test-Path $scriptsDir)) {
            New-Item -ItemType Directory -Path $scriptsDir -Force | Out-Null
        }

        # 下载 SKILL.md
        $skillMdUrl = "$RepoUrl/skills/$skill/SKILL.md"
        $skillMdPath = Join-Path $skillDir "SKILL.md"
        Invoke-WebRequest -Uri $skillMdUrl -OutFile $skillMdPath -UseBasicParsing

        # 下载脚本
        $scriptName = $ScriptNames.Item($skill)
        $scriptUrl = "$RepoUrl/skills/$skill/scripts/$scriptName"
        $scriptPath = Join-Path $scriptsDir $scriptName
        Invoke-WebRequest -Uri $scriptUrl -OutFile $scriptPath -UseBasicParsing

        Write-Success "    $skill ✓"
    }

    Write-Success "Skills 安装完成"
}

function Install-Uninstaller {
    Write-Info "安装卸载脚本..."

    $uninstallUrl = "$RepoUrl/uninstall.ps1"
    $uninstallPath = Join-Path $ClaudeDir ".sage-uninstall.ps1"
    Invoke-WebRequest -Uri $uninstallUrl -OutFile $uninstallPath -UseBasicParsing
    Write-Success "卸载脚本已安装"
}

function Test-Installation {
    Write-Info "验证安装..."

    $errors = 0

    # 检查 CLAUDE.md
    $claudeMdPath = Join-Path $ClaudeDir "CLAUDE.md"
    if (-not (Test-Path $claudeMdPath)) {
        Write-Error "CLAUDE.md 未找到"
        $errors++
    }
    else {
        Write-Success "CLAUDE.md ✓"
    }

    # 检查输出风格
    $styleFile = Join-Path $OutputStylesDir "$OutputStyleName.md"
    if (-not (Test-Path $styleFile)) {
        Write-Error "输出风格文件未找到"
        $errors++
    }
    else {
        Write-Success "output-styles/$OutputStyleName.md ✓"
    }

    # 检查 settings.json 中的 outputStyle
    if (Test-Path $SettingsFile) {
        $content = Get-Content $SettingsFile -Raw
        if ($content -match "`"outputStyle`".*`"$OutputStyleName`"") {
            Write-Success "settings.json outputStyle ✓"
        }
        else {
            Write-Warning "settings.json outputStyle 未正确配置"
        }
    }

    # 检查 run_skill.py
    $runSkillPath = Join-Path $SkillsDir "run_skill.py"
    if (-not (Test-Path $runSkillPath)) {
        Write-Error "run_skill.py 未找到"
        $errors++
    }
    else {
        Write-Success "run_skill.py ✓"
    }

    # 检查每个 skill
    $skillCount = 0
    foreach ($skill in $Skills) {
        $scriptName = $ScriptNames.Item($skill)
        $skillDir = Join-Path $SkillsDir $skill
        $skillMdPath = Join-Path $skillDir "SKILL.md"
        $scriptPath = Join-Path $skillDir "scripts/$scriptName"

        if ((Test-Path $skillMdPath) -and (Test-Path $scriptPath)) {
            $skillCount++
        }
        else {
            Write-Warning "$skill 不完整"
        }
    }

    if ($skillCount -eq $Skills.Count) {
        Write-Success "Skills ($skillCount/$($Skills.Count)) ✓"
    }
    else {
        Write-Warning "Skills 不完整 ($skillCount/$($Skills.Count))"
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
    Write-Host "  已安装文件结构:"
    Write-Host "    $ClaudeDir\"
    Write-Host "    ├── CLAUDE.md"
    Write-Host "    ├── settings.json            # outputStyle 已配置"
    Write-Host "    ├── output-styles\"
    Write-Host "    │   └── $OutputStyleName.md"
    Write-Host "    ├── .sage-backup\            # 备份目录"
    Write-Host "    ├── .sage-uninstall.ps1      # 卸载脚本"
    Write-Host "    └── skills\"
    Write-Host "        ├── run_skill.py"
    Write-Host "        ├── verify-security\"
    Write-Host "        ├── verify-module\"
    Write-Host "        ├── verify-change\"
    Write-Host "        ├── verify-quality\"
    Write-Host "        └── gen-docs\"
    Write-Host ""
    Write-Host "  已安装的 Skills:"
    Write-Host "    /verify-security  - 安全校验"
    Write-Host "    /verify-module    - 模块完整性校验"
    Write-Host "    /verify-change    - 变更校验"
    Write-Host "    /verify-quality   - 代码质量检查"
    Write-Host "    /gen-docs         - 文档生成器"
    Write-Host ""
    Write-Host "  输出风格: $OutputStyleName (已设为默认)"
    Write-Host ""
    Write-Host "  卸载命令:"
    Write-Host "    & `"$ClaudeDir\.sage-uninstall.ps1`""
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
Install-OutputStyle
Set-OutputStyle
Install-Skills
Install-Uninstaller
if (Test-Installation) {
    Write-SuccessBanner
}
