---
name: prompt-engineering
description: Prompt 工程技术。Zero-shot、Few-shot、CoT、ReAct、ToT、模板设计、优化技巧。当用户提到 Prompt 工程、Few-shot、CoT、思维链、ReAct、提示词优化时使用。
---

# 🎨 符箓秘典 · Prompt 工程 (Prompt Engineering)

## Prompt 模式

```
Zero-shot → Few-shot → CoT → Self-Consistency → ToT → ReAct
   │          │         │           │              │      │
   └─ 直接 ───┴─ 示例 ──┴─ 推理 ─────┴─ 多路 ────────┴─ 行动
```

### 模式对比
| 模式 | 复杂度 | 准确性 | Token 消耗 | 适用场景 |
|------|--------|--------|------------|----------|
| Zero-shot | 低 | 中 | 低 | 简单任务、通用问题 |
| Few-shot | 中 | 高 | 中 | 格式化输出、分类 |
| CoT | 中 | 高 | 中 | 推理、数学、逻辑 |
| Self-Consistency | 高 | 极高 | 高 | 关键决策 |
| ToT | 极高 | 极高 | 极高 | 复杂规划 |
| ReAct | 高 | 高 | 高 | 工具调用、Agent |

## Zero-shot Prompting

### 基础模板
```python
prompt = """
任务: {task_description}

输入: {input}

输出:
"""

# 示例
prompt = """
任务: 将以下文本分类为正面、负面或中性情感。

输入: 这个产品质量不错，但价格有点贵。

输出:
"""
```

### 指令优化
```python
# ❌ 模糊指令
"告诉我关于 Python 的事情"

# ✅ 清晰指令
"""
请用 3 个要点总结 Python 的核心特性:
1. 语言特点
2. 主要应用领域
3. 生态系统优势

每个要点不超过 50 字。
"""
```

### 角色设定
```python
system_prompt = """
你是一位资深的 Python 安全专家，拥有 10 年渗透测试经验。
你的回答应该:
- 技术准确，引用 CVE 编号
- 提供可执行的代码示例
- 强调安全最佳实践
"""

user_prompt = "如何防御 SQL 注入？"
```

## Few-shot Prompting

### 标准 Few-shot
```python
prompt = """
将产品评论分类为正面或负面。

示例 1:
评论: 这个耳机音质很棒，佩戴舒适。
分类: 正面

示例 2:
评论: 电池续航太差，用不到一天就没电了。
分类: 负面

示例 3:
评论: 包装精美，但产品质量一般。
分类: 负面

现在分类:
评论: {new_review}
分类:
"""
```

### Few-shot 示例选择
```python
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

# 示例库
examples = [
    {"input": "2+2", "output": "4"},
    {"input": "3*5", "output": "15"},
    {"input": "10/2", "output": "5"},
    {"input": "sqrt(16)", "output": "4"},
]

# 语义相似度选择器
example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples,
    OpenAIEmbeddings(),
    Chroma,
    k=2  # 选择最相似的 2 个示例
)

# 动态 Few-shot
example_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="输入: {input}\n输出: {output}"
)

prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
    prefix="计算以下表达式:",
    suffix="输入: {input}\n输出:",
    input_variables=["input"]
)

print(prompt.format(input="sqrt(25)"))
```

### 结构化输出
```python
prompt = """
从文本中提取实体，输出 JSON 格式。

示例:
文本: 张三在北京的阿里巴巴工作，年薪 50 万。
输出:
{
  "person": "张三",
  "location": "北京",
  "organization": "阿里巴巴",
  "salary": "50万"
}

现在提取:
文本: {text}
输出:
"""
```

## Chain-of-Thought (CoT)

### 标准 CoT
```python
prompt = """
问题: 一个班级有 23 名学生。如果每个学生需要 3 支铅笔，
老师已经有 17 支铅笔，还需要买多少支？

让我们一步步思考:
1. 总共需要的铅笔数 = 23 × 3 = 69 支
2. 已有铅笔数 = 17 支
3. 还需要购买 = 69 - 17 = 52 支

答案: 52 支
"""
```

### Zero-shot CoT
```python
# 神奇的咒语: "Let's think step by step"
prompt = """
问题: {question}

让我们一步步思考:
"""

# 中文版本
prompt = """
问题: {question}

让我们逐步分析:
"""
```

### Few-shot CoT
```python
prompt = """
问题: 咖啡店有 9 杯咖啡，卖出 5 杯后又做了 7 杯，现在有多少杯？

推理过程:
1. 初始: 9 杯
2. 卖出后: 9 - 5 = 4 杯
3. 又做了: 4 + 7 = 11 杯

答案: 11 杯

---

问题: 停车场有 12 辆车，开走 3 辆，又来了 8 辆，现在有多少辆？

推理过程:
1. 初始: 12 辆
2. 开走后: 12 - 3 = 9 辆
3. 又来了: 9 + 8 = 17 辆

答案: 17 辆

---

问题: {new_question}

推理过程:
"""
```

