# UI 美学

## 色彩理论

### 色彩体系设计
60-30-10配色法则：主色60%、辅色30%、强调色10%。使用HSL而非RGB便于调整。建立语义化色彩令牌（primary/success/danger）。

```css
:root {
  --primary-h: 220;
  --primary-s: 90%;
  --primary-l: 50%;
  --primary: hsl(var(--primary-h) var(--primary-s) var(--primary-l));
  --primary-dark: hsl(var(--primary-h) var(--primary-s) 40%);
  --primary-light: hsl(var(--primary-h) var(--primary-s) 60%);
}
```

## 排版系统

### 排版层级规范
使用模块化比例（1.25/1.333/1.5）。基准16px，标题用比例放大，正文14-18px。行高1.5-1.8。限制字体族≤3种。

```css
:root {
  --fs-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
  --fs-h1: clamp(2rem, 1.5rem + 2vw, 3rem);
  --fs-h2: clamp(1.5rem, 1.2rem + 1.5vw, 2.25rem);
}
body {
  font-size: var(--fs-base);
  line-height: 1.6;
}
```

## 间距系统

### 8px网格间距体系
基准8px，建立4/8/12/16/24/32/48/64px间距令牌。组件内用小间距(4-12)，组件间用中间距(16-32)，区块间用大间距(48+)。

```css
:root {
  --sp-1: 0.25rem; --sp-2: 0.5rem; --sp-3: 0.75rem; --sp-4: 1rem;
  --sp-6: 1.5rem; --sp-8: 2rem; --sp-12: 3rem; --sp-16: 4rem;
}
.stack-sm > * + * { margin-top: var(--sp-2); }
.stack-md > * + * { margin-top: var(--sp-4); }
```

## 视觉层次

### 视觉层次四原则
1. 对比：大小/粗细/颜色差异
2. 对齐：统一对齐建立秩序
3. 重复：一致性建立认知
4. 亲密性：相关元素靠近

## 设计令牌

### Design Token架构
三层架构：基础令牌(颜色/字号原始值)→语义令牌(primary/heading)→组件令牌(button-bg)。

```css
:root {
  --color-gray-50: #f9fafb;
  --color-gray-900: #111827;
  --color-primary: var(--color-blue-600);
  --text-primary: var(--color-gray-900);
  --bg-surface: white;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
}
```

## 暗色模式

### 暗色模式设计规范
背景用深灰(#121212)非纯黑。降低白色文本亮度至#e0e0e0。提升表面层级用更亮灰色。注意色彩对比度WCAG AA。

```css
:root { --bg: white; --text: #111; }
@media (prefers-color-scheme: dark) {
  :root { --bg: #121212; --text: #e0e0e0; }
}
[data-theme="dark"] { --bg: #121212; --text: #e0e0e0; }
body { background: var(--bg); color: var(--text); }
```

## 阴影与层级

### 阴影层级体系
5级阴影：1-贴地(1px) 2-悬浮(2-4px) 3-浮起(8-12px) 4-弹出(16-24px) 5-模态(24-32px)。

```css
:root {
  --shadow-1: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-2: 0 2px 4px rgba(0,0,0,0.08);
  --shadow-3: 0 8px 16px rgba(0,0,0,0.12);
  --shadow-4: 0 16px 24px rgba(0,0,0,0.16);
  --shadow-5: 0 24px 32px rgba(0,0,0,0.2);
}
```

## 审查清单

- [ ] 色彩对比度≥4.5:1
- [ ] 字体≤3种
- [ ] 间距符合8px网格
- [ ] 视觉层级清晰
- [ ] 暗色模式适配
- [ ] 阴影层级合理
