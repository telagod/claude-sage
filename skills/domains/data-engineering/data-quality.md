---
name: data-quality
description: 数据质量保障。Great Expectations、dbt、数据验证、数据测试、数据血缘、完整性检查。当用户提到数据质量、Great Expectations、dbt、数据验证、数据测试时使用。
---

# 🎯 数据质量秘典 · Data Quality

## 质量维度

```
完整性 → 准确性 → 一致性 → 及时性 → 有效性
  │        │        │        │        │
  └─ 非空 ─┴─ 范围 ─┴─ 关联 ─┴─ 新鲜度 ─┴─ 格式
```

## Great Expectations 基础

### 安装和初始化

```bash
# 安装
pip install great_expectations

# 初始化项目
great_expectations init

# 项目结构
great_expectations/
├── great_expectations.yml
├── expectations/
├── checkpoints/
├── plugins/
└── uncommitted/
```

### 创建 Data Context

```python
import great_expectations as gx
from great_expectations.data_context import FileDataContext

# 获取 Data Context
context = gx.get_context()

# 添加数据源
datasource = context.sources.add_pandas("my_datasource")

# 添加数据资产
data_asset = datasource.add_dataframe_asset(name="users_df")

# 构建批次请求
batch_request = data_asset.build_batch_request(dataframe=df)
```

### Expectations 定义

```python
import pandas as pd
import great_expectations as gx

# 创建 Validator
context = gx.get_context()
validator = context.sources.pandas_default.read_dataframe(df)

# 基础 Expectations
validator.expect_table_row_count_to_be_between(min_value=100, max_value=10000)
validator.expect_table_column_count_to_equal(value=5)

# 列存在性
validator.expect_column_to_exist(column="user_id")
validator.expect_column_to_exist(column="email")

# 非空检查
validator.expect_column_values_to_not_be_null(column="user_id")
validator.expect_column_values_to_not_be_null(column="email")

# 唯一性检查
validator.expect_column_values_to_be_unique(column="user_id")
validator.expect_column_values_to_be_unique(column="email")

# 值范围检查
validator.expect_column_values_to_be_between(
    column="age",
    min_value=0,
    max_value=120
)

# 值集合检查
validator.expect_column_values_to_be_in_set(
    column="status",
    value_set=["active", "inactive", "pending"]
)

# 正则表达式检查
validator.expect_column_values_to_match_regex(
    column="email",
    regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

# 类型检查
validator.expect_column_values_to_be_of_type(
    column="age",
    type_="int64"
)

# 保存 Expectation Suite
validator.save_expectation_suite(discard_failed_expectations=False)
```

### 自定义 Expectations

```python
from great_expectations.expectations.expectation import ColumnMapExpectation
from great_expectations.execution_engine import PandasExecutionEngine

class ExpectColumnValuesToBeValidPhoneNumber(ColumnMapExpectation):
    """期望列值为有效电话号码"""

    map_metric = "column_values.match_phone_pattern"

    @classmethod
    def _atomic_prescriptive_template(cls, **kwargs):
        return "values must be valid phone numbers"

    @classmethod
    def _prescriptive_template(cls, **kwargs):
        return "At least $mostly_pct % of values in $column must be valid phone numbers"

# 注册自定义 Expectation
validator.expect_column_values_to_be_valid_phone_number(
    column="phone",
    mostly=0.95
)
```

### Checkpoints 执行

```python
# 创建 Checkpoint
checkpoint_config = {
    "name": "my_checkpoint",
    "config_version": 1.0,
    "class_name": "SimpleCheckpoint",
    "validations": [
        {
            "batch_request": {
                "datasource_name": "my_datasource",
                "data_asset_name": "users_df",
            },
            "expectation_suite_name": "users_suite",
        }
    ],
}

context.add_checkpoint(**checkpoint_config)

# 运行 Checkpoint
result = context.run_checkpoint(
    checkpoint_name="my_checkpoint",
    batch_request=batch_request,
)

# 检查结果
if result["success"]:
    print("All expectations passed!")
else:
    print("Some expectations failed:")
    for validation in result["run_results"].values():
        for result in validation["validation_result"]["results"]:
            if not result["success"]:
                print(f"  - {result['expectation_config']['expectation_type']}")
```

### Data Docs 生成

