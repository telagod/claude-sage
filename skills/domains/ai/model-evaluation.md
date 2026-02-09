---
name: model-evaluation
description: AI 模型评估技术。RAGAS、LLM-as-Judge、评估指标、基准测试、A/B 测试。当用户提到模型评估、RAGAS、LLM-as-Judge、基准测试、评估指标、模型对比时使用。
---

# 📊 天机秘典 · 模型评估 (Model Evaluation)

## 评估体系

```
离线评估 → 在线评估 → 持续监控
    │          │           │
    ├─ 基准测试  ├─ A/B 测试  ├─ 指标追踪
    ├─ 人工评估  ├─ 用户反馈  ├─ 异常检测
    └─ 自动评估  └─ 实时分析  └─ 质量报告
```

### 评估维度
| 维度 | 指标 | 适用场景 |
|------|------|----------|
| 准确性 | Accuracy, F1, Precision, Recall | 分类、NER |
| 相关性 | Relevance, Context Precision | RAG、检索 |
| 忠实性 | Faithfulness, Hallucination Rate | 生成任务 |
| 连贯性 | Coherence, Fluency | 文本生成 |
| 效率 | Latency, Throughput, Cost | 生产部署 |

## RAGAS 框架

### 核心指标
```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from datasets import Dataset

# 准备评估数据
data = {
    "question": ["什么是 RAG？", "如何优化检索？"],
    "answer": ["RAG 是检索增强生成...", "可以使用混合检索..."],
    "contexts": [
        ["RAG 结合了检索和生成...", "向量数据库用于存储..."],
        ["混合检索结合向量和关键词...", "重排可以提升相关性..."]
    ],
    "ground_truth": ["RAG 是一种结合检索和生成的技术", "使用混合检索和重排"]
}

dataset = Dataset.from_dict(data)

# 评估
result = evaluate(
    dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    ],
)

print(result)
```

### Faithfulness（忠实性）
```python
from ragas.metrics import faithfulness

# 衡量答案是否基于提供的上下文
# 分数 0-1，越高越好

# 示例
question = "Python 的创始人是谁？"
context = ["Python 由 Guido van Rossum 在 1991 年创建"]
answer = "Python 由 Guido van Rossum 创建"  # 高忠实性

# 低忠实性示例
bad_answer = "Python 由 James Gosling 创建"  # 编造信息

score = faithfulness.score(
    question=question,
    answer=answer,
    contexts=context
)
```

### Answer Relevancy（答案相关性）
```python
from ragas.metrics import answer_relevancy

# 衡量答案与问题的相关程度
# 分数 0-1，越高越好

question = "如何防御 SQL 注入？"
answer = "使用参数化查询和 ORM 框架可以有效防御 SQL 注入"  # 高相关性
bad_answer = "SQL 是一种数据库查询语言"  # 低相关性

score = answer_relevancy.score(
    question=question,
    answer=answer
)
```

### Context Precision（上下文精确度）
```python
from ragas.metrics import context_precision

# 衡量检索到的上下文中相关信息的比例
# 分数 0-1，越高越好（相关文档排在前面）

question = "什么是向量数据库？"
contexts = [
    "向量数据库用于存储和检索高维向量",  # 相关
    "Pinecone 是一个向量数据库",  # 相关
    "Python 是一种编程语言",  # 不相关
]
ground_truth = "向量数据库是专门用于存储和检索向量的数据库"

score = context_precision.score(
    question=question,
    contexts=contexts,
    ground_truth=ground_truth
)
```

### Context Recall（上下文召回率）
```python
from ragas.metrics import context_recall

# 衡量检索到的上下文是否包含回答问题所需的所有信息
# 分数 0-1，越高越好

question = "RAG 的优势是什么？"
contexts = [
    "RAG 可以减少幻觉",
    "RAG 可以使用最新信息"
]
ground_truth = "RAG 的优势包括减少幻觉、使用最新信息、可解释性强"

# 召回率 = 2/3 = 0.67（缺少"可解释性强"）
```

