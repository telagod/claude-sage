---
name: php
description: PHP 开发技术。Laravel、Symfony、Composer、PSR 标准、Eloquent ORM、Blade 模板。当用户提到 PHP、Laravel、Symfony、Composer、PSR、Eloquent、Blade、Artisan 时使用。
---

# 🐘 PHP 开发 · PHP Development

## 生态架构

```
         Laravel/Symfony
              │
    ┌─────────┼─────────┐
    │         │         │
Eloquent   Blade    Artisan
    │         │         │
    └─────────┼─────────┘
              │
         Composer (PSR)
              │
    ┌─────────┼─────────┐
  Cache    Queue    Session
```

## Laravel 核心

### 路由与控制器
```php
// routes/web.php
use App\Http\Controllers\UserController;

Route::get('/users', [UserController::class, 'index']);
Route::post('/users', [UserController::class, 'store']);
Route::get('/users/{id}', [UserController::class, 'show']);

// 路由组
Route::middleware(['auth'])->group(function () {
    Route::prefix('admin')->group(function () {
        Route::get('/dashboard', [AdminController::class, 'index']);
    });
});

// API 路由
Route::apiResource('posts', PostController::class);
```

### Eloquent ORM
```php
// 模型定义
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class User extends Model
{
    protected $fillable = ['name', 'email', 'password'];
    protected $hidden = ['password', 'remember_token'];
    protected $casts = [
        'email_verified_at' => 'datetime',
        'is_admin' => 'boolean',
    ];

    public function posts(): HasMany
    {
        return $this->hasMany(Post::class);
    }
}

// 查询构建器
$users = User::where('active', true)
    ->whereHas('posts', function ($query) {
        $query->where('published', true);
    })
    ->with('posts')
    ->orderBy('created_at', 'desc')
    ->paginate(15);

// 批量操作
User::where('last_login', '<', now()->subYear())
    ->chunk(100, function ($users) {
        foreach ($users as $user) {
            $user->delete();
        }
    });
```

### 依赖注入与服务容器
```php
// 服务提供者
namespace App\Providers;

use Illuminate\Support\ServiceProvider;

class PaymentServiceProvider extends ServiceProvider
{
    public function register()
    {
        $this->app->singleton(PaymentGateway::class, function ($app) {
            return new StripeGateway(config('services.stripe.key'));
        });
    }
}

// 控制器注入
class OrderController extends Controller
{
    public function __construct(
        private PaymentGateway $payment,
        private OrderRepository $orders
    ) {}

    public function store(Request $request)
    {
        $order = $this->orders->create($request->validated());
        $this->payment->charge($order->total);
        return response()->json($order, 201);
    }
}
```

### Blade 模板
```php
{{-- layouts/app.blade.php --}}
<!DOCTYPE html>
<html>
<head>
    <title>@yield('title')</title>
</head>
<body>
    @include('partials.header')

    <main>
        @yield('content')
    </main>

    @stack('scripts')
</body>
</html>

{{-- users/index.blade.php --}}
@extends('layouts.app')

@section('title', 'Users')

@section('content')
    @forelse($users as $user)
        <div class="user">
            <h3>{{ $user->name }}</h3>
            @if($user->is_admin)
                <span class="badge">Admin</span>
            @endif
        </div>
    @empty
        <p>No users found.</p>
    @endforelse

    {{ $users->links() }}
@endsection
```

### 中间件
```php
namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class CheckApiToken
{
    public function handle(Request $request, Closure $next)
    {
        $token = $request->header('X-API-Token');

        if (!$this->isValidToken($token)) {
            return response()->json(['error' => 'Unauthorized'], 401);
        }

        return $next($request);
    }
}

// 注册中间件
protected $routeMiddleware = [
    'api.token' => \App\Http\Middleware\CheckApiToken::class,
];
```

### 队列与任务
```php
// 任务定义
namespace App\Jobs;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;

class ProcessVideoUpload implements ShouldQueue
{
    use Queueable;

    public $tries = 3;
    public $timeout = 120;

    public function __construct(
        private Video $video
    ) {}

    public function handle()
    {
        // 转码逻辑
        $this->video->transcode();
    }

    public function failed(\Throwable $exception)
    {
        // 失败处理
        $this->video->markAsFailed();
    }
}

// 分发任务
ProcessVideoUpload::dispatch($video)
    ->onQueue('videos')
    ->delay(now()->addMinutes(5));
```

