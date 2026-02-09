---
name: dart
description: Dart 开发技术。Flutter、Widget 树、异步编程、Future、Stream、跨平台开发。当用户提到 Dart、Flutter、Widget、跨平台、移动开发时使用。
---

# 🎯 Dart 开发 · Dart Development

## 生态架构

```
           Flutter Framework
                  │
        ┌─────────┼─────────┐
        │         │         │
    Widgets   Material  Cupertino
        │         │         │
        └─────────┼─────────┘
                  │
            Dart Runtime
                  │
        ┌─────────┼─────────┐
    Future    Stream    Isolate
```

## Dart 语言基础

### 变量与类型
```dart
// 类型推断
var name = 'John';
var age = 30;

// 显式类型
String email = 'john@example.com';
int count = 0;
double price = 99.99;
bool isActive = true;

// 可空类型
String? nullableName;
int? nullableAge;

// late 延迟初始化
late String description;

// final 与 const
final currentTime = DateTime.now();  // 运行时常量
const pi = 3.14159;                  // 编译时常量

// 集合
List<String> names = ['Alice', 'Bob', 'Charlie'];
Set<int> uniqueNumbers = {1, 2, 3};
Map<String, int> scores = {'Alice': 95, 'Bob': 87};
```

### 函数与闭包
```dart
// 基础函数
int add(int a, int b) {
  return a + b;
}

// 箭头函数
int multiply(int a, int b) => a * b;

// 可选参数
String greet(String name, [String? title]) {
  return title != null ? '$title $name' : name;
}

// 命名参数
void printUser({required String name, int age = 0}) {
  print('$name is $age years old');
}

// 高阶函数
List<T> transform<T>(List<T> items, T Function(T) transformer) {
  return items.map(transformer).toList();
}

// 闭包
Function makeAdder(int addBy) {
  return (int i) => i + addBy;
}

var add2 = makeAdder(2);
print(add2(3));  // 5
```

### 类与继承
```dart
// 基础类
class Person {
  String name;
  int age;

  // 构造函数
  Person(this.name, this.age);

  // 命名构造函数
  Person.guest() : name = 'Guest', age = 0;

  // 方法
  void introduce() {
    print('I am $name, $age years old');
  }
}

// 继承
class Student extends Person {
  String school;

  Student(String name, int age, this.school) : super(name, age);

  @override
  void introduce() {
    super.introduce();
    print('I study at $school');
  }
}

// 抽象类
abstract class Animal {
  String name;
  Animal(this.name);

  void makeSound();  // 抽象方法
}

class Dog extends Animal {
  Dog(String name) : super(name);

  @override
  void makeSound() {
    print('$name says: Woof!');
  }
}

// Mixin
mixin Flyable {
  void fly() {
    print('Flying...');
  }
}

class Bird extends Animal with Flyable {
  Bird(String name) : super(name);

  @override
  void makeSound() {
    print('$name says: Chirp!');
  }
}
```

## Flutter Widget 基础

### StatelessWidget
```dart
import 'package:flutter/material.dart';

class UserCard extends StatelessWidget {
  final String name;
  final String email;
  final String? avatarUrl;

  const UserCard({
    Key? key,
    required this.name,
    required this.email,
    this.avatarUrl,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.all(16),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          children: [
            CircleAvatar(
              radius: 30,
              backgroundImage: avatarUrl != null
                  ? NetworkImage(avatarUrl!)
                  : null,
              child: avatarUrl == null ? Icon(Icons.person) : null,
            ),
            SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  SizedBox(height: 4),
                  Text(
                    email,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

### StatefulWidget
```dart
class Counter extends StatefulWidget {
  const Counter({Key? key}) : super(key: key);

  @override
  State<Counter> createState() => _CounterState();
}

class _CounterState extends State<Counter> {
  int _count = 0;

