---
name: performance
description: 性能优化秘典。性能分析方法论、Profiling、火焰图、基准测试、瓶颈优化。当用户提到性能、延迟、吞吐、Profiling、火焰图、基准测试时路由到此。
---

# 🔧 炼器秘典 · 性能优化


## 性能分析方法论

### USE 方法 (Utilization, Saturation, Errors)

对每个资源检查三个维度：

| 维度 | 含义 | 工具 |
|------|------|------|
| Utilization | 资源繁忙时间占比 | `top`, `vmstat`, `iostat` |
| Saturation | 排队等待的工作量 | `vmstat`(r列), `iostat`(avgqu-sz) |
| Errors | 错误事件计数 | `dmesg`, 应用日志 |

```bash
# CPU USE
mpstat -P ALL 1          # Utilization per core
vmstat 1                 # Saturation (r > CPU count)
dmesg | grep -i error    # Errors

# Memory USE
free -m                  # Utilization
vmstat 1 | awk '{print $3,$4}'  # Saturation (si/so > 0 = swapping)

# Disk USE
iostat -xz 1             # Utilization (%util), Saturation (avgqu-sz)

# Network USE
sar -n DEV 1             # Utilization
netstat -s | grep -i error  # Errors
```

### RED 方法 (Rate, Errors, Duration)

面向服务的性能指标：

| 维度 | 含义 | 示例 |
|------|------|------|
| Rate | 每秒请求数 | QPS/RPS |
| Errors | 每秒错误数 | 5xx/s |
| Duration | 请求延迟分布 | P50/P95/P99 |

```promql
# Prometheus PromQL 示例
rate(http_requests_total[5m])                    # Rate
rate(http_requests_total{status=~"5.."}[5m])     # Errors
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))  # P99
```

---

## Profiling 工具

### CPU Profiling

| 语言 | 工具 | 命令 |
|------|------|------|
| Python | cProfile / py-spy | `py-spy record -o profile.svg -- python app.py` |
| Go | pprof | `go tool pprof http://localhost:6060/debug/pprof/profile` |
| Java | async-profiler | `./profiler.sh -d 30 -f flame.html <pid>` |
| Node.js | clinic.js | `clinic flame -- node app.js` |
| Rust | cargo-flamegraph | `cargo flamegraph` |
| 系统级 | perf | `perf record -g -p <pid> -- sleep 30` |

### Memory Profiling

```bash
# Python
python -m memory_profiler script.py
# 或使用 tracemalloc
python -c "import tracemalloc; tracemalloc.start(); ..."

# Go
go tool pprof http://localhost:6060/debug/pprof/heap

# Java
jmap -dump:format=b,file=heap.hprof <pid>
jhat heap.hprof  # 或用 MAT/VisualVM 分析

# 系统级
valgrind --tool=massif ./program
```

### I/O Profiling

```bash
# 磁盘 I/O
iostat -xz 1
iotop -oP
strace -e trace=read,write -p <pid>

# 网络 I/O
ss -tnp                    # 连接状态
tcpdump -i eth0 -w cap.pcap  # 抓包
```

---

## 火焰图

### 生成流程

```bash
# 1. 采集数据
perf record -F 99 -g -p <pid> -- sleep 30

# 2. 生成火焰图
perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg

# 3. 解读
# X轴：函数在采样中出现的比例（越宽=越耗时）
# Y轴：调用栈深度
# 颜色：随机，无特殊含义
```

### 解读要点

| 特征 | 含义 | 行动 |
|------|------|------|
| 宽平顶 | 该函数自身耗时大 | 优化该函数逻辑 |
| 宽塔形 | 调用链深但每层都耗时 | 减少调用层级 |
| 多个窄尖峰 | 多处小开销累积 | 关注热路径 |

---

## 基准测试

### HTTP 基准测试

```bash
# wrk (推荐)
wrk -t12 -c400 -d30s http://localhost:8080/api

# ab (Apache Bench)
ab -n 10000 -c 100 http://localhost:8080/api

# hey
hey -n 10000 -c 100 http://localhost:8080/api

# k6 (脚本化)
k6 run --vus 100 --duration 30s script.js
```

### 代码级基准测试

```python
# Python - pytest-benchmark
def test_sort_benchmark(benchmark):
    data = list(range(1000, 0, -1))
    benchmark(sorted, data)

# Go
func BenchmarkSort(b *testing.B) {
    for i := 0; i < b.N; i++ {
        sort.Ints(generateData())
    }
}

# Rust
#[bench]
fn bench_sort(b: &mut Bencher) {
    b.iter(|| sort_data(test::black_box(generate_data())));
}
```

### 基准测试原则

1. **隔离环境** — 独占机器，关闭无关进程
2. **预热** — 丢弃前 N 次结果
3. **统计显著** — 多次运行取中位数
4. **对比基线** — 优化前后对比，而非绝对值

---

## 常见瓶颈优化

### CPU 密集型

| 问题 | 优化 |
|------|------|
| 热循环 | 算法优化、减少分支 |
| 序列化/反序列化 | 换用高效格式(protobuf/msgpack) |
| 正则表达式 | 预编译、简化模式 |
| 加密运算 | 硬件加速(AES-NI) |

### I/O 密集型

| 问题 | 优化 |
|------|------|
| 同步阻塞 I/O | 异步 I/O (asyncio/epoll) |
| 频繁小文件读写 | 批量合并、缓冲区 |
| 网络往返 | 连接池、批量请求、Pipeline |
| DNS 解析 | 本地缓存 |

### 内存相关

| 问题 | 优化 |
|------|------|
| 内存泄漏 | Profiling 定位 + 修复引用 |
| GC 压力 | 减少分配、对象池 |
| 缓存未命中 | 数据局部性、紧凑布局 |
| 大对象 | 流式处理、分片 |

---

## 数据库性能

### 查询优化

```sql
-- 1. EXPLAIN 分析
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 123;

-- 2. 索引优化
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_composite ON orders(user_id, created_at DESC);

-- 3. 避免 N+1
-- 差：循环查询
-- 好：JOIN 或 IN 批量查询
SELECT o.*, u.name FROM orders o JOIN users u ON o.user_id = u.id;

-- 4. 分页优化
-- 差：OFFSET 大数值
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 100000;
-- 好：游标分页
SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20;
```

### 连接池配置

```yaml
# HikariCP (Java)
maximumPoolSize: 10        # CPU核数 * 2 + 磁盘数
minimumIdle: 5
connectionTimeout: 30000
idleTimeout: 600000

# 通用公式
pool_size = (core_count * 2) + effective_spindle_count
```

---

## 性能优化清单

```yaml
应用层:
  - [ ] 热路径 Profiling 完成
  - [ ] 算法复杂度 ≤ O(n log n)
  - [ ] 无 N+1 查询
  - [ ] 连接池配置合理
  - [ ] 异步 I/O 用于 I/O 密集操作

数据库:
  - [ ] 慢查询 < 100ms (P95)
  - [ ] 索引覆盖高频查询
  - [ ] 无全表扫描
  - [ ] 连接池大小合理

基础设施:
  - [ ] CPU 利用率 < 70% (P95)
  - [ ] 内存利用率 < 80%
  - [ ] 磁盘 I/O 无饱和
  - [ ] 网络无丢包
```