```python
# 构建 Data Docs
context.build_data_docs()

# 打开 Data Docs
context.open_data_docs()

# 自定义 Data Docs 站点
data_docs_config = {
    "sites": {
        "local_site": {
            "class_name": "SiteBuilder",
            "store_backend": {
                "class_name": "TupleFilesystemStoreBackend",
                "base_directory": "uncommitted/data_docs/local_site/",
            },
            "site_index_builder": {
                "class_name": "DefaultSiteIndexBuilder",
            },
        }
    }
}
```

## dbt 数据测试

### 项目结构

```yaml
# dbt_project.yml
name: 'my_project'
version: '1.0.0'
config-version: 2

profile: 'default'

model-paths: ["models"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]

models:
  my_project:
    +materialized: table
```

### Schema 测试

```yaml
# models/schema.yml
version: 2

models:
  - name: users
    description: "User table"
    columns:
      - name: user_id
        description: "Primary key"
        tests:
          - unique
          - not_null

      - name: email
        description: "User email"
        tests:
          - unique
          - not_null
          - dbt_utils.email

      - name: age
        description: "User age"
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 120

      - name: status
        description: "User status"
        tests:
          - not_null
          - accepted_values:
              values: ['active', 'inactive', 'pending']

      - name: created_at
        description: "Creation timestamp"
        tests:
          - not_null
          - dbt_utils.not_future_date

      - name: country_code
        description: "Country code"
        tests:
          - relationships:
              to: ref('countries')
              field: code
```

### 自定义 Data 测试

```sql
-- tests/assert_positive_revenue.sql
-- 测试收入必须为正数

SELECT
    order_id,
    revenue
FROM {{ ref('orders') }}
WHERE revenue <= 0
```

```sql
-- tests/assert_user_email_domain.sql
-- 测试用户邮箱域名

SELECT
    user_id,
    email
FROM {{ ref('users') }}
WHERE email NOT LIKE '%@company.com'
  AND email NOT LIKE '%@partner.com'
```

### Generic 测试

```sql
-- macros/test_valid_date_range.sql
{% test valid_date_range(model, column_name, start_date, end_date) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} < '{{ start_date }}'
   OR {{ column_name }} > '{{ end_date }}'

{% endtest %}
```

```yaml
# 使用 Generic 测试
models:
  - name: events
    columns:
      - name: event_date
        tests:
          - valid_date_range:
              start_date: '2020-01-01'
              end_date: '2025-12-31'
```

### Singular 测试

```sql
-- tests/assert_revenue_consistency.sql
-- 测试收入一致性

WITH order_revenue AS (
    SELECT SUM(amount) AS total
    FROM {{ ref('orders') }}
),
payment_revenue AS (
    SELECT SUM(amount) AS total
    FROM {{ ref('payments') }}
)

SELECT
    o.total AS order_total,
    p.total AS payment_total,
    ABS(o.total - p.total) AS difference
FROM order_revenue o
CROSS JOIN payment_revenue p
WHERE ABS(o.total - p.total) > 0.01
```

### dbt 测试执行

```bash
# 运行所有测试
dbt test

# 运行特定模型的测试
dbt test --select users

# 运行特定测试
dbt test --select test_name:unique_users_user_id

# 运行失败的测试
dbt test --select result:fail

# 存储测试失败记录
dbt test --store-failures
```

### dbt Expectations 包

```yaml
# packages.yml
packages:
  - package: calogica/dbt_expectations
    version: 0.9.0
```

```yaml
# 使用 dbt_expectations
models:
  - name: users
    columns:
      - name: email
        tests:
          - dbt_expectations.expect_column_values_to_match_regex:
              regex: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"

      - name: age
        tests:
          - dbt_expectations.expect_column_mean_to_be_between:
              min_value: 18
              max_value: 65

      - name: created_at
        tests:
          - dbt_expectations.expect_row_values_to_have_recent_data:
              datepart: day
              interval: 7
```

## 数据验证规则

### 完整性检查

