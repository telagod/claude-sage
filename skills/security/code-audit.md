---
name: code-audit
description: 代码安全审计。危险函数识别、污点分析、漏洞挖掘、安全审计。当用户提到代码审计、安全审计、漏洞挖掘、危险函数、sink点、source点、污点分析时使用。
---

# 代码安全审计 (Code Audit)

> Source → 传播路径 → Sink，追踪数据流，发现漏洞

## 审计流程

```
┌─────────────────────────────────────────────────────────────┐
│                    代码审计流程                               │
├─────────────────────────────────────────────────────────────┤
│  1. 信息收集                                                 │
│  ├─ 识别语言、框架、依赖                                     │
│  ├─ 定位入口点（路由、API、用户输入）                        │
│  └─ 梳理数据流向                                             │
│                        ↓                                     │
│  2. 危险函数扫描                                             │
│  ├─ 命令执行 Sink                                            │
│  ├─ SQL 注入 Sink                                            │
│  ├─ 文件操作 Sink                                            │
│  └─ 反序列化 Sink                                            │
│                        ↓                                     │
│  3. 污点分析                                                 │
│  └─ Source (用户输入) → 传播路径 → Sink (危险函数)          │
│                        ↓                                     │
│  4. 漏洞验证 & 报告                                          │
│  └─ PoC 编写 → 影响评估 → 修复建议                          │
└─────────────────────────────────────────────────────────────┘
```

## 危险函数速查

### Python
```python
# 🔴 命令执行
os.system(cmd)
os.popen(cmd)
subprocess.call(cmd, shell=True)
subprocess.Popen(cmd, shell=True)
eval(user_input)
exec(user_input)

# 🔴 SQL 注入
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
cursor.execute("SELECT * FROM users WHERE id = " + user_id)

# 🔴 反序列化
pickle.loads(user_data)
yaml.load(user_data)  # 不安全
marshal.loads(user_data)

# 🔴 文件操作
open(user_path, 'r')  # 路径穿越
shutil.copy(user_src, user_dst)

# 🔴 SSRF
requests.get(user_url)
urllib.request.urlopen(user_url)

# ✅ 安全替代
subprocess.run([cmd, arg1, arg2], shell=False)
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
yaml.safe_load(user_data)
```

### Java
```java
// 🔴 命令执行
Runtime.getRuntime().exec(userInput);
new ProcessBuilder(userInput).start();

// 🔴 SQL 注入
Statement stmt = conn.createStatement();
stmt.execute("SELECT * FROM users WHERE id = " + userId);

// 🔴 反序列化
ObjectInputStream ois = new ObjectInputStream(userInputStream);
ois.readObject();

// 🔴 SSRF
new URL(userUrl).openConnection();
HttpClient.newHttpClient().send(request);

// 🔴 XXE
DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(userXml);

// ✅ 安全替代
PreparedStatement pstmt = conn.prepareStatement("SELECT * FROM users WHERE id = ?");
pstmt.setInt(1, userId);
```

### JavaScript/Node.js
```javascript
// 🔴 命令执行
child_process.exec(userInput);
eval(userInput);
new Function(userInput)();

// 🔴 原型污染
Object.assign(target, userInput);
_.merge(target, userInput);
JSON.parse(userInput);  // 配合 __proto__

// 🔴 SQL 注入
db.query(`SELECT * FROM users WHERE id = ${userId}`);

// 🔴 XSS
element.innerHTML = userInput;
document.write(userInput);

// ✅ 安全替代
child_process.execFile(cmd, [arg1, arg2]);
db.query("SELECT * FROM users WHERE id = ?", [userId]);
element.textContent = userInput;
```

### Go
```go
// 🔴 命令执行
exec.Command("sh", "-c", userInput).Run()

// 🔴 SQL 注入
db.Query("SELECT * FROM users WHERE id = " + userId)

// 🔴 路径穿越
filepath.Join(baseDir, userPath)  // 未校验 ..

// 🔴 SSTI
template.HTML(userInput)

// ✅ 安全替代
exec.Command(cmd, arg1, arg2).Run()
db.Query("SELECT * FROM users WHERE id = ?", userId)
```

## 污点分析

### 概念
```
Source (污点源)     →    传播路径    →    Sink (汇聚点)
用户可控输入              数据流转          危险函数调用
```

### Source 识别
```python
# HTTP 请求参数
request.args.get('param')
request.form.get('param')
request.json.get('param')
request.headers.get('header')
request.cookies.get('cookie')

# 文件输入
open(file).read()
sys.stdin.read()

# 环境变量
os.environ.get('VAR')

# 数据库查询结果（二次注入）
cursor.fetchone()
```

### 传播追踪
```python
# 示例：追踪污点传播
user_input = request.args.get('id')  # Source
processed = user_input.strip()        # 传播
query = f"SELECT * FROM users WHERE id = {processed}"  # 传播
cursor.execute(query)                  # Sink!
```

## 快速扫描命令

```bash
# Python 危险函数
grep -rn "eval\|exec\|os.system\|subprocess\|pickle.loads" --include="*.py" .

# Java 危险函数
grep -rn "Runtime.exec\|ProcessBuilder\|ObjectInputStream\|Statement.execute" --include="*.java" .

# JavaScript 危险函数
grep -rn "eval\|child_process\|innerHTML\|document.write" --include="*.js" .

# Go 危险函数
grep -rn "exec.Command\|template.HTML" --include="*.go" .

# SQL 注入模式
grep -rn "execute.*+\|execute.*f\"\|Query.*+" --include="*.py" --include="*.java" .
```

## 漏洞报告格式

```markdown
## [漏洞类型] - [严重程度: Critical/High/Medium/Low]

**文件:** `path/to/file.py:行号`

**漏洞代码:**
```python
# 有问题的代码片段
user_id = request.args.get('id')
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

**漏洞原理:**
用户输入直接拼接到 SQL 语句中，未经过滤或参数化，导致 SQL 注入。

**污点追踪:**
```
request.args.get('id')  [Source]
    ↓
f"SELECT ... {user_id}" [传播]
    ↓
cursor.execute(query)   [Sink]
```

**PoC:**
```
GET /api/users?id=1' OR '1'='1
```

**修复建议:**
```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```
```

## 审计检查清单

### 输入验证
- [ ] 所有用户输入是否经过验证
- [ ] 是否使用白名单验证
- [ ] 是否有长度限制

### SQL 注入
- [ ] 是否使用参数化查询
- [ ] 是否有 ORM 保护
- [ ] 动态表名/列名是否白名单

### 命令注入
- [ ] 是否避免 shell=True
- [ ] 参数是否正确转义
- [ ] 是否使用白名单命令

### 文件操作
- [ ] 路径是否规范化
- [ ] 是否检查路径穿越
- [ ] 文件类型是否验证

### 认证授权
- [ ] 敏感操作是否验证身份
- [ ] 是否有越权检查
- [ ] 会话管理是否安全

### 加密
- [ ] 是否使用安全算法
- [ ] 密钥管理是否安全
- [ ] 是否有硬编码密钥

---

**代码审计的本质：追踪数据流，发现信任边界的突破。**
