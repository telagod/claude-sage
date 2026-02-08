---
name: cpp
description: C/C++ 开发。系统编程、性能优化、内存管理。当用户提到 C、C++、CMake、内存、指针时使用。
---

# 📜 符箓秘典 · C/C++


## 现代 C++ (C++17/20)

### 智能指针
```cpp
#include <memory>

// unique_ptr - 独占所有权
auto ptr = std::make_unique<MyClass>(args);
ptr->method();

// shared_ptr - 共享所有权
auto shared = std::make_shared<MyClass>(args);
auto copy = shared;  // 引用计数 +1

// weak_ptr - 弱引用，不增加引用计数
std::weak_ptr<MyClass> weak = shared;
if (auto locked = weak.lock()) {
    locked->method();
}
```

### 容器与算法
```cpp
#include <vector>
#include <algorithm>
#include <ranges>

std::vector<int> nums = {1, 2, 3, 4, 5};

// 范围 for
for (const auto& n : nums) {
    std::cout << n << std::endl;
}

// 算法
auto it = std::find(nums.begin(), nums.end(), 3);
std::sort(nums.begin(), nums.end());

// C++20 Ranges
auto even = nums | std::views::filter([](int n) { return n % 2 == 0; });
auto squared = nums | std::views::transform([](int n) { return n * n; });
```

### Lambda 表达式
```cpp
// 基础 lambda
auto add = [](int a, int b) { return a + b; };

// 捕获
int x = 10;
auto capture_val = [x]() { return x; };      // 值捕获
auto capture_ref = [&x]() { return x; };     // 引用捕获
auto capture_all = [=]() { return x; };      // 全部值捕获
auto capture_all_ref = [&]() { return x; };  // 全部引用捕获

// 泛型 lambda (C++14)
auto generic = [](auto a, auto b) { return a + b; };
```

### 并发编程
```cpp
#include <thread>
#include <mutex>
#include <future>

// 线程
std::thread t([]() {
    std::cout << "Hello from thread" << std::endl;
});
t.join();

// 互斥锁
std::mutex mtx;
{
    std::lock_guard<std::mutex> lock(mtx);
    // 临界区
}

// async/future
auto future = std::async(std::launch::async, []() {
    return compute_result();
});
auto result = future.get();

// 条件变量
std::condition_variable cv;
std::unique_lock<std::mutex> lock(mtx);
cv.wait(lock, []() { return ready; });
```

## 内存管理

### RAII 模式
```cpp
class FileHandle {
public:
    FileHandle(const char* path) : file(fopen(path, "r")) {
        if (!file) throw std::runtime_error("Failed to open file");
    }

    ~FileHandle() {
        if (file) fclose(file);
    }

    // 禁止拷贝
    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;

    // 允许移动
    FileHandle(FileHandle&& other) noexcept : file(other.file) {
        other.file = nullptr;
    }

private:
    FILE* file;
};
```

### 内存安全检查
```bash
# AddressSanitizer
g++ -fsanitize=address -g main.cpp -o main
./main

# Valgrind
valgrind --leak-check=full ./main

# 静态分析
clang-tidy main.cpp
cppcheck main.cpp
```

## CMake

### CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.16)
project(MyProject VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 添加可执行文件
add_executable(myapp
    src/main.cpp
    src/utils.cpp
)

# 添加库
add_library(mylib STATIC
    src/lib.cpp
)

# 链接库
target_link_libraries(myapp PRIVATE mylib)

# 包含目录
target_include_directories(myapp PRIVATE ${CMAKE_SOURCE_DIR}/include)

# 查找外部库
find_package(Threads REQUIRED)
target_link_libraries(myapp PRIVATE Threads::Threads)

# 测试
enable_testing()
add_executable(tests tests/test_main.cpp)
add_test(NAME MyTests COMMAND tests)
```

### 构建
```bash
mkdir build && cd build
cmake ..
cmake --build .
ctest  # 运行测试
```

## 测试

### Google Test
```cpp
#include <gtest/gtest.h>

TEST(MathTest, Add) {
    EXPECT_EQ(add(1, 2), 3);
    EXPECT_EQ(add(-1, 1), 0);
}

TEST(MathTest, Divide) {
    EXPECT_DOUBLE_EQ(divide(10, 2), 5.0);
    EXPECT_THROW(divide(1, 0), std::invalid_argument);
}

// Fixture
class UserTest : public ::testing::Test {
protected:
    void SetUp() override {
        user = std::make_unique<User>("Alice");
    }

    std::unique_ptr<User> user;
};

TEST_F(UserTest, GetName) {
    EXPECT_EQ(user->getName(), "Alice");
}
```

## 项目结构

```
myproject/
├── CMakeLists.txt
├── include/
│   └── myproject/
│       ├── utils.h
│       └── types.h
├── src/
│   ├── main.cpp
│   └── utils.cpp
├── tests/
│   └── test_main.cpp
└── build/
```

## 常用库

| 库 | 用途 |
|---|------|
| Boost | 通用库集合 |
| fmt | 格式化输出 |
| spdlog | 日志 |
| nlohmann/json | JSON |
| Catch2/GTest | 测试 |
| OpenSSL | 加密 |

---

