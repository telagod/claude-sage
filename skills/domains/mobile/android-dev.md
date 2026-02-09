---
name: android-dev
description: Android 开发。Jetpack Compose、Kotlin、ViewModel、LiveData、Coroutines、Flow、MVVM、Android架构。当用户提到 Android 开发、Jetpack Compose、Kotlin 时使用。
---

# 🤖 Android 开发 · Android Development

## Jetpack Compose 基础

### Composable 函数
```kotlin
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun Greeting(name: String) {
    Column(
        modifier = Modifier.padding(16.dp)
    ) {
        Text(
            text = "Hello, $name!",
            style = MaterialTheme.typography.headlineMedium
        )

        Spacer(modifier = Modifier.height(8.dp))

        Button(onClick = { /* TODO */ }) {
            Text("Click Me")
        }
    }
}
```

### State 管理
```kotlin
@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }
    var isEnabled by remember { mutableStateOf(true) }

    Column(
        modifier = Modifier.padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Count: $count",
            style = MaterialTheme.typography.headlineLarge
        )

        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Button(onClick = { count-- }) {
                Text("-")
            }
            Button(onClick = { count++ }) {
                Text("+")
            }
        }

        Switch(
            checked = isEnabled,
            onCheckedChange = { isEnabled = it }
        )
    }
}
```

### LazyColumn 列表
```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(users) { user ->
            UserItem(user)
        }
    }
}

@Composable
fun UserItem(user: User) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = null,
                modifier = Modifier.size(48.dp)
            )

            Spacer(modifier = Modifier.width(16.dp))

            Column {
                Text(
                    text = user.name,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = user.email,
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}
```

## Compose 高级

### Side Effects
```kotlin
@Composable
fun TimerScreen() {
    var seconds by remember { mutableStateOf(0) }

    // LaunchedEffect: 启动协程
    LaunchedEffect(Unit) {
        while (true) {
            delay(1000)
            seconds++
        }
    }

    Text("Elapsed: $seconds seconds")
}

@Composable
fun AnalyticsScreen(screenName: String) {
    // DisposableEffect: 清理资源
    DisposableEffect(screenName) {
        analytics.logScreenView(screenName)
        onDispose {
            analytics.logScreenExit(screenName)
        }
    }

    // SideEffect: 同步状态到外部
    SideEffect {
        externalState.update(screenName)
    }
}

@Composable
fun SearchScreen() {
    var query by remember { mutableStateOf("") }
    var results by remember { mutableStateOf<List<Item>>(emptyList()) }

    // snapshotFlow: 监听状态变化
    LaunchedEffect(Unit) {
        snapshotFlow { query }
            .debounce(300)
            .filter { it.isNotEmpty() }
            .collectLatest { q ->
                results = repository.search(q)
            }
    }

    Column {
        TextField(
            value = query,
            onValueChange = { query = it }
        )
        LazyColumn {
            items(results) { item ->
                Text(item.name)
            }
        }
    }
}
```

### Custom Modifier
```kotlin
fun Modifier.shimmer(): Modifier = composed {
    var offsetX by remember { mutableStateOf(0f) }
    val infiniteTransition = rememberInfiniteTransition()

    val shimmerOffset by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1000f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = LinearEasing)
        )
    )

    this.drawWithContent {
        drawContent()
        drawRect(
            brush = Brush.linearGradient(
                colors = listOf(
                    Color.Transparent,
                    Color.White.copy(alpha = 0.3f),
                    Color.Transparent
                ),
                start = Offset(shimmerOffset, 0f),
                end = Offset(shimmerOffset + 200f, 0f)
            )
        )
    }
}

// 使用
Box(
    modifier = Modifier
        .size(200.dp)
        .shimmer()
)
```

