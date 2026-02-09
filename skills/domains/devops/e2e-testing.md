---
name: e2e-testing
description: 端到端测试。Playwright、Cypress、Selenium、页面对象模式、可视化回归测试、跨浏览器测试。当用户提到E2E测试、Playwright、Cypress、端到端测试、可视化回归、UI测试时使用。
---

# 🎭 端到端测试 · E2E Testing

## Playwright vs Cypress

| 特性 | Playwright | Cypress |
|------|-----------|---------|
| 浏览器支持 | Chromium/Firefox/WebKit | Chromium/Firefox/Edge |
| 多标签页 | ✅ 原生支持 | ❌ 不支持 |
| iframe | ✅ 完整支持 | ⚠️ 有限支持 |
| 文件上传/下载 | ✅ 原生支持 | ⚠️ 需插件 |
| 网络拦截 | ✅ 强大 | ✅ 强大 |
| 并行执行 | ✅ 原生支持 | ⚠️ 需付费 |
| 调试体验 | ⚠️ 一般 | ✅ 优秀 |
| 学习曲线 | 平缓 | 平缓 |
| 执行速度 | 快 | 快 |

## Playwright 基础

### 安装与配置
```bash
npm init playwright@latest

# 安装浏览器
npx playwright install

# 运行测试
npx playwright test
npx playwright test --headed  # 显示浏览器
npx playwright test --debug   # 调试模式
```

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'mobile', use: { ...devices['iPhone 13'] } },
  ],

  webServer: {
    command: 'npm run start',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },
});
```

### 基础测试
```typescript
import { test, expect } from '@playwright/test';

test('用户登录流程', async ({ page }) => {
  // 导航
  await page.goto('/login');

  // 填写表单
  await page.fill('input[name="username"]', 'alice');
  await page.fill('input[name="password"]', 'password123');

  // 点击按钮
  await page.click('button[type="submit"]');

  // 等待导航
  await page.waitForURL('/dashboard');

  // 断言
  await expect(page.locator('h1')).toHaveText('欢迎, Alice');
});

test('搜索功能', async ({ page }) => {
  await page.goto('/');

  // 输入搜索
  await page.fill('[data-testid="search-input"]', 'Playwright');
  await page.press('[data-testid="search-input"]', 'Enter');

  // 等待结果
  await page.waitForSelector('.search-results');

  // 断言结果数量
  const results = page.locator('.search-result-item');
  await expect(results).toHaveCount(10);
});
```

### 高级选择器
```typescript
// CSS 选择器
await page.click('button.submit');

// 文本选择器
await page.click('text=登录');
await page.click('button:has-text("提交")');

// XPath
await page.click('xpath=//button[@type="submit"]');

// 组合选择器
await page.click('form >> button:has-text("登录")');

// data-testid (推荐)
await page.click('[data-testid="login-button"]');

// 角色选择器
await page.click('role=button[name="登录"]');

// 链式定位
await page
  .locator('.user-card')
  .filter({ hasText: 'Alice' })
  .locator('button')
  .click();
```

### 等待策略
```typescript
// 等待元素可见
await page.waitForSelector('.modal', { state: 'visible' });

// 等待元素消失
await page.waitForSelector('.loading', { state: 'hidden' });

// 等待网络请求
await page.waitForResponse(resp =>
  resp.url().includes('/api/users') && resp.status() === 200
);

// 等待函数返回 true
await page.waitForFunction(() =>
  document.querySelectorAll('.item').length > 5
);

// 自动等待 (推荐)
await page.click('button'); // 自动等待可点击
await expect(page.locator('h1')).toBeVisible(); // 自动等待可见
```

## Cypress 基础

### 安装与配置
```bash
npm install cypress --save-dev

# 打开 Cypress
npx cypress open

# 运行测试
npx cypress run
```

```javascript
// cypress.config.js
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    retries: {
      runMode: 2,
      openMode: 0,
    },
  },
});
```

### 基础测试
```javascript
describe('用户登录', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('成功登录', () => {
    cy.get('[data-cy="username"]').type('alice');
    cy.get('[data-cy="password"]').type('password123');
    cy.get('[data-cy="submit"]').click();

    cy.url().should('include', '/dashboard');
    cy.contains('欢迎, Alice').should('be.visible');
  });

  it('密码错误', () => {
    cy.get('[data-cy="username"]').type('alice');
    cy.get('[data-cy="password"]').type('wrongpassword');
    cy.get('[data-cy="submit"]').click();

    cy.contains('用户名或密码错误').should('be.visible');
  });
});