### 完整 RAG 评估流程
```python
from langchain.chains import RetrievalQA
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

class RAGEvaluator:
    def __init__(self, qa_chain, test_dataset):
        self.qa_chain = qa_chain
        self.test_dataset = test_dataset

    def run_evaluation(self):
        results = []

        for item in self.test_dataset:
            # 执行 RAG
            response = self.qa_chain({
                "query": item["question"]
            })

            results.append({
                "question": item["question"],
                "answer": response["result"],
                "contexts": [doc.page_content for doc in response["source_documents"]],
                "ground_truth": item["ground_truth"]
            })

        # RAGAS 评估
        dataset = Dataset.from_dict({
            "question": [r["question"] for r in results],
            "answer": [r["answer"] for r in results],
            "contexts": [r["contexts"] for r in results],
            "ground_truth": [r["ground_truth"] for r in results]
        })

        scores = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy]
        )

        return scores

# 使用
evaluator = RAGEvaluator(qa_chain, test_data)
scores = evaluator.run_evaluation()
print(f"Faithfulness: {scores['faithfulness']:.3f}")
print(f"Answer Relevancy: {scores['answer_relevancy']:.3f}")
```

## LLM-as-Judge

### 基础评估器
```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class LLMJudge:
    def __init__(self, model="gpt-4"):
        self.llm = ChatOpenAI(model=model, temperature=0)

    def evaluate_answer(self, question: str, answer: str, criteria: str):
        prompt = ChatPromptTemplate.from_template("""
你是一位专业的评估专家。请评估以下答案的质量。

问题: {question}

答案: {answer}

评估标准: {criteria}

请从以下维度评分（1-5 分）:
1. 准确性: 信息是否正确
2. 完整性: 是否充分回答问题
3. 清晰度: 表达是否清晰易懂
4. 相关性: 是否切题

输出格式:
{{
  "accuracy": <分数>,
  "completeness": <分数>,
  "clarity": <分数>,
  "relevance": <分数>,
  "overall": <总分>,
  "feedback": "<详细反馈>"
}}
""")

        chain = prompt | self.llm
        result = chain.invoke({
            "question": question,
            "answer": answer,
            "criteria": criteria
        })

        return json.loads(result.content)

# 使用
judge = LLMJudge()
score = judge.evaluate_answer(
    question="什么是 RAG？",
    answer="RAG 是检索增强生成技术...",
    criteria="技术准确性和清晰度"
)
```

### 成对比较
```python
def pairwise_comparison(question: str, answer_a: str, answer_b: str):
    prompt = f"""
问题: {question}

答案 A: {answer_a}

答案 B: {answer_b}

请比较两个答案的质量，从以下维度评估:
1. 准确性
2. 完整性
3. 清晰度

选择更好的答案（A 或 B），并说明理由。

输出格式:
{{
  "winner": "A" or "B",
  "reason": "<理由>",
  "confidence": <0-1>
}}
"""

    result = llm.predict(prompt)
    return json.loads(result)

# ELO 排名系统
class ELORanking:
    def __init__(self, k=32):
        self.k = k
        self.ratings = {}

    def update_ratings(self, model_a: str, model_b: str, winner: str):
        ra = self.ratings.get(model_a, 1500)
        rb = self.ratings.get(model_b, 1500)

        ea = 1 / (1 + 10 ** ((rb - ra) / 400))
        eb = 1 / (1 + 10 ** ((ra - rb) / 400))

        if winner == model_a:
            sa, sb = 1, 0
        elif winner == model_b:
            sa, sb = 0, 1
        else:
            sa, sb = 0.5, 0.5

        self.ratings[model_a] = ra + self.k * (sa - ea)
        self.ratings[model_b] = rb + self.k * (sb - eb)

    def get_leaderboard(self):
        return sorted(self.ratings.items(), key=lambda x: x[1], reverse=True)
```