### Navigation
```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            HomeScreen(
                onNavigateToDetail = { id ->
                    navController.navigate("detail/$id")
                }
            )
        }

        composable(
            route = "detail/{itemId}",
            arguments = listOf(navArgument("itemId") { type = NavType.IntType })
        ) { backStackEntry ->
            val itemId = backStackEntry.arguments?.getInt("itemId")
            DetailScreen(itemId = itemId)
        }
    }
}
```

## ViewModel & LiveData

### ViewModel
```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    private val _isLoading = MutableLiveData(false)
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    fun loadUsers() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null

            try {
                val result = repository.getUsers()
                _users.value = result
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun refresh() {
        loadUsers()
    }
}
```

### StateFlow (推荐)
```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(UserUiState())
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    init {
        loadUsers()
    }

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            repository.getUsers()
                .onSuccess { users ->
                    _uiState.update {
                        it.copy(users = users, isLoading = false)
                    }
                }
                .onFailure { error ->
                    _uiState.update {
                        it.copy(error = error.message, isLoading = false)
                    }
                }
        }
    }
}

data class UserUiState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

// Compose 中使用
@Composable
fun UserScreen(viewModel: UserViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsState()

    when {
        uiState.isLoading -> LoadingView()
        uiState.error != null -> ErrorView(uiState.error!!)
        else -> UserList(uiState.users)
    }
}
```

## Kotlin Coroutines

### 基础用法
```kotlin
// 启动协程
viewModelScope.launch {
    val result = withContext(Dispatchers.IO) {
        repository.fetchData()
    }
    updateUI(result)
}

// 并发执行
suspend fun loadData() = coroutineScope {
    val users = async { repository.getUsers() }
    val posts = async { repository.getPosts() }

    CombinedData(
        users = users.await(),
        posts = posts.await()
    )
}

// 超时控制
try {
    withTimeout(5000) {
        repository.fetchData()
    }
} catch (e: TimeoutCancellationException) {
    // 处理超时
}
```

### Flow
```kotlin
class UserRepository {
    fun observeUsers(): Flow<List<User>> = flow {
        while (true) {
            val users = api.getUsers()
            emit(users)
            delay(30000) // 每30秒刷新
        }
    }

    fun searchUsers(query: String): Flow<List<User>> = flow {
        emit(emptyList()) // 初始状态
        delay(300) // 防抖
        val results = api.search(query)
        emit(results)
    }.flowOn(Dispatchers.IO)
}

// ViewModel 中使用
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    val users: StateFlow<List<User>> = repository.observeUsers()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    private val searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<User>> = searchQuery
        .debounce(300)
        .filter { it.isNotEmpty() }
        .flatMapLatest { query ->
            repository.searchUsers(query)
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = emptyList()
        )

    fun search(query: String) {
        searchQuery.value = query
    }
}
```

### Channel
```kotlin
class EventBus {
    private val _events = Channel<Event>(Channel.BUFFERED)
    val events: Flow<Event> = _events.receiveAsFlow()

    suspend fun send(event: Event) {
        _events.send(event)
    }
}

// 使用
viewModelScope.launch {
    eventBus.events.collect { event ->
        when (event) {
            is Event.UserLoggedIn -> handleLogin(event.user)
            is Event.DataUpdated -> refresh()
        }
    }
}
```

## MVVM 架构

### Model
```kotlin
data class User(
    val id: Int,
    val name: String,
    val email: String,
    val avatarUrl: String
)

data class LoginRequest(
    val username: String,
    val password: String
)

data class LoginResponse(
    val token: String,
    val user: User
)
```

### Repository
```kotlin
interface UserRepository {
    suspend fun login(username: String, password: String): Result<LoginResponse>
    suspend fun getProfile(): Result<User>
    fun observeUser(): Flow<User?>
}

class UserRepositoryImpl(
    private val api: ApiService,
    private val userDao: UserDao,
    private val tokenManager: TokenManager
) : UserRepository {

    override suspend fun login(username: String, password: String): Result<LoginResponse> {
        return try {
            val request = LoginRequest(username, password)
            val response = api.login(request)
            tokenManager.saveToken(response.token)
            userDao.insert(response.user)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getProfile(): Result<User> {
        return try {
            val user = api.getProfile()
            userDao.insert(user)
            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override fun observeUser(): Flow<User?> {
        return userDao.observeUser()
    }
}
```

