---
name: state-management
description: 前端状态管理技术。Redux、Zustand、Jotai、Recoil、Context API、状态选择决策。当用户提到状态管理、Redux、Zustand、Jotai、Recoil、全局状态、状态同步时使用。
---

# 🎨 🗂️ 状态管理 · State Management

## 状态管理对比

| 框架 | 模式 | 学习曲线 | 性能 | 适用场景 |
|------|------|----------|------|----------|
| Redux | Flux | 陡峭 | 中 | 大型应用、复杂状态 |
| Zustand | Flux-like | 平缓 | 高 | 中小型应用、快速开发 |
| Jotai | Atomic | 平缓 | 高 | 细粒度更新、原子化状态 |
| Recoil | Atomic | 中等 | 高 | React生态、派生状态 |
| Context | Provider | 简单 | 低 | 简单共享、主题配置 |
| MobX | Reactive | 中等 | 高 | OOP风格、自动追踪 |

## 选择决策树

```
需要状态管理？
  │
  ├─ 简单主题/配置 → Context API
  │
  ├─ 中小型应用
  │   ├─ 喜欢简洁 → Zustand
  │   └─ 需要原子化 → Jotai
  │
  └─ 大型应用
      ├─ 团队熟悉Redux → Redux Toolkit
      ├─ 需要时间旅行 → Redux DevTools
      ├─ 复杂派生状态 → Recoil
      └─ OOP风格 → MobX
```

## Redux Toolkit (推荐)

### 基础配置

```typescript
// store.ts
import { configureStore } from '@reduxjs/toolkit'
import counterReducer from './features/counter/counterSlice'
import userReducer from './features/user/userSlice'

export const store = configureStore({
  reducer: {
    counter: counterReducer,
    user: userReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['user/setTimestamp'],
      },
    }),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
```

### Slice 定义

```typescript
// counterSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface CounterState {
  value: number
  status: 'idle' | 'loading' | 'failed'
}

const initialState: CounterState = {
  value: 0,
  status: 'idle',
}

export const counterSlice = createSlice({
  name: 'counter',
  initialState,
  reducers: {
    increment: (state) => {
      state.value += 1
    },
    decrement: (state) => {
      state.value -= 1
    },
    incrementByAmount: (state, action: PayloadAction<number>) => {
      state.value += action.payload
    },
  },
})

export const { increment, decrement, incrementByAmount } = counterSlice.actions
export default counterSlice.reducer
```

### 异步 Thunk

```typescript
// userSlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'

interface User {
  id: string
  name: string
  email: string
}

export const fetchUser = createAsyncThunk(
  'user/fetchUser',
  async (userId: string) => {
    const response = await fetch(`/api/users/${userId}`)
    return (await response.json()) as User
  }
)

const userSlice = createSlice({
  name: 'user',
  initialState: {
    data: null as User | null,
    loading: false,
    error: null as string | null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchUser.pending, (state) => {
        state.loading = true
      })
      .addCase(fetchUser.fulfilled, (state, action) => {
        state.loading = false
        state.data = action.payload
      })
      .addCase(fetchUser.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed'
      })
  },
})

export default userSlice.reducer
```

### Hooks 使用

```typescript
// hooks.ts
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux'
import type { RootState, AppDispatch } from './store'

export const useAppDispatch = () => useDispatch<AppDispatch>()
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector

// Component
import { useAppDispatch, useAppSelector } from './hooks'
import { increment, fetchUser } from './features/counter/counterSlice'

function Counter() {
  const count = useAppSelector((state) => state.counter.value)
  const dispatch = useAppDispatch()

  return (
    <div>
      <span>{count}</span>
      <button onClick={() => dispatch(increment())}>+</button>
    </div>
  )
}
```

## Zustand (轻量推荐)

### 基础 Store

```typescript
// store.ts
import { create } from 'zustand'

interface BearState {
  bears: number
  increase: () => void
  decrease: () => void
  reset: () => void
}

export const useBearStore = create<BearState>((set) => ({
  bears: 0,
  increase: () => set((state) => ({ bears: state.bears + 1 })),
  decrease: () => set((state) => ({ bears: state.bears - 1 })),
  reset: () => set({ bears: 0 }),
}))

// Component
function BearCounter() {
  const bears = useBearStore((state) => state.bears)
  return <h1>{bears} bears</h1>
}

function Controls() {
  const increase = useBearStore((state) => state.increase)
  return <button onClick={increase}>+1</button>
}
```

### 异步 Actions

