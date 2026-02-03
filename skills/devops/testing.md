---
name: testing
description: 软件测试。单元测试、集成测试、TDD、测试框架。当用户提到测试、单元测试、pytest、Jest、mock、TDD时使用。
---

# 软件测试

> 测试是质量的保障

## 测试金字塔

```
        /\
       /  \     E2E 测试 (少)
      /----\
     /      \   集成测试 (中)
    /--------\
   /          \ 单元测试 (多)
  --------------
```

## Python (pytest)

```python
import pytest
from myapp import calculate, UserService

# 基础测试
def test_add():
    assert calculate.add(1, 2) == 3

# 参数化
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add_params(a, b, expected):
    assert calculate.add(a, b) == expected

# Fixture
@pytest.fixture
def user_service():
    service = UserService()
    yield service
    service.cleanup()

def test_create_user(user_service):
    user = user_service.create("test")
    assert user.name == "test"

# Mock
from unittest.mock import Mock, patch

@patch('myapp.requests.get')
def test_fetch(mock_get):
    mock_get.return_value.json.return_value = {"id": 1}
    result = fetch_user(1)
    assert result["id"] == 1

# 异步测试
@pytest.mark.asyncio
async def test_async_fetch():
    result = await async_fetch()
    assert result is not None
```

### 运行命令
```bash
pytest                      # 运行所有
pytest test_file.py         # 指定文件
pytest -k "test_add"        # 匹配名称
pytest -v                   # 详细输出
pytest --cov=myapp          # 覆盖率
pytest -x                   # 失败即停
```

## JavaScript (Jest/Vitest)

```javascript
import { describe, it, expect, vi } from 'vitest';

// 基础测试
describe('add', () => {
  it('should add two numbers', () => {
    expect(add(1, 2)).toBe(3);
  });

  it.each([
    [1, 2, 3],
    [0, 0, 0],
    [-1, 1, 0],
  ])('add(%i, %i) = %i', (a, b, expected) => {
    expect(add(a, b)).toBe(expected);
  });
});

// Mock
vi.mock('./api', () => ({
  getUser: vi.fn().mockResolvedValue({ id: 1, name: 'test' })
}));

it('should fetch user', async () => {
  const user = await fetchUser(1);
  expect(user.name).toBe('test');
});

// Spy
const spy = vi.spyOn(console, 'log');
doSomething();
expect(spy).toHaveBeenCalledWith('message');
```

## Go (testing)

```go
package main

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestAdd(t *testing.T) {
    result := Add(1, 2)
    assert.Equal(t, 3, result)
}

// 表驱动测试
func TestAddTable(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 1, 2, 3},
        {"zero", 0, 0, 0},
        {"negative", -1, 1, 0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            assert.Equal(t, tt.expected, Add(tt.a, tt.b))
        })
    }
}

// Benchmark
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(1, 2)
    }
}
```

## 测试原则

```yaml
FIRST:
  - Fast: 快速执行
  - Independent: 相互独立
  - Repeatable: 可重复
  - Self-validating: 自验证
  - Timely: 及时编写

AAA:
  - Arrange: 准备数据
  - Act: 执行操作
  - Assert: 验证结果

原则:
  - 每个测试只验证一件事
  - 测试边界条件
  - 测试异常情况
  - 避免测试实现细节
```

## TDD 流程

```
红 → 绿 → 重构

1. 红: 写一个失败的测试
2. 绿: 写最少代码让测试通过
3. 重构: 优化代码，保持测试通过
```

---

**没有测试的代码是遗留代码。**
