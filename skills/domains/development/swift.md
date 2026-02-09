---
name: swift
description: Swift 开发技术。SwiftUI、UIKit、Combine、Swift Concurrency、ARC 内存管理。当用户提到 Swift、SwiftUI、UIKit、Combine、iOS 开发、async/await 时使用。
---

# 🍎 Swift 开发 · Swift Development

## 生态架构

```
         Swift Concurrency
              │
    ┌─────────┼─────────┐
    │         │         │
SwiftUI   UIKit    Combine
    │         │         │
    └─────────┼─────────┘
              │
         Foundation
              │
    ┌─────────┼─────────┐
  CoreData  Network   ARC
```

## SwiftUI 基础

### 视图声明
```swift
import SwiftUI

struct ContentView: View {
    @State private var count = 0
    @State private var isPresented = false

    var body: some View {
        VStack(spacing: 20) {
            Text("Count: \(count)")
                .font(.largeTitle)
                .foregroundColor(.blue)

            Button("Increment") {
                count += 1
            }
            .buttonStyle(.borderedProminent)

            Button("Show Sheet") {
                isPresented = true
            }
            .sheet(isPresented: $isPresented) {
                DetailView()
            }
        }
        .padding()
    }
}
```

### 状态管理
```swift
// @State - 视图内部状态
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        Button("Count: \(count)") {
            count += 1
        }
    }
}

// @Binding - 双向绑定
struct ChildView: View {
    @Binding var text: String

    var body: some View {
        TextField("Enter text", text: $text)
    }
}

// @ObservedObject - 外部可观察对象
class ViewModel: ObservableObject {
    @Published var items: [Item] = []
    @Published var isLoading = false

    func fetchItems() async {
        isLoading = true
        defer { isLoading = false }

        items = await APIClient.shared.fetchItems()
    }
}

struct ListView: View {
    @StateObject private var viewModel = ViewModel()

    var body: some View {
        List(viewModel.items) { item in
            Text(item.name)
        }
        .task {
            await viewModel.fetchItems()
        }
    }
}

// @EnvironmentObject - 环境对象
struct ParentView: View {
    @StateObject private var settings = AppSettings()

    var body: some View {
        ChildView()
            .environmentObject(settings)
    }
}
```

### 列表与导航
```swift
struct ItemListView: View {
    let items: [Item]

    var body: some View {
        NavigationStack {
            List(items) { item in
                NavigationLink(value: item) {
                    ItemRow(item: item)
                }
            }
            .navigationTitle("Items")
            .navigationDestination(for: Item.self) { item in
                ItemDetailView(item: item)
            }
        }
    }
}

// 自定义行视图
struct ItemRow: View {
    let item: Item

    var body: some View {
        HStack {
            AsyncImage(url: item.imageURL) { image in
                image.resizable()
            } placeholder: {
                ProgressView()
            }
            .frame(width: 50, height: 50)
            .clipShape(RoundedRectangle(cornerRadius: 8))

            VStack(alignment: .leading) {
                Text(item.name)
                    .font(.headline)
                Text(item.description)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
    }
}
```

### 动画与过渡
```swift
struct AnimatedView: View {
    @State private var isExpanded = false
    @State private var rotation = 0.0

    var body: some View {
        VStack {
            Rectangle()
                .fill(.blue)
                .frame(width: isExpanded ? 200 : 100,
                       height: isExpanded ? 200 : 100)
                .rotationEffect(.degrees(rotation))
                .animation(.spring(response: 0.5, dampingFraction: 0.6), value: isExpanded)

            Button("Toggle") {
                withAnimation {
                    isExpanded.toggle()
                    rotation += 180
                }
            }
        }
    }
}

// 自定义过渡
extension AnyTransition {
    static var slideAndFade: AnyTransition {
        .asymmetric(
            insertion: .move(edge: .trailing).combined(with: .opacity),
            removal: .move(edge: .leading).combined(with: .opacity)
        )
    }
}
```

## UIKit 核心

### 视图控制器
```swift
import UIKit

class UserViewController: UIViewController {
    private let tableView = UITableView()
    private var users: [User] = []

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        fetchUsers()
    }

    private func setupUI() {
        view.backgroundColor = .systemBackground

        tableView.delegate = self
        tableView.dataSource = self
        tableView.register(UserCell.self, forCellReuseIdentifier: "UserCell")

        view.addSubview(tableView)
        tableView.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            tableView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            tableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            tableView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
    }

    private func fetchUsers() {
        Task {
            users = await APIClient.shared.fetchUsers()
            tableView.reloadData()
        }
    }
}

extension UserViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        users.count
    }

    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "UserCell", for: indexPath) as! UserCell
        cell.configure(with: users[indexPath.row])
        return cell
    }
}
```