### 多维度评估
```python
EVALUATION_DIMENSIONS = {
    "correctness": "答案是否准确无误",
    "completeness": "是否完整回答了问题",
    "conciseness": "表达是否简洁",
    "relevance": "是否切题",
    "helpfulness": "对用户是否有帮助",
    "safety": "是否安全无害",
}

def multi_dimensional_eval(question: str, answer: str):
    results = {}

    for dimension, description in EVALUATION_DIMENSIONS.items():
        prompt = f"""
评估维度: {dimension} - {description}

问题: {question}
答案: {answer}

请对该维度评分（1-5 分）并说明理由。

输出格式:
{{
  "score": <分数>,
  "reason": "<理由>"
}}
"""
        result = llm.predict(prompt)
        results[dimension] = json.loads(result)

    # 计算加权总分
    weights = {
        "correctness": 0.3,
        "completeness": 0.2,
        "conciseness": 0.1,
        "relevance": 0.2,
        "helpfulness": 0.15,
        "safety": 0.05,
    }

    total_score = sum(
        results[dim]["score"] * weights[dim]
        for dim in EVALUATION_DIMENSIONS
    )

    results["total_score"] = total_score
    return results
```

## 基准测试

### MMLU（大规模多任务语言理解）
```python
from datasets import load_dataset

# 加载 MMLU 数据集
dataset = load_dataset("cais/mmlu", "all")

def evaluate_mmlu(model, subject="all", num_samples=100):
    correct = 0
    total = 0

    for item in dataset["test"].select(range(num_samples)):
        question = item["question"]
        choices = item["choices"]
        correct_answer = item["answer"]

        # 构建 Prompt
        prompt = f"""
问题: {question}

选项:
A. {choices[0]}
B. {choices[1]}
C. {choices[2]}
D. {choices[3]}

请选择正确答案（仅输出 A/B/C/D）:
"""

        response = model.predict(prompt).strip()

        if response == ["A", "B", "C", "D"][correct_answer]:
            correct += 1
        total += 1

    accuracy = correct / total
    return accuracy

# 使用
accuracy = evaluate_mmlu(llm, num_samples=100)
print(f"MMLU Accuracy: {accuracy:.2%}")
```

### HumanEval（代码生成）
```python
from human_eval.data import read_problems
from human_eval.evaluation import evaluate_functional_correctness

def evaluate_code_generation(model):
    problems = read_problems()

    samples = []
    for task_id, problem in problems.items():
        prompt = problem["prompt"]

        # 生成代码
        code = model.predict(f"完成以下 Python 函数:\n\n{prompt}")

        samples.append({
            "task_id": task_id,
            "completion": code
        })

    # 保存结果
    with open("samples.jsonl", "w") as f:
        for sample in samples:
            f.write(json.dumps(sample) + "\n")

    # 评估
    results = evaluate_functional_correctness("samples.jsonl")
    return results

# Pass@k 指标
# Pass@1: 生成 1 次代码的通过率
# Pass@10: 生成 10 次代码中至少 1 次通过的概率
```

### GSM8K（数学推理）
```python
from datasets import load_dataset

dataset = load_dataset("gsm8k", "main")

def evaluate_gsm8k(model, num_samples=100):
    correct = 0

    for item in dataset["test"].select(range(num_samples)):
        question = item["question"]
        answer = item["answer"]

        # 提取正确答案
        correct_answer = int(answer.split("####")[1].strip())

        # 使用 CoT
        prompt = f"""
问题: {question}

让我们一步步思考:
"""

        response = model.predict(prompt)

        # 提取模型答案
        try:
            model_answer = extract_number(response)
            if model_answer == correct_answer:
                correct += 1
        except:
            pass

    accuracy = correct / num_samples
    return accuracy
```

