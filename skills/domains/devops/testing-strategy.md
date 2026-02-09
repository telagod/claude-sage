---
name: testing-strategy
description: 测试策略与架构。测试金字塔、测试左移、契约测试、覆盖率策略、测试分层。当用户提到测试策略、测试金字塔、测试左移、契约测试、测试分层、测试覆盖率时使用。
---

# 🎯 测试金字塔 · Testing Strategy

## 测试金字塔 (Test Pyramid)

```
           /\
          /E2E\         10% - 慢、脆弱、昂贵
         /------\
        /  集成  \       20% - 中速、稳定
       /----------\
      /    单元    \     70% - 快、稳定、便宜
     /--------------\
```

### 层级比例
| 层级 | 占比 | 执行时间 | 成本 | 维护性 |
|------|------|----------|------|--------|
| 单元测试 | 70% | <1s | 低 | 高 |
| 集成测试 | 20% | 1-10s | 中 | 中 |
| E2E测试 | 10% | 10s-5m | 高 | 低 |

### 反模式：冰淇淋锥
```
     /--------------\
    /      E2E      \    大量 E2E - 慢、不稳定
   /----------------\
  /       集成       \   少量集成
 /--------------------\
/        单元          \ 极少单元 - 反模式！
```

## 测试左移 (Shift-Left Testing)

```
传统流程:
需求 → 开发 → 测试 → 部署
              ↑
            测试介入晚

左移流程:
需求 → 开发 → 部署
  ↓      ↓      ↓
 测试   测试   测试
  ↑
测试全程参与
```

### 左移实践
```yaml
# 需求阶段
- 可测试性评审
- 验收标准定义
- 测试用例设计

# 开发阶段
- TDD (测试驱动开发)
- 单元测试同步编写
- 代码审查包含测试

# 提交阶段
- Pre-commit Hook
- 本地测试必过
- 静态分析

# CI 阶段
- 自动化测试
- 覆盖率门禁
- 性能基准测试
```

## 契约测试 (Contract Testing)

### 消费者驱动契约 (CDC)
```
Provider API ←→ Contract ←→ Consumer
     ↓                          ↓
  验证契约                   验证契约
```

### Pact 示例
```javascript
// Consumer 端
const { Pact } = require('@pact-foundation/pact');

const provider = new Pact({
  consumer: 'UserService',
  provider: 'OrderService'
});

describe('Order API', () => {
  beforeAll(() => provider.setup());
  afterAll(() => provider.finalize());

  it('获取订单列表', async () => {
    await provider.addInteraction({
      state: '有3个订单',
      uponReceiving: '获取订单请求',
      withRequest: {
        method: 'GET',
        path: '/orders',
        headers: { Accept: 'application/json' }
      },
      willRespondWith: {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        body: [
          { id: 1, status: 'pending' },
          { id: 2, status: 'completed' }
        ]
      }
    });

    const response = await fetch('http://localhost:1234/orders');
    expect(response.status).toBe(200);
  });
});
```

### Provider 验证
```javascript
// Provider 端
const { Verifier } = require('@pact-foundation/pact');

new Verifier({
  provider: 'OrderService',
  providerBaseUrl: 'http://localhost:8080',
  pactUrls: ['./pacts/userservice-orderservice.json'],
  stateHandlers: {
    '有3个订单': async () => {
      // 准备测试数据
      await db.seed(['order1', 'order2', 'order3']);
    }
  }
}).verifyProvider();
```

### Spring Cloud Contract
```groovy
// Contract DSL
Contract.make {
    request {
        method 'GET'
        url '/api/users/1'
    }
    response {
        status 200
        body([
            id: 1,
            name: 'Alice',
            email: 'alice@example.com'
        ])
        headers {
            contentType(applicationJson())
        }
    }
}
```

```java
// Provider 测试
@SpringBootTest
@AutoConfigureStubRunner(
    ids = "com.example:user-service:+:stubs:8080",
    stubsMode = StubRunnerProperties.StubsMode.LOCAL
)
class ContractTest {
    @Test
    void shouldReturnUser() {
        ResponseEntity<User> response = restTemplate
            .getForEntity("http://localhost:8080/api/users/1", User.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody().getName()).isEqualTo("Alice");
    }
}
```

## 测试分层策略

### 单元测试
```python
# 纯函数测试
def test_calculate_discount():
    assert calculate_discount(100, 0.1) == 90
    assert calculate_discount(100, 0) == 100
    assert calculate_discount(0, 0.5) == 0

# Mock 外部依赖
from unittest.mock import Mock, patch

def test_user_service():
    mock_db = Mock()
    mock_db.find_user.return_value = {'id': 1, 'name': 'Alice'}

    service = UserService(mock_db)
    user = service.get_user(1)

    assert user['name'] == 'Alice'
    mock_db.find_user.assert_called_once_with(1)

# 参数化测试
import pytest

@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert input.upper() == expected
```

