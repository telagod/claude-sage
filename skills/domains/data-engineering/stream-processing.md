---
name: stream-processing
description: 流式处理。Kafka Streams、Flink、实时处理、流式计算、窗口函数、状态管理。当用户提到流处理、Kafka Streams、Flink、实时处理、流式计算时使用。
---

# 🌊 流处理秘典 · Stream Processing

## 流处理架构

```
数据源 → 摄取 → 处理 → 聚合 → 输出
  │       │      │      │      │
  └─ Kafka ─┴─ 转换 ─┴─ 窗口 ─┴─ Sink
```

## Kafka Streams 基础

### 拓扑构建

```java
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.kstream.*;
import java.util.Properties;

public class StreamProcessor {
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "stream-processor");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG,
                  Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG,
                  Serdes.String().getClass());

        StreamsBuilder builder = new StreamsBuilder();

        // 构建拓扑
        KStream<String, String> source = builder.stream("input-topic");

        KStream<String, String> processed = source
            .filter((key, value) -> value != null)
            .mapValues(value -> value.toUpperCase())
            .peek((key, value) ->
                System.out.println("Processed: " + key + " -> " + value));

        processed.to("output-topic");

        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.start();

        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
    }
}
```

### 流转换操作

```java
// Map 转换
KStream<String, Integer> lengths = stream
    .mapValues(value -> value.length());

// FlatMap 展开
KStream<String, String> words = stream
    .flatMapValues(value -> Arrays.asList(value.split("\\s+")));

// Filter 过滤
KStream<String, String> filtered = stream
    .filter((key, value) -> value.length() > 10);

// Branch 分支
KStream<String, String>[] branches = stream.branch(
    (key, value) -> value.startsWith("A"),
    (key, value) -> value.startsWith("B"),
    (key, value) -> true  // 默认分支
);

// Merge 合并
KStream<String, String> merged = stream1.merge(stream2);
```

### 状态存储

```java
import org.apache.kafka.streams.state.KeyValueStore;
import org.apache.kafka.streams.state.StoreBuilder;
import org.apache.kafka.streams.state.Stores;

// 创建状态存储
StoreBuilder<KeyValueStore<String, Long>> storeBuilder =
    Stores.keyValueStoreBuilder(
        Stores.persistentKeyValueStore("counts-store"),
        Serdes.String(),
        Serdes.Long()
    );

builder.addStateStore(storeBuilder);

// 使用状态存储
stream.transform(() -> new Transformer<String, String, KeyValue<String, Long>>() {
    private KeyValueStore<String, Long> stateStore;

    @Override
    public void init(ProcessorContext context) {
        this.stateStore = context.getStateStore("counts-store");
    }

    @Override
    public KeyValue<String, Long> transform(String key, String value) {
        Long count = stateStore.get(key);
        if (count == null) count = 0L;
        count++;
        stateStore.put(key, count);
        return KeyValue.pair(key, count);
    }

    @Override
    public void close() {}
}, "counts-store");
```

### 聚合操作

```java
// Count 计数
KTable<String, Long> counts = stream
    .groupByKey()
    .count(Materialized.as("counts-store"));

// Aggregate 聚合
KTable<String, Double> averages = stream
    .groupByKey()
    .aggregate(
        () -> new AggregateValue(0.0, 0L),  // 初始化
        (key, value, aggregate) -> {
            aggregate.sum += Double.parseDouble(value);
            aggregate.count++;
            return aggregate;
        },
        Materialized.with(Serdes.String(), aggregateSerde)
    )
    .mapValues(agg -> agg.sum / agg.count);

// Reduce 归约
KTable<String, String> reduced = stream
    .groupByKey()
    .reduce((value1, value2) -> value1 + "," + value2);
```

### Join 操作

```java
// Stream-Stream Join
KStream<String, String> joined = stream1.join(
    stream2,
    (value1, value2) -> value1 + "-" + value2,
    JoinWindows.ofTimeDifferenceWithNoGrace(Duration.ofMinutes(5)),
    StreamJoined.with(Serdes.String(), Serdes.String(), Serdes.String())
);

// Stream-Table Join
KStream<String, String> enriched = stream.join(
    table,
    (streamValue, tableValue) -> streamValue + "-" + tableValue
);

// Table-Table Join
KTable<String, String> tableJoined = table1.join(
    table2,
    (value1, value2) -> value1 + "-" + value2
);
```