### Artisan 命令
```php
namespace App\Console\Commands;

use Illuminate\Console\Command;

class CleanupOldLogs extends Command
{
    protected $signature = 'logs:cleanup {--days=30}';
    protected $description = 'Clean up old log files';

    public function handle()
    {
        $days = $this->option('days');
        $this->info("Cleaning logs older than {$days} days...");

        $deleted = Log::where('created_at', '<', now()->subDays($days))
            ->delete();

        $this->info("Deleted {$deleted} log entries.");
    }
}
```

## Symfony 组件

### HTTP 基础
```php
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\JsonResponse;

// 请求处理
$request = Request::createFromGlobals();
$name = $request->query->get('name');
$data = $request->request->all();
$file = $request->files->get('upload');

// 响应
$response = new Response('Hello World', 200, [
    'Content-Type' => 'text/plain'
]);

$json = new JsonResponse(['status' => 'success']);
```

### 依赖注入容器
```php
use Symfony\Component\DependencyInjection\ContainerBuilder;
use Symfony\Component\DependencyInjection\Reference;

$container = new ContainerBuilder();

$container->register('mailer', Mailer::class)
    ->addArgument(new Reference('transport'));

$container->register('transport', SmtpTransport::class)
    ->addArgument('%smtp.host%')
    ->addArgument('%smtp.port%');

$mailer = $container->get('mailer');
```

### 事件调度器
```php
use Symfony\Component\EventDispatcher\EventDispatcher;

class OrderPlacedEvent
{
    public function __construct(
        public Order $order
    ) {}
}

$dispatcher = new EventDispatcher();

$dispatcher->addListener('order.placed', function (OrderPlacedEvent $event) {
    // 发送邮件
    $mailer->send($event->order->user->email);
});

$dispatcher->dispatch(new OrderPlacedEvent($order), 'order.placed');
```

## Composer 依赖管理

### composer.json 配置
```json
{
    "name": "vendor/project",
    "type": "project",
    "require": {
        "php": "^8.2",
        "laravel/framework": "^10.0",
        "guzzlehttp/guzzle": "^7.5"
    },
    "require-dev": {
        "phpunit/phpunit": "^10.0",
        "laravel/pint": "^1.0"
    },
    "autoload": {
        "psr-4": {
            "App\\": "app/",
            "Database\\": "database/"
        },
        "files": [
            "app/helpers.php"
        ]
    },
    "scripts": {
        "test": "phpunit",
        "format": "pint"
    }
}
```

### 常用命令
```bash
# 安装依赖
composer install
composer install --no-dev

# 更新依赖
composer update
composer update vendor/package

# 添加包
composer require guzzlehttp/guzzle
composer require --dev phpunit/phpunit

# 自动加载优化
composer dump-autoload -o

# 查看过期包
composer outdated
```

## PSR 标准

### PSR-4 自动加载
```php
// composer.json
{
    "autoload": {
        "psr-4": {
            "App\\": "src/",
            "App\\Tests\\": "tests/"
        }
    }
}

// 目录结构
src/
├── Controllers/
│   └── UserController.php  // App\Controllers\UserController
├── Models/
│   └── User.php            // App\Models\User
└── Services/
    └── PaymentService.php  // App\Services\PaymentService
```

### PSR-12 代码风格
```php
<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;
use Illuminate\Support\Facades\Hash;

class UserService
{
    public function __construct(
        private UserRepository $repository,
        private Mailer $mailer
    ) {
    }

    public function createUser(array $data): User
    {
        $user = $this->repository->create([
            'name' => $data['name'],
            'email' => $data['email'],
            'password' => Hash::make($data['password']),
        ]);

        $this->mailer->sendWelcomeEmail($user);

        return $user;
    }
}
```

### PSR-3 日志接口
```php
use Psr\Log\LoggerInterface;

class OrderProcessor
{
    public function __construct(
        private LoggerInterface $logger
    ) {}

    public function process(Order $order)
    {
        $this->logger->info('Processing order', ['order_id' => $order->id]);

        try {
            $order->process();
            $this->logger->info('Order processed successfully');
        } catch (\Exception $e) {
            $this->logger->error('Order processing failed', [
                'order_id' => $order->id,
                'error' => $e->getMessage()
            ]);
            throw $e;
        }
    }
}
```

