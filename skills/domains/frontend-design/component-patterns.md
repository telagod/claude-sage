# 组件模式

## 布局模板

### 经典布局模式
圣杯布局(header/nav/main/aside/footer)、卡片网格、侧边栏、仪表盘。优先使用Grid，Flexbox做一维布局。

```css
.layout {
  display: grid;
  grid-template:
    "header header" auto
    "nav main" 1fr
    "nav aside" auto
    "footer footer" auto
    / 200px 1fr;
  gap: 1rem;
  min-height: 100vh;
}
@media (max-width: 768px) {
  .layout {
    grid-template: "header" "nav" "main" "aside" "footer" / 1fr;
  }
}
```

### Flexbox卡片网格
```css
.card-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}
.card {
  flex: 1 1 300px;
  max-width: 400px;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: var(--shadow-2);
}
```

## 响应式设计

### 响应式断点策略
移动优先：320px基准→640px(sm)→768px(md)→1024px(lg)→1280px(xl)。使用em单位断点(除以16)。优先容器查询。

```css
.card-container {
  container-type: inline-size;
}
.card {
  padding: 1rem;
}
@container (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 150px 1fr;
    gap: 1rem;
  }
}
```

## 交互模式

### 微交互设计原则
反馈即时(<100ms)、过渡流畅(200-300ms)、状态清晰(hover/active/focus)、减少认知负担。

```css
.btn {
  transition: all 0.2s ease;
}
.btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-3);
}
.btn:active {
  transform: translateY(0);
}
.btn:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}
```

## 动画

### CSS关键帧动画
```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-in {
  animation: fadeInUp 0.4s ease-out;
}
@media (prefers-reduced-motion: reduce) {
  .animate-in {
    animation: none;
  }
}
```

### Framer Motion模板
```javascript
const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.4, ease: "easeOut" }
};
const stagger = {
  animate: { transition: { staggerChildren: 0.1 } }
};
<motion.div variants={stagger}>
  <motion.div variants={fadeInUp} />
</motion.div>
```

## 表单设计

### 表单UX模式
标签上置、内联验证、清晰错误提示、禁用状态明显、必填标记、合理分组、自动聚焦首字段。

```css
.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.input {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}
.input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
}
```

## 卡片组件

### 玻璃拟态卡片
```css
.glass-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}
```

## 导航模式

### 响应式导航栏
```css
.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
}
.nav-links {
  display: flex;
  gap: 2rem;
}
@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
  .nav-links.open {
    display: flex;
    flex-direction: column;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    padding: 1rem;
  }
}
```

## 审查清单

- [ ] 响应式适配
- [ ] 交互状态完整
- [ ] 无障碍支持
- [ ] 性能优化
- [ ] 浏览器兼容
- [ ] 动画流畅
