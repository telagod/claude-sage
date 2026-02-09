---
name: cross-platform
description: 跨平台移动开发。React Native、Flutter、性能对比、原生模块桥接、状态管理。当用户提到跨平台、React Native、Flutter、混合开发时使用。
---

# 🌉 跨平台开发 · Cross-Platform Development

## 框架对比

### React Native vs Flutter

| 维度 | React Native | Flutter |
|------|--------------|---------|
| 语言 | JavaScript/TypeScript | Dart |
| 渲染 | 原生组件 | 自绘引擎 (Skia) |
| 性能 | 接近原生 (桥接开销) | 接近原生 (直接编译) |
| 热重载 | ✅ Fast Refresh | ✅ Hot Reload |
| 生态 | 成熟 (npm) | 快速增长 (pub.dev) |
| 学习曲线 | 低 (Web 开发者友好) | 中 (需学 Dart) |
| UI 一致性 | 跟随系统 | 完全一致 |
| 包体积 | 较小 (~7MB) | 较大 (~15MB) |
| 社区 | Meta + 社区 | Google + 社区 |

### 性能对比

```
启动时间 (冷启动)
Flutter:  ~800ms
RN:       ~1200ms
Native:   ~600ms

渲染性能 (60fps)
Flutter:  58-60fps (自绘)
RN:       55-60fps (桥接)
Native:   60fps

内存占用
Flutter:  ~50MB
RN:       ~60MB
Native:   ~30MB
```

## React Native

### 基础组件
```typescript
import React, { useState } from 'react';
import { View, Text, Button, StyleSheet, FlatList } from 'react-native';

interface User {
  id: number;
  name: string;
  email: string;
}

const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const response = await fetch('https://api.example.com/users');
      const data = await response.json();
      setUsers(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Button title="Load Users" onPress={loadUsers} />

      <FlatList
        data={users}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={styles.item}>
            <Text style={styles.name}>{item.name}</Text>
            <Text style={styles.email}>{item.email}</Text>
          </View>
        )}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  item: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#ccc',
  },
  name: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  email: {
    fontSize: 14,
    color: '#666',
  },
});
```

### Hooks
```typescript
import { useState, useEffect, useCallback, useMemo } from 'react';

const UserScreen: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [filter, setFilter] = useState('');

  // useEffect: 副作用
  useEffect(() => {
    loadUsers();
  }, []);

  // useCallback: 缓存函数
  const loadUsers = useCallback(async () => {
    const data = await fetchUsers();
    setUsers(data);
  }, []);

  // useMemo: 缓存计算结果
  const filteredUsers = useMemo(() => {
    return users.filter(u =>
      u.name.toLowerCase().includes(filter.toLowerCase())
    );
  }, [users, filter]);

  return (
    <View>
      <TextInput
        value={filter}
        onChangeText={setFilter}
        placeholder="Search..."
      />
      <FlatList data={filteredUsers} {...} />
    </View>
  );
};
```

### Navigation
```typescript
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

type RootStackParamList = {
  Home: undefined;
  Detail: { userId: number };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

const App: React.FC = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen
          name="Home"
          component={HomeScreen}
        />
        <Stack.Screen
          name="Detail"
          component={DetailScreen}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

// 使用
const HomeScreen: React.FC<NativeStackScreenProps<RootStackParamList, 'Home'>> = ({ navigation }) => {
  return (
    <Button
      title="Go to Detail"
      onPress={() => navigation.navigate('Detail', { userId: 1 })}
    />
  );
};

const DetailScreen: React.FC<NativeStackScreenProps<RootStackParamList, 'Detail'>> = ({ route }) => {
  const { userId } = route.params;
  return <Text>User ID: {userId}</Text>;
};
```