## 数据库迁移

### 迁移文件
```php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('posts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->string('title');
            $table->text('content');
            $table->boolean('published')->default(false);
            $table->timestamp('published_at')->nullable();
            $table->timestamps();
            $table->softDeletes();

            $table->index(['user_id', 'published']);
            $table->fullText(['title', 'content']);
        });
    }

    public function down()
    {
        Schema::dropIfExists('posts');
    }
};
```

## 测试

### PHPUnit 单元测试
```php
namespace Tests\Unit;

use PHPUnit\Framework\TestCase;
use App\Services\Calculator;

class CalculatorTest extends TestCase
{
    private Calculator $calculator;

    protected function setUp(): void
    {
        $this->calculator = new Calculator();
    }

    public function test_addition()
    {
        $result = $this->calculator->add(2, 3);
        $this->assertEquals(5, $result);
    }

    public function test_division_by_zero()
    {
        $this->expectException(\DivisionByZeroError::class);
        $this->calculator->divide(10, 0);
    }
}
```

### Laravel 功能测试
```php
namespace Tests\Feature;

use Tests\TestCase;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;

class UserApiTest extends TestCase
{
    use RefreshDatabase;

    public function test_can_create_user()
    {
        $response = $this->postJson('/api/users', [
            'name' => 'John Doe',
            'email' => 'john@example.com',
            'password' => 'password123'
        ]);

        $response->assertStatus(201)
            ->assertJsonStructure(['id', 'name', 'email']);

        $this->assertDatabaseHas('users', [
            'email' => 'john@example.com'
        ]);
    }
}
```

## 性能优化

### 缓存策略
```php
use Illuminate\Support\Facades\Cache;

// 基础缓存
$users = Cache::remember('users.all', 3600, function () {
    return User::all();
});

// 标签缓存
Cache::tags(['users', 'posts'])->put('user.1.posts', $posts, 3600);
Cache::tags(['users'])->flush();

// 缓存锁
Cache::lock('process-order-' . $orderId, 10)->get(function () {
    // 独占处理
});
```

### 数据库优化
```php
// 预加载关联
$users = User::with(['posts', 'comments'])->get();

// 延迟预加载
$users->load('posts.comments');

// 只查询需要的列
User::select('id', 'name', 'email')->get();

// 分块处理
User::chunk(100, function ($users) {
    foreach ($users as $user) {
        // 处理
    }
});
```

## 安全最佳实践

### 输入验证
```php
use Illuminate\Http\Request;

class UserController extends Controller
{
    public function store(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'email' => 'required|email|unique:users',
            'password' => 'required|min:8|confirmed',
            'age' => 'nullable|integer|min:18|max:120'
        ]);

        return User::create($validated);
    }
}
```

### SQL 注入防护
```php
// ✅ 正确：参数绑定
$users = DB::select('SELECT * FROM users WHERE email = ?', [$email]);

// ✅ 正确：查询构建器
$users = DB::table('users')->where('email', $email)->get();

// ❌ 错误：字符串拼接
$users = DB::select("SELECT * FROM users WHERE email = '$email'");
```

### CSRF 保护
```php
// Blade 表单
<form method="POST" action="/users">
    @csrf
    <input type="text" name="name">
    <button type="submit">Submit</button>
</form>

// API 排除
protected $except = [
    'api/*',
];
```

## 框架对比

| 特性 | Laravel | Symfony |
|------|---------|---------|
| 学习曲线 | 平缓 | 陡峭 |
| ORM | Eloquent | Doctrine |
| 模板引擎 | Blade | Twig |
| 适用场景 | 快速开发 | 企业级 |
| 性能 | 中等 | 较高 |
| 生态 | 丰富 | 模块化 |

## 工具清单

| 工具 | 用途 |
|------|------|
| Laravel | 全栈框架 |
| Symfony | 企业级框架 |
| Composer | 依赖管理 |
| PHPUnit | 单元测试 |
| Laravel Pint | 代码格式化 |
| PHPStan | 静态分析 |
| Laravel Telescope | 调试工具 |
| Laravel Horizon | 队列监控 |

---
