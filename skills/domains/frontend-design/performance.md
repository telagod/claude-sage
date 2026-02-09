---
name: performance
description: 前端性能优化技术。懒加载、代码分割、虚拟滚动、Web Vitals、性能监控。当用户提到性能优化、懒加载、代码分割、虚拟滚动、LCP、FID、CLS、性能指标时使用。
---

# 🎨 ⚡ 性能优化 · Performance Optimization

## 性能指标 (Core Web Vitals)

| 指标 | 含义 | 目标值 | 测量内容 |
|------|------|--------|----------|
| LCP | Largest Contentful Paint | < 2.5s | 最大内容绘制时间 |
| FID | First Input Delay | < 100ms | 首次输入延迟 |
| CLS | Cumulative Layout Shift | < 0.1 | 累积布局偏移 |
| FCP | First Contentful Paint | < 1.8s | 首次内容绘制 |
| TTI | Time to Interactive | < 3.8s | 可交互时间 |
| TBT | Total Blocking Time | < 200ms | 总阻塞时间 |

## 性能优化决策树

```
性能问题？
  │
  ├─ 加载慢
  │   ├─ Bundle 大 → 代码分割 + Tree Shaking
  │   ├─ 资源多 → 懒加载 + 预加载
  │   └─ 网络慢 → CDN + 压缩 + HTTP/2
  │
  ├─ 渲染慢
  │   ├─ 列表长 → 虚拟滚动
  │   ├─ 重渲染 → React.memo + useMemo
  │   └─ 布局抖动 → 固定尺寸 + CSS优化
  │
  └─ 交互慢
      ├─ JS 阻塞 → Web Worker + 时间切片
      ├─ 动画卡顿 → CSS动画 + requestAnimationFrame
      └─ 事件处理 → 防抖节流 + 事件委托
```

## 代码分割 (Code Splitting)

### React.lazy + Suspense

```typescript
import { lazy, Suspense } from 'react'

// 路由级别分割
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Profile = lazy(() => import('./pages/Profile'))
const Settings = lazy(() => import('./pages/Settings'))

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  )
}
```

### 组件级别分割

```typescript
import { lazy, Suspense } from 'react'

// 重量级组件懒加载
const HeavyChart = lazy(() => import('./components/HeavyChart'))
const RichTextEditor = lazy(() => import('./components/RichTextEditor'))

function Dashboard() {
  const [showChart, setShowChart] = useState(false)

  return (
    <div>
      <button onClick={() => setShowChart(true)}>Show Chart</button>
      {showChart && (
        <Suspense fallback={<div>Loading chart...</div>}>
          <HeavyChart />
        </Suspense>
      )}
    </div>
  )
}
```

### 动态导入

```typescript
// 条件加载
async function loadFeature(featureName: string) {
  if (featureName === 'analytics') {
    const { Analytics } = await import('./features/Analytics')
    return Analytics
  } else if (featureName === 'reporting') {
    const { Reporting } = await import('./features/Reporting')
    return Reporting
  }
}

// 按需加载工具库
async function processData(data: any[]) {
  const { default: _ } = await import('lodash-es')
  return _.groupBy(data, 'category')
}
```

### Webpack 配置

```javascript
// webpack.config.js
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        // 第三方库单独打包
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10,
        },
        // 公共代码提取
        common: {
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true,
        },
        // React 相关单独打包
        react: {
          test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
          name: 'react',
          priority: 20,
        },
      },
    },
  },
}
```

### Vite 配置

```typescript
// vite.config.ts
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'router': ['react-router-dom'],
          'ui': ['@mui/material', '@emotion/react'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
})
```

## 懒加载 (Lazy Loading)

### 图片懒加载