### 自定义基准测试
```python
class CustomBenchmark:
    def __init__(self, test_cases: list):
        self.test_cases = test_cases

    def run(self, model):
        results = []

        for case in self.test_cases:
            start_time = time.time()

            response = model.predict(case["input"])

            latency = time.time() - start_time

            # 评估
            score = self._evaluate(
                response,
                case["expected_output"],
                case["criteria"]
            )

            results.append({
                "input": case["input"],
                "output": response,
                "expected": case["expected_output"],
                "score": score,
                "latency": latency
            })

        return self._aggregate_results(results)

    def _evaluate(self, output, expected, criteria):
        # 使用 LLM-as-Judge
        judge = LLMJudge()
        return judge.evaluate(output, expected, criteria)

    def _aggregate_results(self, results):
        return {
            "avg_score": np.mean([r["score"] for r in results]),
            "avg_latency": np.mean([r["latency"] for r in results]),
            "pass_rate": sum(r["score"] >= 0.8 for r in results) / len(results),
            "details": results
        }
```

## 评估指标

### 分类指标
```python
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)

def evaluate_classification(y_true, y_pred):
    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average='weighted'
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": confusion_matrix(y_true, y_pred),
        "report": classification_report(y_true, y_pred)
    }
```

### 生成指标
```python
from rouge import Rouge
from nltk.translate.bleu_score import sentence_bleu

def evaluate_generation(predictions, references):
    rouge = Rouge()

    # ROUGE 分数
    rouge_scores = rouge.get_scores(predictions, references, avg=True)

    # BLEU 分数
    bleu_scores = []
    for pred, ref in zip(predictions, references):
        score = sentence_bleu([ref.split()], pred.split())
        bleu_scores.append(score)

    return {
        "rouge-1": rouge_scores["rouge-1"]["f"],
        "rouge-2": rouge_scores["rouge-2"]["f"],
        "rouge-l": rouge_scores["rouge-l"]["f"],
        "bleu": np.mean(bleu_scores)
    }
```

### 检索指标
```python
def evaluate_retrieval(retrieved_docs, relevant_docs, k=5):
    # Precision@K
    precision_at_k = len(set(retrieved_docs[:k]) & set(relevant_docs)) / k

    # Recall@K
    recall_at_k = len(set(retrieved_docs[:k]) & set(relevant_docs)) / len(relevant_docs)

    # MRR (Mean Reciprocal Rank)
    for i, doc in enumerate(retrieved_docs, 1):
        if doc in relevant_docs:
            mrr = 1 / i
            break
    else:
        mrr = 0

    # NDCG (Normalized Discounted Cumulative Gain)
    dcg = sum(
        (1 if retrieved_docs[i] in relevant_docs else 0) / np.log2(i + 2)
        for i in range(k)
    )
    idcg = sum(1 / np.log2(i + 2) for i in range(min(k, len(relevant_docs))))
    ndcg = dcg / idcg if idcg > 0 else 0

    return {
        "precision@k": precision_at_k,
        "recall@k": recall_at_k,
        "mrr": mrr,
        "ndcg@k": ndcg
    }
```

## A/B 测试

### 在线 A/B 测试框架
```python
import random
from dataclasses import dataclass
from typing import Dict

@dataclass
class Variant:
    name: str
    model: Any
    traffic_ratio: float

class ABTest:
    def __init__(self, variants: list[Variant]):
        self.variants = variants
        self.results = {v.name: {"count": 0, "scores": []} for v in variants}

    def get_variant(self, user_id: str) -> Variant:
        # 一致性哈希分流
        hash_value = hash(user_id) % 100
        cumulative = 0

        for variant in self.variants:
            cumulative += variant.traffic_ratio * 100
            if hash_value < cumulative:
                return variant

        return self.variants[-1]

    def log_result(self, variant_name: str, score: float):
        self.results[variant_name]["count"] += 1
        self.results[variant_name]["scores"].append(score)

    def get_statistics(self):
        stats = {}
        for name, data in self.results.items():
            if data["count"] > 0:
                stats[name] = {
                    "count": data["count"],
                    "mean": np.mean(data["scores"]),
                    "std": np.std(data["scores"]),
                    "p95": np.percentile(data["scores"], 95)
                }
        return stats

# 使用
ab_test = ABTest([
    Variant("gpt-4", gpt4_model, 0.5),
    Variant("claude-3", claude_model, 0.5)
])

# 处理请求
user_id = "user_123"
variant = ab_test.get_variant(user_id)
response = variant.model.predict(query)

# 记录结果（用户反馈或自动评估）
score = evaluate_response(response)
ab_test.log_result(variant.name, score)

# 查看统计
print(ab_test.get_statistics())
```