### ViewModel
```kotlin
@HiltViewModel
class LoginViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()

    fun updateUsername(username: String) {
        _uiState.update { it.copy(username = username) }
    }

    fun updatePassword(password: String) {
        _uiState.update { it.copy(password = password) }
    }

    fun login() {
        val state = _uiState.value
        if (!state.isValid) return

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }

            repository.login(state.username, state.password)
                .onSuccess {
                    _uiState.update { it.copy(isLoading = false, isLoggedIn = true) }
                }
                .onFailure { error ->
                    _uiState.update {
                        it.copy(isLoading = false, error = error.message)
                    }
                }
        }
    }
}

data class LoginUiState(
    val username: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val error: String? = null,
    val isLoggedIn: Boolean = false
) {
    val isValid: Boolean
        get() = username.isNotEmpty() && password.length >= 6
}
```

### View (Compose)
```kotlin
@Composable
fun LoginScreen(
    viewModel: LoginViewModel = hiltViewModel(),
    onLoginSuccess: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(uiState.isLoggedIn) {
        if (uiState.isLoggedIn) {
            onLoginSuccess()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center
    ) {
        OutlinedTextField(
            value = uiState.username,
            onValueChange = viewModel::updateUsername,
            label = { Text("Username") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(8.dp))

        OutlinedTextField(
            value = uiState.password,
            onValueChange = viewModel::updatePassword,
            label = { Text("Password") },
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier.fillMaxWidth()
        )

        if (uiState.error != null) {
            Text(
                text = uiState.error!!,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 8.dp)
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = viewModel::login,
            enabled = uiState.isValid && !uiState.isLoading,
            modifier = Modifier.fillMaxWidth()
        ) {
            if (uiState.isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    color = MaterialTheme.colorScheme.onPrimary
                )
            } else {
                Text("Login")
            }
        }
    }
}
```

## 依赖注入 (Hilt)

### 配置
```kotlin
@HiltAndroidApp
class MyApplication : Application()

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MyApp()
        }
    }
}
```

### Module
```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(AuthInterceptor())
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl
    ): UserRepository
}
```

## Room 数据库

### Entity
```kotlin
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: Int,
    val name: String,
    val email: String,
    @ColumnInfo(name = "avatar_url") val avatarUrl: String,
    @ColumnInfo(name = "created_at") val createdAt: Long = System.currentTimeMillis()
)
```

### DAO
```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun observeAll(): Flow<List<UserEntity>>

    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getById(id: Int): UserEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: UserEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(users: List<UserEntity>)

    @Delete
    suspend fun delete(user: UserEntity)

    @Query("DELETE FROM users")
    suspend fun deleteAll()
}
```

### Database
```kotlin
@Database(
    entities = [UserEntity::class],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        )
        .fallbackToDestructiveMigration()
        .build()
    }

    @Provides
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }
}
```

## 网络层

### Retrofit
```kotlin
interface ApiService {
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): LoginResponse

    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: Int): User

    @GET("users")
    suspend fun getUsers(
        @Query("page") page: Int,
        @Query("limit") limit: Int = 20
    ): List<User>

    @Multipart
    @POST("upload")
    suspend fun uploadImage(
        @Part file: MultipartBody.Part
    ): UploadResponse
}
```

### Interceptor
```kotlin
class AuthInterceptor(
    private val tokenManager: TokenManager
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val original = chain.request()
        val token = tokenManager.getToken()

        val request = if (token != null) {
            original.newBuilder()
                .header("Authorization", "Bearer $token")
                .build()
        } else {
            original
        }

        return chain.proceed(request)
    }
}

class LoggingInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        Log.d("API", "Request: ${request.method} ${request.url}")

        val response = chain.proceed(request)
        Log.d("API", "Response: ${response.code}")

        return response
    }
}
```