### 状态管理 (Redux Toolkit)
```typescript
import { createSlice, createAsyncThunk, configureStore } from '@reduxjs/toolkit';

// Async Thunk
export const fetchUsers = createAsyncThunk(
  'users/fetch',
  async () => {
    const response = await fetch('https://api.example.com/users');
    return response.json();
  }
);

// Slice
const userSlice = createSlice({
  name: 'users',
  initialState: {
    items: [] as User[],
    loading: false,
    error: null as string | null,
  },
  reducers: {
    addUser: (state, action) => {
      state.items.push(action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed';
      });
  },
});

export const { addUser } = userSlice.actions;

// Store
export const store = configureStore({
  reducer: {
    users: userSlice.reducer,
  },
});

// 使用
import { useDispatch, useSelector } from 'react-redux';

const UserList: React.FC = () => {
  const dispatch = useDispatch();
  const { items, loading } = useSelector((state: RootState) => state.users);

  useEffect(() => {
    dispatch(fetchUsers());
  }, []);

  return <FlatList data={items} {...} />;
};
```

### 原生模块桥接
```typescript
// NativeModules (调用原生代码)
import { NativeModules } from 'react-native';

const { BiometricAuth } = NativeModules;

const authenticate = async () => {
  try {
    const result = await BiometricAuth.authenticate('Unlock App');
    console.log('Auth success:', result);
  } catch (error) {
    console.error('Auth failed:', error);
  }
};

// iOS (Swift)
@objc(BiometricAuth)
class BiometricAuth: NSObject {
  @objc
  func authenticate(_ reason: String, resolver: @escaping RCTPromiseResolveBlock, rejecter: @escaping RCTPromiseRejectBlock) {
    let context = LAContext()
    context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: reason) { success, error in
      if success {
        resolver(["success": true])
      } else {
        rejecter("AUTH_FAILED", error?.localizedDescription, error)
      }
    }
  }
}

// Android (Kotlin)
class BiometricAuthModule(reactContext: ReactApplicationContext) : ReactContextBaseJavaModule(reactContext) {
  override fun getName() = "BiometricAuth"

  @ReactMethod
  fun authenticate(reason: String, promise: Promise) {
    val executor = ContextCompat.getMainExecutor(reactApplicationContext)
    val biometricPrompt = BiometricPrompt(currentActivity!!, executor,
      object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
          promise.resolve(mapOf("success" to true))
        }
        override fun onAuthenticationFailed() {
          promise.reject("AUTH_FAILED", "Authentication failed")
        }
      }
    )

    val promptInfo = BiometricPrompt.PromptInfo.Builder()
      .setTitle(reason)
      .setNegativeButtonText("Cancel")
      .build()

    biometricPrompt.authenticate(promptInfo)
  }
}
```

## Flutter

### Widget 基础
```dart
import 'package:flutter/material.dart';

class UserList extends StatefulWidget {
  @override
  _UserListState createState() => _UserListState();
}

class _UserListState extends State<UserList> {
  List<User> users = [];
  bool loading = false;

  @override
  void initState() {
    super.initState();
    loadUsers();
  }

  Future<void> loadUsers() async {
    setState(() => loading = true);
    try {
      final response = await http.get(Uri.parse('https://api.example.com/users'));
      final data = jsonDecode(response.body) as List;
      setState(() {
        users = data.map((json) => User.fromJson(json)).toList();
      });
    } catch (e) {
      print('Error: $e');
    } finally {
      setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Users')),
      body: loading
          ? Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: users.length,
              itemBuilder: (context, index) {
                final user = users[index];
                return ListTile(
                  title: Text(user.name),
                  subtitle: Text(user.email),
                );
              },
            ),
    );
  }
}
```

### Provider 状态管理
```dart
import 'package:provider/provider.dart';

// Model
class UserProvider extends ChangeNotifier {
  List<User> _users = [];
  bool _loading = false;
  String? _error;

  List<User> get users => _users;
  bool get loading => _loading;
  String? get error => _error;

  Future<void> loadUsers() async {
    _loading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await http.get(Uri.parse('https://api.example.com/users'));
      final data = jsonDecode(response.body) as List;
      _users = data.map((json) => User.fromJson(json)).toList();
    } catch (e) {
      _error = e.toString();
    } finally {
      _loading = false;
      notifyListeners();
    }
  }
}

// 注册
void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => UserProvider()),
      ],
      child: MyApp(),
    ),
  );
}

// 使用
class UserList extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer<UserProvider>(
      builder: (context, provider, child) {
        if (provider.loading) {
          return Center(child: CircularProgressIndicator());
        }

        if (provider.error != null) {
          return Center(child: Text('Error: ${provider.error}'));
        }

        return ListView.builder(
          itemCount: provider.users.length,
          itemBuilder: (context, index) {
            final user = provider.users[index];
            return ListTile(
              title: Text(user.name),
              subtitle: Text(user.email),
            );
          },
        );
      },
    );
  }
}
```

