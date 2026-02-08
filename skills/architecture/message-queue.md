---
name: message-queue
description: 消息队列秘典。Kafka、RabbitMQ、Redis Streams、事件驱动架构。当用户提到消息队列、Kafka、RabbitMQ、事件驱动、CQRS、Saga时路由到此。
---

# 🏗 阵法秘典 · 消息队列


## 核心概念

```
Producer → Broker → Consumer
  发送       存储       消费
  
模式:
  点对点 (Queue):  1 Producer → 1 Consumer
  发布订阅 (Topic): 1 Producer → N Consumers
```

| 概念 | 含义 | 类比 |
|------|------|------|
| Producer | 消息生产者 | 发令者 |
| Consumer | 消息消费者 | 执行者 |
| Broker | 消息中间件 | 传令阵 |
| Topic/Queue | 消息通道 | 传音符 |
| Partition | 分区（并行单元） | 阵眼 |
| Offset | 消费位置 | 修行进度 |

---

## Kafka

### 架构

```
Producer ──→ Broker Cluster ──→ Consumer Group
               │
          ┌────┴────┐
          │ Topic-A  │
          │ P0 P1 P2 │  (3 Partitions)
          └──────────┘
          
Replication: Leader + Followers
ZooKeeper/KRaft: 元数据管理
```

### 生产者

```python
from confluent_kafka import Producer

conf = {
    'bootstrap.servers': 'kafka:9092',
    'acks': 'all',                    # 等待所有副本确认
    'retries': 3,
    'retry.backoff.ms': 1000,
    'enable.idempotence': True,       # 幂等生产者
    'linger.ms': 5,                   # 批量发送延迟
    'batch.size': 16384,              # 批量大小
    'compression.type': 'snappy',     # 压缩
}

producer = Producer(conf)

def delivery_report(err, msg):
    if err:
        print(f"Delivery failed: {err}")

producer.produce(
    topic='orders',
    key=order_id.encode(),    # 相同 key → 相同 partition → 有序
    value=json.dumps(order).encode(),
    callback=delivery_report
)
producer.flush()
```

### 消费者

```python
from confluent_kafka import Consumer

conf = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'order-processor',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,      # 手动提交
    'max.poll.interval.ms': 300000,
}

consumer = Consumer(conf)
consumer.subscribe(['orders'])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            handle_error(msg.error())
            continue
        
        process_message(msg.value())
        consumer.commit(asynchronous=False)  # 处理成功后提交
finally:
    consumer.close()
```

### Kafka 关键配置

```yaml
Broker:
  num.partitions: 6                # 默认分区数
  default.replication.factor: 3    # 副本数
  min.insync.replicas: 2           # 最小同步副本
  log.retention.hours: 168         # 保留 7 天
  log.segment.bytes: 1073741824    # 1GB 段文件

Topic 设计:
  分区数 = max(生产吞吐/单分区写入能力, 消费者数)
  副本数 = 3 (生产环境)
  Key 选择: 业务ID (保证同一实体有序)
```

---

## RabbitMQ

### Exchange 类型

| 类型 | 路由规则 | 适用场景 |
|------|----------|----------|
| Direct | 精确匹配 routing key | 点对点 |
| Fanout | 广播到所有绑定队列 | 发布订阅 |
| Topic | 通配符匹配 routing key | 灵活路由 |
| Headers | 匹配消息头 | 复杂路由 |

```
Producer → Exchange → Binding → Queue → Consumer
              │
         routing_key 匹配
```

### 可靠性保证

```yaml
生产者:
  - Publisher Confirms (确认模式)
  - 持久化消息 (delivery_mode=2)
  - 事务模式 (性能差，不推荐)

Broker:
  - 持久化队列 (durable=True)
  - 镜像队列 / Quorum Queue
  - 磁盘持久化

消费者:
  - 手动 ACK (auto_ack=False)
  - 预取限制 (prefetch_count)
  - 死信队列 (DLX) 处理失败消息
```

### 死信队列 (DLQ)