```python
import pandas as pd

def check_completeness(df: pd.DataFrame, required_columns: list) -> dict:
    """检查数据完整性"""
    results = {}

    # 检查必需列
    missing_columns = set(required_columns) - set(df.columns)
    results['missing_columns'] = list(missing_columns)

    # 检查空值
    null_counts = df[required_columns].isnull().sum()
    results['null_counts'] = null_counts.to_dict()

    # 检查空字符串
    for col in required_columns:
        if df[col].dtype == 'object':
            empty_count = (df[col] == '').sum()
            results[f'{col}_empty_count'] = empty_count

    return results

# 使用示例
required_cols = ['user_id', 'email', 'name']
completeness = check_completeness(df, required_cols)
```

### 准确性检查

```python
def check_accuracy(df: pd.DataFrame) -> dict:
    """检查数据准确性"""
    results = {}

    # 数值范围检查
    if 'age' in df.columns:
        invalid_age = df[(df['age'] < 0) | (df['age'] > 120)]
        results['invalid_age_count'] = len(invalid_age)

    # 格式检查
    if 'email' in df.columns:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        invalid_email = df[~df['email'].str.match(email_pattern, na=False)]
        results['invalid_email_count'] = len(invalid_email)

    # 逻辑检查
    if 'start_date' in df.columns and 'end_date' in df.columns:
        invalid_dates = df[df['start_date'] > df['end_date']]
        results['invalid_date_range_count'] = len(invalid_dates)

    return results
```

### 一致性检查

```python
def check_consistency(df1: pd.DataFrame, df2: pd.DataFrame, key: str) -> dict:
    """检查数据一致性"""
    results = {}

    # 主键一致性
    keys1 = set(df1[key])
    keys2 = set(df2[key])

    results['only_in_df1'] = len(keys1 - keys2)
    results['only_in_df2'] = len(keys2 - keys1)
    results['in_both'] = len(keys1 & keys2)

    # 值一致性
    merged = df1.merge(df2, on=key, suffixes=('_1', '_2'))
    for col in df1.columns:
        if col != key and f'{col}_2' in merged.columns:
            inconsistent = merged[merged[f'{col}_1'] != merged[f'{col}_2']]
            results[f'{col}_inconsistent_count'] = len(inconsistent)

    return results
```

### 及时性检查

```python
from datetime import datetime, timedelta

def check_timeliness(df: pd.DataFrame, timestamp_col: str, max_age_hours: int = 24) -> dict:
    """检查数据及时性"""
    results = {}

    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    now = datetime.now()
    threshold = now - timedelta(hours=max_age_hours)

    # 过期数据
    stale_data = df[df[timestamp_col] < threshold]
    results['stale_count'] = len(stale_data)
    results['stale_percentage'] = len(stale_data) / len(df) * 100

    # 最新数据时间
    results['latest_timestamp'] = df[timestamp_col].max()
    results['oldest_timestamp'] = df[timestamp_col].min()
    results['data_age_hours'] = (now - df[timestamp_col].max()).total_seconds() / 3600

    return results
```

## 数据血缘追踪

### dbt 血缘

```sql
-- models/staging/stg_users.sql
SELECT
    user_id,
    email,
    created_at
FROM {{ source('raw', 'users') }}

-- models/marts/dim_users.sql
SELECT
    user_id,
    email,
    DATE(created_at) AS created_date
FROM {{ ref('stg_users') }}

-- models/marts/fct_orders.sql
SELECT
    o.order_id,
    u.user_id,
    o.amount
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('dim_users') }} u
    ON o.user_id = u.user_id
```

```bash
# 生成血缘图
dbt docs generate
dbt docs serve

# 查看血缘关系
# http://localhost:8080
```

### 自定义血缘追踪

