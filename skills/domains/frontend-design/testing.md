---
name: testing
description: 前端测试技术。Vitest、Playwright、Jest、Cypress、测试金字塔、E2E测试、单元测试、集成测试。当用户提到前端测试、Vitest、Playwright、E2E测试、单元测试、测试覆盖率时使用。
---

# 🎨 🧪 前端测试 · Frontend Testing

## 测试金字塔

```
        /\
       /  \  E2E Tests (10%)
      /----\
     /      \ Integration Tests (20%)
    /--------\
   /          \ Unit Tests (70%)
  /____________\
```

| 层级 | 数量 | 速度 | 成本 | 信心 |
|------|------|------|------|------|
| E2E | 少 | 慢 | 高 | 高 |
| 集成 | 中 | 中 | 中 | 中 |
| 单元 | 多 | 快 | 低 | 低 |

## 测试策略决策树

```
需要测试什么？
  │
  ├─ 纯函数/工具 → 单元测试 (Vitest/Jest)
  │
  ├─ React 组件
  │   ├─ UI 渲染 → 组件测试 (Testing Library)
  │   ├─ 交互逻辑 → 集成测试
  │   └─ 视觉回归 → Chromatic/Percy
  │
  ├─ API 集成 → MSW Mock + 集成测试
  │
  └─ 用户流程 → E2E 测试 (Playwright/Cypress)
```

## Vitest (推荐)

### 基础配置

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'src/test/'],
    },
  },
})
```

### 单元测试

```typescript
// utils.test.ts
import { describe, it, expect } from 'vitest'
import { formatCurrency, debounce } from './utils'

describe('formatCurrency', () => {
  it('formats number to currency', () => {
    expect(formatCurrency(1234.56)).toBe('$1,234.56')
  })

  it('handles zero', () => {
    expect(formatCurrency(0)).toBe('$0.00')
  })

  it('handles negative numbers', () => {
    expect(formatCurrency(-100)).toBe('-$100.00')
  })
})

describe('debounce', () => {
  it('delays function execution', async () => {
    let count = 0
    const fn = debounce(() => count++, 100)

    fn()
    fn()
    fn()

    expect(count).toBe(0)

    await new Promise((resolve) => setTimeout(resolve, 150))
    expect(count).toBe(1)
  })
})
```

### React 组件测试

```typescript
// Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { Button } from './Button'

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click</Button>)

    fireEvent.click(screen.getByText('Click'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('applies variant styles', () => {
    render(<Button variant="primary">Click</Button>)
    expect(screen.getByRole('button')).toHaveClass('btn-primary')
  })
})
```

### Hooks 测试

```typescript
// useCounter.test.ts
import { renderHook, act } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { useCounter } from './useCounter'

describe('useCounter', () => {
  it('initializes with default value', () => {
    const { result } = renderHook(() => useCounter())
    expect(result.current.count).toBe(0)
  })

  it('increments counter', () => {
    const { result } = renderHook(() => useCounter())

    act(() => {
      result.current.increment()
    })

    expect(result.current.count).toBe(1)
  })

  it('decrements counter', () => {
    const { result } = renderHook(() => useCounter(5))

    act(() => {
      result.current.decrement()
    })

    expect(result.current.count).toBe(4)
  })

  it('resets counter', () => {
    const { result } = renderHook(() => useCounter(10))

    act(() => {
      result.current.increment()
      result.current.reset()
    })

    expect(result.current.count).toBe(10)
  })
})
```

### 异步测试

```typescript
// api.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fetchUser, createUser } from './api'

// Mock fetch
global.fetch = vi.fn()

describe('API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches user successfully', async () => {
    const mockUser = { id: '1', name: 'John' }
    ;(fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockUser,
    })

    const user = await fetchUser('1')
    expect(user).toEqual(mockUser)
    expect(fetch).toHaveBeenCalledWith('/api/users/1')
  })

  it('handles fetch error', async () => {
    ;(fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 404,
    })

    await expect(fetchUser('999')).rejects.toThrow('User not found')
  })

  it('creates user', async () => {
    const newUser = { name: 'Jane', email: 'jane@example.com' }
    const createdUser = { id: '2', ...newUser }

    ;(fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => createdUser,
    })

    const result = await createUser(newUser)
    expect(result).toEqual(createdUser)
  })
})
```

## MSW (Mock Service Worker)

### 配置 MSW

```typescript
// src/mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/api/users/:id', ({ params }) => {
    const { id } = params
    return HttpResponse.json({
      id,
      name: 'John Doe',
      email: 'john@example.com',
    })
  }),

  http.post('/api/users', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json(
      { id: '123', ...body },
      { status: 201 }
    )
  }),

  http.delete('/api/users/:id', () => {
    return new HttpResponse(null, { status: 204 })
  }),
]

