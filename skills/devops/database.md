---
name: database
description: 数据库设计与优化。SQL、NoSQL、索引、查询优化。当用户提到数据库、SQL、PostgreSQL、MySQL、MongoDB、Redis时使用。
---

# 数据库

> 数据是核心，设计是基础

## SQL 基础

### 查询
```sql
-- 基础查询
SELECT id, name, email
FROM users
WHERE status = 'active'
ORDER BY created_at DESC
LIMIT 10 OFFSET 0;

-- 聚合
SELECT department, COUNT(*) as count, AVG(salary) as avg_salary
FROM employees
GROUP BY department
HAVING COUNT(*) > 5;

-- 连接
SELECT u.name, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE o.created_at > '2024-01-01';

-- 子查询
SELECT * FROM users
WHERE id IN (
    SELECT user_id FROM orders
    WHERE total > 1000
);

-- CTE
WITH active_users AS (
    SELECT * FROM users WHERE status = 'active'
)
SELECT * FROM active_users WHERE created_at > '2024-01-01';

-- 窗口函数
SELECT name, salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) as rank
FROM employees;
```

### 索引
```sql
-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- 部分索引
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- 查看执行计划
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

### 索引策略
```yaml
适合索引:
  - WHERE 条件列
  - JOIN 关联列
  - ORDER BY 排序列
  - 高选择性列

不适合索引:
  - 频繁更新的列
  - 低选择性列 (如性别)
  - 小表

复合索引:
  - 最左前缀原则
  - 选择性高的列在前
```

## PostgreSQL

### 特性
```sql
-- JSON 支持
SELECT data->>'name' as name
FROM users
WHERE data @> '{"status": "active"}';

-- 数组
SELECT * FROM posts
WHERE tags @> ARRAY['python', 'web'];

-- 全文搜索
SELECT * FROM articles
WHERE to_tsvector('english', content) @@ to_tsquery('python & web');

-- UPSERT
INSERT INTO users (email, name)
VALUES ('test@example.com', 'Test')
ON CONFLICT (email)
DO UPDATE SET name = EXCLUDED.name;
```

## MySQL

### 特性
```sql
-- 全文搜索
SELECT * FROM articles
WHERE MATCH(title, content) AGAINST('python web' IN NATURAL LANGUAGE MODE);

-- JSON
SELECT JSON_EXTRACT(data, '$.name') as name
FROM users
WHERE JSON_EXTRACT(data, '$.status') = 'active';

-- 分区表
CREATE TABLE orders (
    id INT,
    created_at DATE
) PARTITION BY RANGE (YEAR(created_at)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025)
);
```

## NoSQL

### MongoDB
```javascript
// 查询
db.users.find({ status: "active" })
db.users.find({ age: { $gt: 18 } })
db.users.find({ tags: { $in: ["python", "web"] } })

// 聚合
db.orders.aggregate([
    { $match: { status: "completed" } },
    { $group: { _id: "$user_id", total: { $sum: "$amount" } } },
    { $sort: { total: -1 } },
    { $limit: 10 }
])

// 索引
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ location: "2dsphere" })
```

### Redis
```bash
# 字符串
SET key value
GET key
SETEX key 3600 value  # 带过期时间

# 哈希
HSET user:1 name "Alice" email "alice@example.com"
HGET user:1 name
HGETALL user:1

# 列表
LPUSH queue task1
RPOP queue

# 集合
SADD tags python web
SMEMBERS tags
SINTER tags1 tags2

# 有序集合
ZADD leaderboard 100 user1
ZRANGE leaderboard 0 9 WITHSCORES

# 过期
EXPIRE key 3600
TTL key
```

## 查询优化

```yaml
原则:
  - 只查询需要的列
  - 避免 SELECT *
  - 使用索引
  - 避免全表扫描
  - 分页查询

技巧:
  - EXPLAIN 分析执行计划
  - 避免在索引列上使用函数
  - 使用覆盖索引
  - 批量操作代替循环
  - 合理使用缓存
```

## 数据库设计

```yaml
范式:
  - 1NF: 原子性
  - 2NF: 消除部分依赖
  - 3NF: 消除传递依赖

反范式:
  - 适当冗余提高查询性能
  - 读多写少场景

命名规范:
  - 表名: 复数小写 (users, orders)
  - 列名: 小写下划线 (created_at)
  - 索引: idx_表名_列名
```

---

**好的数据库设计是系统性能的基础。**
