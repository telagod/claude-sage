#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');

const VERSION = require(path.join(__dirname, '..', 'package.json')).version;
const HOME = os.homedir();
const SKIP = ['__pycache__', '.pyc', '.pyo', '.egg-info', '.DS_Store', 'Thumbs.db', '.git'];
const PKG_ROOT = path.join(__dirname, '..');

// ── ANSI ──

const c = {
  b: s => `\x1b[1m${s}\x1b[0m`,
  d: s => `\x1b[2m${s}\x1b[0m`,
  red: s => `\x1b[31m${s}\x1b[0m`,
  grn: s => `\x1b[32m${s}\x1b[0m`,
  ylw: s => `\x1b[33m${s}\x1b[0m`,
  blu: s => `\x1b[34m${s}\x1b[0m`,
  mag: s => `\x1b[35m${s}\x1b[0m`,
  cyn: s => `\x1b[36m${s}\x1b[0m`,
};

function banner() {
  console.log(c.mag(`
   ██████╗ ██████╗ ██████╗ ███████╗
  ██╔════╝██╔═══██╗██╔══██╗██╔════╝
  ██║     ██║   ██║██║  ██║█████╗
  ██║     ██║   ██║██║  ██║██╔══╝
  ╚██████╗╚██████╔╝██████╔╝███████╗
   ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
   █████╗ ██████╗ ██╗   ██╗███████╗███████╗
  ██╔══██╗██╔══██╗╚██╗ ██╔╝██╔════╝██╔════╝
  ███████║██████╔╝ ╚████╔╝ ███████╗███████╗
  ██╔══██║██╔══██╗  ╚██╔╝  ╚════██║╚════██║
  ██║  ██║██████╔╝   ██║   ███████║███████║
  ╚═╝  ╚═╝╚═════╝    ╚═╝   ╚══════╝╚══════╝`));
  console.log(c.d(`  ☠️  邪修红尘仙 · 宿命深渊  v${VERSION}\n`));
}

function divider(title) {
  const line = '─'.repeat(44);
  console.log(`\n${c.d('┌' + line + '┐')}\n${c.d('│')} ${c.b(title)}${' '.repeat(Math.max(0, 43 - title.length))}${c.d('│')}\n${c.d('└' + line + '┘')}`);
}

function step(n, total, msg) { console.log(`\n  ${c.cyn(`[${n}/${total}]`)} ${c.b(msg)}`); }
function ok(msg) { console.log(`  ${c.grn('✔')} ${msg}`); }
function warn(msg) { console.log(`  ${c.ylw('⚠')} ${msg}`); }
function info(msg) { console.log(`  ${c.blu('ℹ')} ${msg}`); }
function fail(msg) { console.log(`  ${c.red('✘')} ${msg}`); }

// ── 工具 ──

function shouldSkip(name) { return SKIP.some(p => name.includes(p)); }

function copyRecursive(src, dest) {
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    if (shouldSkip(path.basename(src))) return;
    fs.mkdirSync(dest, { recursive: true });
    fs.readdirSync(src).forEach(f => {
      if (!shouldSkip(f)) copyRecursive(path.join(src, f), path.join(dest, f));
    });
  } else {
    if (shouldSkip(path.basename(src))) return;
    fs.copyFileSync(src, dest);
  }
}

function rmSafe(p) {
  if (fs.existsSync(p)) fs.rmSync(p, { recursive: true, force: true });
}

function deepMergeNew(target, source, prefix, log) {
  for (const key of Object.keys(source)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
      if (!target[key] || typeof target[key] !== 'object') {
        target[key] = {};
        log.push({ k: fullKey, a: 'new', v: '{}' });
      }
      deepMergeNew(target[key], source[key], fullKey, log);
    } else if (Array.isArray(source[key]) && Array.isArray(target[key])) {
      const added = source[key].filter(v => !target[key].includes(v));
      if (added.length > 0) {
        target[key] = [...target[key], ...added];
        log.push({ k: fullKey, a: 'add', v: `+${added.length}` });
      } else {
        log.push({ k: fullKey, a: 'keep', v: '完整' });
      }
    } else if (key in target) {
      log.push({ k: fullKey, a: 'keep', v: JSON.stringify(target[key]) });
    } else {
      target[key] = source[key];
      log.push({ k: fullKey, a: 'set', v: JSON.stringify(source[key]) });
    }
  }
  return target;
}

