---
name: ios-dev
description: iOS 开发。SwiftUI、UIKit、Combine、MVVM、VIPER、Auto Layout、iOS架构。当用户提到 iOS 开发、SwiftUI、UIKit、Combine 时使用。
---

# 🍎 iOS 开发 · iOS Development

## SwiftUI 基础

### View 组件
```swift
import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack(spacing: 20) {
            Text("Hello, SwiftUI")
                .font(.largeTitle)
                .foregroundColor(.blue)

            Image(systemName: "star.fill")
                .resizable()
                .frame(width: 50, height: 50)

            Button("Tap Me") {
                print("Button tapped")
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }
}
```

### State 管理
```swift
struct CounterView: View {
    @State private var count = 0
    @State private var isOn = false

    var body: some View {
        VStack {
            Text("Count: \(count)")
                .font(.title)

            HStack {
                Button("-") { count -= 1 }
                Button("+") { count += 1 }
            }

            Toggle("Enable", isOn: $isOn)
        }
    }
}
```

### Binding 双向绑定
```swift
struct ParentView: View {
    @State private var text = ""

    var body: some View {
        VStack {
            Text("Input: \(text)")
            ChildView(text: $text)
        }
    }
}

struct ChildView: View {
    @Binding var text: String

    var body: some View {
        TextField("Enter text", text: $text)
            .textFieldStyle(.roundedBorder)
            .padding()
    }
}
```

## SwiftUI 高级

### ObservableObject
```swift
class UserViewModel: ObservableObject {
    @Published var username = ""
    @Published var isLoading = false
    @Published var users: [User] = []

    func fetchUsers() async {
        isLoading = true
        defer { isLoading = false }

        do {
            let url = URL(string: "https://api.example.com/users")!
            let (data, _) = try await URLSession.shared.data(from: url)
            users = try JSONDecoder().decode([User].self, from: data)
        } catch {
            print("Error: \(error)")
        }
    }
}

struct UserListView: View {
    @StateObject private var viewModel = UserViewModel()

    var body: some View {
        List(viewModel.users) { user in
            Text(user.name)
        }
        .task {
            await viewModel.fetchUsers()
        }
        .overlay {
            if viewModel.isLoading {
                ProgressView()
            }
        }
    }
}
```

### Environment
```swift
// 自定义 Environment Key
struct ThemeKey: EnvironmentKey {
    static let defaultValue = Theme.light
}

extension EnvironmentValues {
    var theme: Theme {
        get { self[ThemeKey.self] }
        set { self[ThemeKey.self] = newValue }
    }
}

// 使用
struct RootView: View {
    @State private var theme = Theme.dark

    var body: some View {
        ContentView()
            .environment(\.theme, theme)
    }
}

struct ContentView: View {
    @Environment(\.theme) var theme

    var body: some View {
        Text("Hello")
            .foregroundColor(theme.textColor)
    }
}
```

### Custom ViewModifier
```swift
struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(Color.white)
            .cornerRadius(10)
            .shadow(radius: 5)
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardModifier())
    }
}

// 使用
Text("Card Content")
    .cardStyle()
```

## UIKit 集成

### UIViewController 包装
```swift
import UIKit
import SwiftUI

struct CameraView: UIViewControllerRepresentable {
    @Binding var image: UIImage?
    @Environment(\.dismiss) var dismiss

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.sourceType = .camera
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: CameraView

        init(_ parent: CameraView) {
            self.parent = parent
        }

        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            if let image = info[.originalImage] as? UIImage {
                parent.image = image
            }
            parent.dismiss()
        }
    }
}
```

### UIView 包装
```swift
struct MapView: UIViewRepresentable {
    @Binding var region: MKCoordinateRegion

    func makeUIView(context: Context) -> MKMapView {
        let mapView = MKMapView()
        mapView.delegate = context.coordinator
        return mapView
    }

    func updateUIView(_ uiView: MKMapView, context: Context) {
        uiView.setRegion(region, animated: true)
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, MKMapViewDelegate {
        var parent: MapView

        init(_ parent: MapView) {
            self.parent = parent
        }
    }
}
```

### Auto Layout
```swift
class CustomViewController: UIViewController {
    let titleLabel = UILabel()
    let button = UIButton()

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
    }

    func setupUI() {
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        button.translatesAutoresizingMaskIntoConstraints = false

        view.addSubview(titleLabel)
        view.addSubview(button)

        NSLayoutConstraint.activate([
            titleLabel.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20),
            titleLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),

            button.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 20),
            button.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            button.widthAnchor.constraint(equalToConstant: 200),
            button.heightAnchor.constraint(equalToConstant: 44)
        ])
    }
}
```

