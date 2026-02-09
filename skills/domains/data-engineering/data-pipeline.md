---
name: data-pipeline
description: 数据管道编排。Airflow、Dagster、Prefect、ETL、数据编排、调度策略。当用户提到数据管道、Airflow、Dagster、Prefect、ETL、数据编排时使用。
---

# 🔄 数据管道秘典 · Data Pipeline

## 管道架构

```
数据源 → 提取 → 转换 → 加载 → 目标
  │       │      │      │      │
  └─ API ─┴─ 清洗 ─┴─ 聚合 ─┴─ 存储
```

## Airflow DAG 开发

### 基础 DAG 结构

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'etl_pipeline',
    default_args=default_args,
    description='ETL pipeline for user data',
    schedule_interval='0 2 * * *',  # 每天凌晨2点
    catchup=False,
    tags=['etl', 'production'],
) as dag:

    def extract_data(**context):
        """提取数据"""
        execution_date = context['execution_date']
        # 提取逻辑
        return {'records': 1000}

    def transform_data(**context):
        """转换数据"""
        ti = context['ti']
        data = ti.xcom_pull(task_ids='extract')
        # 转换逻辑
        return {'processed': data['records']}

    def load_data(**context):
        """加载数据"""
        ti = context['ti']
        data = ti.xcom_pull(task_ids='transform')
        # 加载逻辑
        print(f"Loaded {data['processed']} records")

    extract = PythonOperator(
        task_id='extract',
        python_callable=extract_data,
    )

    transform = PythonOperator(
        task_id='transform',
        python_callable=transform_data,
    )

    load = PythonOperator(
        task_id='load',
        python_callable=load_data,
    )

    extract >> transform >> load
```

### Operators 使用

```python
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator

# SQL Operator
create_table = PostgresOperator(
    task_id='create_table',
    postgres_conn_id='postgres_default',
    sql="""
        CREATE TABLE IF NOT EXISTS user_stats (
            date DATE,
            user_count INT,
            active_count INT
        );
    """,
)

# HTTP Operator
fetch_api = SimpleHttpOperator(
    task_id='fetch_api',
    http_conn_id='api_default',
    endpoint='/users',
    method='GET',
    headers={'Authorization': 'Bearer {{ var.value.api_token }}'},
    response_filter=lambda response: response.json(),
)

# S3 Operator
upload_to_s3 = S3CreateBucketOperator(
    task_id='upload_to_s3',
    bucket_name='data-lake-{{ ds_nodash }}',
    aws_conn_id='aws_default',
)
```

### Sensors 使用

```python
from airflow.sensors.filesystem import FileSensor
from airflow.providers.http.sensors.http import HttpSensor
from airflow.sensors.external_task import ExternalTaskSensor

# 文件传感器
wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/data/input/{{ ds }}/data.csv',
    poke_interval=60,  # 每60秒检查一次
    timeout=3600,  # 1小时超时
    mode='poke',
)

# HTTP 传感器
wait_for_api = HttpSensor(
    task_id='wait_for_api',
    http_conn_id='api_default',
    endpoint='/health',
    request_params={},
    response_check=lambda response: response.status_code == 200,
    poke_interval=30,
)

# 外部任务传感器
wait_for_upstream = ExternalTaskSensor(
    task_id='wait_for_upstream',
    external_dag_id='upstream_dag',
    external_task_id='final_task',
    execution_delta=timedelta(hours=1),
)
```

### XCom 数据传递

```python
from airflow.decorators import task

@task
def extract_data():
    """使用 TaskFlow API"""
    data = {'users': [1, 2, 3], 'count': 3}
    return data

@task
def transform_data(data: dict):
    """自动接收上游数据"""
    transformed = {
        'users': [u * 2 for u in data['users']],
        'count': data['count']
    }
    return transformed

@task
def load_data(data: dict):
    """加载数据"""
    print(f"Loading {data['count']} users")

# 链式调用
data = extract_data()
transformed = transform_data(data)
load_data(transformed)
```

### 动态任务生成

```python
from airflow.decorators import task

@task
def get_partitions():
    """获取分区列表"""
    return ['2024-01', '2024-02', '2024-03']

@task
def process_partition(partition: str):
    """处理单个分区"""
    print(f"Processing {partition}")