function printMergeLog(log) {
  log.forEach(({ k, a, v }) => {
    if (a === 'keep') console.log(`  ${c.d('·')} ${c.d(`${k} (保留: ${v})`)}`);
    else console.log(`  ${c.grn('+')} ${c.cyn(k)} = ${v}`);
  });
}

// ── 认证 ──

function detectClaudeAuth(settings) {
  const env = settings.env || {};
  if (env.ANTHROPIC_BASE_URL && env.ANTHROPIC_AUTH_TOKEN) return { type: 'custom', detail: env.ANTHROPIC_BASE_URL };
  if (process.env.ANTHROPIC_API_KEY) return { type: 'env', detail: 'ANTHROPIC_API_KEY' };
  if (process.env.ANTHROPIC_BASE_URL && process.env.ANTHROPIC_AUTH_TOKEN) return { type: 'env-custom', detail: process.env.ANTHROPIC_BASE_URL };
  const cred = path.join(HOME, '.claude', '.credentials.json');
  if (fs.existsSync(cred)) {
    try {
      const cc = JSON.parse(fs.readFileSync(cred, 'utf8'));
      if (cc.claudeAiOauth || cc.apiKey) return { type: 'login', detail: 'claude login' };
    } catch (e) { warn(`凭证文件损坏: ${cred}`); }
  }
  return null;
}

function detectCodexAuth() {
  if (process.env.OPENAI_API_KEY) return { type: 'env', detail: 'OPENAI_API_KEY' };
  const auth = path.join(HOME, '.codex', 'auth.json');
  if (fs.existsSync(auth)) {
    try {
      const a = JSON.parse(fs.readFileSync(auth, 'utf8'));
      if (a.token || a.api_key) return { type: 'login', detail: 'codex login' };
    } catch (e) { warn(`凭证文件损坏: ${auth}`); }
  }
  const cfg = path.join(HOME, '.codex', 'config.toml');
  if (fs.existsSync(cfg)) {
    if (fs.readFileSync(cfg, 'utf8').includes('base_url')) return { type: 'custom', detail: 'config.toml' };
  }
  return null;
}

// ── 模板 ──

const SETTINGS_TEMPLATE = {
  $schema: 'https://json.schemastore.org/claude-code-settings.json',
  env: {
    CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS: '1',
    CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC: '1'
  },
  alwaysThinkingEnabled: true,
  model: 'opus',
  outputStyle: 'abyss-cultivator',
  attribution: { commit: '', pr: '' },
  permissions: {
    allow: [
      'Bash', 'LS', 'Read', 'Agent', 'Write', 'Edit', 'MultiEdit',
      'Glob', 'Grep', 'WebFetch', 'WebSearch', 'TodoWrite',
      'NotebookRead', 'NotebookEdit'
    ]
  }
};

const CCLINE_CMD = process.platform === 'win32' ? 'ccline' : '~/.claude/ccline/ccline';
const CCLINE_STATUS_LINE = {
  statusLine: {
    type: 'command',
    command: CCLINE_CMD,
    padding: 0
  }
};

// ── CLI 参数 ──

const args = process.argv.slice(2);
let target = null;
let uninstallTarget = null;
let autoYes = false;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--target' && args[i + 1]) { target = args[++i]; }
  else if (args[i] === '--uninstall' && args[i + 1]) { uninstallTarget = args[++i]; }
  else if (args[i] === '--yes' || args[i] === '-y') { autoYes = true; }
  else if (args[i] === '--help' || args[i] === '-h') {
    banner();
    console.log(`${c.b('用法:')}  npx code-abyss [选项]

${c.b('选项:')}
  --target ${c.cyn('<claude|codex>')}      安装目标
  --uninstall ${c.cyn('<claude|codex>')}   卸载目标
  --yes, -y                    全自动模式
  --help, -h                   显示帮助

${c.b('示例:')}
  npx code-abyss                        ${c.d('# 交互菜单')}
  npx code-abyss --target claude -y      ${c.d('# 零配置一键安装')}
  npx code-abyss --uninstall claude      ${c.d('# 直接卸载')}
`);
    process.exit(0);
  }
}