// src/mocks/server.ts
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)

// src/test/setup.ts
import { beforeAll, afterEach, afterAll } from 'vitest'
import { server } from '../mocks/server'

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

### 使用 MSW 测试

```typescript
// UserProfile.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { server } from '../mocks/server'
import { http, HttpResponse } from 'msw'
import { UserProfile } from './UserProfile'

describe('UserProfile', () => {
  it('displays user data', async () => {
    render(<UserProfile userId="1" />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('john@example.com')).toBeInTheDocument()
    })
  })

  it('handles loading state', () => {
    render(<UserProfile userId="1" />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('handles error state', async () => {
    server.use(
      http.get('/api/users/:id', () => {
        return new HttpResponse(null, { status: 500 })
      })
    )

    render(<UserProfile userId="1" />)

    await waitFor(() => {
      expect(screen.getByText('Error loading user')).toBeInTheDocument()
    })
  })
})
```

## Playwright (E2E 推荐)

### 配置 Playwright

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

### 基础 E2E 测试

```typescript
// e2e/login.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Login', () => {
  test('successful login', async ({ page }) => {
    await page.goto('/login')

    await page.fill('input[name="email"]', 'user@example.com')
    await page.fill('input[name="password"]', 'password123')
    await page.click('button[type="submit"]')

    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('h1')).toContainText('Dashboard')
  })

  test('shows error for invalid credentials', async ({ page }) => {
    await page.goto('/login')

    await page.fill('input[name="email"]', 'wrong@example.com')
    await page.fill('input[name="password"]', 'wrongpass')
    await page.click('button[type="submit"]')

    await expect(page.locator('.error')).toContainText('Invalid credentials')
  })

  test('validates required fields', async ({ page }) => {
    await page.goto('/login')
    await page.click('button[type="submit"]')

    await expect(page.locator('input[name="email"]:invalid')).toBeVisible()
  })
})
```

### Page Object Model

```typescript
// e2e/pages/LoginPage.ts
import { Page, Locator } from '@playwright/test'

export class LoginPage {
  readonly page: Page
  readonly emailInput: Locator
  readonly passwordInput: Locator
  readonly submitButton: Locator
  readonly errorMessage: Locator

  constructor(page: Page) {
    this.page = page
    this.emailInput = page.locator('input[name="email"]')
    this.passwordInput = page.locator('input[name="password"]')
    this.submitButton = page.locator('button[type="submit"]')
    this.errorMessage = page.locator('.error')
  }

  async goto() {
    await this.page.goto('/login')
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email)
    await this.passwordInput.fill(password)
    await this.submitButton.click()
  }
}

// 使用 Page Object
test('login with page object', async ({ page }) => {
  const loginPage = new LoginPage(page)
  await loginPage.goto()
  await loginPage.login('user@example.com', 'password123')

  await expect(page).toHaveURL('/dashboard')
})
```

### API 测试

```typescript
// e2e/api.spec.ts
import { test, expect } from '@playwright/test'

test.describe('API', () => {
  test('GET /api/users', async ({ request }) => {
    const response = await request.get('/api/users')
    expect(response.ok()).toBeTruthy()

    const users = await response.json()
    expect(users).toHaveLength(10)
    expect(users[0]).toHaveProperty('id')
    expect(users[0]).toHaveProperty('name')
  })

  test('POST /api/users', async ({ request }) => {
    const response = await request.post('/api/users', {
      data: {
        name: 'New User',
        email: 'new@example.com',
      },
    })

    expect(response.status()).toBe(201)
    const user = await response.json()
    expect(user.name).toBe('New User')
  })

  test('handles authentication', async ({ request }) => {
    const response = await request.get('/api/protected', {
      headers: {
        Authorization: 'Bearer token123',
      },
    })

    expect(response.ok()).toBeTruthy()
  })
})
```

