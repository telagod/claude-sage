---
name: kotlin
description: Kotlin 开发技术。Jetpack Compose、Coroutines、Flow、Android 开发、协程并发。当用户提到 Kotlin、Jetpack Compose、Coroutines、Flow、Android 开发时使用。
---

# 🤖 Kotlin 开发 · Kotlin Development

## 生态架构

```
         Kotlin Coroutines
              │
    ┌─────────┼─────────┐
    │         │         │
  Flow    Channel   StateFlow
    │         │         │
    └─────────┼─────────┘
              │
      Jetpack Compose
              │
    ┌─────────┼─────────┐
  ViewModel  Room    Retrofit
```

## Kotlin 语言特性

### 空安全
```kotlin
// 可空类型
var name: String? = null
val length = name?.length ?: 0  // Elvis 操作符

// 安全调用链
val city = user?.address?.city

// 非空断言 (谨慎使用)
val length = name!!.length

// let 作用域函数
name?.let {
    println("Name is $it")
}

// 智能转换
fun process(value: Any) {
    if (value is String) {
        println(value.length)  // 自动转换为 String
    }
}
```

### 数据类与密封类
```kotlin
// 数据类
data class User(
    val id: String,
    val name: String,
    val email: String
) {
    fun isAdmin() = email.endsWith("@admin.com")
}

val user = User("1", "John", "john@example.com")
val updated = user.copy(name = "Jane")

// 密封类 (类型安全的枚举)
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

fun handleResult(result: Result<User>) {
    when (result) {
        is Result.Success -> println(result.data)
        is Result.Error -> println(result.message)
        Result.Loading -> println("Loading...")
    }
}
```

### 扩展函数
```kotlin
// 为现有类添加方法
fun String.isEmail(): Boolean {
    return this.contains("@") && this.contains(".")
}

fun List<Int>.average(): Double {
    return if (isEmpty()) 0.0 else sum().toDouble() / size
}

// 使用
val email = "test@example.com"
if (email.isEmail()) {
    println("Valid email")
}

val numbers = listOf(1, 2, 3, 4, 5)
println(numbers.average())  // 3.0
```

### 高阶函数与 Lambda
```kotlin
// 高阶函数
fun <T> List<T>.customFilter(predicate: (T) -> Boolean): List<T> {
    val result = mutableListOf<T>()
    for (item in this) {
        if (predicate(item)) {
            result.add(item)
        }
    }
    return result
}

// 使用
val numbers = listOf(1, 2, 3, 4, 5)
val evens = numbers.customFilter { it % 2 == 0 }

// 函数类型参数
fun performOperation(x: Int, y: Int, operation: (Int, Int) -> Int): Int {
    return operation(x, y)
}

val sum = performOperation(5, 3) { a, b -> a + b }
val product = performOperation(5, 3) { a, b -> a * b }
```

## Jetpack Compose

### 组合函数
```kotlin
import androidx.compose.runtime.*
import androidx.compose.material3.*
import androidx.compose.foundation.layout.*

@Composable
fun UserProfile(user: User) {
    var isExpanded by remember { mutableStateOf(false) }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
            .clickable { isExpanded = !isExpanded }
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = user.name,
                style = MaterialTheme.typography.headlineMedium
            )

            Text(
                text = user.email,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.secondary
            )

            AnimatedVisibility(visible = isExpanded) {
                Text(
                    text = user.bio,
                    modifier = Modifier.padding(top = 8.dp)
                )
            }
        }
    }
}
```

### 状态管理
```kotlin
// remember - 组合内状态
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}

// rememberSaveable - 配置变更后保留
@Composable
fun SaveableCounter() {
    var count by rememberSaveable { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}

// ViewModel 状态
class UserViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _users.value = repository.getUsers()
        }
    }
}

@Composable
fun UserList(viewModel: UserViewModel = viewModel()) {
    val users by viewModel.users.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadUsers()
    }

    LazyColumn {
        items(users) { user ->
            UserItem(user)
        }
    }
}
```

### 列表与导航
```kotlin
@Composable
fun ItemList(items: List<Item>, onItemClick: (Item) -> Unit) {
    LazyColumn {
        items(items, key = { it.id }) { item ->
            ItemRow(
                item = item,
                onClick = { onItemClick(item) }
            )
        }
    }
}

@Composable
fun ItemRow(item: Item, onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(16.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Column {
            Text(
                text = item.name,
                style = MaterialTheme.typography.titleMedium
            )
            Text(
                text = item.description,
                style = MaterialTheme.typography.bodySmall
            )
        }

        Icon(
            imageVector = Icons.Default.ChevronRight,
            contentDescription = null
        )
    }
}

// Navigation
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController, startDestination = "home") {
        composable("home") {
            HomeScreen(
                onNavigateToDetail = { id ->
                    navController.navigate("detail/$id")
                }
            )
        }
        composable(
            route = "detail/{id}",
            arguments = listOf(navArgument("id") { type = NavType.StringType })
        ) { backStackEntry ->
            val id = backStackEntry.arguments?.getString("id")
            DetailScreen(id = id)
        }
    }
}
```

