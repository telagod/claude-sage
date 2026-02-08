#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');

const VERSION = '1.5.1';

// 需要跳过的文件/目录
const SKIP_PATTERNS = [
  '__pycache__', '.pyc', '.pyo', '.egg-info',
  '.DS_Store', 'Thumbs.db', '.git'
];

function shouldSkip(name) {
  return SKIP_PATTERNS.some(p => name.includes(p));
}

function copyRecursive(src, dest) {
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    if (shouldSkip(path.basename(src))) return;
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }
    fs.readdirSync(src).forEach(file => {
      if (!shouldSkip(file)) {
        copyRecursive(path.join(src, file), path.join(dest, file));
      }
    });
  } else {
    if (shouldSkip(path.basename(src))) return;
    fs.copyFileSync(src, dest);
  }
}

function rmRecursive(p) {
  if (!fs.existsSync(p)) return;
  fs.rmSync(p, { recursive: true, force: true });
}

// 解析命令行参数
const args = process.argv.slice(2);
let target = null;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--target' && args[i + 1]) {
    target = args[i + 1];
    i++;
  } else if (args[i] === '--help' || args[i] === '-h') {
    console.log(`
☠️ Code Abyss v${VERSION} - 邪修红尘仙·宿命深渊

用法:
  npx code-abyss [选项]

选项:
  --target <claude|codex>  安装目标 (claude 或 codex)
  --help, -h               显示帮助信息

示例:
  npx code-abyss --target claude
  npx code-abyss --target codex
`);
    process.exit(0);
  }
}

// 交互选择目标
if (!target) {
  console.log('☠️ Code Abyss 安装器\n');
  console.log('请选择安装目标:');
  console.log('  1) Claude Code (~/.claude/)');
  console.log('  2) Codex CLI (~/.codex/)');

  const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
  });

  readline.question('\n选择 [1/2]: ', (answer) => {
    readline.close();
    target = answer === '2' ? 'codex' : 'claude';
    runInstall(target);
  });
} else {
  runInstall(target);
}

function runInstall(target) {
  if (!['claude', 'codex'].includes(target)) {
    console.error('❌ 错误: --target 必须是 claude 或 codex');
    process.exit(1);
  }

  const homeDir = os.homedir();
  const targetDir = path.join(homeDir, `.${target}`);
  const backupDir = path.join(targetDir, '.sage-backup');
  const manifestPath = path.join(backupDir, 'manifest.json');

  console.log(`\n☠️ 开始安装到 ${targetDir}\n`);

  // 创建目录
  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }
  if (!fs.existsSync(backupDir)) {
    fs.mkdirSync(backupDir, { recursive: true });
  }

  // 包根目录
  const pkgRoot = path.join(__dirname, '..');

  // 安装清单
  const filesToInstall = [
    { src: 'config/CLAUDE.md', dest: target === 'claude' ? 'CLAUDE.md' : null },
    { src: 'config/AGENTS.md', dest: target === 'codex' ? 'AGENTS.md' : null },
    { src: 'output-styles', dest: target === 'claude' ? 'output-styles' : null },
    { src: 'skills', dest: 'skills' }
  ].filter(f => f.dest !== null);

  // 记录安装的文件（用于卸载）
  const manifest = {
    version: VERSION,
    target: target,
    timestamp: new Date().toISOString(),
    installed: [],
    backups: []
  };

  filesToInstall.forEach(({ src, dest }) => {
    const srcPath = path.join(pkgRoot, src);
    const destPath = path.join(targetDir, dest);

    if (!fs.existsSync(srcPath)) {
      console.warn(`⚠️  跳过: ${src} (源文件不存在)`);
      return;
    }

    // 备份现有文件
    if (fs.existsSync(destPath)) {
      const backupPath = path.join(backupDir, dest);
      console.log(`📦 备份: ${dest}`);
      rmRecursive(backupPath);
      copyRecursive(destPath, backupPath);
      manifest.backups.push(dest);
    }

    // 复制新文件
    console.log(`📝 安装: ${dest}`);
    rmRecursive(destPath);
    copyRecursive(srcPath, destPath);
    manifest.installed.push(dest);
  });

  // 更新 settings.json
  const settingsPath = path.join(targetDir, 'settings.json');
  let settings = {};

  if (fs.existsSync(settingsPath)) {
    try {
      settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
    } catch (e) {
      console.warn(`⚠️  settings.json 解析失败，将创建新文件`);
      settings = {};
    }
    // 备份
    const backupPath = path.join(backupDir, 'settings.json');
    fs.copyFileSync(settingsPath, backupPath);
    manifest.backups.push('settings.json');
  }

  if (target === 'claude') {
    settings.outputStyle = 'abyss-cultivator';
    console.log(`⚙️  配置: outputStyle = abyss-cultivator`);
  }

  fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + '\n');
  manifest.installed.push('settings.json');

  // 写入 manifest
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + '\n');

  // 创建卸载脚本
  const uninstallPath = path.join(targetDir, '.sage-uninstall.js');
  const uninstallSrc = path.join(pkgRoot, 'bin', 'uninstall.js');
  fs.copyFileSync(uninstallSrc, uninstallPath);
  fs.chmodSync(uninstallPath, '755');

  console.log(`\n⚚ 劫——破——了——！！！\n`);
  console.log(`✅ 安装完成: ${targetDir}`);
  console.log(`\n卸载命令: node ${uninstallPath}\n`);
}