### 集成测试
```java
@SpringBootTest
@Testcontainers
class OrderServiceIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
        .withDatabaseName("testdb");

    @Autowired
    private OrderService orderService;

    @Test
    void shouldCreateOrder() {
        Order order = new Order("user123", List.of("item1", "item2"));
        Order saved = orderService.create(order);

        assertThat(saved.getId()).isNotNull();
        assertThat(saved.getStatus()).isEqualTo(OrderStatus.PENDING);
    }

    @Test
    void shouldHandleTransaction() {
        assertThrows(InsufficientStockException.class, () -> {
            orderService.createWithInsufficientStock();
        });

        // 验证事务回滚
        assertThat(orderRepository.count()).isEqualTo(0);
    }
}
```

### 组件测试
```typescript
// API 组件测试
import request from 'supertest';
import { app } from '../src/app';

describe('User API', () => {
  it('POST /users - 创建用户', async () => {
    const response = await request(app)
      .post('/users')
      .send({ name: 'Alice', email: 'alice@example.com' })
      .expect(201);

    expect(response.body).toMatchObject({
      name: 'Alice',
      email: 'alice@example.com'
    });
  });

  it('GET /users/:id - 获取用户', async () => {
    const response = await request(app)
      .get('/users/1')
      .expect(200);

    expect(response.body.id).toBe(1);
  });
});
```

## 测试覆盖率策略

### 覆盖率类型
```
行覆盖率 (Line Coverage)     - 代码行是否执行
分支覆盖率 (Branch Coverage)  - 条件分支是否覆盖
函数覆盖率 (Function Coverage) - 函数是否调用
语句覆盖率 (Statement Coverage) - 语句是否执行
```

### 覆盖率配置
```javascript
// Jest 配置
module.exports = {
  collectCoverage: true,
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    },
    './src/core/': {
      branches: 90,
      functions: 95,
      lines: 95,
      statements: 95
    }
  },
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/test/',
    '.*\\.config\\.js'
  ]
};
```

```python
# pytest-cov 配置
[tool.pytest.ini_options]
addopts = """
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
"""

[tool.coverage.run]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__init__.py"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:"
]
```

### 覆盖率门禁
```yaml
# GitHub Actions
- name: Test with coverage
  run: npm test -- --coverage

- name: Coverage check
  run: |
    COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
    if (( $(echo "$COVERAGE < 80" | bc -l) )); then
      echo "Coverage $COVERAGE% is below 80%"
      exit 1
    fi
```

## TDD (测试驱动开发)

### Red-Green-Refactor
```
1. Red   - 写失败的测试
2. Green - 写最少代码让测试通过
3. Refactor - 重构代码
```

### TDD 示例
```python
# 1. Red - 写测试
def test_fizzbuzz():
    assert fizzbuzz(3) == "Fizz"
    assert fizzbuzz(5) == "Buzz"
    assert fizzbuzz(15) == "FizzBuzz"
    assert fizzbuzz(7) == "7"

# 2. Green - 实现
def fizzbuzz(n):
    if n % 15 == 0:
        return "FizzBuzz"
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)

# 3. Refactor - 优化
def fizzbuzz(n):
    result = ""
    if n % 3 == 0:
        result += "Fizz"
    if n % 5 == 0:
        result += "Buzz"
    return result or str(n)
```

## BDD (行为驱动开发)

### Gherkin 语法
```gherkin
Feature: 用户登录
  作为一个用户
  我想要登录系统
  以便访问我的账户

  Scenario: 成功登录
    Given 用户已注册
    When 用户输入正确的用户名和密码
    Then 用户应该看到欢迎页面

  Scenario: 密码错误
    Given 用户已注册
    When 用户输入错误的密码
    Then 用户应该看到错误提示
```

### Cucumber 实现
```javascript
const { Given, When, Then } = require('@cucumber/cucumber');
const { expect } = require('chai');

Given('用户已注册', async function() {
  await this.db.createUser({
    username: 'alice',
    password: 'password123'
  });
});

When('用户输入正确的用户名和密码', async function() {
  this.response = await this.api.login('alice', 'password123');
});

Then('用户应该看到欢迎页面', function() {
  expect(this.response.status).to.equal(200);
  expect(this.response.body.message).to.include('欢迎');
});
```

## 测试数据管理