## 性能优化

### LazyColumn 优化
```kotlin
@Composable
fun OptimizedList(items: List<Item>) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(
            items = items,
            key = { it.id } // 关键：提供稳定的 key
        ) { item ->
            ItemCard(item)
        }
    }
}

@Composable
fun ItemCard(item: Item) {
    // 使用 remember 避免重组时重新计算
    val formattedDate = remember(item.timestamp) {
        formatDate(item.timestamp)
    }

    Card {
        Text(formattedDate)
    }
}
```

### 图片加载 (Coil)
```kotlin
@Composable
fun AsyncImage(url: String) {
    AsyncImage(
        model = ImageRequest.Builder(LocalContext.current)
            .data(url)
            .crossfade(true)
            .memoryCachePolicy(CachePolicy.ENABLED)
            .diskCachePolicy(CachePolicy.ENABLED)
            .build(),
        contentDescription = null,
        modifier = Modifier.size(200.dp)
    )
}
```

### 避免过度重组
```kotlin
@Composable
fun ExpensiveScreen(data: Data) {
    // ❌ 错误：每次重组都会创建新实例
    val processor = DataProcessor()

    // ✅ 正确：使用 remember
    val processor = remember { DataProcessor() }

    // ✅ 使用 derivedStateOf 避免不必要的重组
    val filteredData by remember {
        derivedStateOf {
            data.items.filter { it.isActive }
        }
    }
}
```

## 测试

### Unit Test
```kotlin
@Test
fun `login success updates state correctly`() = runTest {
    val repository = FakeUserRepository()
    val viewModel = LoginViewModel(repository)

    viewModel.updateUsername("test")
    viewModel.updatePassword("password")
    viewModel.login()

    advanceUntilIdle()

    val state = viewModel.uiState.value
    assertTrue(state.isLoggedIn)
    assertNull(state.error)
}

class FakeUserRepository : UserRepository {
    var loginResult: Result<LoginResponse>? = null

    override suspend fun login(username: String, password: String): Result<LoginResponse> {
        return loginResult ?: Result.success(
            LoginResponse("token", User(1, "Test", "test@example.com", ""))
        )
    }

    override suspend fun getProfile(): Result<User> {
        return Result.success(User(1, "Test", "test@example.com", ""))
    }

    override fun observeUser(): Flow<User?> = flowOf(null)
}
```

### UI Test
```kotlin
@get:Rule
val composeTestRule = createComposeRule()

@Test
fun loginFlow() {
    composeTestRule.setContent {
        LoginScreen(onLoginSuccess = {})
    }

    composeTestRule
        .onNodeWithText("Username")
        .performTextInput("testuser")

    composeTestRule
        .onNodeWithText("Password")
        .performTextInput("password123")

    composeTestRule
        .onNodeWithText("Login")
        .performClick()

    composeTestRule
        .onNodeWithText("Welcome")
        .assertIsDisplayed()
}
```

## 工具清单

| 工具 | 用途 |
|------|------|
| Android Studio | IDE |
| Gradle | 构建工具 |
| Hilt | 依赖注入 |
| Retrofit | 网络请求 |
| Room | 数据库 |
| Coil | 图片加载 |
| LeakCanary | 内存泄漏检测 |
| Detekt | 代码规范 |

## 最佳实践

- ✅ Jetpack Compose 优先，View 系统按需使用
- ✅ MVVM 架构 + Repository 模式
- ✅ StateFlow 替代 LiveData
- ✅ Kotlin Coroutines 处理异步
- ✅ Hilt 依赖注入
- ✅ Room 本地持久化
- ✅ 使用 key 优化 LazyColumn
- ✅ remember/derivedStateOf 避免重组
- ✅ 单元测试覆盖 ViewModel
- ✅ UI 测试验证关键流程

---