### 副作用处理
```kotlin
@Composable
fun EffectsExample() {
    // LaunchedEffect - 启动协程
    LaunchedEffect(key1 = Unit) {
        // 组合进入时执行一次
        loadData()
    }

    // DisposableEffect - 清理资源
    DisposableEffect(Unit) {
        val listener = setupListener()
        onDispose {
            listener.remove()
        }
    }

    // SideEffect - 发布状态到非 Compose 代码
    SideEffect {
        analytics.trackScreenView("Home")
    }

    // derivedStateOf - 派生状态
    val items = remember { mutableStateListOf<Item>() }
    val hasItems by remember {
        derivedStateOf { items.isNotEmpty() }
    }
}
```

## Kotlin Coroutines

### 基础协程
```kotlin
import kotlinx.coroutines.*

// 启动协程
fun main() = runBlocking {
    launch {
        delay(1000L)
        println("World!")
    }
    println("Hello,")
}

// async/await 并发
suspend fun fetchUserData(userId: String): UserData = coroutineScope {
    val userDeferred = async { fetchUser(userId) }
    val postsDeferred = async { fetchPosts(userId) }
    val friendsDeferred = async { fetchFriends(userId) }

    UserData(
        user = userDeferred.await(),
        posts = postsDeferred.await(),
        friends = friendsDeferred.await()
    )
}

// 超时控制
suspend fun fetchWithTimeout() {
    try {
        withTimeout(5000L) {
            fetchData()
        }
    } catch (e: TimeoutCancellationException) {
        println("Request timed out")
    }
}
```

### 协程作用域
```kotlin
class MyViewModel : ViewModel() {
    // ViewModel 作用域
    fun loadData() {
        viewModelScope.launch {
            try {
                val data = repository.fetchData()
                _state.value = State.Success(data)
            } catch (e: Exception) {
                _state.value = State.Error(e.message)
            }
        }
    }
}

class MyActivity : AppCompatActivity() {
    // 生命周期作用域
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    updateUI(state)
                }
            }
        }
    }
}

// 自定义作用域
class DataRepository {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun fetchData() {
        scope.launch {
            // 后台任务
        }
    }

    fun cleanup() {
        scope.cancel()
    }
}
```

### 调度器
```kotlin
// Dispatchers.Main - UI 线程
lifecycleScope.launch(Dispatchers.Main) {
    updateUI()
}

// Dispatchers.IO - IO 操作
withContext(Dispatchers.IO) {
    val data = database.query()
}

// Dispatchers.Default - CPU 密集型
withContext(Dispatchers.Default) {
    val result = complexCalculation()
}

// 切换调度器
suspend fun loadData() {
    val data = withContext(Dispatchers.IO) {
        fetchFromNetwork()
    }
    withContext(Dispatchers.Main) {
        displayData(data)
    }
}
```

## Flow 流式编程

### Flow 基础
```kotlin
import kotlinx.coroutines.flow.*

// 创建 Flow
fun simpleFlow(): Flow<Int> = flow {
    for (i in 1..3) {
        delay(100)
        emit(i)
    }
}

// 收集 Flow
suspend fun collectFlow() {
    simpleFlow().collect { value ->
        println(value)
    }
}

// Flow 操作符
fun transformFlow(): Flow<String> = flow {
    emit(1)
    emit(2)
    emit(3)
}.map { value ->
    "Number: $value"
}.filter { text ->
    text.contains("2")
}
```

### StateFlow 与 SharedFlow
```kotlin
class UserRepository {
    // StateFlow - 状态流 (有初始值)
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    // SharedFlow - 事件流 (无初始值)
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun loadUsers() {
        val result = api.getUsers()
        _users.value = result
        _events.emit(Event.UsersLoaded)
    }
}

// 在 ViewModel 中使用
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    val users = repository.users
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    init {
        viewModelScope.launch {
            repository.events.collect { event ->
                handleEvent(event)
            }
        }
    }
}
```

### Flow 操作符链
```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery

    val searchResults: StateFlow<List<Result>> = searchQuery
        .debounce(300)
        .filter { it.length >= 3 }
        .distinctUntilChanged()
        .flatMapLatest { query ->
            repository.search(query)
                .catch { emit(emptyList()) }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}
```

## Android 架构