## Combine 响应式

### Publisher 基础
```swift
import Combine

class DataService {
    func fetchData() -> AnyPublisher<[Item], Error> {
        URLSession.shared
            .dataTaskPublisher(for: URL(string: "https://api.example.com/items")!)
            .map(\.data)
            .decode(type: [Item].self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }
}

class ViewModel: ObservableObject {
    @Published var items: [Item] = []
    @Published var error: Error?

    private var cancellables = Set<AnyCancellable>()
    private let service = DataService()

    func load() {
        service.fetchData()
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    if case .failure(let error) = completion {
                        self?.error = error
                    }
                },
                receiveValue: { [weak self] items in
                    self?.items = items
                }
            )
            .store(in: &cancellables)
    }
}
```

### Operators
```swift
// Map & Filter
let numbers = [1, 2, 3, 4, 5].publisher
numbers
    .map { $0 * 2 }
    .filter { $0 > 5 }
    .sink { print($0) }
    .store(in: &cancellables)

// Debounce (搜索防抖)
@Published var searchText = ""

$searchText
    .debounce(for: .milliseconds(300), scheduler: DispatchQueue.main)
    .removeDuplicates()
    .sink { text in
        self.performSearch(text)
    }
    .store(in: &cancellables)

// CombineLatest
Publishers.CombineLatest($username, $password)
    .map { username, password in
        !username.isEmpty && password.count >= 6
    }
    .assign(to: &$isValid)
```

### Subject
```swift
class EventBus {
    static let shared = EventBus()

    let userLoggedIn = PassthroughSubject<User, Never>()
    let dataUpdated = CurrentValueSubject<[Item], Never>([])

    private init() {}
}

// 发送
EventBus.shared.userLoggedIn.send(user)

// 订阅
EventBus.shared.userLoggedIn
    .sink { user in
        print("User logged in: \(user.name)")
    }
    .store(in: &cancellables)
```

## MVVM 架构

### Model
```swift
struct User: Codable, Identifiable {
    let id: Int
    let name: String
    let email: String
}

struct LoginRequest: Codable {
    let username: String
    let password: String
}

struct LoginResponse: Codable {
    let token: String
    let user: User
}
```

### Repository
```swift
protocol UserRepository {
    func login(username: String, password: String) async throws -> LoginResponse
    func fetchProfile() async throws -> User
}

class UserRepositoryImpl: UserRepository {
    private let apiClient: APIClient

    init(apiClient: APIClient = .shared) {
        self.apiClient = apiClient
    }

    func login(username: String, password: String) async throws -> LoginResponse {
        let request = LoginRequest(username: username, password: password)
        return try await apiClient.post("/auth/login", body: request)
    }

    func fetchProfile() async throws -> User {
        try await apiClient.get("/user/profile")
    }
}
```

### ViewModel
```swift
@MainActor
class LoginViewModel: ObservableObject {
    @Published var username = ""
    @Published var password = ""
    @Published var isLoading = false
    @Published var error: String?
    @Published var isLoggedIn = false

    private let repository: UserRepository

    init(repository: UserRepository = UserRepositoryImpl()) {
        self.repository = repository
    }

    var isValid: Bool {
        !username.isEmpty && password.count >= 6
    }

    func login() async {
        guard isValid else { return }

        isLoading = true
        error = nil

        do {
            let response = try await repository.login(username: username, password: password)
            TokenManager.shared.save(response.token)
            isLoggedIn = true
        } catch {
            self.error = error.localizedDescription
        }

        isLoading = false
    }
}
```

### View
```swift
struct LoginView: View {
    @StateObject private var viewModel = LoginViewModel()

    var body: some View {
        VStack(spacing: 20) {
            TextField("Username", text: $viewModel.username)
                .textFieldStyle(.roundedBorder)

            SecureField("Password", text: $viewModel.password)
                .textFieldStyle(.roundedBorder)

            if let error = viewModel.error {
                Text(error)
                    .foregroundColor(.red)
                    .font(.caption)
            }

            Button("Login") {
                Task {
                    await viewModel.login()
                }
            }
            .disabled(!viewModel.isValid || viewModel.isLoading)
            .buttonStyle(.borderedProminent)

            if viewModel.isLoading {
                ProgressView()
            }
        }
        .padding()
        .fullScreenCover(isPresented: $viewModel.isLoggedIn) {
            HomeView()
        }
    }
}
```