// ── 卸载 ──

function runUninstall(tgt) {
  if (!['claude', 'codex'].includes(tgt)) { fail('--uninstall 必须是 claude 或 codex'); process.exit(1); }
  const targetDir = path.join(HOME, `.${tgt}`);
  const backupDir = path.join(targetDir, '.sage-backup');
  const manifestPath = path.join(backupDir, 'manifest.json');
  if (!fs.existsSync(manifestPath)) { fail(`未找到安装记录: ${manifestPath}`); process.exit(1); }

  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  divider(`卸载 Code Abyss v${manifest.version}`);

  (manifest.installed || []).forEach(f => {
    const p = path.join(targetDir, f);
    if (fs.existsSync(p)) { rmSafe(p); console.log(`  ${c.red('✘')} ${f}`); }
  });
  (manifest.backups || []).forEach(f => {
    const bp = path.join(backupDir, f);
    const tp = path.join(targetDir, f);
    if (fs.existsSync(bp)) { fs.renameSync(bp, tp); ok(`恢复: ${f}`); }
  });

  rmSafe(backupDir);
  const us = path.join(targetDir, '.sage-uninstall.js');
  if (fs.existsSync(us)) fs.unlinkSync(us);
  console.log('');
  ok(c.b('卸载完成\n'));
}

// ── 安装核心 ──

function installCore(tgt) {
  const targetDir = path.join(HOME, `.${tgt}`);
  const backupDir = path.join(targetDir, '.sage-backup');
  const manifestPath = path.join(backupDir, 'manifest.json');

  step(1, 3, `安装核心文件 → ${c.cyn(targetDir)}`);
  fs.mkdirSync(backupDir, { recursive: true });

  const filesToInstall = [
    { src: 'config/CLAUDE.md', dest: tgt === 'claude' ? 'CLAUDE.md' : null },
    { src: 'config/AGENTS.md', dest: tgt === 'codex' ? 'AGENTS.md' : null },
    { src: 'output-styles', dest: tgt === 'claude' ? 'output-styles' : null },
    { src: 'skills', dest: 'skills' }
  ].filter(f => f.dest !== null);

  const manifest = { version: VERSION, target: tgt, timestamp: new Date().toISOString(), installed: [], backups: [] };

  filesToInstall.forEach(({ src, dest }) => {
    const srcPath = path.join(PKG_ROOT, src);
    const destPath = path.join(targetDir, dest);
    if (!fs.existsSync(srcPath)) { warn(`跳过: ${src}`); return; }
    if (fs.existsSync(destPath)) {
      const bp = path.join(backupDir, dest);
      rmSafe(bp); copyRecursive(destPath, bp); manifest.backups.push(dest);
      info(`备份: ${c.d(dest)}`);
    }
    ok(dest);
    rmSafe(destPath); copyRecursive(srcPath, destPath); manifest.installed.push(dest);
  });

  const settingsPath = path.join(targetDir, 'settings.json');
  let settings = {};
  if (fs.existsSync(settingsPath)) {
    try { settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8')); } catch (e) { warn(`settings.json 解析失败，将使用空配置`); settings = {}; }
    fs.copyFileSync(settingsPath, path.join(backupDir, 'settings.json'));
    manifest.backups.push('settings.json');
  }
  if (tgt === 'claude') {
    settings.outputStyle = 'abyss-cultivator';
    ok(`outputStyle = ${c.mag('abyss-cultivator')}`);
  }
  fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + '\n');
  manifest.installed.push('settings.json');
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + '\n');

  const uSrc = path.join(PKG_ROOT, 'bin', 'uninstall.js');
  const uDest = path.join(targetDir, '.sage-uninstall.js');
  if (fs.existsSync(uSrc)) { fs.copyFileSync(uSrc, uDest); fs.chmodSync(uDest, '755'); }

  return { targetDir, settingsPath, settings, manifest, manifestPath };
}

