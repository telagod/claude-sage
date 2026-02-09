---
name: build-tools
description: 前端构建工具。Vite、Webpack、Turbopack、esbuild、构建优化、插件生态。当用户提到构建工具、Vite、Webpack、Turbopack、打包优化、构建配置时使用。
---

# 🎨 🔧 构建工具 · Build Tools

## 构建工具对比

| 工具 | 开发速度 | 生产构建 | 生态 | 学习曲线 | 适用场景 |
|------|----------|----------|------|----------|----------|
| Vite | 极快 | 快 | 成熟 | 低 | 现代项目、快速开发 |
| Webpack | 慢 | 中 | 最丰富 | 陡峭 | 复杂配置、企业项目 |
| Turbopack | 极快 | 快 | 新兴 | 低 | Next.js 项目 |
| esbuild | 极快 | 极快 | 基础 | 低 | 简单项目、库打包 |
| Rollup | 中 | 快 | 成熟 | 中 | 库打包、Tree Shaking |
| Parcel | 快 | 快 | 中等 | 极低 | 零配置项目 |

## 选择决策树

```
选择构建工具？
  │
  ├─ 新项目
  │   ├─ React/Vue → Vite
  │   ├─ Next.js → Turbopack (内置)
  │   └─ 零配置 → Parcel
  │
  ├─ 库开发
  │   ├─ 需要 Tree Shaking → Rollup
  │   └─ 极致性能 → esbuild
  │
  └─ 老项目
      ├─ 复杂配置 → 保持 Webpack
      └─ 可迁移 → 迁移到 Vite
```

## Vite (推荐)

### 基础配置

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@utils': path.resolve(__dirname, './src/utils'),
    },
  },
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'router': ['react-router-dom'],
        },
      },
    },
  },
})
```

### 环境变量

```typescript
// .env
VITE_API_URL=https://api.example.com
VITE_APP_TITLE=My App

// .env.development
VITE_API_URL=http://localhost:8080

// .env.production
VITE_API_URL=https://prod-api.example.com

// 使用环境变量
const apiUrl = import.meta.env.VITE_API_URL
const isDev = import.meta.env.DEV
const isProd = import.meta.env.PROD
```

### 自定义插件

```typescript
// vite-plugin-custom.ts
import type { Plugin } from 'vite'

export function customPlugin(): Plugin {
  return {
    name: 'vite-plugin-custom',

    // 开发服务器启动时
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        console.log('Request:', req.url)
        next()
      })
    },

    // 转换代码
    transform(code, id) {
      if (id.endsWith('.custom')) {
        return {
          code: transformCustomFile(code),
          map: null,
        }
      }
    },

    // 构建开始
    buildStart() {
      console.log('Build started')
    },

    // 构建结束
    buildEnd() {
      console.log('Build finished')
    },
  }
}

// 使用插件
export default defineConfig({
  plugins: [react(), customPlugin()],
})
```

### 优化配置

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    // 代码分割
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react')) {
              return 'react-vendor'
            }
            if (id.includes('@mui')) {
              return 'mui-vendor'
            }
            return 'vendor'
          }
        },
      },
    },

    // 压缩配置
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },

    // Chunk 大小警告
    chunkSizeWarningLimit: 1000,

    // CSS 代码分割
    cssCodeSplit: true,
  },

  // 依赖预构建
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom'],
    exclude: ['@vite/client'],
  },
})
```

## Webpack

### 基础配置

```javascript
// webpack.config.js
const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const TerserPlugin = require('terser-webpack-plugin')

module.exports = {
  entry: './src/index.tsx',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash].js',
    clean: true,
  },

  resolve: {
    extensions: ['.ts', '.tsx', '.js', '.jsx'],
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },

  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader', 'postcss-loader'],
      },
      {
        test: /\.(png|jpg|gif|svg)$/,
        type: 'asset/resource',
      },
    ],
  },

  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
    new MiniCssExtractPlugin({
      filename: '[name].[contenthash].css',
    }),
  ],

  optimization: {
    minimizer: [new TerserPlugin()],
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10,
        },
      },
    },
  },
}
```

### 开发服务器

```javascript
// webpack.dev.js
const { merge } = require('webpack-merge')
const common = require('./webpack.config.js')

module.exports = merge(common, {
  mode: 'development',
  devtool: 'inline-source-map',

  devServer: {
    static: './dist',
    port: 3000,
    hot: true,
    open: true,
    historyApiFallback: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
})
```