describe('购物车', () => {
  it('添加商品到购物车', () => {
    cy.visit('/products');

    // 添加商品
    cy.get('[data-cy="product-1"]').within(() => {
      cy.contains('加入购物车').click();
    });

    // 验证购物车
    cy.get('[data-cy="cart-count"]').should('have.text', '1');

    // 打开购物车
    cy.get('[data-cy="cart-icon"]').click();
    cy.get('[data-cy="cart-items"]').should('have.length', 1);
  });
});
```

### Cypress 命令
```javascript
// 导航
cy.visit('/page');
cy.go('back');
cy.reload();

// 查找元素
cy.get('.class');
cy.contains('text');
cy.find('.child');

// 交互
cy.click();
cy.type('text');
cy.clear();
cy.check();
cy.select('option');

// 断言
cy.should('be.visible');
cy.should('have.text', 'Hello');
cy.should('have.class', 'active');
cy.should('have.length', 3);

// 别名
cy.get('.user').as('user');
cy.get('@user').click();
```

## 页面对象模式 (Page Object Model)

### Playwright POM
```typescript
// pages/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}

  // 定位器
  get usernameInput() {
    return this.page.locator('[data-testid="username"]');
  }

  get passwordInput() {
    return this.page.locator('[data-testid="password"]');
  }

  get submitButton() {
    return this.page.locator('button[type="submit"]');
  }

  get errorMessage() {
    return this.page.locator('.error-message');
  }

  // 操作方法
  async goto() {
    await this.page.goto('/login');
  }

  async login(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async getErrorText() {
    return await this.errorMessage.textContent();
  }
}

// tests/login.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

test('用户登录', async ({ page }) => {
  const loginPage = new LoginPage(page);

  await loginPage.goto();
  await loginPage.login('alice', 'password123');

  await expect(page).toHaveURL('/dashboard');
});
```

### Cypress POM
```javascript
// cypress/pages/LoginPage.js
export class LoginPage {
  visit() {
    cy.visit('/login');
  }

  fillUsername(username) {
    cy.get('[data-cy="username"]').type(username);
    return this;
  }

  fillPassword(password) {
    cy.get('[data-cy="password"]').type(password);
    return this;
  }

  submit() {
    cy.get('[data-cy="submit"]').click();
    return this;
  }

  getErrorMessage() {
    return cy.get('.error-message');
  }
}

// cypress/e2e/login.cy.js
import { LoginPage } from '../pages/LoginPage';

describe('登录测试', () => {
  const loginPage = new LoginPage();

  it('成功登录', () => {
    loginPage
      .visit()
      .fillUsername('alice')
      .fillPassword('password123')
      .submit();

    cy.url().should('include', '/dashboard');
  });
});
```

## 网络拦截与 Mock

### Playwright 网络拦截
```typescript
test('Mock API 响应', async ({ page }) => {
  // 拦截并 Mock
  await page.route('**/api/users', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: 1, name: 'Alice' },
        { id: 2, name: 'Bob' }
      ])
    });
  });

  await page.goto('/users');
  await expect(page.locator('.user-item')).toHaveCount(2);
});

test('修改请求', async ({ page }) => {
  await page.route('**/api/login', route => {
    const request = route.request();
    route.continue({
      headers: {
        ...request.headers(),
        'X-Custom-Header': 'test'
      }
    });
  });

  await page.goto('/login');
});

test('等待 API 响应', async ({ page }) => {
  const responsePromise = page.waitForResponse('**/api/users');

  await page.goto('/users');

  const response = await responsePromise;
  expect(response.status()).toBe(200);

  const data = await response.json();
  expect(data).toHaveLength(10);
});
```

### Cypress 网络拦截
```javascript
describe('API Mock', () => {
  it('拦截并 Mock', () => {
    cy.intercept('GET', '/api/users', {
      statusCode: 200,
      body: [
        { id: 1, name: 'Alice' },
        { id: 2, name: 'Bob' }
      ]
    }).as('getUsers');

    cy.visit('/users');
    cy.wait('@getUsers');

    cy.get('.user-item').should('have.length', 2);
  });

  it('使用 Fixture', () => {
    cy.intercept('GET', '/api/users', { fixture: 'users.json' });
    cy.visit('/users');
  });

  it('动态响应', () => {
    cy.intercept('POST', '/api/users', (req) => {
      req.reply({
        statusCode: 201,
        body: {
          id: 999,
          ...req.body
        }
      });
    });

    cy.visit('/users/new');
    cy.get('[data-cy="name"]').type('Charlie');
    cy.get('[data-cy="submit"]').click();
  });
});
```

## 可视化回归测试

### Playwright 截图对比
```typescript
test('页面截图对比', async ({ page }) => {
  await page.goto('/');

  // 全页面截图
  await expect(page).toHaveScreenshot('homepage.png');

  // 元素截图
  await expect(page.locator('.header')).toHaveScreenshot('header.png');

  // 自定义配置
  await expect(page).toHaveScreenshot('homepage-full.png', {
    fullPage: true,
    mask: [page.locator('.dynamic-content')], // 遮罩动态内容
  });
});