// ── Claude 后续 ──

async function postClaude(ctx) {
  const { select, checkbox, confirm, input } = await import('@inquirer/prompts');

  step(2, 3, '认证检测');
  const auth = detectClaudeAuth(ctx.settings);
  if (auth) {
    ok(`${c.b(auth.type)} → ${auth.detail}`);
  } else {
    warn('未检测到 API 认证');
    info(`支持: ${c.cyn('claude login')} | ${c.cyn('ANTHROPIC_API_KEY')} | ${c.cyn('自定义 provider')}`);
    if (!autoYes) {
      const doCfg = await confirm({ message: '配置自定义 provider?', default: false });
      if (doCfg) {
        if (!ctx.settings.env) ctx.settings.env = {};
        const url = await input({ message: 'ANTHROPIC_BASE_URL:' });
        const token = await input({ message: 'ANTHROPIC_AUTH_TOKEN:' });
        if (url) ctx.settings.env.ANTHROPIC_BASE_URL = url;
        if (token) ctx.settings.env.ANTHROPIC_AUTH_TOKEN = token;
        fs.writeFileSync(ctx.settingsPath, JSON.stringify(ctx.settings, null, 2) + '\n');
        ok('provider 已配置');
      }
    }
  }

  step(3, 3, '可选配置');
  if (autoYes) {
    info('自动模式: 合并推荐配置');
    const log = [];
    deepMergeNew(ctx.settings, SETTINGS_TEMPLATE, '', log);
    printMergeLog(log);
    fs.writeFileSync(ctx.settingsPath, JSON.stringify(ctx.settings, null, 2) + '\n');
    ok('settings.json 合并完成');
    return;
  }

  const choices = await checkbox({
    message: '选择要安装的配置 (空格选择, 回车确认)',
    choices: [
      { name: '精细合并推荐 settings.json (保留现有配置)', value: 'settings', checked: true },
      { name: '安装 ccline 状态栏 (需要 Nerd Font)', value: 'ccline' },
    ],
  });

  if (choices.includes('settings')) {
    const log = [];
    deepMergeNew(ctx.settings, SETTINGS_TEMPLATE, '', log);
    printMergeLog(log);
    fs.writeFileSync(ctx.settingsPath, JSON.stringify(ctx.settings, null, 2) + '\n');
    ok('settings.json 合并完成');
  }
  if (choices.includes('ccline')) {
    await installCcline(ctx);
  }
}

async function installCcline(ctx) {
  console.log('');
  info('安装 ccline 状态栏...');
  const { execSync } = require('child_process');

  let installed = false;
  try { execSync('ccline --version', { stdio: 'pipe' }); installed = true; } catch (e) {}
  if (!installed) {
    const cclineBin = path.join(HOME, '.claude', 'ccline', 'ccline');
    if (fs.existsSync(cclineBin)) installed = true;
  }

  if (!installed) {
    info('ccline 未检测到，正在安装...');
    try {
      execSync('npm install -g @cometix/ccline', { stdio: 'inherit' });
      installed = true;
      ok('ccline 安装成功');
    } catch (e) {
      warn('npm install -g @cometix/ccline 失败');
      info(`手动: ${c.cyn('https://github.com/Haleclipse/CCometixLine/releases')}`);
    }
  } else {
    ok('ccline 已安装');
  }

  const cclineConfig = path.join(HOME, '.claude', 'ccline', 'config.toml');
  if (installed && !fs.existsSync(cclineConfig)) {
    try { execSync('ccline --init', { stdio: 'inherit' }); ok('ccline 默认配置已生成'); }
    catch (e) { warn('ccline --init 失败，可手动运行'); }
  } else if (fs.existsSync(cclineConfig)) {
    ok('ccline/config.toml (已存在)');
  }

  ctx.settings.statusLine = CCLINE_STATUS_LINE.statusLine;
  ok(`statusLine → ${c.cyn(CCLINE_STATUS_LINE.statusLine.command)}`);
  fs.writeFileSync(ctx.settingsPath, JSON.stringify(ctx.settings, null, 2) + '\n');

  console.log('');
  warn(`需要 ${c.b('Nerd Font')} 字体`);
  info(`推荐: FiraCode Nerd Font / JetBrainsMono Nerd Font`);
  info(`下载: ${c.cyn('https://www.nerdfonts.com/')}`);
  info(`配置: ${c.cyn('ccline --config')}`);
  ok('ccline 配置完成');
}