### Auto Layout
```swift
class CustomView: UIView {
    private let titleLabel = UILabel()
    private let imageView = UIImageView()

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupViews()
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    private func setupViews() {
        addSubview(imageView)
        addSubview(titleLabel)

        imageView.translatesAutoresizingMaskIntoConstraints = false
        titleLabel.translatesAutoresizingMaskIntoConstraints = false

        NSLayoutConstraint.activate([
            imageView.topAnchor.constraint(equalTo: topAnchor, constant: 16),
            imageView.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
            imageView.widthAnchor.constraint(equalToConstant: 60),
            imageView.heightAnchor.constraint(equalToConstant: 60),

            titleLabel.leadingAnchor.constraint(equalTo: imageView.trailingAnchor, constant: 12),
            titleLabel.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),
            titleLabel.centerYAnchor.constraint(equalTo: imageView.centerYAnchor)
        ])
    }
}
```

### 导航与生命周期
```swift
class MainViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Main"
        navigationItem.rightBarButtonItem = UIBarButtonItem(
            barButtonSystemItem: .add,
            target: self,
            action: #selector(addTapped)
        )
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        // 视图即将显示
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        // 视图已显示
    }

    @objc private func addTapped() {
        let detailVC = DetailViewController()
        navigationController?.pushViewController(detailVC, animated: true)
    }
}
```

## Combine 响应式编程

### Publisher 与 Subscriber
```swift
import Combine

class DataService {
    private var cancellables = Set<AnyCancellable>()

    func fetchData() {
        URLSession.shared.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: [Item].self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    switch completion {
                    case .finished:
                        print("Completed")
                    case .failure(let error):
                        print("Error: \(error)")
                    }
                },
                receiveValue: { items in
                    print("Received \(items.count) items")
                }
            )
            .store(in: &cancellables)
    }
}
```

### 操作符链
```swift
class SearchViewModel: ObservableObject {
    @Published var searchText = ""
    @Published var results: [Result] = []

    private var cancellables = Set<AnyCancellable>()

    init() {
        $searchText
            .debounce(for: .milliseconds(300), scheduler: DispatchQueue.main)
            .removeDuplicates()
            .filter { !$0.isEmpty }
            .flatMap { query in
                self.search(query: query)
                    .catch { _ in Just([]) }
            }
            .assign(to: &$results)
    }

    private func search(query: String) -> AnyPublisher<[Result], Error> {
        URLSession.shared.dataTaskPublisher(for: searchURL(query))
            .map(\.data)
            .decode(type: [Result].self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }
}
```

### Subject 类型
```swift
import Combine

class EventBus {
    static let shared = EventBus()

    let userLoggedIn = PassthroughSubject<User, Never>()
    let dataUpdated = CurrentValueSubject<[Item], Never>([])

    private init() {}
}

// 使用
EventBus.shared.userLoggedIn
    .sink { user in
        print("User logged in: \(user.name)")
    }
    .store(in: &cancellables)

EventBus.shared.userLoggedIn.send(currentUser)
```

## Swift Concurrency

### async/await
```swift
// 异步函数
func fetchUser(id: String) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

// 并发调用
func fetchMultipleUsers(ids: [String]) async throws -> [User] {
    try await withThrowingTaskGroup(of: User.self) { group in
        for id in ids {
            group.addTask {
                try await fetchUser(id: id)
            }
        }

        var users: [User] = []
        for try await user in group {
            users.append(user)
        }
        return users
    }
}

// 在视图中使用
struct UserView: View {
    @State private var user: User?

    var body: some View {
        Group {
            if let user = user {
                Text(user.name)
            } else {
                ProgressView()
            }
        }
        .task {
            user = try? await fetchUser(id: "123")
        }
    }
}
```

### Actor 并发安全
```swift
actor DatabaseManager {
    private var cache: [String: Data] = [:]

    func getData(key: String) async -> Data? {
        if let cached = cache[key] {
            return cached
        }

        let data = await fetchFromNetwork(key: key)
        cache[key] = data
        return data
    }

    func clearCache() {
        cache.removeAll()
    }
}

// 使用
let db = DatabaseManager()
let data = await db.getData(key: "user_123")
```

### AsyncSequence
```swift
struct AsyncLineReader: AsyncSequence {
    typealias Element = String

    let url: URL

    func makeAsyncIterator() -> AsyncIterator {
        AsyncIterator(url: url)
    }

    struct AsyncIterator: AsyncIteratorProtocol {
        let url: URL
        private var lines: [String]?
        private var index = 0

        mutating func next() async throws -> String? {
            if lines == nil {
                let content = try String(contentsOf: url)
                lines = content.components(separatedBy: .newlines)
            }

            guard let lines = lines, index < lines.count else {
                return nil
            }

            defer { index += 1 }
            return lines[index]
        }
    }
}

// 使用
for try await line in AsyncLineReader(url: fileURL) {
    print(line)
}
```

## 内存管理 (ARC)