## Flink DataStream API

### 基础流处理

```java
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.api.common.functions.MapFunction;

public class FlinkStreamProcessor {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env =
            StreamExecutionEnvironment.getExecutionEnvironment();

        // 从 Kafka 读取
        DataStream<String> stream = env
            .addSource(new FlinkKafkaConsumer<>(
                "input-topic",
                new SimpleStringSchema(),
                properties
            ));

        // 转换处理
        DataStream<String> processed = stream
            .filter(value -> value != null)
            .map(new MapFunction<String, String>() {
                @Override
                public String map(String value) {
                    return value.toUpperCase();
                }
            });

        // 写入 Kafka
        processed.addSink(new FlinkKafkaProducer<>(
            "output-topic",
            new SimpleStringSchema(),
            properties
        ));

        env.execute("Flink Stream Processor");
    }
}
```

### 窗口函数

```java
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;

// 滚动窗口 (Tumbling Window)
DataStream<Tuple2<String, Long>> tumblingCounts = stream
    .keyBy(value -> value.getKey())
    .window(TumblingProcessingTimeWindows.of(Time.minutes(5)))
    .sum(1);

// 滑动窗口 (Sliding Window)
DataStream<Tuple2<String, Long>> slidingCounts = stream
    .keyBy(value -> value.getKey())
    .window(SlidingProcessingTimeWindows.of(
        Time.minutes(10),  // 窗口大小
        Time.minutes(5)    // 滑动步长
    ))
    .sum(1);

// 会话窗口 (Session Window)
DataStream<Tuple2<String, Long>> sessionCounts = stream
    .keyBy(value -> value.getKey())
    .window(ProcessingTimeSessionWindows.withGap(Time.minutes(10)))
    .sum(1);

// 全局窗口 (Global Window)
DataStream<Tuple2<String, Long>> globalCounts = stream
    .keyBy(value -> value.getKey())
    .window(GlobalWindows.create())
    .trigger(CountTrigger.of(100))  // 每100条触发
    .sum(1);
```

### 窗口聚合

```java
import org.apache.flink.streaming.api.functions.windowing.WindowFunction;
import org.apache.flink.util.Collector;

// 增量聚合 + 全窗口函数
DataStream<String> result = stream
    .keyBy(value -> value.getKey())
    .window(TumblingProcessingTimeWindows.of(Time.minutes(5)))
    .aggregate(
        new AverageAggregate(),  // 增量聚合
        new WindowResultFunction()  // 全窗口处理
    );

// AverageAggregate 实现
class AverageAggregate implements AggregateFunction<
    Tuple2<String, Double>,
    Tuple2<Double, Long>,
    Double> {

    @Override
    public Tuple2<Double, Long> createAccumulator() {
        return new Tuple2<>(0.0, 0L);
    }

    @Override
    public Tuple2<Double, Long> add(
        Tuple2<String, Double> value,
        Tuple2<Double, Long> accumulator) {
        return new Tuple2<>(
            accumulator.f0 + value.f1,
            accumulator.f1 + 1L
        );
    }

    @Override
    public Double getResult(Tuple2<Double, Long> accumulator) {
        return accumulator.f0 / accumulator.f1;
    }

    @Override
    public Tuple2<Double, Long> merge(
        Tuple2<Double, Long> a,
        Tuple2<Double, Long> b) {
        return new Tuple2<>(a.f0 + b.f0, a.f1 + b.f1);
    }
}
```

### ProcessFunction