```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class DataLineage:
    """数据血缘"""
    table_name: str
    upstream_tables: List[str]
    transformation: str
    created_at: str

class LineageTracker:
    """血缘追踪器"""

    def __init__(self):
        self.lineage: Dict[str, DataLineage] = {}

    def register(self, table_name: str, upstream: List[str], transformation: str):
        """注册血缘关系"""
        self.lineage[table_name] = DataLineage(
            table_name=table_name,
            upstream_tables=upstream,
            transformation=transformation,
            created_at=datetime.now().isoformat()
        )

    def get_upstream(self, table_name: str, recursive: bool = False) -> List[str]:
        """获取上游表"""
        if table_name not in self.lineage:
            return []

        upstream = self.lineage[table_name].upstream_tables

        if recursive:
            all_upstream = set(upstream)
            for table in upstream:
                all_upstream.update(self.get_upstream(table, recursive=True))
            return list(all_upstream)

        return upstream

    def get_downstream(self, table_name: str) -> List[str]:
        """获取下游表"""
        downstream = []
        for name, lineage in self.lineage.items():
            if table_name in lineage.upstream_tables:
                downstream.append(name)
        return downstream

# 使用示例
tracker = LineageTracker()

tracker.register('stg_users', ['raw.users'], 'SELECT * FROM raw.users')
tracker.register('dim_users', ['stg_users'], 'SELECT user_id, email FROM stg_users')
tracker.register('fct_orders', ['stg_orders', 'dim_users'], 'JOIN transformation')

print(tracker.get_upstream('fct_orders', recursive=True))
# ['stg_orders', 'dim_users', 'stg_users', 'raw.users']
```

## 数据质量监控

### 质量指标计算

```python
import pandas as pd
from typing import Dict

class DataQualityMetrics:
    """数据质量指标"""

    @staticmethod
    def calculate_completeness(df: pd.DataFrame) -> float:
        """完整性得分"""
        total_cells = df.size
        non_null_cells = df.count().sum()
        return (non_null_cells / total_cells) * 100

    @staticmethod
    def calculate_uniqueness(df: pd.DataFrame, key_columns: List[str]) -> float:
        """唯一性得分"""
        total_rows = len(df)
        unique_rows = df[key_columns].drop_duplicates().shape[0]
        return (unique_rows / total_rows) * 100

    @staticmethod
    def calculate_validity(df: pd.DataFrame, rules: Dict) -> float:
        """有效性得分"""
        total_rows = len(df)
        valid_rows = total_rows

        for column, rule in rules.items():
            if rule['type'] == 'range':
                invalid = df[
                    (df[column] < rule['min']) | (df[column] > rule['max'])
                ]
                valid_rows -= len(invalid)
            elif rule['type'] == 'regex':
                invalid = df[~df[column].str.match(rule['pattern'], na=False)]
                valid_rows -= len(invalid)

        return (valid_rows / total_rows) * 100

    @staticmethod
    def calculate_overall_score(metrics: Dict[str, float]) -> float:
        """综合质量得分"""
        weights = {
            'completeness': 0.3,
            'uniqueness': 0.2,
            'validity': 0.3,
            'timeliness': 0.2,
        }

        score = sum(metrics.get(k, 0) * v for k, v in weights.items())
        return score

# 使用示例
metrics = DataQualityMetrics()

completeness = metrics.calculate_completeness(df)
uniqueness = metrics.calculate_uniqueness(df, ['user_id'])
validity = metrics.calculate_validity(df, {
    'age': {'type': 'range', 'min': 0, 'max': 120}
})

overall = metrics.calculate_overall_score({
    'completeness': completeness,
    'uniqueness': uniqueness,
    'validity': validity,
    'timeliness': 95.0,
})

print(f"Overall Quality Score: {overall:.2f}%")
```

### 质量告警

```python
class QualityAlert:
    """质量告警"""

    def __init__(self, thresholds: Dict[str, float]):
        self.thresholds = thresholds

    def check_and_alert(self, metrics: Dict[str, float]) -> List[str]:
        """检查并生成告警"""
        alerts = []

        for metric, value in metrics.items():
            threshold = self.thresholds.get(metric)
            if threshold and value < threshold:
                alerts.append(
                    f"ALERT: {metric} is {value:.2f}%, "
                    f"below threshold {threshold}%"
                )

        return alerts

# 使用示例
alert_system = QualityAlert({
    'completeness': 95.0,
    'uniqueness': 99.0,
    'validity': 98.0,
})

alerts = alert_system.check_and_alert({
    'completeness': 92.5,
    'uniqueness': 99.5,
    'validity': 97.0,
})

for alert in alerts:
    print(alert)
    # 发送通知（Slack/Email/PagerDuty）
```

## Soda Core 集成

### 安装和配置

```bash
# 安装
pip install soda-core-postgres

# 配置
# configuration.yml
data_source my_datasource:
  type: postgres
  host: localhost
  port: 5432
  username: user
  password: pass
  database: mydb
```

### Checks 定义