```typescript
// 原生 loading 属性
function ImageGallery({ images }: { images: string[] }) {
  return (
    <div>
      {images.map((src, i) => (
        <img
          key={i}
          src={src}
          loading="lazy"
          alt={`Image ${i}`}
          width="400"
          height="300"
        />
      ))}
    </div>
  )
}

// Intersection Observer
import { useEffect, useRef, useState } from 'react'

function LazyImage({ src, alt }: { src: string; alt: string }) {
  const [isLoaded, setIsLoaded] = useState(false)
  const imgRef = useRef<HTMLImageElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsLoaded(true)
          observer.disconnect()
        }
      },
      { rootMargin: '50px' }
    )

    if (imgRef.current) {
      observer.observe(imgRef.current)
    }

    return () => observer.disconnect()
  }, [])

  return (
    <img
      ref={imgRef}
      src={isLoaded ? src : '/placeholder.jpg'}
      alt={alt}
      className={isLoaded ? 'loaded' : 'loading'}
    />
  )
}
```

### 路由预加载

```typescript
import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

// 预加载下一个可能的路由
function useRoutePreload() {
  const location = useLocation()

  useEffect(() => {
    if (location.pathname === '/dashboard') {
      // 预加载 Profile 页面
      import('./pages/Profile')
    } else if (location.pathname === '/profile') {
      // 预加载 Settings 页面
      import('./pages/Settings')
    }
  }, [location])
}

// Link 悬停预加载
function PreloadLink({ to, children }: { to: string; children: ReactNode }) {
  const handleMouseEnter = () => {
    if (to === '/dashboard') {
      import('./pages/Dashboard')
    }
  }

  return (
    <Link to={to} onMouseEnter={handleMouseEnter}>
      {children}
    </Link>
  )
}
```

## 虚拟滚动 (Virtual Scrolling)

### react-window

```typescript
import { FixedSizeList } from 'react-window'

interface Item {
  id: string
  name: string
}

function VirtualList({ items }: { items: Item[] }) {
  const Row = ({ index, style }: { index: number; style: CSSProperties }) => (
    <div style={style}>
      {items[index].name}
    </div>
  )

  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  )
}
```

### 动态高度列表

```typescript
import { VariableSizeList } from 'react-window'

function DynamicList({ items }: { items: Item[] }) {
  const listRef = useRef<VariableSizeList>(null)

  // 计算每项高度
  const getItemSize = (index: number) => {
    return items[index].content.length > 100 ? 120 : 60
  }

  const Row = ({ index, style }: { index: number; style: CSSProperties }) => (
    <div style={style}>
      <h3>{items[index].title}</h3>
      <p>{items[index].content}</p>
    </div>
  )

  return (
    <VariableSizeList
      ref={listRef}
      height={600}
      itemCount={items.length}
      itemSize={getItemSize}
      width="100%"
    >
      {Row}
    </VariableSizeList>
  )
}
```

### 虚拟网格

```typescript
import { FixedSizeGrid } from 'react-window'

function VirtualGrid({ items }: { items: Item[] }) {
  const COLUMN_COUNT = 4
  const ROW_COUNT = Math.ceil(items.length / COLUMN_COUNT)

  const Cell = ({ columnIndex, rowIndex, style }: any) => {
    const index = rowIndex * COLUMN_COUNT + columnIndex
    if (index >= items.length) return null

    return (
      <div style={style}>
        <img src={items[index].thumbnail} alt={items[index].name} />
        <p>{items[index].name}</p>
      </div>
    )
  }

  return (
    <FixedSizeGrid
      columnCount={COLUMN_COUNT}
      columnWidth={200}
      height={600}
      rowCount={ROW_COUNT}
      rowHeight={200}
      width={800}
    >
      {Cell}
    </FixedSizeGrid>
  )
}
```

### 自定义虚拟滚动