```java
import org.apache.flink.streaming.api.functions.ProcessFunction;
import org.apache.flink.util.Collector;

// 低级 API - 完全控制
DataStream<String> processed = stream.process(
    new ProcessFunction<String, String>() {
        @Override
        public void processElement(
            String value,
            Context ctx,
            Collector<String> out) throws Exception {

            // 访问时间戳
            long timestamp = ctx.timestamp();

            // 注册定时器
            ctx.timerService().registerProcessingTimeTimer(
                timestamp + 60000
            );

            // 输出结果
            out.collect(value.toUpperCase());
        }

        @Override
        public void onTimer(
            long timestamp,
            OnTimerContext ctx,
            Collector<String> out) throws Exception {
            // 定时器触发
            out.collect("Timer fired at " + timestamp);
        }
    }
);
```

### 状态管理

```java
import org.apache.flink.api.common.state.*;
import org.apache.flink.configuration.Configuration;

// ValueState - 单值状态
class StatefulMapFunction extends RichMapFunction<String, String> {
    private transient ValueState<Long> countState;

    @Override
    public void open(Configuration parameters) {
        ValueStateDescriptor<Long> descriptor =
            new ValueStateDescriptor<>("count", Long.class, 0L);
        countState = getRuntimeContext().getState(descriptor);
    }

    @Override
    public String map(String value) throws Exception {
        Long count = countState.value();
        count++;
        countState.update(count);
        return value + " (count: " + count + ")";
    }
}

// ListState - 列表状态
class ListStateFunction extends RichFlatMapFunction<String, String> {
    private transient ListState<String> listState;

    @Override
    public void open(Configuration parameters) {
        ListStateDescriptor<String> descriptor =
            new ListStateDescriptor<>("list", String.class);
        listState = getRuntimeContext().getListState(descriptor);
    }

    @Override
    public void flatMap(String value, Collector<String> out) throws Exception {
        listState.add(value);

        // 输出所有历史值
        for (String item : listState.get()) {
            out.collect(item);
        }
    }
}

// MapState - 映射状态
class MapStateFunction extends RichFlatMapFunction<
    Tuple2<String, String>, String> {

    private transient MapState<String, Long> mapState;

    @Override
    public void open(Configuration parameters) {
        MapStateDescriptor<String, Long> descriptor =
            new MapStateDescriptor<>("map", String.class, Long.class);
        mapState = getRuntimeContext().getMapState(descriptor);
    }

    @Override
    public void flatMap(
        Tuple2<String, String> value,
        Collector<String> out) throws Exception {

        String key = value.f1;
        Long count = mapState.get(key);
        if (count == null) count = 0L;
        count++;
        mapState.put(key, count);

        out.collect(key + ": " + count);
    }
}
```

### Checkpoint 和 Savepoint

```java
// 启用 Checkpoint
env.enableCheckpointing(60000);  // 每60秒

// Checkpoint 配置
env.getCheckpointConfig().setCheckpointingMode(
    CheckpointingMode.EXACTLY_ONCE
);
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(30000);
env.getCheckpointConfig().setCheckpointTimeout(600000);
env.getCheckpointConfig().setMaxConcurrentCheckpoints(1);

// 外部化 Checkpoint
env.getCheckpointConfig().enableExternalizedCheckpoints(
    ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION
);

// 从 Savepoint 恢复
// flink run -s /path/to/savepoint your-job.jar
```

## 窗口类型对比

| 窗口类型 | 特点 | 使用场景 |
|----------|------|----------|
| 滚动窗口 | 固定大小，无重叠 | 每小时统计、日报 |
| 滑动窗口 | 固定大小，有重叠 | 移动平均、趋势分析 |
| 会话窗口 | 动态大小，基于间隔 | 用户会话、活动检测 |
| 全局窗口 | 无时间限制 | 自定义触发逻辑 |

## 时间语义

### Event Time vs Processing Time

```java
// Event Time - 事件时间
env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);

DataStream<Event> stream = env
    .addSource(new EventSource())
    .assignTimestampsAndWatermarks(
        WatermarkStrategy
            .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(10))
            .withTimestampAssigner((event, timestamp) -> event.getTimestamp())
    );

// Processing Time - 处理时间
env.setStreamTimeCharacteristic(TimeCharacteristic.ProcessingTime);

DataStream<Event> stream = env
    .addSource(new EventSource())
    .window(TumblingProcessingTimeWindows.of(Time.minutes(5)));
```

