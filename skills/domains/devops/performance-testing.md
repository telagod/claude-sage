---
name: performance-testing
description: 性能测试。k6、JMeter、Gatling、负载测试、压力测试、浸泡测试、性能指标分析。当用户提到性能测试、k6、JMeter、负载测试、压力测试、基准测试时使用。
---

# ⚡ 性能测试 · Performance Testing

## 性能测试类型

```
负载测试 (Load Testing)
  └─ 验证系统在预期负载下的表现

压力测试 (Stress Testing)
  └─ 找到系统的极限和崩溃点

浸泡测试 (Soak Testing)
  └─ 长时间运行检测内存泄漏

峰值测试 (Spike Testing)
  └─ 突发流量下的系统表现

容量测试 (Capacity Testing)
  └─ 确定系统最大容量
```

### 测试场景对比
| 类型 | 用户数 | 持续时间 | 目标 |
|------|--------|----------|------|
| 负载测试 | 预期峰值 | 30分钟-2小时 | 验证性能指标 |
| 压力测试 | 超出峰值 | 1-3小时 | 找到崩溃点 |
| 浸泡测试 | 正常负载 | 8-72小时 | 检测内存泄漏 |
| 峰值测试 | 瞬间激增 | 短时间 | 测试弹性 |

## k6 基础

### 安装
```bash
# macOS
brew install k6

# Linux
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# Docker
docker run --rm -i grafana/k6 run - <script.js
```

### 基础脚本
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,        // 虚拟用户数
  duration: '30s', // 持续时间
};