test('跨浏览器截图', async ({ page, browserName }) => {
  await page.goto('/');
  await expect(page).toHaveScreenshot(`homepage-${browserName}.png`);
});
```

### Percy 集成
```typescript
// Playwright + Percy
import { test } from '@playwright/test';
import percySnapshot from '@percy/playwright';

test('Percy 可视化测试', async ({ page }) => {
  await page.goto('/');

  // 拍摄快照
  await percySnapshot(page, 'Homepage');

  // 交互后再拍摄
  await page.click('[data-testid="menu"]');
  await percySnapshot(page, 'Homepage - Menu Open');
});
```

```javascript
// Cypress + Percy
describe('可视化回归', () => {
  it('首页快照', () => {
    cy.visit('/');
    cy.percySnapshot('Homepage');
  });

  it('响应式快照', () => {
    cy.visit('/');
    cy.percySnapshot('Homepage Desktop', {
      widths: [1280, 1920]
    });

    cy.viewport('iphone-x');
    cy.percySnapshot('Homepage Mobile');
  });
});
```

### Chromatic (Storybook)
```javascript
// .storybook/main.js
module.exports = {
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx)'],
  addons: ['@storybook/addon-essentials'],
};

// Button.stories.tsx
export default {
  title: 'Components/Button',
  component: Button,
};

export const Primary = () => <Button variant="primary">Click me</Button>;
export const Secondary = () => <Button variant="secondary">Click me</Button>;

// package.json
{
  "scripts": {
    "chromatic": "chromatic --project-token=<token>"
  }
}
```

## 跨浏览器测试

### Playwright 多浏览器
```typescript
// playwright.config.ts
export default defineConfig({
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
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 13'] },
    },
  ],
});

// 运行特定浏览器
// npx playwright test --project=firefox
```

### 设备模拟
```typescript
test('移动端测试', async ({ page }) => {
  await page.goto('/');

  // 验证移动端布局
  const menu = page.locator('.mobile-menu');
  await expect(menu).toBeVisible();

  // 触摸操作
  await page.locator('.swipeable').swipe({ direction: 'left' });
});

test('平板测试', async ({ browser }) => {
  const context = await browser.newContext({
    ...devices['iPad Pro'],
  });

  const page = await context.newPage();
  await page.goto('/');
});
```

## 文件上传与下载

### Playwright 文件操作
```typescript
test('文件上传', async ({ page }) => {
  await page.goto('/upload');

  // 单文件上传
  await page.setInputFiles('input[type="file"]', 'path/to/file.pdf');

  // 多文件上传
  await page.setInputFiles('input[type="file"]', [
    'file1.jpg',
    'file2.jpg'
  ]);

  // 从 Buffer 上传
  await page.setInputFiles('input[type="file"]', {
    name: 'test.txt',
    mimeType: 'text/plain',
    buffer: Buffer.from('file content')
  });
});

test('文件下载', async ({ page }) => {
  const downloadPromise = page.waitForEvent('download');

  await page.click('a[download]');

  const download = await downloadPromise;
  const path = await download.path();

  // 验证文件
  expect(download.suggestedFilename()).toBe('report.pdf');
});
```

### Cypress 文件操作
```javascript
describe('文件操作', () => {
  it('文件上传', () => {
    cy.visit('/upload');

    // 需要 cypress-file-upload 插件
    cy.get('input[type="file"]').attachFile('example.json');

    cy.contains('上传成功').should('be.visible');
  });

  it('文件下载', () => {
    cy.visit('/download');

    cy.get('a[download]').click();

    // 验证下载
    cy.readFile('cypress/downloads/report.pdf').should('exist');
  });
});
```

## 认证与状态管理

### Playwright 认证
```typescript
// global-setup.ts
async function globalSetup() {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto('/login');
  await page.fill('[name="username"]', 'alice');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  // 保存认证状态
  await page.context().storageState({ path: 'auth.json' });
  await browser.close();
}