### MVVM 模式
```kotlin
// Model
data class User(
    val id: String,
    val name: String,
    val email: String
)

// Repository
class UserRepository(
    private val api: ApiService,
    private val dao: UserDao
) {
    fun getUsers(): Flow<List<User>> = flow {
        // 先发射缓存数据
        emit(dao.getAll())

        // 然后获取网络数据
        val users = api.getUsers()
        dao.insertAll(users)
        emit(users)
    }
}

// ViewModel
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    init {
        loadUsers()
    }

    private fun loadUsers() {
        viewModelScope.launch {
            repository.getUsers()
                .catch { e ->
                    _uiState.value = UiState.Error(e.message ?: "Unknown error")
                }
                .collect { users ->
                    _uiState.value = UiState.Success(users)
                }
        }
    }
}

sealed class UiState {
    object Loading : UiState()
    data class Success(val users: List<User>) : UiState()
    data class Error(val message: String) : UiState()
}

// View (Compose)
@Composable
fun UserScreen(viewModel: UserViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsState()

    when (val state = uiState) {
        is UiState.Loading -> LoadingIndicator()
        is UiState.Success -> UserList(state.users)
        is UiState.Error -> ErrorMessage(state.message)
    }
}
```

## Room 数据库

### 实体与 DAO
```kotlin
// Entity
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "name") val name: String,
    @ColumnInfo(name = "email") val email: String,
    @ColumnInfo(name = "created_at") val createdAt: Long
)

// DAO
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAll(): Flow<List<UserEntity>>

    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getById(userId: String): UserEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: UserEntity)

    @Insert
    suspend fun insertAll(users: List<UserEntity>)

    @Update
    suspend fun update(user: UserEntity)

    @Delete
    suspend fun delete(user: UserEntity)

    @Query("DELETE FROM users WHERE created_at < :timestamp")
    suspend fun deleteOlderThan(timestamp: Long)
}

// Database
@Database(entities = [UserEntity::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}
```

## Retrofit 网络请求

### API 定义
```kotlin
interface ApiService {
    @GET("users")
    suspend fun getUsers(): List<User>

    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User

    @POST("users")
    suspend fun createUser(@Body user: CreateUserRequest): User

    @PUT("users/{id}")
    suspend fun updateUser(
        @Path("id") userId: String,
        @Body user: UpdateUserRequest
    ): User

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") userId: String)

    @GET("search")
    suspend fun search(@Query("q") query: String): SearchResult
}

// Retrofit 配置
object RetrofitClient {
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("Authorization", "Bearer $token")
                .build()
            chain.proceed(request)
        }
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    val api: ApiService = Retrofit.Builder()
        .baseUrl("https://api.example.com/")
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
        .create(ApiService::class.java)
}
```

## 依赖注入 (Hilt)

### 模块配置
```kotlin
@HiltAndroidApp
class MyApplication : Application()

@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideApiService(): ApiService {
        return RetrofitClient.api
    }

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return AppDatabase.getDatabase(context)
    }

    @Provides
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }
}

// 注入使用
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {
    // ...
}

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ...
    }
}
```

## 测试

### 单元测试
```kotlin
class CalculatorTest {
    private lateinit var calculator: Calculator

    @Before
    fun setup() {
        calculator = Calculator()
    }

    @Test
    fun `addition should return correct result`() {
        val result = calculator.add(2, 3)
        assertEquals(5, result)
    }

    @Test
    fun `division by zero should throw exception`() {
        assertThrows<ArithmeticException> {
            calculator.divide(10, 0)
        }
    }
}

// 协程测试
@ExperimentalCoroutinesApi
class UserViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var viewModel: UserViewModel
    private lateinit var repository: FakeUserRepository

    @Before
    fun setup() {
        repository = FakeUserRepository()
        viewModel = UserViewModel(repository)
    }

    @Test
    fun `loadUsers should update state to success`() = runTest {
        val users = listOf(User("1", "John", "john@example.com"))
        repository.setUsers(users)

        viewModel.loadUsers()

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Success)
        assertEquals(users, (state as UiState.Success).users)
    }
}
```

## 最佳实践

| 场景 | 推荐做法 |
|------|----------|
| 异步操作 | 使用 Coroutines + Flow |
| 状态管理 | StateFlow + ViewModel |
| 依赖注入 | Hilt |
| 网络请求 | Retrofit + OkHttp |
| 本地存储 | Room + DataStore |
| UI 开发 | Jetpack Compose |

## 工具清单

| 工具 | 用途 |
|------|------|
| Android Studio | 官方 IDE |
| Gradle | 构建工具 |
| Kotlin Coroutines | 异步编程 |
| Jetpack Compose | 声明式 UI |
| Hilt | 依赖注入 |
| Retrofit | 网络请求 |
| Room | 数据库 |
| Coil | 图片加载 |

---