### Fixture 模式
```python
import pytest

@pytest.fixture
def sample_user():
    return {
        'id': 1,
        'name': 'Alice',
        'email': 'alice@example.com'
    }

@pytest.fixture
def db_session():
    session = create_session()
    yield session
    session.rollback()
    session.close()

def test_create_user(db_session, sample_user):
    user = User(**sample_user)
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
```

### Factory 模式
```javascript
// Factory Bot
const { Factory } = require('rosie');

Factory.define('user')
  .sequence('id')
  .attr('name', () => faker.name.findName())
  .attr('email', () => faker.internet.email())
  .attr('createdAt', () => new Date());

// 使用
const user = Factory.build('user');
const users = Factory.buildList('user', 10);
const savedUser = await Factory.create('user'); // 保存到数据库
```

### 测试数据隔离
```java
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class UserServiceTest {

    @BeforeEach
    void setUp() {
        // 每个测试前清理
        userRepository.deleteAll();
    }

    @Test
    @Transactional
    void testCreateUser() {
        // 测试结束自动回滚
    }

    @Test
    @Sql("/test-data/users.sql")
    void testWithSqlData() {
        // 使用 SQL 脚本准备数据
    }
}
```

## 测试隔离与并行

### 并行执行
```javascript
// Jest 并行配置
module.exports = {
  maxWorkers: '50%', // 使用 50% CPU
  testTimeout: 10000,
  bail: 1, // 首次失败即停止
};
```

```python
# pytest 并行
pytest -n auto  # 自动检测 CPU 核心数
pytest -n 4     # 使用 4 个进程
```

### 测试隔离
```typescript
describe('Order Service', () => {
  let service: OrderService;
  let mockDb: jest.Mocked<Database>;

  beforeEach(() => {
    // 每个测试独立实例
    mockDb = createMockDatabase();
    service = new OrderService(mockDb);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should create order', () => {
    // 测试逻辑
  });
});
```

## 快照测试

### Jest 快照
```javascript
test('renders correctly', () => {
  const tree = renderer.create(
    <UserProfile user={{ name: 'Alice', age: 30 }} />
  ).toJSON();

  expect(tree).toMatchSnapshot();
});

// 更新快照
// npm test -- -u
```

### API 响应快照
```python
def test_api_response(snapshot):
    response = client.get('/api/users/1')
    snapshot.assert_match(response.json(), 'user_response.json')
```

## 变异测试 (Mutation Testing)

### Stryker 配置
```javascript
// stryker.conf.js
module.exports = {
  mutate: ['src/**/*.ts', '!src/**/*.spec.ts'],
  testRunner: 'jest',
  reporters: ['html', 'clear-text', 'progress'],
  coverageAnalysis: 'perTest',
  thresholds: { high: 80, low: 60, break: 50 }
};
```

### 变异示例
```javascript
// 原始代码
function isAdult(age) {
  return age >= 18;
}

// 变异体
function isAdult(age) {
  return age > 18;  // >= 变为 >
}

// 如果测试没有覆盖边界值 18，变异体存活
// 说明测试不够充分
```

## 测试最佳实践

### AAA 模式
```python
def test_user_registration():
    # Arrange - 准备
    user_data = {'username': 'alice', 'email': 'alice@example.com'}

    # Act - 执行
    result = register_user(user_data)

    # Assert - 断言
    assert result.success is True
    assert result.user.username == 'alice'
```

### 测试命名
```javascript
// ❌ 不好
test('test1', () => {});

// ✅ 好
test('should return 404 when user not found', () => {});
test('should create order with valid items', () => {});
test('should throw error when stock insufficient', () => {});
```

### 单一职责
```python
# ❌ 测试多个功能
def test_user_operations():
    user = create_user()
    update_user(user)
    delete_user(user)

# ✅ 拆分测试
def test_create_user():
    user = create_user()
    assert user.id is not None

def test_update_user():
    user = create_user()
    updated = update_user(user, {'name': 'Bob'})
    assert updated.name == 'Bob'

def test_delete_user():
    user = create_user()
    delete_user(user)
    assert find_user(user.id) is None
```

## 工具清单

| 工具 | 用途 | 语言 |
|------|------|------|
| Jest | 单元/集成测试 | JavaScript |
| Pytest | 单元/集成测试 | Python |
| JUnit 5 | 单元/集成测试 | Java |
| Pact | 契约测试 | 多语言 |
| Testcontainers | 集成测试 | Java/Go/Python |
| Stryker | 变异测试 | JavaScript |
| Pitest | 变异测试 | Java |
| Faker | 测试数据生成 | 多语言 |

---