# 动态生成任务
partitions = get_partitions()
process_partition.expand(partition=partitions)
```

## Dagster 资源管理

### Assets 定义

```python
from dagster import asset, AssetExecutionContext, MaterializeResult
import pandas as pd

@asset(
    description="Raw user data from API",
    group_name="ingestion",
    compute_kind="python",
)
def raw_users(context: AssetExecutionContext) -> pd.DataFrame:
    """提取原始用户数据"""
    context.log.info("Fetching users from API")
    df = pd.DataFrame({
        'user_id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie']
    })
    return df

@asset(
    description="Cleaned user data",
    group_name="transformation",
    deps=[raw_users],
)
def cleaned_users(context: AssetExecutionContext, raw_users: pd.DataFrame) -> pd.DataFrame:
    """清洗用户数据"""
    context.log.info(f"Cleaning {len(raw_users)} users")
    df = raw_users.dropna()
    df['name'] = df['name'].str.upper()
    return df

@asset(
    description="User statistics",
    group_name="analytics",
    deps=[cleaned_users],
)
def user_stats(context: AssetExecutionContext, cleaned_users: pd.DataFrame) -> MaterializeResult:
    """计算用户统计"""
    count = len(cleaned_users)
    context.log.info(f"Total users: {count}")

    return MaterializeResult(
        metadata={
            "user_count": count,
            "preview": cleaned_users.head().to_markdown(),
        }
    )
```

### Resources 配置

```python
from dagster import resource, ConfigurableResource
from pydantic import Field
import psycopg2

class PostgresResource(ConfigurableResource):
    """Postgres 资源"""
    host: str = Field(description="Database host")
    port: int = Field(default=5432)
    database: str
    user: str
    password: str

    def get_connection(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
        )

@asset
def users_from_db(postgres: PostgresResource) -> pd.DataFrame:
    """从数据库读取用户"""
    conn = postgres.get_connection()
    df = pd.read_sql("SELECT * FROM users", conn)
    conn.close()
    return df
```

### Jobs 和 Schedules

```python
from dagster import define_asset_job, ScheduleDefinition, AssetSelection

# 定义 Job
etl_job = define_asset_job(
    name="etl_job",
    selection=AssetSelection.groups("ingestion", "transformation"),
    description="ETL pipeline job",
)

analytics_job = define_asset_job(
    name="analytics_job",
    selection=AssetSelection.groups("analytics"),
)

# 定义 Schedule
daily_schedule = ScheduleDefinition(
    job=etl_job,
    cron_schedule="0 2 * * *",  # 每天凌晨2点
)

hourly_schedule = ScheduleDefinition(
    job=analytics_job,
    cron_schedule="0 * * * *",  # 每小时
)
```

### Sensors 监听

```python
from dagster import sensor, RunRequest, SensorEvaluationContext
import os

@sensor(
    job=etl_job,
    minimum_interval_seconds=60,
)
def file_sensor(context: SensorEvaluationContext):
    """监听文件到达"""
    files = os.listdir('/data/input')
    for file in files:
        if file.endswith('.csv'):
            yield RunRequest(
                run_key=file,
                run_config={
                    "ops": {
                        "process_file": {
                            "config": {"filename": file}
                        }
                    }
                }
            )
```

### Partitions 分区

```python
from dagster import DailyPartitionsDefinition, asset

daily_partitions = DailyPartitionsDefinition(start_date="2024-01-01")

@asset(
    partitions_def=daily_partitions,
)
def daily_users(context: AssetExecutionContext) -> pd.DataFrame:
    """按日分区的用户数据"""
    partition_date = context.partition_key
    context.log.info(f"Processing partition: {partition_date}")
    # 处理特定日期的数据
    return pd.DataFrame()
```

## Prefect 工作流

### Tasks 和 Flows

```python
from prefect import task, flow
from prefect.tasks import task_input_hash
from datetime import timedelta

@task(
    retries=3,
    retry_delay_seconds=60,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1),
)
def extract_data(source: str) -> dict:
    """提取数据任务"""
    print(f"Extracting from {source}")
    return {'records': 1000}

@task
def transform_data(data: dict) -> dict:
    """转换数据任务"""
    print(f"Transforming {data['records']} records")
    return {'processed': data['records']}