```typescript
import { useState, useEffect, useRef } from 'react'

function useVirtualScroll<T>(
  items: T[],
  itemHeight: number,
  containerHeight: number
) {
  const [scrollTop, setScrollTop] = useState(0)

  const startIndex = Math.floor(scrollTop / itemHeight)
  const endIndex = Math.ceil((scrollTop + containerHeight) / itemHeight)
  const visibleItems = items.slice(startIndex, endIndex + 1)

  const totalHeight = items.length * itemHeight
  const offsetY = startIndex * itemHeight

  return {
    visibleItems,
    totalHeight,
    offsetY,
    onScroll: (e: React.UIEvent<HTMLDivElement>) => {
      setScrollTop(e.currentTarget.scrollTop)
    },
  }
}

function CustomVirtualList({ items }: { items: Item[] }) {
  const { visibleItems, totalHeight, offsetY, onScroll } = useVirtualScroll(
    items,
    50,
    600
  )

  return (
    <div style={{ height: 600, overflow: 'auto' }} onScroll={onScroll}>
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map((item) => (
            <div key={item.id} style={{ height: 50 }}>
              {item.name}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
```

## React 性能优化

### React.memo

```typescript
import { memo } from 'react'

// 避免不必要的重渲染
const ExpensiveComponent = memo(function ExpensiveComponent({
  data,
  onUpdate,
}: {
  data: Data
  onUpdate: (id: string) => void
}) {
  return <div>{/* 复杂渲染逻辑 */}</div>
})

// 自定义比较函数
const CustomMemo = memo(
  function Component({ user }: { user: User }) {
    return <div>{user.name}</div>
  },
  (prevProps, nextProps) => {
    // 只在 user.id 变化时重渲染
    return prevProps.user.id === nextProps.user.id
  }
)
```

### useMemo + useCallback

```typescript
import { useMemo, useCallback } from 'react'

function DataTable({ data, filter }: { data: Item[]; filter: string }) {
  // 缓存计算结果
  const filteredData = useMemo(() => {
    return data.filter((item) => item.name.includes(filter))
  }, [data, filter])

  const sortedData = useMemo(() => {
    return [...filteredData].sort((a, b) => a.name.localeCompare(b.name))
  }, [filteredData])

  // 缓存回调函数
  const handleClick = useCallback(
    (id: string) => {
      console.log('Clicked:', id)
    },
    []
  )

  return (
    <div>
      {sortedData.map((item) => (
        <Row key={item.id} item={item} onClick={handleClick} />
      ))}
    </div>
  )
}
```

### 状态批量更新

```typescript
import { unstable_batchedUpdates } from 'react-dom'

// React 18 自动批处理
function Component() {
  const [count, setCount] = useState(0)
  const [flag, setFlag] = useState(false)

  const handleClick = () => {
    // React 18 中自动批处理，只触发一次渲染
    setCount((c) => c + 1)
    setFlag((f) => !f)
  }

  // React 17 需要手动批处理
  const handleClickLegacy = () => {
    unstable_batchedUpdates(() => {
      setCount((c) => c + 1)
      setFlag((f) => !f)
    })
  }
}
```

### 时间切片

```typescript
// 使用 startTransition 标记低优先级更新
import { startTransition, useState } from 'react'

function SearchResults() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<string[]>([])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // 高优先级：立即更新输入框
    setQuery(e.target.value)

    // 低优先级：延迟更新搜索结果
    startTransition(() => {
      const filtered = heavySearch(e.target.value)
      setResults(filtered)
    })
  }

  return (
    <div>
      <input value={query} onChange={handleChange} />
      <ul>
        {results.map((r) => (
          <li key={r}>{r}</li>
        ))}
      </ul>
    </div>
  )
}
```

## 资源优化

### 图片优化

```typescript
// Next.js Image 组件
import Image from 'next/image'

function OptimizedImage() {
  return (
    <Image
      src="/hero.jpg"
      alt="Hero"
      width={1200}
      height={600}
      priority // LCP 图片优先加载
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,..."
    />
  )
}

// 响应式图片
function ResponsiveImage() {
  return (
    <picture>
      <source
        srcSet="/hero.webp"
        type="image/webp"
        media="(min-width: 768px)"
      />
      <source srcSet="/hero-mobile.jpg" media="(max-width: 767px)" />
      <img src="/hero.jpg" alt="Hero" loading="lazy" />
    </picture>
  )
}
```

