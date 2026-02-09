# UX 原则

## 可用性

### Nielsen十大可用性原则
1. 系统状态可见
2. 系统匹配现实
3. 用户控制自由
4. 一致性标准
5. 防错
6. 识别优于回忆
7. 灵活高效
8. 美学简约
9. 帮助识别错误
10. 帮助文档

## 无障碍

### WCAG 2.1速查
- **可感知**：文本替代、时基媒体、适配性、可辨别
- **可操作**：键盘、足够时间、无癫痫、导航
- **可理解**：可读、可预测、输入辅助
- **健壮**：兼容性

### ARIA标签最佳实践
```html
<button aria-label="关闭对话框">
  <svg aria-hidden="true">...</svg>
</button>
<nav aria-label="主导航">
  <ul role="list">...</ul>
</nav>
<div role="alert" aria-live="assertive">错误消息</div>
```

### 键盘导航支持
```javascript
element.addEventListener("keydown", e => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    handleClick();
  }
  if (e.key === "Escape") {
    closeModal();
  }
});
element.setAttribute("tabindex", "0");
```

## 信息架构

### 信息架构设计模式
- 层级结构(树形)
- 顺序结构(线性)
- 矩阵结构(网格)
- 数据库结构(标签)

导航深度≤3层，广度5±2项。

## 用户流程

### 用户流程设计原则
减少步骤、清晰进度、允许跳过、保存状态、提供退出、即时反馈。关键流程≤3步。

## 加载体验

### 骨架屏与加载策略
优先级：骨架屏>进度条>加载动画>空白。首屏<1s，交互<100ms，加载>1s显示进度。

```css
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
}
@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

## 反馈设计

### 用户反馈模式
- **Toast**(临时提示)
- **Alert**(重要警告)
- **Modal**(阻断操作)
- **Inline**(表单验证)

成功绿、警告黄、错误红、信息蓝。

```css
.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: var(--shadow-4);
  animation: slideInRight 0.3s ease;
}
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
```

## 移动端优先

### 移动端设计原则
触摸目标≥44px、拇指热区、避免悬停、简化导航、减少输入、优化性能、考虑单手操作。

```css
.btn-touch {
  min-height: 44px;
  min-width: 44px;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}
@media (hover: hover) {
  .btn-touch:hover {
    background: var(--primary-dark);
  }
}
```

## 性能感知

### 感知性能优化
骨架屏、乐观更新、预加载、懒加载、渐进增强。让用户感觉快比实际快更重要。

## 审查清单

- [ ] 符合Nielsen原则
- [ ] WCAG AA达标
- [ ] 键盘可访问
- [ ] 移动端友好
- [ ] 加载状态清晰
- [ ] 反馈及时

## 最佳实践

1. 用户优先于技术
2. 简单优于复杂
3. 一致性建立信任
4. 反馈建立信心
5. 可访问性非可选
