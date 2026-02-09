---
name: shell
description: Shell 脚本开发。Bash、自动化、系统管理。当用户提到 Shell、Bash、脚本、自动化、Linux命令时使用。
---

# 📜 符箓秘典 · Shell


## Bash 基础

### 变量与字符串
```bash
#!/bin/bash

# 变量
name="Alice"
age=25
readonly PI=3.14

# 字符串操作
str="Hello World"
echo ${#str}           # 长度: 11
echo ${str:0:5}        # 截取: Hello
echo ${str/World/Bash} # 替换: Hello Bash
echo ${str,,}          # 小写: hello world
echo ${str^^}          # 大写: HELLO WORLD

# 默认值
echo ${var:-default}   # 如果 var 未设置，返回 default
echo ${var:=default}   # 如果 var 未设置，设置并返回 default
```

### 数组
```bash
# 索引数组
arr=("a" "b" "c")
echo ${arr[0]}         # 第一个元素
echo ${arr[@]}         # 所有元素
echo ${#arr[@]}        # 数组长度

# 遍历
for item in "${arr[@]}"; do
    echo "$item"
done

# 关联数组 (Bash 4+)
declare -A map
map[name]="Alice"
map[age]=25
echo ${map[name]}
```

### 条件判断
```bash
# 字符串比较
if [[ "$str1" == "$str2" ]]; then
    echo "Equal"
fi

# 数值比较
if [[ $a -eq $b ]]; then echo "Equal"; fi
if [[ $a -lt $b ]]; then echo "Less"; fi
if [[ $a -gt $b ]]; then echo "Greater"; fi

# 文件测试
if [[ -f "$file" ]]; then echo "File exists"; fi
if [[ -d "$dir" ]]; then echo "Directory exists"; fi
if [[ -r "$file" ]]; then echo "Readable"; fi
if [[ -w "$file" ]]; then echo "Writable"; fi
if [[ -x "$file" ]]; then echo "Executable"; fi

# 逻辑运算
if [[ $a -gt 0 && $b -gt 0 ]]; then echo "Both positive"; fi
if [[ $a -gt 0 || $b -gt 0 ]]; then echo "At least one positive"; fi
```

### 循环
```bash
# for 循环
for i in {1..5}; do
    echo $i
done

for file in *.txt; do
    echo "Processing $file"
done

# while 循环
while read -r line; do
    echo "$line"
done < file.txt

# until 循环
count=0
until [[ $count -ge 5 ]]; do
    echo $count
    ((count++))
done
```

### 函数
```bash
# 定义函数
greet() {
    local name="$1"
    echo "Hello, $name!"
    return 0
}

# 调用
greet "Alice"
result=$?  # 获取返回值

# 返回字符串
get_date() {
    echo "$(date +%Y-%m-%d)"
}
today=$(get_date)
```

## 实用脚本模板

### 带参数的脚本
```bash
#!/bin/bash
set -euo pipefail

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] <input>

Options:
    -o, --output FILE   Output file
    -v, --verbose       Verbose mode
    -h, --help          Show this help
EOF
    exit 1
}

# 默认值
OUTPUT=""
VERBOSE=false

# 解析参数
while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        -*)
            echo "Unknown option: $1"
            usage
            ;;
        *)
            INPUT="$1"
            shift
            ;;
    esac
done

# 检查必需参数
if [[ -z "${INPUT:-}" ]]; then
    echo "Error: Input is required"
    usage
fi

# 主逻辑
main() {
    if $VERBOSE; then
        echo "Processing $INPUT..."
    fi
    # 处理逻辑
}

main
```

### 日志函数
```bash
#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

die() {
    log_error "$1"
    exit 1
}
```

### 错误处理
```bash
#!/bin/bash
set -euo pipefail

# 错误处理
trap 'echo "Error on line $LINENO"; exit 1' ERR

# 清理函数
cleanup() {
    rm -f "$TEMP_FILE"
}
trap cleanup EXIT

TEMP_FILE=$(mktemp)
```

## 常用命令组合

### 文本处理
```bash
# grep - 搜索
grep -r "pattern" .
grep -v "exclude"          # 排除
grep -i "case insensitive" # 忽略大小写
grep -E "regex"            # 正则

# sed - 替换
sed 's/old/new/g' file
sed -i 's/old/new/g' file  # 原地修改
sed -n '10,20p' file       # 打印行

# awk - 处理
awk '{print $1}' file      # 第一列
awk -F: '{print $1}' /etc/passwd
awk 'NR>1 {sum+=$1} END {print sum}' file

# 组合
cat file | grep "pattern" | awk '{print $2}' | sort | uniq -c
```

### 文件操作
```bash
# 查找
find . -name "*.txt"
find . -type f -mtime -7   # 7天内修改
find . -size +100M         # 大于100M
find . -name "*.log" -exec rm {} \;

# 批量重命名
for f in *.txt; do
    mv "$f" "${f%.txt}.md"
done

# 批量处理
find . -name "*.py" | xargs grep "TODO"
```

### 网络
```bash
# curl
curl -s https://api.example.com/data
curl -X POST -H "Content-Type: application/json" -d '{"key":"value"}' URL
curl -o output.file URL

# 端口检查
nc -zv host 80
ss -tulpn | grep :80
```

## 最佳实践

```bash
#!/bin/bash
# 1. 使用 set 选项
set -euo pipefail

# 2. 引用变量
echo "$variable"

# 3. 使用 [[ ]] 而非 [ ]
if [[ -f "$file" ]]; then

# 4. 使用 $() 而非反引号
result=$(command)

# 5. 使用 local 声明局部变量
func() {
    local var="value"
}

# 6. 检查命令是否存在
command -v git &>/dev/null || die "git not found"

# 7. 使用 shellcheck 检查
# shellcheck script.sh
```

---