export default function () {
  const res = http.get('https://api.example.com/users');

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
```

### 运行测试
```bash
# 基础运行
k6 run script.js

# 指定参数
k6 run --vus 100 --duration 5m script.js

# 输出结果
k6 run --out json=results.json script.js
k6 run --out influxdb=http://localhost:8086/k6 script.js
```

## k6 高级场景

### 阶梯式负载
```javascript
export const options = {
  stages: [
    { duration: '2m', target: 100 },  // 2分钟爬升到100用户
    { duration: '5m', target: 100 },  // 保持100用户5分钟
    { duration: '2m', target: 200 },  // 爬升到200用户
    { duration: '5m', target: 200 },  // 保持200用户
    { duration: '2m', target: 0 },    // 降到0
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95%请求<500ms
    http_req_failed: ['rate<0.01'],   // 错误率<1%
  },
};
```

### 压力测试
```javascript
export const options = {
  stages: [
    { duration: '5m', target: 100 },
    { duration: '10m', target: 100 },
    { duration: '5m', target: 200 },
    { duration: '10m', target: 200 },
    { duration: '5m', target: 300 },
    { duration: '10m', target: 300 },
    { duration: '5m', target: 400 },
    { duration: '10m', target: 400 },
    { duration: '5m', target: 0 },
  ],
};
```

### 峰值测试
```javascript
export const options = {
  stages: [
    { duration: '10s', target: 100 },  // 正常负载
    { duration: '1m', target: 100 },
    { duration: '10s', target: 1400 }, // 突然激增
    { duration: '3m', target: 1400 },
    { duration: '10s', target: 100 },  // 恢复正常
    { duration: '3m', target: 100 },
    { duration: '10s', target: 0 },
  ],
};
```

### 浸泡测试
```javascript
export const options = {
  stages: [
    { duration: '5m', target: 100 },   // 爬升
    { duration: '8h', target: 100 },   // 保持8小时
    { duration: '5m', target: 0 },     // 降低
  ],
};
```

## k6 实战示例

### 登录流程测试
```javascript
import http from 'k6/http';
import { check, group, sleep } from 'k6';

export const options = {
  vus: 50,
  duration: '5m',
  thresholds: {
    'http_req_duration{name:login}': ['p(95)<1000'],
    'http_req_duration{name:dashboard}': ['p(95)<500'],
  },
};

export default function () {
  group('用户登录流程', () => {
    // 1. 访问登录页
    let res = http.get('https://example.com/login');
    check(res, { 'login page loaded': (r) => r.status === 200 });

    // 2. 提交登录
    res = http.post('https://example.com/api/login', {
      username: 'testuser',
      password: 'password123',
    }, {
      tags: { name: 'login' },
    });

    check(res, {
      'login successful': (r) => r.status === 200,
      'token received': (r) => r.json('token') !== undefined,
    });

    const token = res.json('token');

    // 3. 访问受保护页面
    res = http.get('https://example.com/dashboard', {
      headers: { Authorization: `Bearer ${token}` },
      tags: { name: 'dashboard' },
    });

    check(res, { 'dashboard loaded': (r) => r.status === 200 });

    sleep(1);
  });
}
```

### API 批量测试
```javascript
import http from 'k6/http';
import { check } from 'k6';

export default function () {
  const requests = [
    ['GET', 'https://api.example.com/users'],
    ['GET', 'https://api.example.com/products'],
    ['GET', 'https://api.example.com/orders'],
  ];

  const responses = http.batch(requests.map(([method, url]) => ({
    method,
    url,
  })));

  responses.forEach((res, i) => {
    check(res, {
      [`${requests[i][1]} status 200`]: (r) => r.status === 200,
    });
  });
}
```

### 文件上传测试
```javascript
import http from 'k6/http';
import { check } from 'k6';

const binFile = open('./test-file.pdf', 'b');

export default function () {
  const data = {
    file: http.file(binFile, 'test-file.pdf'),
    description: 'Test upload',
  };

  const res = http.post('https://api.example.com/upload', data);

  check(res, {
    'upload successful': (r) => r.status === 201,
  });
}
```

### WebSocket 测试
```javascript
import ws from 'k6/ws';
import { check } from 'k6';

export default function () {
  const url = 'ws://example.com/ws';

  const res = ws.connect(url, {}, function (socket) {
    socket.on('open', () => {
      console.log('connected');
      socket.send(JSON.stringify({ type: 'subscribe', channel: 'updates' }));
    });

    socket.on('message', (data) => {
      console.log('Message received:', data);
    });

    socket.on('close', () => console.log('disconnected'));

    socket.setTimeout(() => {
      socket.close();
    }, 10000);
  });

  check(res, { 'status is 101': (r) => r && r.status === 101 });
}
```

## JMeter 基础

### 安装
```bash
# 下载
wget https://dlcdn.apache.org//jmeter/binaries/apache-jmeter-5.6.2.tgz
tar -xzf apache-jmeter-5.6.2.tgz

# 运行 GUI
./apache-jmeter-5.6.2/bin/jmeter

# 命令行运行
./apache-jmeter-5.6.2/bin/jmeter -n -t test.jmx -l results.jtl
```

### 测试计划结构
```
Test Plan
├── Thread Group (线程组)
│   ├── HTTP Request (HTTP请求)
│   ├── HTTP Header Manager (请求头)
│   ├── Assertions (断言)
│   └── Listeners (监听器)
├── CSV Data Set Config (CSV数据)
└── Summary Report (汇总报告)
```

### HTTP 请求配置
```xml
<!-- JMeter 测试计划示例 -->
<HTTPSamplerProxy>
  <elementProp name="HTTPsampler.Arguments">
    <collectionProp name="Arguments.arguments">
      <elementProp name="username" elementType="HTTPArgument">
        <stringProp name="Argument.value">testuser</stringProp>
      </elementProp>
    </collectionProp>
  </elementProp>
  <stringProp name="HTTPSampler.domain">api.example.com</stringProp>
  <stringProp name="HTTPSampler.port">443</stringProp>
  <stringProp name="HTTPSampler.protocol">https</stringProp>
  <stringProp name="HTTPSampler.path">/api/login</stringProp>
  <stringProp name="HTTPSampler.method">POST</stringProp>
</HTTPSamplerProxy>
```

### 线程组配置
```
Number of Threads (users): 100
Ramp-up period (seconds): 60
Loop Count: 10

实际含义：
- 100个并发用户
- 60秒内逐步启动
- 每个用户执行10次
- 总请求数：100 * 10 = 1000
```

### 断言配置
```xml
<ResponseAssertion>
  <collectionProp name="Asserion.test_strings">
    <stringProp name="49586">200</stringProp>
  </collectionProp>
  <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
  <stringProp name="Assertion.assume_success">false</stringProp>
  <intProp name="Assertion.test_type">8</intProp>
</ResponseAssertion>
```

## JMeter 高级功能

### CSV 参数化
```csv
# users.csv
username,password
user1,pass1
user2,pass2
user3,pass3
```

```xml
<CSVDataSet>
  <stringProp name="filename">users.csv</stringProp>
  <stringProp name="variableNames">username,password</stringProp>
  <boolProp name="recycle">true</boolProp>
  <boolProp name="stopThread">false</boolProp>
</CSVDataSet>

<!-- 使用变量 -->
<stringProp name="Argument.value">${username}</stringProp>
```

### 正则提取器
```xml
<RegexExtractor>
  <stringProp name="RegexExtractor.refname">token</stringProp>
  <stringProp name="RegexExtractor.regex">"token":"([^"]+)"</stringProp>
  <stringProp name="RegexExtractor.template">$1$</stringProp>
  <stringProp name="RegexExtractor.default">NOT_FOUND</stringProp>
  <intProp name="RegexExtractor.match_number">1</intProp>
