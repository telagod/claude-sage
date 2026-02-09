#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const targetDir = path.dirname(__filename);
const backupDir = path.join(targetDir, '.sage-backup');
const manifestPath = path.join(backupDir, 'manifest.json');

if (!fs.existsSync(manifestPath)) {
  console.error('❌ 未找到安装记录 (manifest.json)');
  process.exit(1);
}

let manifest;
try {
  manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
} catch (e) {
  console.error('❌ manifest.json 解析失败:', e.message);
  process.exit(1);
}

console.log(`\n🗑️  卸载 Code Abyss v${manifest.version}...\n`);

// 1. 删除安装的文件
(manifest.installed || []).forEach(f => {
  const p = path.join(targetDir, f);
  if (fs.existsSync(p)) {
    fs.rmSync(p, { recursive: true, force: true });
    console.log(`🗑️  删除: ${f}`);
  }
});

// 2. 恢复备份
(manifest.backups || []).forEach(f => {
  const bp = path.join(backupDir, f);
  const tp = path.join(targetDir, f);
  if (fs.existsSync(bp)) {
    fs.renameSync(bp, tp);
    console.log(`✅ 恢复: ${f}`);
  }
});

// 3. 清理备份目录和卸载脚本自身
fs.rmSync(backupDir, { recursive: true, force: true });
fs.unlinkSync(__filename);

console.log('\n✅ 卸载完成\n');