@task
def load_data(data: dict):
    """加载数据任务"""
    print(f"Loading {data['processed']} records")

@flow(name="ETL Pipeline", log_prints=True)
def etl_flow(source: str = "api"):
    """ETL 工作流"""
    raw_data = extract_data(source)
    transformed = transform_data(raw_data)
    load_data(transformed)
```

### 并发控制

```python
from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner

@task
def process_item(item: int) -> int:
    """处理单个项目"""
    return item * 2

@flow(task_runner=ConcurrentTaskRunner())
def parallel_flow():
    """并发执行任务"""
    items = range(10)
    results = process_item.map(items)
    return results
```

### Deployments 部署

```python
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule

deployment = Deployment.build_from_flow(
    flow=etl_flow,
    name="etl-production",
    schedule=CronSchedule(cron="0 2 * * *"),
    work_queue_name="production",
    parameters={"source": "database"},
    tags=["production", "etl"],
)

deployment.apply()
```

### Blocks 配置

```python
from prefect.blocks.system import Secret, JSON

# 存储密钥
secret = Secret(value="my-secret-key")
secret.save("api-key")

# 存储配置
config = JSON(value={"host": "localhost", "port": 5432})
config.save("db-config")

# 使用 Block
@task
def connect_db():
    """连接数据库"""
    config = JSON.load("db-config")
    api_key = Secret.load("api-key")
    print(f"Connecting to {config.value['host']}")
```

## 调度策略

### Cron 表达式

| 表达式 | 说明 | 示例 |
|--------|------|------|
| `0 2 * * *` | 每天凌晨2点 | 日批处理 |
| `0 */4 * * *` | 每4小时 | 增量同步 |
| `0 0 * * 0` | 每周日午夜 | 周报生成 |
| `0 0 1 * *` | 每月1号 | 月度汇总 |
| `*/15 * * * *` | 每15分钟 | 实时监控 |

### 事件驱动调度

```python
# Airflow 文件触发
from airflow.sensors.filesystem import FileSensor

wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/data/trigger.flag',
    poke_interval=10,
)

# Dagster 传感器触发
from dagster import sensor, RunRequest

@sensor(job=my_job)
def s3_sensor(context):
    """S3 文件到达触发"""
    new_files = check_s3_bucket()
    for file in new_files:
        yield RunRequest(run_key=file)

# Prefect 自动化触发
from prefect.events import DeploymentEventTrigger

trigger = DeploymentEventTrigger(
    expect={"resource.id": "s3://bucket/data"},
    match_related={"resource.type": "file"},
)
```

### 依赖调度

```python
# Airflow 跨 DAG 依赖
from airflow.sensors.external_task import ExternalTaskSensor

wait_upstream = ExternalTaskSensor(
    task_id='wait_upstream',
    external_dag_id='upstream_dag',
    external_task_id='final_task',
)

# Dagster 资产依赖
@asset(deps=[upstream_asset])
def downstream_asset():
    pass

# Prefect 子流程
@flow
def parent_flow():
    child_flow()
```

## 错误处理

### 重试策略

```python
# Airflow 重试
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(hours=1),
}

# Dagster 重试
from dagster import RetryPolicy

@asset(
    retry_policy=RetryPolicy(
        max_retries=3,
        delay=60,
    )
)
def my_asset():
    pass

# Prefect 重试
@task(
    retries=3,
    retry_delay_seconds=60,
    retry_jitter_factor=0.5,
)
def my_task():
    pass
```

### 失败回调

```python
# Airflow 回调
def on_failure_callback(context):
    """失败回调"""
    task = context['task_instance']
    send_alert(f"Task {task.task_id} failed")

task = PythonOperator(
    task_id='my_task',
    python_callable=my_func,
    on_failure_callback=on_failure_callback,
)

# Dagster 钩子
from dagster import failure_hook

@failure_hook
def slack_on_failure(context):
    """失败通知"""
    send_slack_message(f"Asset {context.asset_key} failed")

@asset(hooks={slack_on_failure})
def my_asset():
    pass
```

## 监控告警

### 指标收集

```python
# Airflow 指标
from airflow.metrics import Stats