</RegexExtractor>

<!-- 后续请求使用 -->
<stringProp name="Header.value">Bearer ${token}</stringProp>
```

### BeanShell 脚本
```java
// 前置处理器
import java.util.Date;
import java.text.SimpleDateFormat;

SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
String timestamp = sdf.format(new Date());
vars.put("timestamp", timestamp);

// 后置处理器
String response = prev.getResponseDataAsString();
log.info("Response: " + response);

if (prev.getResponseCode().equals("200")) {
    vars.put("status", "success");
} else {
    vars.put("status", "failed");
}
```

## 性能指标分析

### 关键指标
```
响应时间 (Response Time)
├── 平均响应时间 (Average)
├── 中位数 (Median/P50)
├── 90分位 (P90)
├── 95分位 (P95)
└── 99分位 (P99)

吞吐量 (Throughput)
├── 请求/秒 (RPS)
├── 事务/秒 (TPS)
└── 数据传输速率 (MB/s)

错误率 (Error Rate)
├── HTTP错误 (4xx/5xx)
├── 超时错误
└── 连接错误

并发用户数 (Concurrent Users)
└── 活跃用户数
```

### 指标阈值示例
```javascript
// k6 阈值配置
export const options = {
  thresholds: {
    // 响应时间
    'http_req_duration': ['p(95)<500', 'p(99)<1000'],

    // 错误率
    'http_req_failed': ['rate<0.01'],

    // 吞吐量
    'http_reqs': ['rate>100'],

    // 特定请求
    'http_req_duration{name:login}': ['p(95)<1000'],
    'http_req_duration{name:api}': ['p(95)<200'],
  },
};
```

### 性能基准
| 场景 | P95响应时间 | 错误率 | 吞吐量 |
|------|-------------|--------|--------|
| API查询 | <200ms | <0.1% | >1000 RPS |
| API写入 | <500ms | <0.5% | >500 RPS |
| 页面加载 | <2s | <1% | >100 RPS |
| 文件上传 | <5s | <2% | >50 RPS |

## Gatling 示例

### 基础脚本
```scala
import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class BasicSimulation extends Simulation {

  val httpProtocol = http
    .baseUrl("https://api.example.com")
    .acceptHeader("application/json")
    .userAgentHeader("Gatling")

  val scn = scenario("Basic Load Test")
    .exec(
      http("Get Users")
        .get("/users")
        .check(status.is(200))
    )
    .pause(1)

  setUp(
    scn.inject(
      rampUsers(100) during (60 seconds)
    )
  ).protocols(httpProtocol)
}
```

### 复杂场景
```scala
class AdvancedSimulation extends Simulation {

  val httpProtocol = http.baseUrl("https://api.example.com")

  val login = exec(
    http("Login")
      .post("/api/login")
      .body(StringBody("""{"username":"${username}","password":"${password}"}"""))
      .check(jsonPath("$.token").saveAs("token"))
  )

  val browse = exec(
    http("Get Dashboard")
      .get("/dashboard")
      .header("Authorization", "Bearer ${token}")
  )

  val scn = scenario("User Journey")
    .feed(csv("users.csv").circular)
    .exec(login)
    .pause(2)
    .exec(browse)

  setUp(
    scn.inject(
      atOnceUsers(10),
      rampUsers(50) during (30 seconds),
      constantUsersPerSec(20) during (1 minute)
    )
  ).protocols(httpProtocol)
}
```

## 性能监控集成

### Prometheus + Grafana
```yaml
# k6 输出到 Prometheus
export const options = {
  ext: {
    loadimpact: {
      projectID: 123456,
      name: "Performance Test"
    }
  }
};

