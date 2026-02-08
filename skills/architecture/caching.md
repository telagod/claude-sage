---
name: caching
description: 缓存策略秘典。缓存模式、Redis实践、三大问题、CDN、缓存一致性。当用户提到缓存、Redis、CDN、缓存穿透、缓存击穿、缓存雪崩时路由到此。
---

# 🏗 阵法秘典 · 缓存策略


## 缓存层次

```
客户端缓存 (浏览器/App)
    ↓ miss
CDN 缓存 (边缘节点)
    ↓ miss
网关缓存 (Nginx/API Gateway)
    ↓ miss
应用缓存 (本地内存/进程内)
    ↓ miss
分布式缓存 (Redis/Memcached)
    ↓ miss
数据库
```

| 层级 | 延迟 | 容量 | 一致性 |
|------|------|------|--------|
| L1 本地内存 | ~ns | MB级 | 进程内一致 |
| L2 分布式缓存 | ~ms | GB级 | 最终一致 |
| L3 CDN | ~10ms | TB级 | TTL控制 |
| DB | ~10-100ms | PB级 | 强一致 |

---

## 缓存模式

### Cache-Aside (旁路缓存)

```
读:
  1. 查缓存 → 命中 → 返回
  2. 未命中 → 查DB → 写入缓存 → 返回

写:
  1. 更新DB
  2. 删除缓存 (而非更新)
```

```python
def get_user(user_id: str) -> dict:
    # 1. 查缓存
    cached = redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    
    # 2. 查DB
    user = db.query("SELECT * FROM users WHERE id = %s", user_id)
    
    # 3. 写缓存
    redis.setex(f"user:{user_id}", 3600, json.dumps(user))
    return user

def update_user(user_id: str, data: dict):
    db.execute("UPDATE users SET ... WHERE id = %s", user_id)
    redis.delete(f"user:{user_id}")  # 删除而非更新
```

**适用**：通用场景，应用控制缓存逻辑。

### Read-Through (读穿透)

```
读:
  1. 查缓存 → 命中 → 返回
  2. 未命中 → 缓存层自动查DB → 写入缓存 → 返回

应用只与缓存交互，不直接访问DB。
```

**适用**：缓存中间件支持（如 Hibernate L2 Cache）。

### Write-Through (写穿透)

```
写:
  1. 写缓存
  2. 缓存层同步写DB
  3. 两者都成功才返回
```

**适用**：强一致性要求，写入不频繁。

### Write-Behind (异步写回)

```
写:
  1. 写缓存 → 立即返回
  2. 缓存层异步批量写DB

风险: 缓存宕机可能丢数据
```

**适用**：写入频繁、可容忍短暂不一致。

---

## Redis 实践

### 数据结构选型

| 结构 | 场景 | 示例 |
|------|------|------|
| String | 简单KV、计数器 | 用户信息、页面PV |
| Hash | 对象属性 | 用户Profile各字段 |
| List | 队列、最新列表 | 消息队列、最新动态 |
| Set | 去重、交集 | 标签、共同好友 |
| Sorted Set | 排行榜、延迟队列 | 积分排名、定时任务 |
| Stream | 消息流 | 事件日志 |

### 过期策略

```yaml
策略:
  惰性删除: 访问时检查是否过期
  定期删除: 每秒随机检查一批 key
  内存淘汰: 内存满时触发

淘汰策略 (maxmemory-policy):
  volatile-lru:   有过期时间的 key 中 LRU
  allkeys-lru:    所有 key 中 LRU (推荐)
  volatile-ttl:   有过期时间的 key 中 TTL 最小
  noeviction:     不淘汰，写入报错
```

### 分布式锁