### 统计显著性检验
```python
from scipy import stats

def check_significance(results_a, results_b, alpha=0.05):
    # t 检验
    t_stat, p_value = stats.ttest_ind(results_a, results_b)

    is_significant = p_value < alpha

    # 效应量（Cohen's d）
    pooled_std = np.sqrt(
        (np.std(results_a) ** 2 + np.std(results_b) ** 2) / 2
    )
    cohens_d = (np.mean(results_a) - np.mean(results_b)) / pooled_std

    return {
        "p_value": p_value,
        "is_significant": is_significant,
        "cohens_d": cohens_d,
        "interpretation": "large" if abs(cohens_d) > 0.8 else "medium" if abs(cohens_d) > 0.5 else "small"
    }
```

## 持续监控

### 实时指标追踪
```python
from prometheus_client import Counter, Histogram, Gauge

# 定义指标
request_count = Counter('llm_requests_total', 'Total LLM requests', ['model', 'status'])
latency = Histogram('llm_latency_seconds', 'LLM latency', ['model'])
quality_score = Gauge('llm_quality_score', 'LLM quality score', ['model'])

class MonitoredLLM:
    def __init__(self, model, model_name):
        self.model = model
        self.model_name = model_name

    def predict(self, prompt: str):
        start_time = time.time()

        try:
            response = self.model.predict(prompt)
            request_count.labels(model=self.model_name, status='success').inc()

            # 记录延迟
            latency.labels(model=self.model_name).observe(time.time() - start_time)

            # 评估质量
            score = self._evaluate_quality(response)
            quality_score.labels(model=self.model_name).set(score)

            return response

        except Exception as e:
            request_count.labels(model=self.model_name, status='error').inc()
            raise
```

### 异常检测
```python
class AnomalyDetector:
    def __init__(self, window_size=100, threshold=2.0):
        self.window_size = window_size
        self.threshold = threshold
        self.history = []

    def check(self, value: float) -> bool:
        self.history.append(value)

        if len(self.history) < self.window_size:
            return False

        # 保持窗口大小
        self.history = self.history[-self.window_size:]

        # Z-score 异常检测
        mean = np.mean(self.history)
        std = np.std(self.history)

        if std == 0:
            return False

        z_score = abs((value - mean) / std)

        return z_score > self.threshold

# 使用
detector = AnomalyDetector()

for score in quality_scores:
    if detector.check(score):
        alert(f"Quality anomaly detected: {score}")
```

## 评估工具

| 工具 | 类型 | 功能 |
|------|------|------|
| RAGAS | 框架 | RAG 专用评估 |
| LangSmith | 平台 | LLM 应用监控 |
| Phoenix | 开源 | 可观测性平台 |
| PromptTools | 库 | Prompt 测试 |
| OpenAI Evals | 框架 | 模型评估 |
| Weights & Biases | 平台 | 实验追踪 |

## 最佳实践

- ✅ 多维度评估：准确性、相关性、忠实性、效率
- ✅ 自动化评估：使用 RAGAS、LLM-as-Judge
- ✅ 人工抽检：定期人工审核样本
- ✅ 基准测试：使用标准数据集对比
- ✅ A/B 测试：在线对比不同版本
- ✅ 持续监控：实时追踪质量指标
- ✅ 版本管理：记录模型和 Prompt 版本
- ✅ 反馈闭环：收集用户反馈改进
- ❌ 避免：单一指标、无基准、无监控

---