```typescript
interface UserStore {
  user: User | null
  loading: boolean
  fetchUser: (id: string) => Promise<void>
}

export const useUserStore = create<UserStore>((set) => ({
  user: null,
  loading: false,
  fetchUser: async (id) => {
    set({ loading: true })
    try {
      const res = await fetch(`/api/users/${id}`)
      const user = await res.json()
      set({ user, loading: false })
    } catch (error) {
      set({ loading: false })
    }
  },
}))
```

### 中间件

```typescript
import { create } from 'zustand'
import { persist, devtools } from 'zustand/middleware'

interface AuthState {
  token: string | null
  login: (token: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set) => ({
        token: null,
        login: (token) => set({ token }),
        logout: () => set({ token: null }),
      }),
      {
        name: 'auth-storage',
      }
    )
  )
)
```

### Immer 集成

```typescript
import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'

interface TodoState {
  todos: Array<{ id: string; text: string; done: boolean }>
  addTodo: (text: string) => void
  toggleTodo: (id: string) => void
}

export const useTodoStore = create<TodoState>()(
  immer((set) => ({
    todos: [],
    addTodo: (text) =>
      set((state) => {
        state.todos.push({ id: Date.now().toString(), text, done: false })
      }),
    toggleTodo: (id) =>
      set((state) => {
        const todo = state.todos.find((t) => t.id === id)
        if (todo) todo.done = !todo.done
      }),
  }))
)
```

## Jotai (原子化)

### Atom 定义

```typescript
import { atom } from 'jotai'

// 原始 atom
export const countAtom = atom(0)

// 派生 atom (只读)
export const doubleCountAtom = atom((get) => get(countAtom) * 2)

// 派生 atom (读写)
export const incrementAtom = atom(
  (get) => get(countAtom),
  (get, set) => set(countAtom, get(countAtom) + 1)
)

// 异步 atom
export const userAtom = atom(async (get) => {
  const userId = get(userIdAtom)
  const response = await fetch(`/api/users/${userId}`)
  return response.json()
})
```

### 使用 Atoms

```typescript
import { useAtom, useAtomValue, useSetAtom } from 'jotai'

function Counter() {
  const [count, setCount] = useAtom(countAtom)
  const doubleCount = useAtomValue(doubleCountAtom)
  const increment = useSetAtom(incrementAtom)

  return (
    <div>
      <p>Count: {count}</p>
      <p>Double: {doubleCount}</p>
      <button onClick={increment}>+1</button>
    </div>
  )
}
```

### 原子家族

```typescript
import { atomFamily } from 'jotai/utils'

// 为每个 ID 创建独立 atom
export const todoAtomFamily = atomFamily((id: string) =>
  atom({
    id,
    text: '',
    done: false,
  })
)

function TodoItem({ id }: { id: string }) {
  const [todo, setTodo] = useAtom(todoAtomFamily(id))

  return (
    <div>
      <input
        value={todo.text}
        onChange={(e) => setTodo({ ...todo, text: e.target.value })}
      />
      <input
        type="checkbox"
        checked={todo.done}
        onChange={(e) => setTodo({ ...todo, done: e.target.checked })}
      />
    </div>
  )
}
```

### 持久化

```typescript
import { atomWithStorage } from 'jotai/utils'

export const themeAtom = atomWithStorage<'light' | 'dark'>('theme', 'light')

// 自定义存储
export const customAtom = atomWithStorage(
  'custom-key',
  { value: 0 },
  {
    getItem: (key) => {
      const value = localStorage.getItem(key)
      return value ? JSON.parse(value) : { value: 0 }
    },
    setItem: (key, value) => {
      localStorage.setItem(key, JSON.stringify(value))
    },
    removeItem: (key) => {
      localStorage.removeItem(key)
    },
  }
)
```

## Recoil

### Atom 和 Selector

```typescript
import { atom, selector } from 'recoil'

// Atom
export const textState = atom({
  key: 'textState',
  default: '',
})

// Selector (派生状态)
export const charCountState = selector({
  key: 'charCountState',
  get: ({ get }) => {
    const text = get(textState)
    return text.length
  },
})

// 异步 Selector
export const userState = selector({
  key: 'userState',
  get: async ({ get }) => {
    const userId = get(userIdState)
    const response = await fetch(`/api/users/${userId}`)
    return response.json()
  },
})
```

### 使用 Recoil

```typescript
import { useRecoilState, useRecoilValue, useSetRecoilState } from 'recoil'

function TextInput() {
  const [text, setText] = useRecoilState(textState)
  const charCount = useRecoilValue(charCountState)

  return (
    <div>
      <input value={text} onChange={(e) => setText(e.target.value)} />
      <p>Character Count: {charCount}</p>
    </div>
  )
}
```