```
正常队列 ──(消费失败/TTL过期/队列满)──→ 死信交换机 → 死信队列
                                                        │
                                              人工处理 / 重试
```

---

## Redis Streams

```bash
# 生产
XADD orders * user_id "123" amount "99.99"

# 消费组
XGROUP CREATE orders order-group $ MKSTREAM
XREADGROUP GROUP order-group consumer-1 COUNT 10 BLOCK 5000 STREAMS orders >

# 确认
XACK orders order-group <message-id>

# 查看待处理
XPENDING orders order-group
```

| 特性 | 适用 | 不适用 |
|------|------|--------|
| 轻量级 | 中小规模、低延迟 | 海量数据持久化 |
| 消费组 | 多消费者并行 | 复杂路由 |
| 内存存储 | 实时处理 | 长期存储 |

---

## 事件驱动架构

### Event Sourcing

```
传统: 只存最终状态
  Account { balance: 100 }

Event Sourcing: 存储所有事件
  AccountCreated { initial: 0 }
  MoneyDeposited { amount: 200 }
  MoneyWithdrawn { amount: 100 }
  → 重放得到 balance: 100
```

### CQRS (Command Query Responsibility Segregation)

```
Command (写) ──→ Write Model ──→ Event Store
                                    │
                              Event Bus
                                    │
Query (读) ←── Read Model ←── Projection
```

### Saga 模式

```
分布式事务编排:

Choreography (编舞):
  Order → Payment → Inventory → Shipping
    每个服务监听事件，自主决策

Orchestration (编排):
  Saga Orchestrator
    ├→ Order Service: 创建订单
    ├→ Payment Service: 扣款
    ├→ Inventory Service: 扣库存
    └→ Shipping Service: 发货
    
  失败补偿:
    Shipping失败 → 补偿Inventory → 补偿Payment → 补偿Order
```

---

## 选型对比

| 维度 | Kafka | RabbitMQ | Redis Streams |
|------|-------|----------|---------------|
| 吞吐量 | 极高 (百万/s) | 高 (万/s) | 高 (十万/s) |
| 延迟 | ms 级 | μs-ms 级 | μs 级 |
| 持久化 | 磁盘 | 磁盘/内存 | 内存+AOF |
| 消息顺序 | 分区内有序 | 队列内有序 | 流内有序 |
| 消息回溯 | ✅ 支持 | ❌ 不支持 | ✅ 支持 |
| 协议 | 自有协议 | AMQP | Redis协议 |
| 适用 | 大数据/日志/流处理 | 业务消息/RPC | 轻量级实时 |

### 选型决策树

```
需要消息回溯？
  ├─ 是 → Kafka / Redis Streams
  └─ 否 → 需要复杂路由？
       ├─ 是 → RabbitMQ
       └─ 否 → 吞吐量要求？
            ├─ 极高 (>10万/s) → Kafka
            ├─ 中等 → RabbitMQ
            └─ 轻量 → Redis Streams
```

---

## 常见问题

### 消息丢失

```yaml
防丢三板斧:
  生产端: acks=all + retries + 幂等
  Broker: replication + 持久化 + min.insync.replicas
  消费端: 手动提交 + 处理后确认
```

### 消息重复

```yaml
幂等处理:
  - 数据库唯一约束 (message_id)
  - Redis SETNX 去重
  - 业务层幂等设计 (状态机)
```

### 消息积压

```yaml
应急:
  - 增加消费者实例
  - 临时扩大分区 (Kafka)
  - 跳过非关键消息

根治:
  - 优化消费者处理速度
  - 合理设置分区数
  - 监控消费 lag 告警
```

---

## 最佳实践

```yaml
设计:
  - 消息体尽量小，大数据用引用
  - 消息必须包含唯一ID和时间戳
  - 定义清晰的消息 Schema (Avro/Protobuf)
  - 版本兼容 (向后兼容)

运维:
  - 监控消费 lag
  - 死信队列告警
  - 定期清理过期消息
  - 容量规划 (磁盘/内存)

安全:
  - TLS 加密传输
  - SASL 认证
  - ACL 授权
  - 审计日志
```

