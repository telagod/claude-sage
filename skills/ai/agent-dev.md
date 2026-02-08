---
name: agent-dev
description: AI Agent 开发。多 Agent 编排、工具调用、RAG 系统、Prompt 工程。当用户提到 Agent、RAG、Prompt、LangChain、向量数据库时使用。
---

# 🔮 丹鼎秘典 · AI Agent 开发


## Agent 架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Agent 系统                              │
├─────────────────────────────────────────────────────────────┤
│  用户输入 → 意图理解 → 规划 → 执行 → 反思 → 输出            │
│              │          │      │      │                      │
│           Prompt     Planner  Tools  Memory                  │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. Prompt 工程

```yaml
结构化 Prompt:
  - System: 角色定义、能力边界、行为规范
  - Context: 背景信息、相关知识
  - Task: 具体任务、输出格式
  - Examples: Few-shot 示例

技巧:
  - 明确角色和边界
  - 分步骤引导思考
  - 提供输出格式示例
  - 设置安全护栏
```

### 2. 工具调用

```python
# 工具定义
tools = [
    {
        "name": "search",
        "description": "搜索知识库",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"}
            },
            "required": ["query"]
        }
    }
]

# 工具执行
def execute_tool(name: str, args: dict) -> str:
    if name == "search":
        return search_knowledge_base(args["query"])
    raise ValueError(f"Unknown tool: {name}")
```

### 3. 记忆系统

```yaml
短期记忆:
  - 对话历史
  - 当前任务上下文
  - 工具调用结果

长期记忆:
  - 向量数据库存储
  - 用户偏好
  - 历史交互摘要

记忆管理:
  - 滑动窗口
  - 摘要压缩
  - 重要性排序
```

## RAG 系统

### 架构

```
文档 → 分块 → 嵌入 → 向量库
                        ↓
查询 → 嵌入 → 检索 → 重排序 → 生成
```

### 实现

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# 文档处理
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", "。", "，", " "]
)
chunks = splitter.split_documents(documents)

# 向量存储
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(chunks, embeddings)

# 检索
retriever = vectorstore.as_retriever(
    search_type="mmr",  # 最大边际相关性
    search_kwargs={"k": 5, "fetch_k": 20}
)
```

### 优化策略

```yaml
分块策略:
  - 语义分块 vs 固定长度
  - 重叠避免信息丢失
  - 保留元数据

检索优化:
  - 混合检索 (关键词 + 向量)
  - 重排序 (Reranker)
  - 查询扩展

生成优化:
  - 引用来源
  - 置信度评估
  - 幻觉检测
```

## 多 Agent 编排

### 模式

```yaml
顺序执行:
  Agent A → Agent B → Agent C

并行执行:
  Agent A ─┬─→ Agent B ─┬─→ 汇总
           └─→ Agent C ─┘

层级结构:
  Orchestrator
      ├── Planner Agent
      ├── Executor Agent
      └── Reviewer Agent

对话式:
  Agent A ←→ Agent B (多轮交互)
```

### 实现示例

```python
class Orchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.reviewer = ReviewerAgent()

    async def run(self, task: str) -> str:
        # 规划
        plan = await self.planner.plan(task)

        # 执行
        results = []
        for step in plan.steps:
            result = await self.executor.execute(step)
            results.append(result)

        # 审查
        final = await self.reviewer.review(task, results)
        return final
```

## 评估与监控

```yaml
评估维度:
  - 准确性: 答案正确率
  - 相关性: 检索质量
  - 完整性: 信息覆盖
  - 一致性: 多次回答稳定性

监控指标:
  - 延迟 (P50/P95/P99)
  - Token 消耗
  - 工具调用成功率
  - 用户满意度
```

## 框架选择

```yaml
LangChain:
  - 优点: 生态丰富，组件多
  - 缺点: 抽象层多，调试难
  - 适合: 快速原型

LlamaIndex:
  - 优点: RAG 专精
  - 缺点: Agent 能力弱
  - 适合: 知识库应用

原生实现:
  - 优点: 完全可控
  - 缺点: 开发成本高
  - 适合: 生产系统
```

## 最佳实践

```yaml
开发:
  - Prompt 版本控制
  - 单元测试覆盖
  - 成本预算控制
  - 降级策略

部署:
  - 流式输出
  - 超时处理
  - 重试机制
  - 缓存策略

安全:
  - 输入验证
  - 输出过滤
  - 权限控制
  - 审计日志
```

---