  void _increment() {
    setState(() {
      _count++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          'Count: $_count',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        SizedBox(height: 16),
        ElevatedButton(
          onPressed: _increment,
          child: Text('Increment'),
        ),
      ],
    );
  }
}
```

### 布局 Widget
```dart
class LayoutExample extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Layout Example')),
      body: Column(
        children: [
          // Row 水平布局
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              Icon(Icons.star),
              Icon(Icons.favorite),
              Icon(Icons.thumb_up),
            ],
          ),

          // Stack 层叠布局
          Stack(
            children: [
              Container(
                width: 200,
                height: 200,
                color: Colors.blue,
              ),
              Positioned(
                top: 20,
                left: 20,
                child: Text('Overlay Text'),
              ),
            ],
          ),

          // Expanded 填充剩余空间
          Expanded(
            child: Container(
              color: Colors.grey[200],
              child: Center(child: Text('Expanded Area')),
            ),
          ),

          // ListView
          Expanded(
            child: ListView.builder(
              itemCount: 20,
              itemBuilder: (context, index) {
                return ListTile(
                  leading: Icon(Icons.person),
                  title: Text('Item $index'),
                  subtitle: Text('Description'),
                  trailing: Icon(Icons.chevron_right),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
```

### 导航与路由
```dart
// 基础导航
Navigator.push(
  context,
  MaterialPageRoute(builder: (context) => DetailScreen()),
);

Navigator.pop(context);

// 命名路由
MaterialApp(
  initialRoute: '/',
  routes: {
    '/': (context) => HomeScreen(),
    '/detail': (context) => DetailScreen(),
    '/settings': (context) => SettingsScreen(),
  },
);

Navigator.pushNamed(context, '/detail');

// 传递参数
Navigator.pushNamed(
  context,
  '/detail',
  arguments: {'id': '123', 'name': 'Item'},
);

// 接收参数
class DetailScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final args = ModalRoute.of(context)!.settings.arguments as Map;
    return Scaffold(
      appBar: AppBar(title: Text(args['name'])),
      body: Center(child: Text('ID: ${args['id']}')),
    );
  }
}
```

## 状态管理

### Provider
```dart
import 'package:provider/provider.dart';

// Model
class Counter with ChangeNotifier {
  int _count = 0;

  int get count => _count;

  void increment() {
    _count++;
    notifyListeners();
  }

  void reset() {
    _count = 0;
    notifyListeners();
  }
}

// 提供者
void main() {
  runApp(
    ChangeNotifierProvider(
      create: (context) => Counter(),
      child: MyApp(),
    ),
  );
}

// 消费者
class CounterScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Counter')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Consumer<Counter>(
              builder: (context, counter, child) {
                return Text(
                  'Count: ${counter.count}',
                  style: Theme.of(context).textTheme.headlineMedium,
                );
              },
            ),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                context.read<Counter>().increment();
              },
              child: Text('Increment'),
            ),
          ],
        ),
      ),
    );
  }
}
```

### Riverpod
```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Provider 定义
final counterProvider = StateNotifierProvider<CounterNotifier, int>((ref) {
  return CounterNotifier();
});

class CounterNotifier extends StateNotifier<int> {
  CounterNotifier() : super(0);

  void increment() => state++;
  void decrement() => state--;
}

// 使用
class CounterScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(counterProvider);

    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('Count: $count'),
            ElevatedButton(
              onPressed: () => ref.read(counterProvider.notifier).increment(),
              child: Text('Increment'),
            ),
          ],
        ),
      ),
    );
  }
}
```

## 异步编程

### Future
```dart
// 基础 Future
Future<String> fetchUserName() async {
  await Future.delayed(Duration(seconds: 2));
  return 'John Doe';
}

// 使用 async/await
void loadUser() async {
  try {
    final name = await fetchUserName();
    print('User: $name');
  } catch (e) {
    print('Error: $e');
  }
}

// Future.then
fetchUserName().then((name) {
  print('User: $name');
}).catchError((error) {
  print('Error: $error');
});

// 并发执行
Future<void> loadMultipleData() async {
  final results = await Future.wait([
    fetchUserName(),
    fetchUserEmail(),
    fetchUserAge(),
  ]);

  print('Name: ${results[0]}');
  print('Email: ${results[1]}');
  print('Age: ${results[2]}');
}