## VIPER 架构

```
View ←→ Presenter ←→ Interactor
         ↓              ↓
      Router        Entity
```

### Entity
```swift
struct Article: Codable {
    let id: Int
    let title: String
    let content: String
}
```

### Interactor
```swift
protocol ArticleInteractorProtocol {
    func fetchArticles() async throws -> [Article]
}

class ArticleInteractor: ArticleInteractorProtocol {
    private let repository: ArticleRepository

    init(repository: ArticleRepository) {
        self.repository = repository
    }

    func fetchArticles() async throws -> [Article] {
        try await repository.fetchArticles()
    }
}
```

### Presenter
```swift
@MainActor
protocol ArticlePresenterProtocol: ObservableObject {
    var articles: [Article] { get }
    var isLoading: Bool { get }
    func loadArticles()
    func didSelectArticle(_ article: Article)
}

@MainActor
class ArticlePresenter: ArticlePresenterProtocol {
    @Published var articles: [Article] = []
    @Published var isLoading = false

    private let interactor: ArticleInteractorProtocol
    private let router: ArticleRouterProtocol

    init(interactor: ArticleInteractorProtocol, router: ArticleRouterProtocol) {
        self.interactor = interactor
        self.router = router
    }

    func loadArticles() {
        Task {
            isLoading = true
            do {
                articles = try await interactor.fetchArticles()
            } catch {
                print("Error: \(error)")
            }
            isLoading = false
        }
    }

    func didSelectArticle(_ article: Article) {
        router.navigateToDetail(article)
    }
}
```

### View
```swift
struct ArticleListView<Presenter: ArticlePresenterProtocol>: View {
    @ObservedObject var presenter: Presenter

    var body: some View {
        List(presenter.articles, id: \.id) { article in
            Button(article.title) {
                presenter.didSelectArticle(article)
            }
        }
        .task {
            presenter.loadArticles()
        }
    }
}
```

### Router
```swift
protocol ArticleRouterProtocol {
    func navigateToDetail(_ article: Article)
}

class ArticleRouter: ArticleRouterProtocol {
    weak var viewController: UIViewController?

    func navigateToDetail(_ article: Article) {
        let detailVC = ArticleDetailBuilder.build(article: article)
        viewController?.navigationController?.pushViewController(detailVC, animated: true)
    }
}
```

## 网络层

### APIClient
```swift
class APIClient {
    static let shared = APIClient()
    private let baseURL = "https://api.example.com"

    func get<T: Decodable>(_ path: String) async throws -> T {
        try await request(path, method: "GET")
    }

    func post<T: Decodable, B: Encodable>(_ path: String, body: B) async throws -> T {
        try await request(path, method: "POST", body: body)
    }

    private func request<T: Decodable, B: Encodable>(_ path: String, method: String, body: B? = nil as String?) async throws -> T {
        guard let url = URL(string: baseURL + path) else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let token = TokenManager.shared.token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
        }

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw APIError.httpError(httpResponse.statusCode)
        }

        return try JSONDecoder().decode(T.self, from: data)
    }
}

enum APIError: Error {
    case invalidURL
    case invalidResponse
    case httpError(Int)
}
```

## 数据持久化

### UserDefaults
```swift
class SettingsManager {
    static let shared = SettingsManager()

    @UserDefault(key: "isDarkMode", defaultValue: false)
    var isDarkMode: Bool

    @UserDefault(key: "language", defaultValue: "en")
    var language: String
}

@propertyWrapper
struct UserDefault<T> {
    let key: String
    let defaultValue: T

    var wrappedValue: T {
        get {
            UserDefaults.standard.object(forKey: key) as? T ?? defaultValue
        }
        set {
            UserDefaults.standard.set(newValue, forKey: key)
        }
    }
}
```

### Keychain
```swift
class KeychainManager {
    static let shared = KeychainManager()

    func save(_ value: String, forKey key: String) {
        let data = value.data(using: .utf8)!
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]

        SecItemDelete(query as CFDictionary)
        SecItemAdd(query as CFDictionary, nil)
    }

    func get(forKey key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true
        ]

        var result: AnyObject?
        SecItemCopyMatching(query as CFDictionary, &result)

        guard let data = result as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }
}
```

