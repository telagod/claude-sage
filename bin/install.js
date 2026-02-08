#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const os = require('os');

const VERSION = '1.5.1';
const REPO_URL = 'https://github.com/telagod/code-abyss.git';

// 解析命令行参数
const args = process.argv.slice(2);
let target = null;
let ref = `v${VERSION}`;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--target' && args[i + 1]) {
    target = args[i + 1];
    i++;
  } else if (args[i] === '--ref' && args[i + 1]) {
    ref = args[i + 1];
    i++;
  } else if (args[i] === '--help' || args[i] === '-h') {
    console.log(`
☠️ Code Abyss - 邪修红尘仙·宿命深渊

用法:
  npx code-abyss [选项]

选项:
  --target <claude|codex>  安装目标 (claude 或 codex)
  --ref <version>          Git ref (默认: v${VERSION})
  --help, -h               显示帮助信息

示例:
  npx code-abyss --target claude
  npx code-abyss --target codex --ref main
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
    runInstall(target, ref);
  });
} else {
  runInstall(target, ref);
}

function runInstall(target, ref) {
  if (!['claude', 'codex'].includes(target)) {
    console.error('❌ 错误: --target 必须是 claude 或 codex');
    process.exit(1);
  }

  const homeDir = os.homedir();
  const targetDir = path.join(homeDir, `.${target}`);
  const backupDir = path.join(targetDir, '.sage-backup');
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

  console.log(`\n☠️ 开始安装到 ${targetDir}\n`);

  // 创建目标目录
  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }

  // 创建备份目录
  if (!fs.existsSync(backupDir)) {
    fs.mkdirSync(backupDir, { recursive: true });
  }

  // 获取包根目录
  const pkgRoot = path.join(__dirname, '..');

  // 备份并复制文件
  const filesToInstall = [
    { src: 'config/CLAUDE.md', dest: target === 'claude' ? 'CLAUDE.md' : null },
    { src: 'config/AGENTS.md', dest: target === 'codex' ? 'AGENTS.md' : null },
    { src: 'output-styles', dest: target === 'claude' ? 'output-styles' : null },
    { src: 'skills', dest: 'skills' }
  ];

  filesToInstall.forEach(({ src, dest }) => {
    if (!dest) return;

    const srcPath = path.join(pkgRoot, src);
    const destPath = path.join(targetDir, dest);

    // 备份现有文件
    if (fs.existsSync(destPath)) {
      const backupPath = path.join(backupDir, `${dest}.${timestamp}`);
      console.log(`📦 备份: ${dest} -> .sage-backup/`);
      copyRecursive(destPath, backupPath);
    }

    // 复制新文件
    console.log(`📝 安装: ${dest}`);
    copyRecursive(srcPath, destPath);
  });

  // 更新 settings.json
  const settingsPath = path.join(targetDir, 'settings.json');
  let settings = {};

  if (fs.existsSync(settingsPath)) {
    const backupPath = path.join(backupDir, `settings.json.${timestamp}`);
    fs.copyFileSync(settingsPath, backupPath);
    console.log(`📦 备份: settings.json -> .sage-backup/`);
    settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
  }

  if (target === 'claude') {
    settings.outputStyle = 'abyss-cultivator';
    console.log(`⚙️  配置: outputStyle = abyss-cultivator`);
  }

  fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2));

  // 创建卸载脚本
  const uninstallScript = `#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const backupDir = '${backupDir}';
const targetDir = '${targetDir}';

console.log('🗑️  卸载 Code Abyss...');

// 恢复备份
const backups = fs.readdirSync(backupDir).filter(f => f.includes('${timestamp}'));
backups.forEach(backup => {
  const original = backup.replace('.${timestamp}', '');
  const backupPath = path.join(backupDir, backup);
  const targetPath = path.join(targetDir, original);

  if (fs.existsSync(targetPath)) {
    fs.rmSync(targetPath, { recursive: true, force: true });
  }

  fs.renameSync(backupPath, targetPath);
  console.log(\`✅ 恢复: \${original}\`);
});

console.log('✅ 卸载完成');
`;

  const uninstallPath = path.join(targetDir, '.sage-uninstall.js');
  fs.writeFileSync(uninstallPath, uninstallScript);
  fs.chmodSync(uninstallPath, '755');

  console.log(`\n⚚ 劫——破——了——！！！\n`);
  console.log(`✅ 安装完成: ${targetDir}`);
  console.log(`\n卸载命令: node ${uninstallPath}\n`);
}

function copyRecursive(src, dest) {
  const stat = fs.statSync(src);

  if (stat.isDirectory()) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }
    fs.readdirSync(src).forEach(file => {
      copyRecursive(path.join(src, file), path.join(dest, file));
    });
  } else {
    fs.copyFileSync(src, dest);
  }
}
