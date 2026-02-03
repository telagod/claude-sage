---
name: go
description: Go 开发。高并发、微服务、云原生、CLI工具。当用户提到 Go、Golang、Gin、Echo、goroutine 时使用。
---

# Go 开发

> 简洁高效，并发为王

## Web 框架

### Gin
```go
package main

import (
    "net/http"
    "github.com/gin-gonic/gin"
)

type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name" binding:"required"`
    Email string `json:"email" binding:"required,email"`
}

func main() {
    r := gin.Default()

    // 中间件
    r.Use(gin.Logger())
    r.Use(gin.Recovery())

    // 路由组
    api := r.Group("/api")
    {
        api.GET("/users/:id", getUser)
        api.POST("/users", createUser)
        api.PUT("/users/:id", updateUser)
        api.DELETE("/users/:id", deleteUser)
    }

    r.Run(":8080")
}

func getUser(c *gin.Context) {
    id := c.Param("id")
    c.JSON(http.StatusOK, gin.H{"id": id})
}

func createUser(c *gin.Context) {
    var user User
    if err := c.ShouldBindJSON(&user); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }
    c.JSON(http.StatusCreated, user)
}
```

### Echo
```go
package main

import (
    "net/http"
    "github.com/labstack/echo/v4"
    "github.com/labstack/echo/v4/middleware"
)

func main() {
    e := echo.New()

    e.Use(middleware.Logger())
    e.Use(middleware.Recover())

    e.GET("/users/:id", getUser)
    e.POST("/users", createUser)

    e.Logger.Fatal(e.Start(":8080"))
}

func getUser(c echo.Context) error {
    id := c.Param("id")
    return c.JSON(http.StatusOK, map[string]string{"id": id})
}
```

## 并发编程

### Goroutine & Channel
```go
package main

import (
    "fmt"
    "sync"
)

// 基础并发
func worker(id int, jobs <-chan int, results chan<- int) {
    for j := range jobs {
        results <- j * 2
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)

    // 启动 worker
    for w := 1; w <= 3; w++ {
        go worker(w, jobs, results)
    }

    // 发送任务
    for j := 1; j <= 9; j++ {
        jobs <- j
    }
    close(jobs)

    // 收集结果
    for a := 1; a <= 9; a++ {
        <-results
    }
}

// WaitGroup
func parallelFetch(urls []string) []string {
    var wg sync.WaitGroup
    results := make([]string, len(urls))

    for i, url := range urls {
        wg.Add(1)
        go func(i int, url string) {
            defer wg.Done()
            results[i] = fetch(url)
        }(i, url)
    }

    wg.Wait()
    return results
}

// Context 控制
func fetchWithTimeout(ctx context.Context, url string) (string, error) {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()

    body, _ := io.ReadAll(resp.Body)
    return string(body), nil
}
```

## 错误处理

```go
package main

import (
    "errors"
    "fmt"
)

// 自定义错误
var ErrNotFound = errors.New("not found")

type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

// 错误包装
func getUser(id int) (*User, error) {
    user, err := db.FindUser(id)
    if err != nil {
        return nil, fmt.Errorf("getUser(%d): %w", id, err)
    }
    return user, nil
}

// 错误检查
func handleUser(id int) error {
    user, err := getUser(id)
    if err != nil {
        if errors.Is(err, ErrNotFound) {
            return nil // 忽略未找到
        }
        return err
    }
    // 处理 user
    return nil
}
```

## 测试

```go
package main

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestAdd(t *testing.T) {
    result := Add(1, 2)
    assert.Equal(t, 3, result)
}

// 表驱动测试
func TestAddTable(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 1, 2, 3},
        {"zero", 0, 0, 0},
        {"negative", -1, 1, 0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            assert.Equal(t, tt.expected, Add(tt.a, tt.b))
        })
    }
}

// Benchmark
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(1, 2)
    }
}
```

```bash
go test ./...
go test -v
go test -cover
go test -bench=.
go test -race  # 竞态检测
```

## CLI 工具

### Cobra
```go
package main

import (
    "fmt"
    "github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
    Use:   "myapp",
    Short: "My CLI application",
}

var serveCmd = &cobra.Command{
    Use:   "serve",
    Short: "Start the server",
    Run: func(cmd *cobra.Command, args []string) {
        port, _ := cmd.Flags().GetInt("port")
        fmt.Printf("Starting server on port %d\n", port)
    },
}

func init() {
    serveCmd.Flags().IntP("port", "p", 8080, "Port to listen on")
    rootCmd.AddCommand(serveCmd)
}

func main() {
    rootCmd.Execute()
}
```

## 项目结构

```
myproject/
├── go.mod
├── go.sum
├── main.go
├── cmd/
│   └── myapp/
│       └── main.go
├── internal/
│   ├── handler/
│   ├── service/
│   └── repository/
├── pkg/
│   └── utils/
└── tests/
```

## 常用库

| 库 | 用途 |
|---|------|
| gin/echo | Web 框架 |
| gorm | ORM |
| cobra | CLI |
| viper | 配置 |
| zap/zerolog | 日志 |
| testify | 测试 |
| wire | 依赖注入 |

---

**Go: 少即是多，简洁即力量。**