// FutureBuilder Widget
class UserProfile extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return FutureBuilder<User>(
      future: fetchUser(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return CircularProgressIndicator();
        }

        if (snapshot.hasError) {
          return Text('Error: ${snapshot.error}');
        }

        if (!snapshot.hasData) {
          return Text('No data');
        }

        final user = snapshot.data!;
        return Text('User: ${user.name}');
      },
    );
  }
}
```

### Stream
```dart
// 创建 Stream
Stream<int> countStream() async* {
  for (int i = 1; i <= 5; i++) {
    await Future.delayed(Duration(seconds: 1));
    yield i;
  }
}

// 监听 Stream
void listenToStream() {
  countStream().listen(
    (value) {
      print('Value: $value');
    },
    onError: (error) {
      print('Error: $error');
    },
    onDone: () {
      print('Stream completed');
    },
  );
}

// StreamController
class ChatService {
  final _messageController = StreamController<String>.broadcast();

  Stream<String> get messages => _messageController.stream;

  void sendMessage(String message) {
    _messageController.add(message);
  }

  void dispose() {
    _messageController.close();
  }
}

// StreamBuilder Widget
class MessageList extends StatelessWidget {
  final ChatService chatService;

  const MessageList({required this.chatService});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<String>(
      stream: chatService.messages,
      builder: (context, snapshot) {
        if (snapshot.hasError) {
          return Text('Error: ${snapshot.error}');
        }

        if (!snapshot.hasData) {
          return Text('No messages');
        }

        return Text('Latest: ${snapshot.data}');
      },
    );
  }
}

// Stream 操作符
Stream<int> transformedStream() {
  return countStream()
      .where((value) => value % 2 == 0)
      .map((value) => value * 2)
      .take(3);
}
```

## 网络请求

### HTTP 包
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiClient {
  static const baseUrl = 'https://api.example.com';

  Future<List<User>> fetchUsers() async {
    final response = await http.get(Uri.parse('$baseUrl/users'));

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => User.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load users');
    }
  }

  Future<User> createUser(User user) async {
    final response = await http.post(
      Uri.parse('$baseUrl/users'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(user.toJson()),
    );

    if (response.statusCode == 201) {
      return User.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to create user');
    }
  }

  Future<void> deleteUser(String id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/users/$id'),
    );

    if (response.statusCode != 204) {
      throw Exception('Failed to delete user');
    }
  }
}

// 数据模型
class User {
  final String id;
  final String name;
  final String email;

  User({required this.id, required this.name, required this.email});

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['name'],
      email: json['email'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
    };
  }
}
```

### Dio 包
```dart
import 'package:dio/dio.dart';

class DioClient {
  final Dio _dio = Dio(
    BaseOptions(
      baseUrl: 'https://api.example.com',
      connectTimeout: Duration(seconds: 5),
      receiveTimeout: Duration(seconds: 3),
    ),
  );

  DioClient() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          options.headers['Authorization'] = 'Bearer $token';
          return handler.next(options);
        },
        onError: (error, handler) {
          print('Error: ${error.message}');
          return handler.next(error);
        },
      ),
    );
  }

  Future<List<User>> getUsers() async {
    try {
      final response = await _dio.get('/users');
      return (response.data as List)
          .map((json) => User.fromJson(json))
          .toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Exception _handleError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
        return Exception('Connection timeout');
      case DioExceptionType.receiveTimeout:
        return Exception('Receive timeout');
      case DioExceptionType.badResponse:
        return Exception('Server error: ${error.response?.statusCode}');
      default:
        return Exception('Network error');
    }
  }
}
```

## 本地存储

### SharedPreferences
```dart
import 'package:shared_preferences/shared_preferences.dart';

class PreferencesService {
  Future<void> saveString(String key, String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(key, value);
  }

  Future<String?> getString(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(key);
  }

  Future<void> saveInt(String key, int value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(key, value);
  }

  Future<void> saveBool(String key, bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(key, value);
  }

  Future<void> remove(String key) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(key);
  }
}
```