### 字体优化

```css
/* 字体预加载 */
<link
  rel="preload"
  href="/fonts/inter.woff2"
  as="font"
  type="font/woff2"
  crossorigin
/>

/* font-display 策略 */
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter.woff2') format('woff2');
  font-display: swap; /* 立即显示备用字体 */
  font-weight: 400;
}

/* 可变字体 */
@font-face {
  font-family: 'Inter Variable';
  src: url('/fonts/inter-variable.woff2') format('woff2-variations');
  font-weight: 100 900;
}
```

### 预加载策略

```html
<!-- DNS 预解析 -->
<link rel="dns-prefetch" href="https://api.example.com" />

<!-- 预连接 -->
<link rel="preconnect" href="https://cdn.example.com" />

<!-- 预加载关键资源 -->
<link rel="preload" href="/critical.css" as="style" />
<link rel="preload" href="/hero.jpg" as="image" />

<!-- 预获取下一页资源 -->
<link rel="prefetch" href="/next-page.js" />

<!-- 预渲染下一页 -->
<link rel="prerender" href="/next-page" />
```

## 性能监控

### Web Vitals 测量

```typescript
import { onCLS, onFID, onLCP, onFCP, onTTFB } from 'web-vitals'

function sendToAnalytics(metric: Metric) {
  const body = JSON.stringify(metric)
  const url = '/api/analytics'

  // 使用 sendBeacon 确保数据发送
  if (navigator.sendBeacon) {
    navigator.sendBeacon(url, body)
  } else {
    fetch(url, { body, method: 'POST', keepalive: true })
  }
}

// 监控所有指标
onCLS(sendToAnalytics)
onFID(sendToAnalytics)
onLCP(sendToAnalytics)
onFCP(sendToAnalytics)
onTTFB(sendToAnalytics)
```

### Performance API

```typescript
// 测量自定义指标
function measureCustomMetric() {
  performance.mark('feature-start')

  // 执行操作
  doSomething()

  performance.mark('feature-end')
  performance.measure('feature-duration', 'feature-start', 'feature-end')

  const measure = performance.getEntriesByName('feature-duration')[0]
  console.log('Duration:', measure.duration)
}

// 监控资源加载
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.entryType === 'resource') {
      console.log(`${entry.name}: ${entry.duration}ms`)
    }
  }
})

observer.observe({ entryTypes: ['resource', 'navigation'] })
```

### React DevTools Profiler

```typescript
import { Profiler } from 'react'

function onRenderCallback(
  id: string,
  phase: 'mount' | 'update',
  actualDuration: number,
  baseDuration: number,
  startTime: number,
  commitTime: number
) {
  console.log(`${id} (${phase}) took ${actualDuration}ms`)
}

function App() {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      <Dashboard />
    </Profiler>
  )
}
```

## 最佳实践清单

- ✅ 使用代码分割减小初始 bundle 大小
- ✅ 懒加载非关键资源和路由
- ✅ 虚拟滚动处理长列表
- ✅ 使用 React.memo 避免不必要的重渲染
- ✅ useMemo/useCallback 缓存计算和回调
- ✅ 图片使用 WebP 格式 + 懒加载
- ✅ 字体使用 font-display: swap
- ✅ 预加载关键资源
- ✅ 监控 Core Web Vitals
- ✅ 使用 CDN 加速静态资源
- ✅ 启用 Gzip/Brotli 压缩
- ✅ 实施 HTTP/2 或 HTTP/3

## 工具清单

| 工具 | 用途 |
|------|------|
| Lighthouse | 性能审计 |
| WebPageTest | 详细性能分析 |
| Chrome DevTools | 性能分析和调试 |
| React DevTools Profiler | React 性能分析 |
| webpack-bundle-analyzer | Bundle 分析 |
| web-vitals | Core Web Vitals 监控 |
| react-window | 虚拟滚动 |
| Sentry | 性能监控 |

---