# 或使用 xk6-output-prometheus-remote
K6_PROMETHEUS_REMOTE_URL=http://localhost:9090/api/v1/write k6 run script.js
```

### InfluxDB 集成
```bash
# 启动 InfluxDB
docker run -d -p 8086:8086 influxdb:1.8

# k6 输出到 InfluxDB
k6 run --out influxdb=http://localhost:8086/k6 script.js
```

### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "k6 Performance Dashboard",
    "panels": [
      {
        "title": "Response Time",
        "targets": [
          {
            "measurement": "http_req_duration",
            "select": [["value", "mean"]]
          }
        ]
      },
      {
        "title": "Throughput",
        "targets": [
          {
            "measurement": "http_reqs",
            "select": [["count", "sum"]]
          }
        ]
      }
    ]
  }
}
```

## CI/CD 集成

### GitHub Actions
```yaml
name: Performance Test

on:
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨2点
  workflow_dispatch:

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run k6 test
        uses: grafana/k6-action@v0.3.0
        with:
          filename: tests/performance.js
          flags: --out json=results.json

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: k6-results
          path: results.json

      - name: Check thresholds
        run: |
          if grep -q '"thresholds".*"failed":true' results.json; then
            echo "Performance thresholds failed"
            exit 1
          fi
```

### GitLab CI
```yaml
performance:
  image: grafana/k6:latest
  stage: test
  script:
    - k6 run --out json=results.json tests/performance.js
  artifacts:
    paths:
      - results.json
    reports:
      performance: results.json
  only:
    - schedules
```

## 性能测试最佳实践

### 测试环境
```yaml
要求:
  - 独立环境，避免干扰
  - 配置与生产环境一致
  - 稳定的网络环境
  - 充足的资源（CPU/内存/带宽）

避免:
  - 在生产环境测试
  - 共享测试环境
  - 资源不足的环境
```

### 测试数据
```javascript
// ✅ 使用真实数据分布
const users = [
  { type: 'light', weight: 70 },   // 70%轻度用户
  { type: 'medium', weight: 20 },  // 20%中度用户
  { type: 'heavy', weight: 10 },   // 10%重度用户
];

// ✅ 数据隔离
const userId = `user_${__VU}_${__ITER}`;

// ✅ 清理测试数据
export function teardown(data) {
  // 清理逻辑
}
```

### 渐进式测试
```
1. 基准测试 (Baseline)
   └─ 单用户，建立基准

2. 负载测试 (Load)
   └─ 预期负载，验证性能

3. 压力测试 (Stress)
   └─ 超出负载，找到极限

4. 浸泡测试 (Soak)
   └─ 长时间运行，检测泄漏
```

### 结果分析
```javascript
// k6 自定义指标
import { Trend, Counter } from 'k6/metrics';

const loginDuration = new Trend('login_duration');
const loginErrors = new Counter('login_errors');

export default function () {
  const start = Date.now();
  const res = http.post('/login', payload);
  loginDuration.add(Date.now() - start);

  if (res.status !== 200) {
    loginErrors.add(1);
  }
}
```

## 工具对比

| 工具 | 语言 | 学习曲线 | 性能 | 云支持 | 开源 |
|------|------|----------|------|--------|------|
| k6 | JavaScript | 低 | 高 | ✅ | ✅ |
| JMeter | Java/GUI | 中 | 中 | ⚠️ | ✅ |
| Gatling | Scala | 高 | 高 | ✅ | ✅ |
| Locust | Python | 低 | 中 | ⚠️ | ✅ |
| Artillery | JavaScript | 低 | 中 | ✅ | ✅ |

### 选择建议
```
k6:
  ✅ 现代化、易用、性能好
  ✅ 适合 DevOps 集成
  ✅ 云原生支持

JMeter:
  ✅ 功能全面、插件丰富
  ✅ GUI 适合初学者
  ⚠️ 资源消耗较大

Gatling:
  ✅ 高性能、DSL 优雅
  ⚠️ 学习曲线陡峭
  ✅ 适合大规模测试

Locust:
  ✅ Python 生态
  ✅ 分布式支持
  ⚠️ 性能不如 k6/Gatling
```

---