### Riverpod (推荐)
```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Provider
final userRepositoryProvider = Provider((ref) => UserRepository());

final usersProvider = FutureProvider<List<User>>((ref) async {
  final repository = ref.watch(userRepositoryProvider);
  return repository.getUsers();
});

// 使用
class UserList extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final usersAsync = ref.watch(usersProvider);

    return usersAsync.when(
      data: (users) => ListView.builder(
        itemCount: users.length,
        itemBuilder: (context, index) {
          return ListTile(title: Text(users[index].name));
        },
      ),
      loading: () => Center(child: CircularProgressIndicator()),
      error: (error, stack) => Center(child: Text('Error: $error')),
    );
  }
}

// StateNotifier (复杂状态)
class UserNotifier extends StateNotifier<AsyncValue<List<User>>> {
  UserNotifier(this.repository) : super(const AsyncValue.loading()) {
    loadUsers();
  }

  final UserRepository repository;

  Future<void> loadUsers() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => repository.getUsers());
  }

  Future<void> refresh() async {
    loadUsers();
  }
}

final userNotifierProvider = StateNotifierProvider<UserNotifier, AsyncValue<List<User>>>((ref) {
  return UserNotifier(ref.watch(userRepositoryProvider));
});
```

### Navigation
```dart
import 'package:go_router/go_router.dart';

final router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => HomeScreen(),
    ),
    GoRoute(
      path: '/detail/:id',
      builder: (context, state) {
        final id = state.pathParameters['id']!;
        return DetailScreen(userId: int.parse(id));
      },
    ),
  ],
);

void main() {
  runApp(MaterialApp.router(
    routerConfig: router,
  ));
}

// 使用
context.go('/detail/123');
context.push('/detail/123');
context.pop();
```

### Platform Channels (原生桥接)
```dart
// Flutter 端
import 'package:flutter/services.dart';

class BiometricAuth {
  static const platform = MethodChannel('com.example.app/biometric');

  static Future<bool> authenticate(String reason) async {
    try {
      final result = await platform.invokeMethod('authenticate', {'reason': reason});
      return result['success'] as bool;
    } on PlatformException catch (e) {
      print('Error: ${e.message}');
      return false;
    }
  }
}

// iOS (Swift)
class BiometricAuthPlugin: NSObject, FlutterPlugin {
  static func register(with registrar: FlutterPluginRegistrar) {
    let channel = FlutterMethodChannel(name: "com.example.app/biometric", binaryMessenger: registrar.messenger())
    let instance = BiometricAuthPlugin()
    registrar.addMethodCallDelegate(instance, channel: channel)
  }

  func handle(_ call: FlutterMethodCall, result: @escaping FlutterResult) {
    if call.method == "authenticate" {
      let args = call.arguments as! [String: Any]
      let reason = args["reason"] as! String

      let context = LAContext()
      context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: reason) { success, error in
        DispatchQueue.main.async {
          result(["success": success])
        }
      }
    }
  }
}

// Android (Kotlin)
class BiometricAuthPlugin: FlutterPlugin, MethodCallHandler {
  private lateinit var channel: MethodChannel

  override fun onAttachedToEngine(binding: FlutterPlugin.FlutterPluginBinding) {
    channel = MethodChannel(binding.binaryMessenger, "com.example.app/biometric")
    channel.setMethodCallHandler(this)
  }

  override fun onMethodCall(call: MethodCall, result: Result) {
    if (call.method == "authenticate") {
      val reason = call.argument<String>("reason")!!
      // BiometricPrompt 实现...
      result.success(mapOf("success" to true))
    }
  }
}
```

## 架构对比

### React Native 架构
```
JavaScript Thread
      ↓
  Bridge (JSON)
      ↓
Native Thread (iOS/Android)
      ↓
   UI Rendering
```

### Flutter 架构
```
Dart Code
    ↓
Dart VM / AOT
    ↓
Skia Engine
    ↓
Platform (OpenGL/Metal/Vulkan)
```