### Watermark 生成

```java
// 周期性 Watermark
class PeriodicWatermarkGenerator implements WatermarkGenerator<Event> {
    private long maxTimestamp = Long.MIN_VALUE;
    private final long maxOutOfOrderness = 5000;

    @Override
    public void onEvent(Event event, long eventTimestamp, WatermarkOutput output) {
        maxTimestamp = Math.max(maxTimestamp, eventTimestamp);
    }

    @Override
    public void onPeriodicEmit(WatermarkOutput output) {
        output.emitWatermark(new Watermark(maxTimestamp - maxOutOfOrderness));
    }
}

// 标点 Watermark
class PunctuatedWatermarkGenerator implements WatermarkGenerator<Event> {
    @Override
    public void onEvent(Event event, long eventTimestamp, WatermarkOutput output) {
        if (event.hasWatermarkMarker()) {
            output.emitWatermark(new Watermark(eventTimestamp));
        }
    }

    @Override
    public void onPeriodicEmit(WatermarkOutput output) {
        // 不需要周期性发射
    }
}
```

## 背压处理

### Kafka Streams 背压

```java
// 配置消费者
props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 500);
props.put(ConsumerConfig.FETCH_MIN_BYTES_CONFIG, 1024);
props.put(ConsumerConfig.FETCH_MAX_WAIT_MS_CONFIG, 500);

// 配置生产者
props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 33554432);
props.put(ProducerConfig.BATCH_SIZE_CONFIG, 16384);
props.put(ProducerConfig.LINGER_MS_CONFIG, 10);
```

### Flink 背压监控

```java
// 配置缓冲区
env.setBufferTimeout(100);

// 监控背压
// Web UI -> Job -> BackPressure

// 调整并行度
stream.map(new MyMapFunction()).setParallelism(4);
```

## 容错机制

### Exactly-Once 语义

```java
// Kafka Streams Exactly-Once
props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG,
          StreamsConfig.EXACTLY_ONCE_V2);

// Flink Exactly-Once
env.enableCheckpointing(60000);
env.getCheckpointConfig().setCheckpointingMode(
    CheckpointingMode.EXACTLY_ONCE
);

// Kafka Sink Exactly-Once
FlinkKafkaProducer<String> producer = new FlinkKafkaProducer<>(
    "output-topic",
    new SimpleStringSchema(),
    properties,
    FlinkKafkaProducer.Semantic.EXACTLY_ONCE
);
```

### 故障恢复

```java
// Kafka Streams 自动恢复
// 状态存储自动从 Changelog Topic 恢复

// Flink 从 Checkpoint 恢复
// 自动从最近的 Checkpoint 恢复

// 手动从 Savepoint 恢复
// flink run -s /path/to/savepoint your-job.jar
```

## 性能优化

### Kafka Streams 优化

```java
// 增加并行度
props.put(StreamsConfig.NUM_STREAM_THREADS_CONFIG, 4);

// 优化状态存储
props.put(StreamsConfig.CACHE_MAX_BYTES_BUFFERING_CONFIG, 10 * 1024 * 1024);
props.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 1000);

// RocksDB 配置
props.put(StreamsConfig.ROCKSDB_CONFIG_SETTER_CLASS_CONFIG,
          CustomRocksDBConfig.class);
```

### Flink 优化

```java
// 调整并行度
env.setParallelism(8);

// 配置内存
env.getConfig().setTaskManagerMemory(MemorySize.ofMebiBytes(2048));

// 启用对象重用
env.getConfig().enableObjectReuse();

// 配置网络缓冲区
env.getConfig().setNetworkBufferMemory(64 * 1024 * 1024);
```

## Python API

### Kafka Streams Python (kafka-python)

```python
from kafka import KafkaConsumer, KafkaProducer
import json

consumer = KafkaConsumer(
    'input-topic',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

for message in consumer:
    value = message.value

    # 处理逻辑
    processed = {
        'key': value['key'],
        'value': value['value'].upper()
    }

    producer.send('output-topic', processed)
    producer.flush()
```

### PyFlink

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema

env = StreamExecutionEnvironment.get_execution_environment()

