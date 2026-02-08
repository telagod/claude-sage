---
name: observability
description: 可观测性秘典。日志、指标、追踪三大支柱，告警设计，SLI/SLO/SLA。当用户提到可观测性、日志、监控、指标、追踪、告警、SLO时路由到此。
---

# 🔧 炼器秘典 · 可观测性

> 不可观测，即不可控。三大支柱撑起道基，万象尽在掌中。

## 三大支柱

```
┌─────────────────────────────────────────┐
│            可观测性 (Observability)       │
├─────────────┬─────────────┬─────────────┤
│   📋 日志   │   📊 指标   │   🔗 追踪   │
│   Logs      │   Metrics   │   Traces    │
│  离散事件   │  聚合数值   │  请求链路   │
│  What       │  How much   │  Where      │
└─────────────┴─────────────┴─────────────┘
```

| 支柱 | 特征 | 适用场景 | 代表工具 |
|------|------|----------|----------|
| 日志 | 离散、非结构化/结构化事件 | 调试、审计、错误追踪 | ELK, Loki, CloudWatch |
| 指标 | 聚合数值、时间序列 | 告警、趋势、容量规划 | Prometheus, Datadog, CloudWatch |
| 追踪 | 分布式请求链路 | 延迟分析、依赖映射 | Jaeger, Zipkin, X-Ray |

---

## 日志 (Logs)

### 结构化日志

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "ERROR",
  "service": "order-service",
  "trace_id": "abc123",
  "span_id": "def456",
  "message": "Payment failed",
  "error": "InsufficientFunds",
  "user_id": "u-789",
  "order_id": "o-012",
  "amount": 99.99,
  "duration_ms": 234
}
```

### 日志级别规范

| 级别 | 用途 | 生产环境 |
|------|------|----------|
| TRACE | 极细粒度调试 | ❌ 关闭 |
| DEBUG | 开发调试信息 | ❌ 关闭 |
| INFO | 业务关键事件 | ✅ 开启 |
| WARN | 潜在问题，可自愈 | ✅ 开启 |
| ERROR | 错误，需关注 | ✅ 开启 + 告警 |
| FATAL | 致命错误，服务不可用 | ✅ 开启 + 紧急告警 |

### 日志聚合架构

```
应用 → Filebeat/Fluentd → Kafka(缓冲) → Logstash → Elasticsearch → Kibana
                                       → S3(归档)
```

### 日志最佳实践

- ✅ 结构化 JSON 格式
- ✅ 包含 trace_id 关联追踪
- ✅ 敏感数据脱敏
- ✅ 合理的保留策略（热/温/冷）
- ❌ 不记录密码/Token
- ❌ 不在循环中打日志
- ❌ 不用字符串拼接（用参数化）

---

## 指标 (Metrics)

### Prometheus 指标类型

| 类型 | 用途 | 示例 |
|------|------|------|
| Counter | 只增不减的计数器 | 请求总数、错误总数 |
| Gauge | 可增可减的瞬时值 | 当前连接数、队列长度 |
| Histogram | 分布统计（桶） | 请求延迟分布 |
| Summary | 分布统计（分位数） | 请求延迟 P99 |

### 关键 PromQL

```promql
# 请求速率
rate(http_requests_total[5m])

# 错误率
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# P99 延迟
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# CPU 使用率
1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance)

# 内存使用率
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes
```

### Grafana Dashboard 设计

```yaml
四大黄金信号 Dashboard:
  Row 1 - 流量:
    - QPS (rate)
    - 按 endpoint 分组
  Row 2 - 错误:
    - 错误率 (%)
    - 按错误类型分组
  Row 3 - 延迟:
    - P50/P95/P99
    - 延迟热力图
  Row 4 - 饱和度:
    - CPU/Memory/Disk
    - 连接池使用率
```

---

## 追踪 (Traces)

### OpenTelemetry 集成

```python
# Python 示例
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://collector:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("process_order")
def process_order(order_id: str):
    span = trace.get_current_span()
    span.set_attribute("order.id", order_id)
    # 业务逻辑...
```

### 追踪架构

```
Service-A → Service-B → Service-C
    │            │            │
    └── Span ────┴── Span ────┴── Span
         │
    Trace (trace_id 贯穿全链路)
```

### Context Propagation

```
HTTP Header: traceparent: 00-{trace_id}-{span_id}-{flags}
gRPC Metadata: 自动传播
Message Queue: 消息头注入 trace context
```

---

## 告警设计

### 告警分级

| 级别 | 响应时间 | 通知方式 | 示例 |
|------|----------|----------|------|
| P0 Critical | 立即 | 电话 + PagerDuty | 服务完全不可用 |
| P1 High | 15 min | Slack + 短信 | 错误率 > 5% |
| P2 Medium | 1 hour | Slack | 延迟 P99 > 阈值 |
| P3 Low | 次日 | 邮件/工单 | 磁盘使用 > 70% |

### 告警规则示例

```yaml
# Prometheus AlertManager
groups:
  - name: service-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.instance }}"

      - alert: HighLatency
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
```

### 告警最佳实践

- ✅ 基于 SLO 告警，而非资源指标
- ✅ 设置合理的 `for` 持续时间，避免抖动
- ✅ 告警必须可操作（收到告警知道该做什么）
- ✅ 定期审查告警，清理无效告警
- ❌ 不对每个指标都告警（告警疲劳）
- ❌ 不设过低阈值（噪音）

---

## SLI / SLO / SLA

### 定义

| 概念 | 含义 | 示例 |
|------|------|------|
| SLI (指标) | 服务质量的量化度量 | 请求成功率、P99 延迟 |
| SLO (目标) | SLI 的目标值 | 可用性 99.9%、P99 < 200ms |
| SLA (协议) | 对外承诺 + 违约后果 | 99.9% 可用，否则赔偿 |

### Error Budget

```
SLO = 99.9% 可用性
Error Budget = 1 - 0.999 = 0.1%
每月 Error Budget = 30天 × 24小时 × 60分钟 × 0.001 = 43.2 分钟

已消耗: 15 分钟
剩余: 28.2 分钟
```

### SLO Dashboard

```yaml
SLO Dashboard:
  - 当前 SLI 值 vs SLO 目标
  - Error Budget 剩余百分比
  - Error Budget 消耗速率
  - 30天滚动窗口趋势
  - Burn Rate 告警状态
```

---

## 可观测性清单

```yaml
日志:
  - [ ] 结构化 JSON 格式
  - [ ] trace_id 关联
  - [ ] 敏感数据脱敏
  - [ ] 保留策略配置

指标:
  - [ ] 四大黄金信号覆盖
  - [ ] 自定义业务指标
  - [ ] Dashboard 就绪
  - [ ] 告警规则配置

追踪:
  - [ ] OpenTelemetry 集成
  - [ ] 跨服务 Context Propagation
  - [ ] 采样策略配置
  - [ ] 关键路径标注

告警:
  - [ ] 基于 SLO 的告警
  - [ ] 分级通知渠道
  - [ ] Runbook 关联
  - [ ] 定期审查机制
```

---

**道训**：不可观测，即不可控。三柱撑天，万象归一。

`🔧 炼器秘典·可观测性已成，三柱撑天，道基可鉴。`