### 新架构 (React Native 0.68+)
```
JavaScript
    ↓
JSI (JavaScript Interface)
    ↓
C++ Turbo Modules
    ↓
Native (直接调用，无序列化)
```

## 性能优化

### React Native
```typescript
// 1. 使用 memo 避免重渲染
const UserItem = React.memo<{ user: User }>(({ user }) => {
  return (
    <View>
      <Text>{user.name}</Text>
    </View>
  );
});

// 2. FlatList 优化
<FlatList
  data={users}
  renderItem={({ item }) => <UserItem user={item} />}
  keyExtractor={(item) => item.id.toString()}
  initialNumToRender={10}
  maxToRenderPerBatch={10}
  windowSize={5}
  removeClippedSubviews={true}
  getItemLayout={(data, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
/>

// 3. 使用 Hermes 引擎
// android/app/build.gradle
project.ext.react = [
    enableHermes: true
]

// 4. 图片优化
<Image
  source={{ uri: url }}
  resizeMode="cover"
  style={{ width: 200, height: 200 }}
/>
```

### Flutter
```dart
// 1. const 构造函数
const Text('Hello'); // 编译时常量，不会重建

// 2. ListView.builder (懒加载)
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) {
    return ItemWidget(items[index]);
  },
);

// 3. RepaintBoundary (隔离重绘)
RepaintBoundary(
  child: ExpensiveWidget(),
);

// 4. 缓存图片
CachedNetworkImage(
  imageUrl: url,
  placeholder: (context, url) => CircularProgressIndicator(),
  errorWidget: (context, url, error) => Icon(Icons.error),
);

// 5. 使用 Keys
ListView.builder(
  itemBuilder: (context, index) {
    return ItemWidget(
      key: ValueKey(items[index].id),
      item: items[index],
    );
  },
);
```

## 包体积优化

### React Native
```bash
# Android
# 启用 Proguard
android {
  buildTypes {
    release {
      minifyEnabled true
      shrinkResources true
    }
  }
}

# 分包 (App Bundle)
./gradlew bundleRelease

# iOS
# 启用 Bitcode
ENABLE_BITCODE = YES
```

### Flutter
```bash
# 分析包体积
flutter build apk --analyze-size
flutter build ios --analyze-size

# 移除未使用资源
flutter build apk --tree-shake-icons

# 分架构打包
flutter build apk --split-per-abi
```

## 选型建议

| 场景 | 推荐 | 理由 |
|------|------|------|
| 团队有 Web 背景 | React Native | 学习成本低 |
| 追求极致性能 | Flutter | 自绘引擎，性能稳定 |
| UI 高度定制 | Flutter | 完全控制渲染 |
| 快速原型 | React Native | 生态成熟，库丰富 |
| 复杂动画 | Flutter | 60fps 保证 |
| 需要大量原生交互 | React Native | 桥接成熟 |
| 长期维护 | Flutter | Google 官方支持 |

## 工具清单

| 工具 | React Native | Flutter |
|------|--------------|---------|
| IDE | VS Code / WebStorm | Android Studio / VS Code |
| 调试 | Flipper / React DevTools | Flutter DevTools |
| 状态管理 | Redux / MobX / Zustand | Provider / Riverpod / Bloc |
| 导航 | React Navigation | go_router |
| 网络 | Axios / Fetch | http / dio |
| 存储 | AsyncStorage / MMKV | shared_preferences / Hive |
| 图片 | react-native-fast-image | cached_network_image |
| 测试 | Jest / Detox | flutter_test / integration_test |

## 最佳实践

### React Native
- ✅ 使用 TypeScript 提升类型安全
- ✅ Hermes 引擎提升性能
- ✅ FlatList 替代 ScrollView
- ✅ memo/useMemo/useCallback 优化渲染
- ✅ 新架构 (JSI) 减少桥接开销
- ✅ Flipper 调试网络和布局
- ✅ Fastlane 自动化部署

### Flutter
- ✅ const 构造函数减少重建
- ✅ ListView.builder 懒加载
- ✅ Riverpod 管理状态
- ✅ go_router 声明式路由
- ✅ freezed 生成不可变模型
- ✅ flutter_test 单元测试
- ✅ 使用 Keys 优化列表

---