### Atom Family

```typescript
import { atomFamily } from 'recoil'

export const todoItemState = atomFamily({
  key: 'todoItem',
  default: (id: string) => ({
    id,
    text: '',
    done: false,
  }),
})

function TodoItem({ id }: { id: string }) {
  const [todo, setTodo] = useRecoilState(todoItemState(id))

  return (
    <input
      value={todo.text}
      onChange={(e) => setTodo({ ...todo, text: e.target.value })}
    />
  )
}
```

## Context API

### 基础 Context

```typescript
import { createContext, useContext, useState, ReactNode } from 'react'

interface ThemeContextType {
  theme: 'light' | 'dark'
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'))
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}
```

### 优化 Context

```typescript
import { createContext, useContext, useMemo, ReactNode } from 'react'

// 分离状态和更新函数
const StateContext = createContext<State | undefined>(undefined)
const DispatchContext = createContext<Dispatch | undefined>(undefined)

export function Provider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState)

  // 防止不必要的重渲染
  const memoizedState = useMemo(() => state, [state])
  const memoizedDispatch = useMemo(() => dispatch, [dispatch])

  return (
    <StateContext.Provider value={memoizedState}>
      <DispatchContext.Provider value={memoizedDispatch}>
        {children}
      </DispatchContext.Provider>
    </StateContext.Provider>
  )
}
```

## 性能优化

### Redux 选择器优化

```typescript
import { createSelector } from '@reduxjs/toolkit'

// 基础选择器
const selectTodos = (state: RootState) => state.todos
const selectFilter = (state: RootState) => state.filter

// Memoized 选择器
export const selectFilteredTodos = createSelector(
  [selectTodos, selectFilter],
  (todos, filter) => {
    switch (filter) {
      case 'completed':
        return todos.filter((t) => t.done)
      case 'active':
        return todos.filter((t) => !t.done)
      default:
        return todos
    }
  }
)
```

### Zustand 选择器

```typescript
// 避免不必要的重渲染
function Component() {
  // ❌ 整个 state 变化都会重渲染
  const state = useStore()

  // ✅ 只在 bears 变化时重渲染
  const bears = useStore((state) => state.bears)

  // ✅ 使用 shallow 比较
  const { bears, increase } = useStore(
    (state) => ({ bears: state.bears, increase: state.increase }),
    shallow
  )
}
```

### Jotai 优化

```typescript
// 使用 selectAtom 避免不必要的重渲染
import { selectAtom } from 'jotai/utils'

const userAtom = atom({ name: 'John', age: 30 })
const nameAtom = selectAtom(userAtom, (user) => user.name)

function Component() {
  // 只在 name 变化时重渲染
  const name = useAtomValue(nameAtom)
}
```

## 最佳实践

### 状态分层

```
全局状态 (Redux/Zustand)
  ├─ 用户认证
  ├─ 主题配置
  └─ 全局通知

服务器状态 (React Query/SWR)
  ├─ API 数据
  ├─ 缓存管理
  └─ 乐观更新

组件状态 (useState/useReducer)
  ├─ 表单输入
  ├─ UI 交互
  └─ 临时数据
```

### 命名规范

```typescript
// Redux
const userSlice = createSlice({ name: 'user', ... })
export const { setUser, clearUser } = userSlice.actions

// Zustand
export const useUserStore = create<UserStore>(...)

// Jotai
export const userAtom = atom<User | null>(null)
export const userNameAtom = atom((get) => get(userAtom)?.name)

// Recoil
export const userState = atom({ key: 'userState', ... })
export const userNameState = selector({ key: 'userNameState', ... })
```

### 错误处理

```typescript
// Redux Toolkit
const userSlice = createSlice({
  name: 'user',
  initialState: {
    data: null,
    error: null as string | null,
    loading: false,
  },
  extraReducers: (builder) => {
    builder.addCase(fetchUser.rejected, (state, action) => {
      state.error = action.error.message || 'Unknown error'
      state.loading = false
    })
  },
})

// Zustand
export const useStore = create<Store>((set) => ({
  error: null,
  fetchData: async () => {
    try {
      const data = await api.fetch()
      set({ data, error: null })
    } catch (error) {
      set({ error: error.message })
    }
  },
}))
```

## 工具清单

| 工具 | 用途 |
|------|------|
| Redux DevTools | 时间旅行调试 |
| Zustand DevTools | Zustand 状态调试 |
| Jotai DevTools | Atom 依赖可视化 |
| Recoil DevTools | Recoil 状态调试 |
| React Query DevTools | 服务器状态调试 |
| Immer | 不可变数据更新 |

---