### 生产优化

```javascript
// webpack.prod.js
const { merge } = require('webpack-merge')
const common = require('./webpack.config.js')
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin')
const CompressionPlugin = require('compression-webpack-plugin')
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer')

module.exports = merge(common, {
  mode: 'production',
  devtool: 'source-map',

  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true,
          },
        },
      }),
      new CssMinimizerPlugin(),
    ],

    splitChunks: {
      chunks: 'all',
      maxInitialRequests: 10,
      cacheGroups: {
        react: {
          test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
          name: 'react',
          priority: 20,
        },
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10,
        },
      },
    },

    runtimeChunk: 'single',
  },

  plugins: [
    new CompressionPlugin({
      algorithm: 'gzip',
      test: /\.(js|css|html|svg)$/,
      threshold: 10240,
      minRatio: 0.8,
    }),
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      openAnalyzer: false,
    }),
  ],
})
```

### 自定义 Loader

```javascript
// custom-loader.js
module.exports = function(source) {
  // 转换源代码
  const transformed = source.replace(/console\.log/g, '// console.log')

  // 返回转换后的代码
  return transformed
}

// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.js$/,
        use: [
          {
            loader: path.resolve(__dirname, 'custom-loader.js'),
          },
        ],
      },
    ],
  },
}
```

### 自定义 Plugin

```javascript
// custom-plugin.js
class CustomPlugin {
  apply(compiler) {
    compiler.hooks.emit.tapAsync('CustomPlugin', (compilation, callback) => {
      // 在生成资源前执行
      console.log('Assets:', Object.keys(compilation.assets))

      // 添加自定义文件
      compilation.assets['custom.txt'] = {
        source: () => 'Custom content',
        size: () => 14,
      }

      callback()
    })

    compiler.hooks.done.tap('CustomPlugin', (stats) => {
      // 构建完成后执行
      console.log('Build completed!')
    })
  }
}

module.exports = CustomPlugin

// 使用插件
plugins: [new CustomPlugin()]
```

## Turbopack (Next.js)

### Next.js 配置

```javascript
// next.config.js
module.exports = {
  // 启用 Turbopack (Next.js 13+)
  experimental: {
    turbo: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
      resolveAlias: {
        '@': './src',
      },
    },
  },

  // 其他配置
  reactStrictMode: true,
  swcMinify: true,

  webpack: (config, { isServer }) => {
    // 自定义 Webpack 配置（Turbopack 不支持时回退）
    if (!isServer) {
      config.resolve.fallback = {
        fs: false,
        net: false,
        tls: false,
      }
    }
    return config
  },
}
```

### 使用 Turbopack

```bash
# 开发模式使用 Turbopack
next dev --turbo

# package.json
{
  "scripts": {
    "dev": "next dev --turbo",
    "build": "next build",
    "start": "next start"
  }
}
```

## esbuild

### 基础配置

```javascript
// build.js
const esbuild = require('esbuild')

esbuild.build({
  entryPoints: ['src/index.tsx'],
  bundle: true,
  outfile: 'dist/bundle.js',
  minify: true,
  sourcemap: true,
  target: ['es2020'],
  loader: {
    '.ts': 'ts',
    '.tsx': 'tsx',
    '.png': 'file',
  },
  define: {
    'process.env.NODE_ENV': '"production"',
  },
}).catch(() => process.exit(1))
```

### 开发服务器

```javascript
// serve.js
const esbuild = require('esbuild')

esbuild.serve(
  {
    servedir: 'public',
    port: 3000,
  },
  {
    entryPoints: ['src/index.tsx'],
    bundle: true,
    outfile: 'public/bundle.js',
    loader: { '.ts': 'ts', '.tsx': 'tsx' },
  }
).then(server => {
  console.log(`Server running at http://localhost:${server.port}`)
})
```

### 插件系统

```javascript
// esbuild-plugin-custom.js
const customPlugin = {
  name: 'custom',
  setup(build) {
    // 解析路径
    build.onResolve({ filter: /^custom:/ }, args => ({
      path: args.path,
      namespace: 'custom',
    }))

    // 加载内容
    build.onLoad({ filter: /.*/, namespace: 'custom' }, args => ({
      contents: 'export default "custom content"',
      loader: 'js',
    }))
  },
}