// playwright.config.ts
export default defineConfig({
  globalSetup: require.resolve('./global-setup'),
  use: {
    storageState: 'auth.json',
  },
});

// 测试自动使用已登录状态
test('访问受保护页面', async ({ page }) => {
  await page.goto('/dashboard'); // 已登录
});
```

### Cypress Session
```javascript
// cypress/support/commands.js
Cypress.Commands.add('login', (username, password) => {
  cy.session([username, password], () => {
    cy.visit('/login');
    cy.get('[data-cy="username"]').type(username);
    cy.get('[data-cy="password"]').type(password);
    cy.get('[data-cy="submit"]').click();
    cy.url().should('include', '/dashboard');
  });
});

// 测试中使用
describe('Dashboard', () => {
  beforeEach(() => {
    cy.login('alice', 'password123');
    cy.visit('/dashboard');
  });

  it('显示用户信息', () => {
    cy.contains('Alice').should('be.visible');
  });
});
```

## CI/CD 集成

### GitHub Actions - Playwright
```yaml
name: Playwright Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Run tests
        run: npx playwright test

      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
```

### GitHub Actions - Cypress
```yaml
name: Cypress Tests

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Cypress run
        uses: cypress-io/github-action@v5
        with:
          start: npm start
          wait-on: 'http://localhost:3000'
          browser: chrome

      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: cypress-screenshots
          path: cypress/screenshots

      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: cypress-videos
          path: cypress/videos
```

### Docker 运行
```dockerfile
# Playwright Dockerfile
FROM mcr.microsoft.com/playwright:v1.40.0-focal

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

CMD ["npx", "playwright", "test"]
```

```yaml
# docker-compose.yml
services:
  e2e:
    build: .
    environment:
      - CI=true
    volumes:
      - ./playwright-report:/app/playwright-report
```

## 调试技巧

### Playwright 调试
```typescript
// 调试模式
test('调试测试', async ({ page }) => {
  await page.goto('/');

  // 暂停执行
  await page.pause();

  // 慢速执行
  await page.click('button', { delay: 1000 });

  // 打印日志
  console.log(await page.title());

  // 截图
  await page.screenshot({ path: 'debug.png' });
});

// 命令行调试
// npx playwright test --debug
// npx playwright test --headed --slowMo=1000
```

### Cypress 调试
```javascript
describe('调试', () => {
  it('调试测试', () => {
    cy.visit('/');

    // 暂停
    cy.pause();

    // 打印日志
    cy.get('.user').then($el => {
      console.log($el.text());
    });

    // 调试命令
    cy.get('.user').debug();

    // 截图
    cy.screenshot('debug');
  });
});
```

## 最佳实践

### 选择器优先级
```
1. data-testid (推荐)
2. role + accessible name
3. 稳定的 class/id
4. 文本内容 (谨慎)
5. CSS 选择器 (避免)
6. XPath (避免)
```

### 测试独立性
```typescript
// ❌ 测试依赖
test('创建用户', async ({ page }) => {
  // 创建用户
});

test('编辑用户', async ({ page }) => {
  // 依赖上一个测试
});

// ✅ 独立测试
test('编辑用户', async ({ page }) => {
  // 通过 API 准备数据
  await request.post('/api/users', { data: testUser });

  // 执行测试
  await page.goto(`/users/${testUser.id}/edit`);
});
```

### 减少等待时间
```typescript
// ❌ 固定等待
await page.waitForTimeout(5000);

// ✅ 智能等待
await page.waitForSelector('.loaded');
await page.waitForLoadState('networkidle');
```

## 工具清单

| 工具 | 用途 | 特点 |
|------|------|------|
| Playwright | E2E 测试 | 多浏览器、强大 API |
| Cypress | E2E 测试 | 优秀调试体验 |
| Selenium | E2E 测试 | 老牌、多语言 |
| Percy | 可视化回归 | 云端对比 |
| Chromatic | Storybook 可视化 | 组件级测试 |
| Puppeteer | 浏览器自动化 | Chrome DevTools |

---