// ── Codex 后续 ──

async function postCodex() {
  const { confirm } = await import('@inquirer/prompts');
  const cfgPath = path.join(HOME, '.codex', 'config.toml');
  const exists = fs.existsSync(cfgPath);

  step(2, 3, '认证检测');
  const auth = detectCodexAuth();
  if (auth) {
    ok(`${c.b(auth.type)} → ${auth.detail}`);
  } else {
    warn('未检测到 API 认证');
    info(`支持: ${c.cyn('codex login')} | ${c.cyn('OPENAI_API_KEY')} | ${c.cyn('自定义 provider')}`);
  }

  step(3, 3, '可选配置');
  if (autoYes) {
    if (!exists) {
      const src = path.join(PKG_ROOT, 'config', 'codex-config.example.toml');
      if (fs.existsSync(src)) {
        fs.copyFileSync(src, cfgPath);
        ok('写入: ~/.codex/config.toml (模板)');
        warn('请编辑 base_url 和 model');
      }
    } else {
      ok('config.toml 已存在');
    }
    return;
  }

  if (!exists) {
    warn('未检测到 ~/.codex/config.toml');
    const doWrite = await confirm({ message: '写入推荐 config.toml (含自定义 provider 模板)?', default: true });
    if (doWrite) {
      const src = path.join(PKG_ROOT, 'config', 'codex-config.example.toml');
      if (fs.existsSync(src)) {
        fs.copyFileSync(src, cfgPath);
        ok('写入: ~/.codex/config.toml');
        warn('请编辑 base_url 和 model');
      }
    }
  } else {
    ok('config.toml 已存在');
  }
}

// ── 主流程 ──

async function main() {
  if (uninstallTarget) { runUninstall(uninstallTarget); return; }

  banner();

  if (target) {
    if (!['claude', 'codex'].includes(target)) { fail('--target 必须是 claude 或 codex'); process.exit(1); }
    const ctx = installCore(target);
    if (target === 'claude') await postClaude(ctx);
    else await postCodex();
    finish(ctx);
    return;
  }

  const { select } = await import('@inquirer/prompts');
  const action = await select({
    message: '请选择操作',
    choices: [
      { name: `安装到 Claude Code ${c.d('(~/.claude/')}${c.d(')')}`, value: 'install-claude' },
      { name: `安装到 Codex CLI   ${c.d('(~/.codex/')}${c.d(')')}`, value: 'install-codex' },
      { name: `${c.red('卸载')} Claude Code`, value: 'uninstall-claude' },
      { name: `${c.red('卸载')} Codex CLI`, value: 'uninstall-codex' },
    ],
  });

  switch (action) {
    case 'install-claude': {
      const ctx = installCore('claude');
      await postClaude(ctx);
      finish(ctx); break;
    }
    case 'install-codex': {
      const ctx = installCore('codex');
      await postCodex();
      finish(ctx); break;
    }
    case 'uninstall-claude': runUninstall('claude'); break;
    case 'uninstall-codex': runUninstall('codex'); break;
  }
}

function finish(ctx) {
  const tgt = ctx.manifest.target;
  divider('安装完成');
  console.log('');
  console.log(`  ${c.b('目标:')}     ${c.cyn(ctx.targetDir)}`);
  console.log(`  ${c.b('版本:')}     v${VERSION}`);
  console.log(`  ${c.b('文件:')}     ${ctx.manifest.installed.length} 个安装, ${ctx.manifest.backups.length} 个备份`);
  console.log(`  ${c.b('卸载:')}     ${c.d(`npx code-abyss --uninstall ${tgt}`)}`);
  console.log('');
  console.log(c.mag(`  ⚚ 劫——破——了——！！！\n`));
}

main().catch(err => { fail(err.message); process.exit(1); });
