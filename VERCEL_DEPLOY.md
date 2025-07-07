# Vercel 部署指南

## 📋 部署前准备

### 1. 安装 Vercel CLI
```bash
npm install -g vercel
```

### 2. 登录 Vercel
```bash
vercel login
```

### 3. 准备环境变量
在 Vercel 控制台设置以下环境变量：

```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
VERCEL_ENV=production
DEBUG=false
LOG_LEVEL=WARNING
MAX_CONCURRENT_REQUESTS=2
REQUEST_TIMEOUT=300
ARXIV_MAX_RESULTS=20
DEEPSEEK_MAX_TOKENS=3000
MAX_PDF_SIZE_MB=10
CRAWL_DELAY=0.5
MAX_RETRIES=2
TIMEOUT=15
```

## 🚀 部署步骤

### 方式一：使用部署脚本（推荐）
```bash
chmod +x deploy.sh
./deploy.sh
```

### 方式二：手动部署
```bash
# 1. 部署到 Vercel
vercel --prod

# 2. 在 Vercel 控制台设置环境变量
```

## 📁 部署架构

```
vercel-deployment/
├── api/
│   └── app.py           # FastAPI 应用入口
├── src/                 # 源代码
├── config/              # 配置文件
├── requirements-vercel.txt  # 优化的依赖
└── vercel.json          # Vercel 配置
```

## 🔧 关键优化

### 1. 依赖优化
- 移除了重量级包（pymupdf、nltk、spacy等）
- 只保留核心功能依赖
- 减少部署包大小

### 2. 性能优化
- 使用临时文件存储
- 限制并发请求数
- 减少超时时间
- 优化内存使用

### 3. 环境适配
- 使用内存数据库
- 临时目录存储
- 无状态设计
- 错误处理优化

## 🌐 访问方式

部署成功后，你可以通过以下方式访问：

- **主页**: `https://your-app.vercel.app/`
- **搜索API**: `https://your-app.vercel.app/api/search`
- **生成API**: `https://your-app.vercel.app/api/generate`
- **健康检查**: `https://your-app.vercel.app/api/health`

## 📱 使用说明

### 1. 网页界面
直接访问主页，输入研究主题即可一键生成创新点

### 2. API 调用
```bash
# 生成创新点
curl -X POST "https://your-app.vercel.app/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "max_papers": 10}'
```

## ⚠️ 注意事项

### 1. 性能限制
- 每次最多处理5篇论文（避免超时）
- 请求超时时间：5分钟
- 并发请求限制：2个

### 2. 存储限制
- 使用临时存储，数据不持久化
- 每次请求都是独立的
- 会话数据存储在内存中

### 3. 成本考虑
- 每个请求都会调用 DeepSeek API
- 建议设置合理的使用频率限制
- 监控 API 使用量

## 🔍 故障排除

### 1. 部署失败
- 检查依赖是否正确
- 确认环境变量已设置
- 查看 Vercel 部署日志

### 2. 运行错误
- 检查 DeepSeek API 密钥
- 确认网络连接
- 查看函数日志

### 3. 性能问题
- 减少 max_papers 参数
- 检查 PDF 文件大小
- 优化搜索关键词

## 🚀 进阶优化

### 1. 数据库集成
可以集成 Vercel 支持的数据库：
- Vercel Postgres
- PlanetScale
- MongoDB Atlas

### 2. 缓存优化
- Redis 缓存
- Vercel Edge Cache
- CDN 加速

### 3. 监控告警
- Vercel Analytics
- Sentry 错误监控
- 自定义监控指标

## 📞 技术支持

如果遇到问题，请：
1. 查看 Vercel 部署日志
2. 检查环境变量配置
3. 确认 API 密钥有效
4. 联系技术支持 