### Self-Consistency CoT
```python
from collections import Counter

def self_consistency_cot(question: str, n_samples: int = 5):
    prompt = f"""
问题: {question}

让我们一步步思考:
"""

    answers = []
    for _ in range(n_samples):
        response = llm.predict(prompt, temperature=0.7)
        # 提取最终答案
        answer = extract_final_answer(response)
        answers.append(answer)

    # 多数投票
    most_common = Counter(answers).most_common(1)[0][0]
    return most_common
```

## ReAct (Reasoning + Acting)

### ReAct 模板
```python
prompt = """
你可以使用以下工具:
- Search[query]: 搜索信息
- Calculate[expression]: 计算数学表达式
- Finish[answer]: 返回最终答案

使用格式:
Thought: 我需要做什么
Action: 工具名[参数]
Observation: 工具返回结果
... (重复 Thought/Action/Observation)
Thought: 我现在知道答案了
Action: Finish[最终答案]

问题: 埃菲尔铁塔的高度是多少米？它比自由女神像高多少？

Thought: 我需要先查询埃菲尔铁塔的高度
Action: Search[埃菲尔铁塔高度]
Observation: 埃菲尔铁塔高 330 米（含天线）

Thought: 现在需要查询自由女神像的高度
Action: Search[自由女神像高度]
Observation: 自由女神像高 93 米（含底座）

Thought: 现在可以计算差值
Action: Calculate[330 - 93]
Observation: 237

Thought: 我现在知道答案了
Action: Finish[埃菲尔铁塔高 330 米，比自由女神像高 237 米]
"""
```

### LangChain ReAct Agent
```python
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.tools import DuckDuckGoSearchRun
from langchain.utilities import PythonREPL

# 定义工具
search = DuckDuckGoSearchRun()
python_repl = PythonREPL()

tools = [
    Tool(
        name="Search",
        func=search.run,
        description="搜索互联网信息"
    ),
    Tool(
        name="Python",
        func=python_repl.run,
        description="执行 Python 代码进行计算"
    )
]

# 初始化 ReAct Agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.REACT_DOCSTORE,
    verbose=True,
    max_iterations=5
)

result = agent.run("2024 年奥运会在哪里举办？有多少个国家参加？")
```

## Tree-of-Thoughts (ToT)

### ToT 实现
```python
class TreeOfThoughts:
    def __init__(self, llm, max_depth=3, beam_width=3):
        self.llm = llm
        self.max_depth = max_depth
        self.beam_width = beam_width

    def solve(self, problem: str):
        # 1. 生成初始思路
        thoughts = self._generate_thoughts(problem, depth=0)

        # 2. 评估思路
        scored_thoughts = self._evaluate_thoughts(problem, thoughts)

        # 3. 选择最佳路径（Beam Search）
        best_thoughts = sorted(scored_thoughts, key=lambda x: x[1], reverse=True)[:self.beam_width]

        # 4. 递归扩展
        if self.max_depth > 1:
            for thought, score in best_thoughts:
                sub_problem = f"{problem}\n已有思路: {thought}\n继续推理:"
                return self.solve(sub_problem)

        return best_thoughts[0][0]

    def _generate_thoughts(self, problem: str, depth: int):
        prompt = f"""
问题: {problem}

生成 3 个不同的解决思路:
1.
2.
3.
"""
        response = self.llm.predict(prompt)
        return self._parse_thoughts(response)

    def _evaluate_thoughts(self, problem: str, thoughts: list):
        scored = []
        for thought in thoughts:
            prompt = f"""
问题: {problem}
思路: {thought}

评估这个思路的质量（0-10 分）:
- 逻辑性
- 可行性
- 完整性

分数:
"""
            score = float(self.llm.predict(prompt).strip())
            scored.append((thought, score))
        return scored
```

## 模板设计

### System/User/Assistant 结构
```python
messages = [
    {
        "role": "system",
        "content": "你是一位专业的 Python 开发者，擅长代码审查和优化。"
    },
    {
        "role": "user",
        "content": "请审查这段代码:\n```python\n{code}\n```"
    },
    {
        "role": "assistant",
        "content": "我会从以下方面审查:\n1. 代码质量\n2. 性能优化\n3. 安全问题"
    },
    {
        "role": "user",
        "content": "重点关注安全问题"
    }
]
```

### 分隔符与结构化
```python
prompt = """
### 指令
将以下代码转换为 TypeScript。

### 输入代码
```python
{python_code}
```

### 输出要求
1. 保持原有逻辑
2. 添加类型注解
3. 使用 ES6+ 语法

### 输出代码
```typescript
"""
```

### 变量插值
```python
from langchain.prompts import PromptTemplate

template = """
作为 {role}，请完成以下任务:

任务: {task}
上下文: {context}
约束条件:
{constraints}

