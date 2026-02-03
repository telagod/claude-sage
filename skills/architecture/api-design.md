---
name: api-design
description: API 设计。RESTful、GraphQL、OpenAPI、版本管理。当用户提到 API设计、RESTful、GraphQL、OpenAPI、接口设计时使用。
---

# API 设计

> 接口即契约，设计即沟通

## RESTful 设计

### 资源命名
```yaml
# 使用名词复数
GET    /users          # 获取用户列表
GET    /users/{id}     # 获取单个用户
POST   /users          # 创建用户
PUT    /users/{id}     # 更新用户
PATCH  /users/{id}     # 部分更新
DELETE /users/{id}     # 删除用户

# 嵌套资源
GET    /users/{id}/orders
POST   /users/{id}/orders

# 避免
GET    /getUsers       # ❌ 动词
GET    /user           # ❌ 单数
POST   /createUser     # ❌ 动词
```

### HTTP 状态码
```yaml
2xx 成功:
  200: OK
  201: Created
  204: No Content

4xx 客户端错误:
  400: Bad Request
  401: Unauthorized
  403: Forbidden
  404: Not Found
  409: Conflict
  422: Unprocessable Entity

5xx 服务端错误:
  500: Internal Server Error
  502: Bad Gateway
  503: Service Unavailable
```

### 响应格式
```json
// 成功响应
{
  "data": {
    "id": 1,
    "name": "Alice"
  }
}

// 列表响应
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}

// 错误响应
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": [
      {"field": "email", "message": "Invalid format"}
    ]
  }
}
```

## OpenAPI 规范

```yaml
openapi: 3.0.3
info:
  title: User API
  version: 1.0.0

paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'

    post:
      summary: Create user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUser'
      responses:
        '201':
          description: Created

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
          format: email

    CreateUser:
      type: object
      required:
        - name
        - email
      properties:
        name:
          type: string
        email:
          type: string
```

## GraphQL

```graphql
# Schema
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  author: User!
}

type Query {
  user(id: ID!): User
  users(limit: Int, offset: Int): [User!]!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
}

input CreateUserInput {
  name: String!
  email: String!
}

# Query
query GetUser($id: ID!) {
  user(id: $id) {
    name
    email
    posts {
      title
    }
  }
}
```

## 版本管理

```yaml
策略:
  URL路径: /api/v1/users (推荐)
  请求头: Accept: application/vnd.api+json;version=1
  查询参数: /api/users?version=1

原则:
  - 向后兼容
  - 废弃通知
  - 迁移指南
```

## 安全设计

```yaml
认证:
  - API Key
  - JWT
  - OAuth 2.0

授权:
  - RBAC
  - ABAC
  - Scope

防护:
  - 速率限制
  - 输入验证
  - HTTPS
```

---

**好的 API 是自解释的。**