def my_task():
    Stats.incr('custom.task.count')
    Stats.timing('custom.task.duration', 100)
    Stats.gauge('custom.task.records', 1000)

# Dagster 元数据
from dagster import MaterializeResult

@asset
def my_asset():
    return MaterializeResult(
        metadata={
            "records_processed": 1000,
            "duration_seconds": 45.2,
        }
    )
```

### SLA 监控

```python
# Airflow SLA
with DAG(
    'my_dag',
    default_args={
        'sla': timedelta(hours=2),
        'sla_miss_callback': sla_miss_alert,
    }
) as dag:
    task = PythonOperator(task_id='task')

# Dagster 资产检查
from dagster import asset_check, AssetCheckResult

@asset_check(asset=my_asset)
def check_freshness():
    """检查数据新鲜度"""
    age = get_data_age()
    return AssetCheckResult(
        passed=age < timedelta(hours=2),
        metadata={"age_hours": age.total_seconds() / 3600}
    )
```

## 数据血缘

### Airflow Lineage

```python
from airflow.lineage import AUTO
from airflow.lineage.entities import File

input_file = File("/data/input.csv")
output_file = File("/data/output.csv")

task = PythonOperator(
    task_id='transform',
    python_callable=transform_func,
    inlets={"auto": AUTO, "datasets": [input_file]},
    outlets={"datasets": [output_file]},
)
```

### Dagster 血缘追踪

```python
from dagster import AssetIn, asset

@asset
def source_data():
    """源数据"""
    return pd.DataFrame()

@asset(
    ins={"source": AssetIn("source_data")},
)
def transformed_data(source: pd.DataFrame):
    """转换数据 - 自动追踪血缘"""
    return source.copy()
```

## 最佳实践

### 幂等性设计

```python
# 使用 UPSERT 而非 INSERT
def load_data(df: pd.DataFrame):
    """幂等加载"""
    df.to_sql(
        'users',
        engine,
        if_exists='replace',  # 或使用 ON CONFLICT
        index=False,
    )

# 使用分区覆盖
def write_partition(df: pd.DataFrame, date: str):
    """分区覆盖写入"""
    path = f"s3://bucket/data/date={date}/"
    df.to_parquet(path, mode='overwrite')
```

### 增量处理

```python
@task
def incremental_extract(last_run: datetime):
    """增量提取"""
    query = f"""
        SELECT * FROM users
        WHERE updated_at > '{last_run}'
    """
    return pd.read_sql(query, engine)

@flow
def incremental_flow():
    """增量流程"""
    last_run = get_last_run_time()
    new_data = incremental_extract(last_run)
    if not new_data.empty:
        transform_and_load(new_data)
```

### 数据验证

```python
@task
def validate_data(df: pd.DataFrame):
    """数据验证"""
    assert not df.empty, "DataFrame is empty"
    assert df['user_id'].is_unique, "Duplicate user_id"
    assert df['email'].notna().all(), "Null emails found"
    assert df['age'].between(0, 120).all(), "Invalid age"
```

## 框架对比

| 特性 | Airflow | Dagster | Prefect |
|------|---------|---------|---------|
| 学习曲线 | 陡峭 | 中等 | 平缓 |
| 资产管理 | ❌ | ✅ | ❌ |
| 动态任务 | ✅ | ✅ | ✅ |
| 本地开发 | 复杂 | 简单 | 简单 |
| UI 体验 | 传统 | 现代 | 现代 |
| 社区生态 | 最大 | 成长中 | 成长中 |
| 企业支持 | Astronomer | Dagster+ | Prefect Cloud |

## 工具清单

| 工具 | 用途 | 推荐场景 |
|------|------|----------|
| Apache Airflow | 批处理编排 | 复杂 DAG、成熟生态 |
| Dagster | 资产管理 | 数据资产、血缘追踪 |
| Prefect | 现代工作流 | 快速开发、动态流程 |
| Luigi | 轻量编排 | 简单管道、Python 原生 |
| Argo Workflows | K8s 编排 | 云原生、容器化 |
| Temporal | 持久化工作流 | 长时任务、状态管理 |

## 触发词

数据管道、Airflow、Dagster、Prefect、ETL、数据编排、DAG、调度、工作流、数据血缘