### 强引用循环
```swift
class Person {
    let name: String
    var apartment: Apartment?

    init(name: String) {
        self.name = name
    }

    deinit {
        print("\(name) is being deinitialized")
    }
}

class Apartment {
    let unit: String
    weak var tenant: Person?  // weak 避免循环引用

    init(unit: String) {
        self.unit = unit
    }

    deinit {
        print("Apartment \(unit) is being deinitialized")
    }
}
```

### 闭包捕获列表
```swift
class ViewController: UIViewController {
    var name = "View Controller"

    func setupHandler() {
        // ❌ 强引用循环
        someAsyncOperation {
            print(self.name)
        }

        // ✅ 使用 weak
        someAsyncOperation { [weak self] in
            guard let self = self else { return }
            print(self.name)
        }

        // ✅ 使用 unowned (确定不会为 nil)
        someAsyncOperation { [unowned self] in
            print(self.name)
        }
    }
}
```

### 值类型 vs 引用类型
```swift
// 值类型 (struct, enum) - 复制语义
struct Point {
    var x: Int
    var y: Int
}

var p1 = Point(x: 0, y: 0)
var p2 = p1
p2.x = 10
print(p1.x)  // 0 (未改变)

// 引用类型 (class) - 共享语义
class Rectangle {
    var width: Int
    var height: Int

    init(width: Int, height: Int) {
        self.width = width
        self.height = height
    }
}

let r1 = Rectangle(width: 10, height: 20)
let r2 = r1
r2.width = 30
print(r1.width)  // 30 (已改变)
```

## 网络请求

### URLSession
```swift
class APIClient {
    static let shared = APIClient()

    func fetch<T: Decodable>(_ type: T.Type, from url: URL) async throws -> T {
        let (data, response) = try await URLSession.shared.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIError.invalidResponse
        }

        return try JSONDecoder().decode(T.self, from: data)
    }

    func post<T: Encodable, R: Decodable>(
        _ endpoint: String,
        body: T
    ) async throws -> R {
        var request = URLRequest(url: URL(string: endpoint)!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(body)

        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(R.self, from: data)
    }
}
```

## CoreData 持久化

### 数据模型
```swift
import CoreData

@objc(Task)
class Task: NSManagedObject {
    @NSManaged var id: UUID
    @NSManaged var title: String
    @NSManaged var isCompleted: Bool
    @NSManaged var createdAt: Date
}

class PersistenceController {
    static let shared = PersistenceController()

    let container: NSPersistentContainer

    init() {
        container = NSPersistentContainer(name: "Model")
        container.loadPersistentStores { _, error in
            if let error = error {
                fatalError("Core Data failed: \(error)")
            }
        }
    }

    func save() {
        let context = container.viewContext
        if context.hasChanges {
            try? context.save()
        }
    }
}

// 使用
let context = PersistenceController.shared.container.viewContext
let task = Task(context: context)
task.id = UUID()
task.title = "New Task"
task.isCompleted = false
task.createdAt = Date()
PersistenceController.shared.save()
```

## 测试

### XCTest 单元测试
```swift
import XCTest
@testable import MyApp

class CalculatorTests: XCTestCase {
    var calculator: Calculator!

    override func setUp() {
        super.setUp()
        calculator = Calculator()
    }

    override func tearDown() {
        calculator = nil
        super.tearDown()
    }

    func testAddition() {
        let result = calculator.add(2, 3)
        XCTAssertEqual(result, 5)
    }

    func testAsyncOperation() async throws {
        let result = try await calculator.fetchResult()
        XCTAssertGreaterThan(result, 0)
    }
}
```

### UI 测试
```swift
class UITests: XCTestCase {
    func testLoginFlow() {
        let app = XCUIApplication()
        app.launch()

        let emailField = app.textFields["Email"]
        emailField.tap()
        emailField.typeText("test@example.com")

        let passwordField = app.secureTextFields["Password"]
        passwordField.tap()
        passwordField.typeText("password123")

        app.buttons["Login"].tap()

        XCTAssertTrue(app.staticTexts["Welcome"].exists)
    }
}
```

## 框架对比

| 特性 | SwiftUI | UIKit |
|------|---------|-------|
| 声明式 | ✅ | ❌ |
| 学习曲线 | 平缓 | 陡峭 |
| 性能 | 优秀 | 优秀 |
| 兼容性 | iOS 13+ | iOS 2+ |
| 自定义能力 | 中等 | 强大 |
| 预览功能 | ✅ | ❌ |

## 工具清单

| 工具 | 用途 |
|------|------|
| Xcode | 官方 IDE |
| Swift Package Manager | 依赖管理 |
| CocoaPods | 依赖管理 |
| Carthage | 依赖管理 |
| Instruments | 性能分析 |
| SwiftLint | 代码规范 |
| Fastlane | 自动化部署 |

---