### SQLite (sqflite)
```dart
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class DatabaseHelper {
  static final DatabaseHelper instance = DatabaseHelper._init();
  static Database? _database;

  DatabaseHelper._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('app.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(
      path,
      version: 1,
      onCreate: _createDB,
    );
  }

  Future _createDB(Database db, int version) async {
    await db.execute('''
      CREATE TABLE users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        created_at INTEGER NOT NULL
      )
    ''');
  }

  Future<void> insertUser(User user) async {
    final db = await database;
    await db.insert('users', user.toMap());
  }

  Future<List<User>> getUsers() async {
    final db = await database;
    final result = await db.query('users');
    return result.map((json) => User.fromMap(json)).toList();
  }

  Future<void> deleteUser(String id) async {
    final db = await database;
    await db.delete('users', where: 'id = ?', whereArgs: [id]);
  }
}
```

## 测试

### 单元测试
```dart
import 'package:test/test.dart';

void main() {
  group('Calculator', () {
    late Calculator calculator;

    setUp(() {
      calculator = Calculator();
    });

    test('addition should return correct result', () {
      expect(calculator.add(2, 3), equals(5));
    });

    test('division by zero should throw exception', () {
      expect(() => calculator.divide(10, 0), throwsException);
    });
  });

  group('User', () {
    test('fromJson should create valid user', () {
      final json = {'id': '1', 'name': 'John', 'email': 'john@example.com'};
      final user = User.fromJson(json);

      expect(user.id, equals('1'));
      expect(user.name, equals('John'));
      expect(user.email, equals('john@example.com'));
    });
  });
}
```

### Widget 测试
```dart
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Counter increments', (WidgetTester tester) async {
    await tester.pumpWidget(MaterialApp(home: Counter()));

    expect(find.text('Count: 0'), findsOneWidget);
    expect(find.text('Count: 1'), findsNothing);

    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    expect(find.text('Count: 0'), findsNothing);
    expect(find.text('Count: 1'), findsOneWidget);
  });

  testWidgets('UserCard displays user info', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: UserCard(
            name: 'John Doe',
            email: 'john@example.com',
          ),
        ),
      ),
    );

    expect(find.text('John Doe'), findsOneWidget);
    expect(find.text('john@example.com'), findsOneWidget);
  });
}
```

## 性能优化

### 列表优化
```dart
// ✅ 使用 ListView.builder
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) {
    return ItemWidget(items[index]);
  },
);

// ❌ 避免直接使用 ListView
ListView(
  children: items.map((item) => ItemWidget(item)).toList(),
);

// const 构造函数
class MyWidget extends StatelessWidget {
  const MyWidget({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Text('Static text');
  }
}
```

### 图片优化
```dart
// 缓存网络图片
CachedNetworkImage(
  imageUrl: 'https://example.com/image.jpg',
  placeholder: (context, url) => CircularProgressIndicator(),
  errorWidget: (context, url, error) => Icon(Icons.error),
);

// 图片压缩
Image.network(
  'https://example.com/image.jpg',
  cacheWidth: 300,
  cacheHeight: 300,
);
```

## 平台对比

| 特性 | Flutter | React Native |
|------|---------|--------------|
| 语言 | Dart | JavaScript |
| 性能 | 接近原生 | 较好 |
| UI 渲染 | Skia 引擎 | 原生组件 |
| 热重载 | ✅ | ✅ |
| 学习曲线 | 中等 | 平缓 |
| 生态 | 快速增长 | 成熟 |

## 工具清单

| 工具 | 用途 |
|------|------|
| Flutter SDK | 开发框架 |
| Dart DevTools | 调试工具 |
| Provider | 状态管理 |
| Riverpod | 状态管理 |
| Dio | 网络请求 |
| sqflite | SQLite 数据库 |
| shared_preferences | 键值存储 |
| flutter_test | 测试框架 |

---