// 使用插件
esbuild.build({
  entryPoints: ['src/index.js'],
  bundle: true,
  plugins: [customPlugin],
  outfile: 'dist/bundle.js',
})
```

## Rollup (库打包)

### 基础配置

```javascript
// rollup.config.js
import resolve from '@rollup/plugin-node-resolve'
import commonjs from '@rollup/plugin-commonjs'
import typescript from '@rollup/plugin-typescript'
import { terser } from 'rollup-plugin-terser'
import peerDepsExternal from 'rollup-plugin-peer-deps-external'

export default {
  input: 'src/index.ts',
  output: [
    {
      file: 'dist/index.js',
      format: 'cjs',
      sourcemap: true,
    },
    {
      file: 'dist/index.esm.js',
      format: 'esm',
      sourcemap: true,
    },
    {
      file: 'dist/index.umd.js',
      format: 'umd',
      name: 'MyLibrary',
      sourcemap: true,
      globals: {
        react: 'React',
        'react-dom': 'ReactDOM',
      },
    },
  ],
  plugins: [
    peerDepsExternal(),
    resolve(),
    commonjs(),
    typescript({ tsconfig: './tsconfig.json' }),
    terser(),
  ],
  external: ['react', 'react-dom'],
}
```

## 性能优化对比

| 优化项 | Vite | Webpack | Turbopack | esbuild |
|--------|------|---------|-----------|---------|
| 冷启动 | < 1s | 10-30s | < 1s | < 1s |
| HMR | < 100ms | 1-3s | < 100ms | N/A |
| 生产构建 | 10-30s | 30-60s | 10-20s | 5-10s |
| Tree Shaking | ✅ | ✅ | ✅ | ✅ |
| 代码分割 | ✅ | ✅ | ✅ | ✅ |

## 迁移指南

### Webpack → Vite

```typescript
// 1. 安装依赖
npm install -D vite @vitejs/plugin-react

// 2. 创建 vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': '/src', // Webpack alias 迁移
    },
  },
})

// 3. 更新 index.html
// 移动到项目根目录，添加：
<script type="module" src="/src/main.tsx"></script>

// 4. 更新环境变量
// REACT_APP_* → VITE_*

// 5. 更新 import
// require() → import
// import.meta.env 替代 process.env
```

## 最佳实践

### 代码分割策略

```typescript
// 路由级别分割
const routes = [
  {
    path: '/dashboard',
    component: lazy(() => import('./pages/Dashboard')),
  },
  {
    path: '/profile',
    component: lazy(() => import('./pages/Profile')),
  },
]

// 第三方库分割
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['@mui/material', '@emotion/react'],
          'chart-vendor': ['recharts', 'd3'],
        },
      },
    },
  },
})
```

### 缓存策略

```typescript
// 文件名哈希
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name].[hash].js',
        chunkFileNames: 'assets/[name].[hash].js',
        assetFileNames: 'assets/[name].[hash].[ext]',
      },
    },
  },
})

// HTTP 缓存头
// nginx.conf
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}
```

### 环境配置

```typescript
// 多环境配置
// vite.config.ts
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())

  return {
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
      __API_URL__: JSON.stringify(env.VITE_API_URL),
    },
    build: {
      sourcemap: mode === 'development',
      minify: mode === 'production',
    },
  }
})
```

## 最佳实践清单

- ✅ 使用 Vite 开发新项目
- ✅ 配置合理的代码分割策略
- ✅ 启用 Tree Shaking 和压缩
- ✅ 使用文件名哈希实现长期缓存
- ✅ 配置 source map 便于调试
- ✅ 使用环境变量管理配置
- ✅ 定期分析 bundle 大小
- ✅ 预构建常用依赖
- ✅ 配置合理的 chunk 大小
- ✅ 在 CI/CD 中缓存依赖

## 工具清单

| 工具 | 用途 |
|------|------|
| Vite | 现代前端构建工具 |
| Webpack | 功能最全的打包工具 |
| Turbopack | Next.js 高性能构建 |
| esbuild | 极速打包工具 |
| Rollup | 库打包工具 |
| webpack-bundle-analyzer | Bundle 分析 |
| vite-plugin-inspect | Vite 插件调试 |
| speed-measure-webpack-plugin | Webpack 性能分析 |

---