```python
import redis
import uuid

def acquire_lock(conn: redis.Redis, lock_name: str, timeout: int = 10) -> str:
    token = str(uuid.uuid4())
    if conn.set(f"lock:{lock_name}", token, nx=True, ex=timeout):
        return token
    return None

def release_lock(conn: redis.Redis, lock_name: str, token: str) -> bool:
    # Lua 脚本保证原子性
    script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """
    return conn.eval(script, 1, f"lock:{lock_name}", token)
```

---

## 三大问题

### 缓存穿透 (Cache Penetration)

```
问题: 查询不存在的数据，每次都打到DB
攻击: 恶意请求大量不存在的ID

解决方案:
  1. 布隆过滤器 (Bloom Filter)
     请求 → 布隆过滤器 → 不存在则直接返回
     
  2. 缓存空值
     redis.setex(f"user:{user_id}", 300, "NULL")  # 短TTL
     
  3. 参数校验
     ID格式校验，拦截非法请求
```

### 缓存击穿 (Cache Breakdown)

```
问题: 热点key过期瞬间，大量请求打到DB

解决方案:
  1. 互斥锁 (Mutex)
     未命中 → 获取锁 → 查DB → 写缓存 → 释放锁
     其他请求等待或返回旧值
     
  2. 永不过期 + 异步更新
     逻辑过期: 缓存中存储过期时间，过期后异步刷新
     
  3. 热点预加载
     提前刷新即将过期的热点key
```

### 缓存雪崩 (Cache Avalanche)

```
问题: 大量key同时过期，或缓存服务宕机

解决方案:
  1. 过期时间加随机值
     ttl = base_ttl + random(0, 300)  # 打散过期时间
     
  2. 多级缓存
     L1(本地) + L2(Redis) → Redis挂了还有本地缓存
     
  3. 熔断降级
     缓存不可用时，限流 + 降级返回默认值
     
  4. Redis 高可用
     Sentinel / Cluster 模式
```

---

## CDN 缓存

### 缓存策略

```yaml
静态资源:
  Cache-Control: public, max-age=31536000, immutable
  文件名含 hash: app.a1b2c3.js

API 响应:
  Cache-Control: public, max-age=60, s-maxage=300
  Vary: Accept-Encoding, Authorization

不缓存:
  Cache-Control: no-store
  Set-Cookie 响应
```

### 缓存失效

```bash
# 主动失效
aws cloudfront create-invalidation \
  --distribution-id E1234 \
  --paths "/api/*" "/images/logo.png"

# 版本化 URL (推荐)
/static/app.v2.js  → 新版本新URL，无需失效
```

---

## 缓存一致性

### 最终一致性方案

```
方案1: 先更新DB，再删缓存 (推荐)
  问题: 删缓存失败 → 数据不一致
  解决: 重试机制 / 消息队列异步删除

方案2: 延迟双删
  1. 删缓存
  2. 更新DB
  3. 延迟N秒再删缓存 (覆盖并发读写)

方案3: 订阅 Binlog
  DB变更 → Binlog → Canal/Debezium → 删除/更新缓存
  最可靠，但架构复杂
```

### 一致性级别选择

| 级别 | 方案 | 延迟 | 复杂度 |
|------|------|------|--------|
| 强一致 | Write-Through | 高 | 中 |
| 最终一致 | Cache-Aside + 删除 | 低 | 低 |
| 最终一致(可靠) | Binlog 订阅 | 中 | 高 |

---

## 最佳实践

```yaml
设计:
  - 缓存 key 规范: {业务}:{实体}:{ID}
  - 合理 TTL: 热数据短(分钟)，冷数据长(小时)
  - 大 value 拆分: 单 value < 10KB
  - 避免 Big Key: 集合类型 < 5000 元素

运维:
  - 监控命中率 (目标 > 95%)
  - 监控内存使用和淘汰率
  - 慢查询日志分析
  - 定期清理无用 key

安全:
  - 禁止外网直连 Redis
  - 启用 AUTH 认证
  - 禁用危险命令 (KEYS/FLUSHALL)
  - 定期备份 (RDB + AOF)
```