### Core Data
```swift
class CoreDataManager {
    static let shared = CoreDataManager()

    lazy var persistentContainer: NSPersistentContainer = {
        let container = NSPersistentContainer(name: "Model")
        container.loadPersistentStores { _, error in
            if let error = error {
                fatalError("Core Data error: \(error)")
            }
        }
        return container
    }()

    var context: NSManagedObjectContext {
        persistentContainer.viewContext
    }

    func save() {
        if context.hasChanges {
            try? context.save()
        }
    }
}

// 使用
let user = User(context: CoreDataManager.shared.context)
user.name = "John"
CoreDataManager.shared.save()
```

## 性能优化

### LazyVStack
```swift
// 大列表优化
ScrollView {
    LazyVStack {
        ForEach(items) { item in
            ItemRow(item: item)
        }
    }
}
```

### Task 优先级
```swift
Task(priority: .high) {
    await loadCriticalData()
}

Task(priority: .background) {
    await syncData()
}
```

### Image 缓存
```swift
class ImageCache {
    static let shared = ImageCache()
    private var cache = NSCache<NSString, UIImage>()

    func get(forKey key: String) -> UIImage? {
        cache.object(forKey: key as NSString)
    }

    func set(_ image: UIImage, forKey key: String) {
        cache.setObject(image, forKey: key as NSString)
    }
}

struct CachedAsyncImage: View {
    let url: URL
    @State private var image: UIImage?

    var body: some View {
        Group {
            if let image = image {
                Image(uiImage: image)
                    .resizable()
            } else {
                ProgressView()
            }
        }
        .task {
            if let cached = ImageCache.shared.get(forKey: url.absoluteString) {
                image = cached
            } else {
                let (data, _) = try? await URLSession.shared.data(from: url)
                if let data = data, let downloaded = UIImage(data: data) {
                    ImageCache.shared.set(downloaded, forKey: url.absoluteString)
                    image = downloaded
                }
            }
        }
    }
}
```

## 测试

### Unit Test
```swift
import XCTest
@testable import MyApp

class LoginViewModelTests: XCTestCase {
    var viewModel: LoginViewModel!
    var mockRepository: MockUserRepository!

    override func setUp() {
        mockRepository = MockUserRepository()
        viewModel = LoginViewModel(repository: mockRepository)
    }

    func testLoginSuccess() async {
        mockRepository.loginResult = .success(LoginResponse(token: "token", user: User(id: 1, name: "Test", email: "test@example.com")))

        viewModel.username = "test"
        viewModel.password = "password"

        await viewModel.login()

        XCTAssertTrue(viewModel.isLoggedIn)
        XCTAssertNil(viewModel.error)
    }

    func testLoginFailure() async {
        mockRepository.loginResult = .failure(APIError.httpError(401))

        viewModel.username = "test"
        viewModel.password = "wrong"

        await viewModel.login()

        XCTAssertFalse(viewModel.isLoggedIn)
        XCTAssertNotNil(viewModel.error)
    }
}

class MockUserRepository: UserRepository {
    var loginResult: Result<LoginResponse, Error>!

    func login(username: String, password: String) async throws -> LoginResponse {
        try loginResult.get()
    }

    func fetchProfile() async throws -> User {
        User(id: 1, name: "Test", email: "test@example.com")
    }
}
```

### UI Test
```swift
class LoginUITests: XCTestCase {
    var app: XCUIApplication!

    override func setUp() {
        app = XCUIApplication()
        app.launch()
    }

    func testLoginFlow() {
        let usernameField = app.textFields["Username"]
        usernameField.tap()
        usernameField.typeText("testuser")

        let passwordField = app.secureTextFields["Password"]
        passwordField.tap()
        passwordField.typeText("password123")

        app.buttons["Login"].tap()

        XCTAssertTrue(app.staticTexts["Welcome"].waitForExistence(timeout: 5))
    }
}
```

## 工具清单

| 工具 | 用途 |
|------|------|
| Xcode | IDE |
| SwiftLint | 代码规范 |
| Fastlane | 自动化部署 |
| CocoaPods | 依赖管理 |
| Swift Package Manager | 官方依赖管理 |
| Instruments | 性能分析 |
| Charles | 网络抓包 |
| Reveal | UI 调试 |

## 最佳实践

- ✅ 使用 SwiftUI 优先，UIKit 按需集成
- ✅ MVVM 架构分离关注点
- ✅ async/await 替代回调地狱
- ✅ Combine 处理响应式流
- ✅ 依赖注入提升可测试性
- ✅ 使用 @MainActor 确保 UI 线程安全
- ✅ LazyVStack 优化大列表
- ✅ 图片缓存减少内存压力
- ✅ Keychain 存储敏感数据
- ✅ 单元测试覆盖核心逻辑

---
