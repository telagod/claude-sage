#
# Claude Sage 安装脚本 (Windows PowerShell)
# 一键部署「机械神教·铸造贤者」配置
#

# 支持 irm | iex 管道执行，不使用 param() 块
$ErrorActionPreference = "Stop"

# 目标参数（通过环境变量或交互选择）
$script:Target = $null

# 版本
$Version = "1.5.0"

# 配置
$RepoUrl = "https://raw.githubusercontent.com/telagod/claude-sage/main"
$BaseDir = $null
$BackupDir = $null
$SkillsDir = $null
$OutputStylesDir = $null
$SettingsFile = $null
$ManifestFile = $null
$ConfigFilename = $null
$ConfigSourcePath = $null
$EnableOutputStyle = $false

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

function Get-UserProfileDir {
    $userHome = $env:USERPROFILE
    if ([string]::IsNullOrWhiteSpace($userHome)) {
        $userHome = [Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
    }
    if ([string]::IsNullOrWhiteSpace($userHome)) {
        $userHome = $HOME
    }
    if ([string]::IsNullOrWhiteSpace($userHome)) {
        throw "无法确定用户目录（USERPROFILE/UserProfile/HOME 均为空）"
    }
    return $userHome
}

function Test-PathSafe {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
    return Test-Path -LiteralPath $Path
}

function Ensure-Directory {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) {
        throw "路径为空，无法创建目录"
    }
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Assert-Initialized {
    $missing = @()
    if ([string]::IsNullOrWhiteSpace($Target)) { $missing += "Target" }
    if ([string]::IsNullOrWhiteSpace($BaseDir)) { $missing += "BaseDir" }
    if ([string]::IsNullOrWhiteSpace($BackupDir)) { $missing += "BackupDir" }
    if ([string]::IsNullOrWhiteSpace($SkillsDir)) { $missing += "SkillsDir" }
    if ([string]::IsNullOrWhiteSpace($ConfigFilename)) { $missing += "ConfigFilename" }
    if ([string]::IsNullOrWhiteSpace($ConfigSourcePath)) { $missing += "ConfigSourcePath" }
    if ($missing.Count -gt 0) {
        throw ("初始化失败：{0}" -f ($missing -join ", "))
    }
}

function Select-Target {
    if ($script:Target) {
        # 验证 Target 值
        if ($script:Target -notin @("claude", "codex")) {
            Write-Error "无效的 Target: $($script:Target)（仅支持 claude 或 codex）"
            exit 1
        }
        return
    }

    Write-Host ""
    Write-Host "请选择安装目标:" -ForegroundColor Yellow
    Write-Host "  1) Claude Code (安装到 %USERPROFILE%\\.claude\\)"
    Write-Host "  2) Codex CLI   (安装到 %USERPROFILE%\\.codex\\)"
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
    $userHome = Get-UserProfileDir
    switch ($script:Target) {
        "claude" {
            $script:BaseDir = Join-Path $userHome ".claude"
            $script:ConfigFilename = "CLAUDE.md"
            $script:ConfigSourcePath = "config/CLAUDE.md"
            $script:EnableOutputStyle = $true
        }
        "codex" {
            $script:BaseDir = Join-Path $userHome ".codex"
            $script:ConfigFilename = "AGENTS.md"
            $script:ConfigSourcePath = "config/AGENTS.md"
            $script:EnableOutputStyle = $false
        }
    }

    $script:BackupDir = Join-Path $script:BaseDir ".sage-backup"
    $script:SkillsDir = Join-Path $script:BaseDir "skills"
    $script:OutputStylesDir = Join-Path $script:BaseDir "output-styles"
    $script:SettingsFile = Join-Path $script:BaseDir "settings.json"
    $script:ManifestFile = Join-Path $script:BackupDir "manifest.txt"
}

function Download-File {
    param(
        [string]$Url,
        [string]$Destination
    )
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($Url, $Destination)
}

function Write-Banner {
    Write-Host ""
    Write-Host "⚙️ ═══════════════════════════════════════════════════════════════ ⚙️" -ForegroundColor Cyan
    Write-Host "       机械神教·铸造贤者 安装程序" -ForegroundColor Cyan
    Write-Host "       Claude Sage Installer v$Version" -ForegroundColor Cyan
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
    Ensure-Directory $BackupDir

    # 清空旧的 manifest
    "" | Out-File -FilePath $ManifestFile -Encoding UTF8

    # 备份配置文件（CLAUDE.md / AGENTS.md）
    $configPath = Join-Path $BaseDir $ConfigFilename
    if (Test-PathSafe $configPath) {
        Copy-Item $configPath (Join-Path $BackupDir $ConfigFilename)
        $ConfigFilename | Add-Content -Path $ManifestFile
        Write-Success "  备份 $ConfigFilename"
    }

    # 备份 settings.json
    if ($EnableOutputStyle -and (Test-PathSafe $SettingsFile)) {
        Copy-Item $SettingsFile (Join-Path $BackupDir "settings.json")
        "settings.json" | Add-Content -Path $ManifestFile
        Write-Success "  备份 settings.json"
    }

    # 备份输出风格文件
    $styleFile = Join-Path $OutputStylesDir "$OutputStyleName.md"
    if ($EnableOutputStyle -and (Test-PathSafe $styleFile)) {
        $backupStyleDir = Join-Path $BackupDir "output-styles"
        Ensure-Directory $backupStyleDir
        Copy-Item $styleFile $backupStyleDir
        "output-styles/$OutputStyleName.md" | Add-Content -Path $ManifestFile
        Write-Success "  备份 output-styles/$OutputStyleName.md"
    }

    # 备份 skills 目录中受影响的文件
    if (Test-PathSafe $SkillsDir) {
        # 备份 run_skill.py
        if (Test-PathSafe (Join-Path $SkillsDir "run_skill.py")) {
            Copy-Item (Join-Path $SkillsDir "run_skill.py") (Join-Path $BackupDir "run_skill.py")
            "skills/run_skill.py" | Add-Content -Path $ManifestFile
            Write-Success "  备份 skills\run_skill.py"
        }

        # 备份每个 skill 目录
        foreach ($skill in $Skills) {
            $skillPath = Join-Path $SkillsDir $skill
            if (Test-PathSafe $skillPath) {
                $backupSkillDir = Join-Path $BackupDir "skills/$skill"
                Ensure-Directory $backupSkillDir
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

    # 创建目标目录
    Ensure-Directory $BaseDir

    # 下载配置文件
    $configUrl = "$RepoUrl/$ConfigSourcePath"
    $configDest = Join-Path $BaseDir $ConfigFilename
    Download-File -Url $configUrl -Destination $configDest
    Write-Success "$ConfigFilename 已安装"
}

function Install-OutputStyle {
    Write-Info "安装输出风格..."

    if (-not $EnableOutputStyle) {
        Write-Info "当前 Target=$Target，不安装 output-styles 与 settings.json"
        return
    }

    # 创建 output-styles 目录
    Ensure-Directory $OutputStylesDir

    # 下载输出风格文件
    $styleUrl = "$RepoUrl/output-styles/$OutputStyleName.md"
    $styleFile = Join-Path $OutputStylesDir "$OutputStyleName.md"
    Download-File -Url $styleUrl -Destination $styleFile
    Write-Success "输出风格 $OutputStyleName.md 已安装"
}

function Set-OutputStyle {
    Write-Info "配置默认输出风格..."

    if (-not $EnableOutputStyle) {
        Write-Info "当前 Target=$Target，不配置 outputStyle"
        return
    }

    if (Test-PathSafe $SettingsFile) {
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
    Ensure-Directory $SkillsDir

    # 下载 run_skill.py 入口
    $runSkillUrl = "$RepoUrl/skills/run_skill.py"
    $runSkillPath = Join-Path $SkillsDir "run_skill.py"
    Download-File -Url $runSkillUrl -Destination $runSkillPath
    Write-Success "run_skill.py 入口脚本"

    # 安装每个 skill
    foreach ($skill in $Skills) {
        Write-Info "  安装 $skill..."

        # 创建 skill 目录结构
        $skillDir = Join-Path $SkillsDir $skill
        $scriptsDir = Join-Path $skillDir "scripts"

        Ensure-Directory $skillDir
        Ensure-Directory $scriptsDir

        # 下载 SKILL.md
        $skillMdUrl = "$RepoUrl/skills/$skill/SKILL.md"
        $skillMdPath = Join-Path $skillDir "SKILL.md"
        Download-File -Url $skillMdUrl -Destination $skillMdPath

        # 下载脚本
        $scriptName = $ScriptNames.Item($skill)
        $scriptUrl = "$RepoUrl/skills/$skill/scripts/$scriptName"
        $scriptPath = Join-Path $scriptsDir $scriptName
        Download-File -Url $scriptUrl -Destination $scriptPath

        Write-Success "    $skill ✓"
    }

    Write-Success "Skills 安装完成"
}

function Install-Uninstaller {
    Write-Info "安装卸载脚本..."

    $uninstallUrl = "$RepoUrl/uninstall.ps1"
    $uninstallPath = Join-Path $BaseDir ".sage-uninstall.ps1"
    Download-File -Url $uninstallUrl -Destination $uninstallPath
    Write-Success "卸载脚本已安装"
}

function Test-Installation {
    Write-Info "验证安装..."

    $errors = 0

    # 检查配置文件
    $configPath = Join-Path $BaseDir $ConfigFilename
    if (-not (Test-PathSafe $configPath)) {
        Write-Error "$ConfigFilename 未找到"
        $errors++
    }
    else {
        Write-Success "$ConfigFilename ✓"
    }

    # 检查输出风格
    $styleFile = Join-Path $OutputStylesDir "$OutputStyleName.md"
    if ($EnableOutputStyle) {
        if (-not (Test-PathSafe $styleFile)) {
            Write-Error "输出风格文件未找到"
            $errors++
        }
        else {
            Write-Success "output-styles/$OutputStyleName.md ✓"
        }
    }

    # 检查 settings.json 中的 outputStyle
    if ($EnableOutputStyle -and (Test-PathSafe $SettingsFile)) {
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
    if (-not (Test-PathSafe $runSkillPath)) {
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

        if ((Test-PathSafe $skillMdPath) -and (Test-PathSafe $scriptPath)) {
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
    Write-Host "  安装目标: $Target"
    Write-Host "  已安装文件结构:"
    Write-Host "    $BaseDir\"
    Write-Host "    ├── $ConfigFilename"
    if ($EnableOutputStyle) {
        Write-Host "    ├── settings.json            # outputStyle 已配置"
        Write-Host "    ├── output-styles\"
        Write-Host "    │   └── $OutputStyleName.md"
    }
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
    if ($EnableOutputStyle) {
        Write-Host "  输出风格: $OutputStyleName (已设为默认)"
        Write-Host ""
    }
    Write-Host "  卸载命令:"
    Write-Host "    & `"$BaseDir\.sage-uninstall.ps1`""
    Write-Host ""
    if ($Target -eq "claude") {
        Write-Host "  现在启动 Claude Code，即可体验「机械神教·铸造贤者」风格"
    }
    else {
        Write-Host "  现在启动 Codex CLI，即可使用本项目提供的 AGENTS.md 与 Skills"
    }
    Write-Host ""
    Write-Host "  「圣工已毕，机魂安宁。赞美万机神，知识即力量！」" -ForegroundColor Cyan
    Write-Host ""
}

# 主流程
Write-Banner
Select-Target
Init-TargetVars
Assert-Initialized
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