# 从 Kafka 读取
kafka_consumer = FlinkKafkaConsumer(
    topics='input-topic',
    deserialization_schema=SimpleStringSchema(),
    properties={'bootstrap.servers': 'localhost:9092'}
)

stream = env.add_source(kafka_consumer)

# 转换处理
processed = stream \
    .filter(lambda x: x is not None) \
    .map(lambda x: x.upper())

# 写入 Kafka
kafka_producer = FlinkKafkaProducer(
    topic='output-topic',
    serialization_schema=SimpleStringSchema(),
    producer_config={'bootstrap.servers': 'localhost:9092'}
)

processed.add_sink(kafka_producer)

env.execute("PyFlink Stream Processor")
```

## 监控指标

### Kafka Streams 指标

```java
// JMX 指标
// kafka.streams:type=stream-metrics,client-id=*
// - commit-latency-avg
// - poll-latency-avg
// - process-latency-avg

// 自定义指标
StreamsMetrics metrics = context.metrics();
Sensor sensor = metrics.addLatencySensor(
    "process",
    "latency",
    "Process latency"
);
```

### Flink 指标

```java
// 注册指标
public class MyMapFunction extends RichMapFunction<String, String> {
    private transient Counter counter;

    @Override
    public void open(Configuration parameters) {
        this.counter = getRuntimeContext()
            .getMetricGroup()
            .counter("myCounter");
    }

    @Override
    public String map(String value) {
        counter.inc();
        return value.toUpperCase();
    }
}
```

## 最佳实践

### 状态大小控制

```java
// 使用 TTL 清理过期状态
StateTtlConfig ttlConfig = StateTtlConfig
    .newBuilder(Time.hours(24))
    .setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)
    .setStateVisibility(StateTtlConfig.StateVisibility.NeverReturnExpired)
    .build();

ValueStateDescriptor<Long> descriptor =
    new ValueStateDescriptor<>("count", Long.class);
descriptor.enableTimeToLive(ttlConfig);
```

### 数据倾斜处理

```java
// 添加随机前缀
stream
    .map(value -> {
        String randomPrefix = String.valueOf(new Random().nextInt(10));
        return Tuple2.of(randomPrefix + "-" + value.getKey(), value);
    })
    .keyBy(tuple -> tuple.f0)
    .window(TumblingProcessingTimeWindows.of(Time.minutes(5)))
    .sum(1);
```

### 延迟数据处理

```java
// 使用侧输出流处理延迟数据
OutputTag<Event> lateOutputTag = new OutputTag<Event>("late-data"){};

DataStream<Event> result = stream
    .keyBy(Event::getKey)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .allowedLateness(Time.minutes(1))
    .sideOutputLateData(lateOutputTag)
    .sum("value");

DataStream<Event> lateStream = result.getSideOutput(lateOutputTag);
```

## 框架对比

| 特性 | Kafka Streams | Flink | Spark Streaming |
|------|---------------|-------|-----------------|
| 部署模式 | 嵌入式 | 独立集群 | 独立集群 |
| 状态管理 | RocksDB | 内存/RocksDB | 内存 |
| Exactly-Once | ✅ | ✅ | ✅ |
| 窗口类型 | 丰富 | 最丰富 | 基础 |
| 学习曲线 | 平缓 | 陡峭 | 中等 |
| 生态集成 | Kafka 生态 | 广泛 | Spark 生态 |

## 工具清单

| 工具 | 用途 | 推荐场景 |
|------|------|----------|
| Kafka Streams | 轻量级流处理 | Kafka 生态、简单转换 |
| Apache Flink | 分布式流处理 | 复杂窗口、状态管理 |
| Spark Streaming | 批流一体 | Spark 生态、批流混合 |
| Apache Storm | 实时计算 | 低延迟、简单拓扑 |
| Apache Samza | LinkedIn 流处理 | Kafka + YARN |
| Pulsar Functions | Pulsar 流处理 | Pulsar 生态 |

## 触发词

流处理、Kafka Streams、Flink、实时处理、流式计算、窗口函数、状态管理、Checkpoint、Watermark、背压