### 视觉回归测试

```typescript
// e2e/visual.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Visual Regression', () => {
  test('homepage screenshot', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveScreenshot('homepage.png')
  })

  test('button states', async ({ page }) => {
    await page.goto('/components')

    const button = page.locator('button.primary')
    await expect(button).toHaveScreenshot('button-default.png')

    await button.hover()
    await expect(button).toHaveScreenshot('button-hover.png')

    await button.focus()
    await expect(button).toHaveScreenshot('button-focus.png')
  })

  test('responsive layout', async ({ page }) => {
    await page.goto('/')

    // Desktop
    await page.setViewportSize({ width: 1920, height: 1080 })
    await expect(page).toHaveScreenshot('desktop.png')

    // Tablet
    await page.setViewportSize({ width: 768, height: 1024 })
    await expect(page).toHaveScreenshot('tablet.png')

    // Mobile
    await page.setViewportSize({ width: 375, height: 667 })
    await expect(page).toHaveScreenshot('mobile.png')
  })
})
```

## 测试最佳实践

### AAA 模式

```typescript
test('user can add item to cart', async ({ page }) => {
  // Arrange - 准备测试环境
  await page.goto('/products')
  const product = page.locator('[data-testid="product-1"]')

  // Act - 执行操作
  await product.locator('button.add-to-cart').click()

  // Assert - 验证结果
  await expect(page.locator('.cart-count')).toHaveText('1')
  await expect(page.locator('.notification')).toContainText('Added to cart')
})
```

### 测试隔离

```typescript
import { test } from '@playwright/test'

test.describe('Todo App', () => {
  test.beforeEach(async ({ page }) => {
    // 每个测试前重置状态
    await page.goto('/')
    await page.evaluate(() => localStorage.clear())
  })

  test('add todo', async ({ page }) => {
    await page.fill('input[name="todo"]', 'Buy milk')
    await page.click('button[type="submit"]')
    await expect(page.locator('.todo-item')).toHaveText('Buy milk')
  })

  test('delete todo', async ({ page }) => {
    // 独立的测试，不依赖前一个测试
    await page.fill('input[name="todo"]', 'Buy milk')
    await page.click('button[type="submit"]')
    await page.click('.todo-item button.delete')
    await expect(page.locator('.todo-item')).toHaveCount(0)
  })
})
```

### 数据驱动测试

```typescript
const testCases = [
  { input: 'hello', expected: 'HELLO' },
  { input: 'world', expected: 'WORLD' },
  { input: '123', expected: '123' },
]

testCases.forEach(({ input, expected }) => {
  test(`converts "${input}" to "${expected}"`, () => {
    expect(toUpperCase(input)).toBe(expected)
  })
})

// Playwright 参数化
const browsers = ['chromium', 'firefox', 'webkit']

browsers.forEach((browserName) => {
  test(`works on ${browserName}`, async ({ browser }) => {
    const context = await browser.newContext()
    const page = await context.newPage()
    await page.goto('/')
    // 测试逻辑
  })
})
```

## 覆盖率配置

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: [
        'src/**/*.test.{ts,tsx}',
        'src/**/*.spec.{ts,tsx}',
        'src/test/**',
        'src/**/*.d.ts',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },
  },
})
```

## CI/CD 集成

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run test:unit
      - run: npm run test:coverage

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:e2e
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

## 最佳实践清单

- ✅ 遵循测试金字塔：70% 单元 + 20% 集成 + 10% E2E
- ✅ 使用 AAA 模式组织测试
- ✅ 测试行为而非实现细节
- ✅ 保持测试独立和隔离
- ✅ 使用有意义的测试描述
- ✅ Mock 外部依赖（API、时间、随机数）
- ✅ 测试边界条件和错误情况
- ✅ 维护合理的覆盖率（80%+）
- ✅ 在 CI/CD 中自动运行测试
- ✅ 使用 Page Object 模式组织 E2E 测试

## 工具清单

| 工具 | 用途 |
|------|------|
| Vitest | 单元测试框架 |
| Playwright | E2E 测试框架 |
| Testing Library | React 组件测试 |
| MSW | API Mock |
| Cypress | E2E 测试（备选） |
| Chromatic | 视觉回归测试 |
| Storybook | 组件开发和测试 |
| Istanbul | 覆盖率报告 |

---
