---
name: data-engineering
description: 数据工程。Airflow、Dagster、Kafka Streams、Flink、dbt、数据管道、流处理、数据质量。当用户提到数据管道、ETL、流处理、数据质量时路由到此。
---

# 🏗️ 数据工程域 · Data Engineering

## 域概览

数据工程域涵盖数据管道编排、流式处理、数据质量保障三大核心领域。

## 秘典索引

| 秘典 | 覆盖范围 | 触发词 |
|------|----------|--------|
| [data-pipeline.md](./data-pipeline.md) | Airflow/Dagster/Prefect/调度编排 | 数据管道、Airflow、Dagster、Prefect、ETL、数据编排 |
| [stream-processing.md](./stream-processing.md) | Kafka Streams/Flink/实时处理 | 流处理、Kafka Streams、Flink、实时处理、流式计算 |
| [data-quality.md](./data-quality.md) | Great Expectations/dbt/数据验证 | 数据质量、Great Expectations、dbt、数据验证、数据测试 |

## 技术栈

```
数据管道层
├── Airflow (调度编排)
├── Dagster (资产管理)
└── Prefect (现代工作流)

流处理层
├── Kafka Streams (轻量级)
├── Flink (分布式流处理)
└── Spark Streaming (批流一体)

质量保障层
├── Great Expectations (数据验证)
├── dbt (数据转换测试)
└── Soda (数据可观测性)
```

## 使用指南

1. **数据管道开发** → 查阅 data-pipeline.md
2. **实时流处理** → 查阅 stream-processing.md
3. **数据质量保障** → 查阅 data-quality.md