```yaml
# checks.yml
checks for users:
  - row_count > 100
  - missing_count(user_id) = 0
  - missing_count(email) = 0
  - duplicate_count(user_id) = 0
  - duplicate_count(email) = 0
  - invalid_count(email) = 0:
      valid format: email
  - invalid_count(age) = 0:
      valid min: 0
      valid max: 120
  - values in (status) must be in ['active', 'inactive', 'pending']
  - freshness(created_at) < 1d
```

### 执行检查

```python
from soda.scan import Scan

# 创建扫描
scan = Scan()
scan.set_data_source_name("my_datasource")
scan.add_configuration_yaml_file("configuration.yml")
scan.add_sodacl_yaml_file("checks.yml")

# 执行扫描
scan.execute()

# 检查结果
if scan.has_check_fails():
    print("Quality checks failed!")
    for check in scan.get_checks_fail():
        print(f"  - {check}")
else:
    print("All quality checks passed!")
```

## 最佳实践

### 分层验证策略

```python
# 1. 源数据验证
def validate_source(df: pd.DataFrame):
    """源数据验证"""
    assert not df.empty, "Source data is empty"
    assert df['id'].is_unique, "Duplicate IDs in source"

# 2. 转换验证
def validate_transformation(input_df: pd.DataFrame, output_df: pd.DataFrame):
    """转换验证"""
    assert len(output_df) <= len(input_df), "Row count increased"
    assert set(output_df['id']).issubset(set(input_df['id'])), "New IDs appeared"

# 3. 目标验证
def validate_target(df: pd.DataFrame):
    """目标验证"""
    assert df['amount'].sum() > 0, "Total amount is zero"
    assert df['date'].max() >= pd.Timestamp.now() - pd.Timedelta(days=1), "Data is stale"
```

### 持续质量监控

```python
import schedule
import time

def run_quality_checks():
    """运行质量检查"""
    df = load_data()

    metrics = {
        'completeness': calculate_completeness(df),
        'validity': calculate_validity(df),
        'timeliness': calculate_timeliness(df),
    }

    # 记录指标
    log_metrics(metrics)

    # 检查告警
    alerts = check_alerts(metrics)
    if alerts:
        send_notifications(alerts)

# 定时执行
schedule.every(1).hours.do(run_quality_checks)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 质量报告生成

```python
def generate_quality_report(df: pd.DataFrame) -> str:
    """生成质量报告"""
    report = []

    report.append("# Data Quality Report")
    report.append(f"Generated at: {datetime.now()}")
    report.append(f"\n## Dataset Overview")
    report.append(f"- Total Rows: {len(df)}")
    report.append(f"- Total Columns: {len(df.columns)}")

    report.append(f"\n## Completeness")
    null_counts = df.isnull().sum()
    for col, count in null_counts.items():
        if count > 0:
            pct = (count / len(df)) * 100
            report.append(f"- {col}: {count} nulls ({pct:.2f}%)")

    report.append(f"\n## Duplicates")
    duplicates = df.duplicated().sum()
    report.append(f"- Total Duplicates: {duplicates}")

    return "\n".join(report)
```

## 工具对比

| 工具 | 优势 | 适用场景 |
|------|------|----------|
| Great Expectations | 丰富的 Expectations、Data Docs | Python 生态、复杂验证 |
| dbt | SQL 原生、血缘追踪 | 数据仓库、转换测试 |
| Soda Core | 简洁的 YAML 配置 | 快速验证、CI/CD |
| Apache Griffin | 大数据质量 | Hadoop/Spark 生态 |
| Deequ | Spark 原生 | 大规模数据验证 |

## 工具清单

| 工具 | 用途 | 推荐场景 |
|------|------|----------|
| Great Expectations | 数据验证框架 | Python 数据管道 |
| dbt | 数据转换测试 | SQL 数据仓库 |
| Soda Core | 数据质量检查 | 轻量级验证 |
| Apache Griffin | 大数据质量 | Hadoop 生态 |
| Deequ | Spark 数据质量 | 大规模数据 |
| Monte Carlo | 数据可观测性 | 企业级监控 |
| Datafold | 数据 Diff | 变更验证 |

## 触发词

数据质量、Great Expectations、dbt、数据验证、数据测试、完整性、准确性、一致性、数据血缘、质量监控