输出格式: {output_format}
"""

prompt = PromptTemplate(
    input_variables=["role", "task", "context", "constraints", "output_format"],
    template=template
)

formatted = prompt.format(
    role="安全工程师",
    task="分析漏洞",
    context="Web 应用",
    constraints="- 仅分析 OWASP Top 10\n- 提供修复建议",
    output_format="JSON"
)
```

## 优化技巧

### 清晰性原则
```python
# ❌ 模糊
"写一些关于 AI 的东西"

# ✅ 清晰
"""
写一篇 500 字的文章，介绍 AI 在医疗领域的应用。
包含:
1. 疾病诊断
2. 药物研发
3. 个性化治疗
每个部分约 150 字。
"""
```

### 分步指令
```python
prompt = """
请按以下步骤分析代码:

步骤 1: 识别代码的主要功能
步骤 2: 列出潜在的安全问题
步骤 3: 对每个问题提供修复建议
步骤 4: 给出优化后的代码

代码:
```python
{code}
```

开始分析:
"""
```

### 约束与边界
```python
prompt = """
生成一个 Python 函数，满足以下要求:

功能: 计算斐波那契数列第 n 项

约束:
- 使用递归实现
- 添加缓存优化
- 包含类型注解
- 添加 docstring
- 处理边界情况 (n < 0)

不要:
- 使用循环
- 使用全局变量
- 导入外部库

代码:
"""
```

### 示例驱动
```python
prompt = """
将自然语言转换为 SQL 查询。

示例 1:
输入: 查询所有年龄大于 30 的用户
输出: SELECT * FROM users WHERE age > 30;

示例 2:
输入: 统计每个部门的员工数量
输出: SELECT department, COUNT(*) FROM employees GROUP BY department;

示例 3:
输入: 查询销售额前 10 的产品
输出: SELECT * FROM products ORDER BY sales DESC LIMIT 10;

现在转换:
输入: {natural_language}
输出:
"""
```

## 高级技巧

### 思维链提示词库
```python
COT_PROMPTS = {
    "zh": [
        "让我们一步步思考:",
        "让我们逐步分析:",
        "让我们分解这个问题:",
        "首先，我们需要理解...",
    ],
    "en": [
        "Let's think step by step:",
        "Let's break this down:",
        "Let's approach this systematically:",
        "First, we need to understand...",
    ]
}
```

### 元提示（Meta-Prompting）
```python
meta_prompt = """
你是一个 Prompt 工程专家。给定一个任务，生成最优的 Prompt。

任务: {task}

生成的 Prompt 应该:
1. 清晰定义角色和目标
2. 包含具体的输出格式
3. 提供 2-3 个示例
4. 设置必要的约束条件

生成的 Prompt:
"""

# 使用 LLM 生成 Prompt
optimized_prompt = llm.predict(meta_prompt.format(task="代码审查"))
```

### 自我批评
```python
def self_critique(question: str):
    # 第一次生成
    answer = llm.predict(f"问题: {question}\n答案:")

    # 自我批评
    critique_prompt = f"""
问题: {question}
答案: {answer}

请批评这个答案的不足之处:
1. 准确性
2. 完整性
3. 清晰度

批评:
"""
    critique = llm.predict(critique_prompt)

    # 改进答案
    improve_prompt = f"""
问题: {question}
初始答案: {answer}
批评意见: {critique}

基于批评意见，生成改进后的答案:
"""
    improved = llm.predict(improve_prompt)
    return improved
```

### 多角色对话
```python
prompt = """
模拟三位专家讨论问题:

问题: {question}

专家 A (乐观派):
{optimistic_view}

专家 B (悲观派):
{pessimistic_view}

专家 C (中立派):
综合 A 和 B 的观点，我认为...
"""
```

## Prompt 模板库

### 代码生成
```yaml
code_generation:
  system: "你是一位资深的 {language} 开发者。"
  template: |
    生成 {language} 代码实现以下功能:

    功能描述: {description}

    要求:
    - 遵循 {language} 最佳实践
    - 添加必要的注释
    - 处理异常情况
    - 包含使用示例

    代码:
```

### 文本摘要
```yaml
summarization:
  template: |
    将以下文本总结为 {length} 字的摘要:

    文本:
    {text}

    摘要要求:
    - 保留关键信息
    - 语言简洁
    - 逻辑清晰

    摘要:
```

### 数据提取
```yaml
extraction:
  template: |
    从文本中提取以下信息:

    提取字段: {fields}

    文本:
    {text}

    输出格式: JSON

    提取结果:
```

## 工具与资源

| 工具 | 类型 | 用途 |
|------|------|------|
| LangChain | 框架 | Prompt 模板管理 |
| PromptBase | 市场 | Prompt 交易平台 |
| OpenPrompt | 库 | Prompt 学习框架 |
| Guidance | 库 | 结构化生成 |
| LMQL | 语言 | Prompt 编程语言 |

## 最佳实践

- ✅ 清晰指令：具体、明确、可执行
- ✅ 结构化：使用分隔符、编号、格式
- ✅ 示例驱动：提供 2-5 个高质量示例
- ✅ 约束明确：说明要做什么和不做什么
- ✅ 迭代优化：测试、分析、改进
- ✅ 版本管理：记录 Prompt 变更历史
- ✅ A/B 测试：对比不同 Prompt 效果
- ❌ 避免：模糊指令、过长 Prompt、无示例

---
