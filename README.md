# 智能论文创新点生成器 (Idea Creator)

## 项目概述

**智能论文创新点生成器**是一个基于人工智能的研究工具，旨在帮助研究人员快速发现和生成新的研究方向。该系统通过以下核心功能实现研究创新：

### 🎯 核心功能

**📚 智能论文收集**
- 根据用户指定的研究主题，自动从 ArXiv 学术数据库中搜索和下载相关论文
- 支持多种搜索策略和筛选条件，确保收集到高质量的研究文献

**🔍 深度创新点分析**
- 利用先进的自然语言处理技术，自动解析每篇论文的结构和内容
- 精准提取论文中的技术创新点、方法突破和理论贡献
- 对每个创新点进行分类、评分和影响力评估

**🚀 智能创新点生成**
- 基于提取的创新点数据，运用组合优化和AI推理算法
- 通过跨领域知识融合，生成具有可行性的新研究方向
- 为每个生成的想法提供实施路径和研究建议

### 💡 应用价值

- **加速研究进程**：快速了解领域前沿，避免重复研究
- **启发创新思维**：发现跨领域的研究机会和组合创新
- **提升研究效率**：自动化文献调研和创新点分析过程
- **支持决策制定**：为研究方向选择提供数据支持

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置API密钥
编辑 `.env` 文件，添加你的AI API密钥：
```bash
# AI API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 其他配置
DEBUG=True
LOG_LEVEL=INFO
```

### 3. 初始化项目
```bash
python main.py setup
```

### 4. 启动应用

#### 🌟 一键式Web界面（推荐）
```bash
# 启动一键式Web界面
python run_ui.py
```
然后在浏览器中访问 `http://localhost:8501`，输入研究主题即可一键生成创新点！

#### 其他启动方式
```bash
# 方式1: 使用启动脚本
python start.py

# 方式2: 直接启动Web界面
python main.py web

# 方式3: 运行完整示例
python example.py
```

## 📋 功能模块

### 1. ArXiv论文爬取模块
- **功能**: 根据主题关键词搜索并下载ArXiv论文
- **技术栈**: Python + arxiv API / requests + beautifulsoup
- **输出**: 论文PDF文件、元数据（标题、作者、摘要、关键词等）

### 2. 论文内容解析模块
- **功能**: 从PDF中提取文本内容，识别论文结构
- **技术栈**: PyPDF2 / pdfplumber + 文本预处理
- **输出**: 结构化文本内容（摘要、方法、实验、结论等）

### 3. 创新点提取模块
- **功能**: 使用AI模型分析论文，识别和提取创新点
- **技术栈**: DeepSeek API + 提示工程
- **输出**: 每篇论文的创新点列表

### 4. 创新点组合生成模块
- **功能**: 基于现有创新点进行排列组合，生成新的创新想法
- **技术栈**: 组合算法 + AI生成
- **输出**: 新的研究方向和创新点

### 5. 结果展示模块
- **功能**: 可视化展示分析结果和生成的创新点
- **技术栈**: Streamlit / Gradio + 图表库
- **输出**: Web界面展示

## 🛠️ 使用方法

### 命令行使用

#### 搜索论文
```bash
# 搜索论文
python main.py search -q "machine learning" -m 20

# 搜索并下载论文
python main.py search -q "deep learning" -c cs.AI -d

# 搜索最近论文
python main.py search -q "transformer" --recent 30
```

#### 解析论文
```bash
# 解析PDF论文
python main.py parse

# 指定输入输出目录
python main.py parse -i data/papers -o data/extracted
```

#### 提取创新点
```bash
# 提取创新点
python main.py extract --provider deepseek

# 指定AI模型
python main.py extract
```

#### 生成新想法
```bash
# 生成新想法
python main.py generate -t "深度学习在自然语言处理中的应用" --provider deepseek

# 指定输入输出目录
python main.py generate -i data/innovations -o data/results -t "AI应用"
```

#### 启动Web界面
```bash
# 启动Web界面
python main.py web

# 指定端口和主机
python main.py web -p 8080 -h 0.0.0.0
```

### 🌟 一键式Web界面使用

1. 运行 `python run_ui.py` 启动Web界面
2. 在浏览器中访问 `http://localhost:8501`
3. 在"🚀 一键生成"页面输入研究主题（如：machine learning, transformer）
4. 点击"🚀 开始生成"按钮
5. 系统将自动完成以下流程：
   - 🔍 搜索相关论文
   - 📥 下载论文PDF
   - 📖 解析论文内容
   - 💡 提取创新点
   - 🚀 生成新想法
6. 查看美观的创新点展示和分析结果
7. 在"📊 结果分析"页面查看历史记录和可视化图表

### 传统Web界面使用

1. 启动Web界面后，在浏览器中访问 `http://localhost:8501`
2. 使用侧边栏导航不同功能模块
3. 按照提示输入参数并执行操作
4. 查看结果和可视化图表

## 📁 项目结构
```
idea_creater/
├── src/
│   ├── crawler/          # ArXiv爬取模块
│   │   └── arxiv_crawler.py
│   ├── parser/           # 论文解析模块
│   │   └── pdf_parser.py
│   ├── extractor/        # 创新点提取模块
│   │   └── innovation_extractor.py
│   ├── generator/        # 创新点组合模块
│   │   └── idea_generator.py
│   ├── ui/              # 用户界面
│   │   └── streamlit_app.py
│   └── utils/           # 工具函数
│       └── logger.py
├── config/              # 配置文件
│   └── settings.py
├── data/                # 数据存储
│   ├── papers/          # PDF论文文件
│   ├── extracted/       # 解析结果
│   ├── innovations/     # 创新点数据
│   └── results/         # 生成结果
├── tests/               # 测试文件
│   └── test_crawler.py
├── logs/                # 日志文件
├── main.py              # 主程序入口
├── start.py             # 启动脚本
├── example.py           # 使用示例
├── requirements.txt     # 依赖管理
├── .env                 # 环境配置
├── .gitignore          # Git忽略文件
└── README.md           # 项目说明
```

## 🔧 配置说明

### 环境变量
- `DEEPSEEK_API_KEY`: DeepSeek API密钥
- `DEBUG`: 调试模式
- `LOG_LEVEL`: 日志级别

### 设置选项
- `ARXIV_MAX_RESULTS`: ArXiv最大搜索结果数
- `CRAWL_DELAY`: 爬取延迟时间
- `MAX_PDF_SIZE_MB`: PDF文件最大大小
- `DEEPSEEK_MODEL`: DeepSeek模型名称

## 📊 输出格式

### 论文元数据
```json
{
  "arxiv_id": "1234.5678",
  "title": "论文标题",
  "authors": ["作者1", "作者2"],
  "abstract": "论文摘要",
  "categories": ["cs.AI", "cs.LG"],
  "published_date": "2023-01-01",
  "pdf_url": "http://arxiv.org/pdf/1234.5678.pdf"
}
```

### 创新点数据
```json
{
  "title": "创新点标题",
  "description": "创新点描述",
  "category": "创新类别",
  "impact": "影响和意义",
  "methodology": "实现方法",
  "novelty_score": 0.85,
  "confidence": 0.9
}
```

### 生成想法
```json
{
  "title": "新想法标题",
  "description": "想法描述",
  "source_innovations": ["来源创新点1", "来源创新点2"],
  "combination_type": "组合类型",
  "feasibility_score": 0.8,
  "novelty_score": 0.9,
  "impact_potential": 0.85,
  "implementation_path": "实施路径",
  "research_directions": ["研究方向1", "研究方向2"]
}
```

## 🧪 测试

本项目为每个核心模块都编写了详细的单元测试，测试文件位于 `tests/` 目录。

### 运行所有测试
```bash
pytest tests/
```
或
```bash
python main.py test
```

### 各模块测试文件说明
| 模块名称         | 测试文件                      | 说明                       |
|----------------|------------------------------|--------------------------|
| ArXiv爬虫      | tests/test_crawler.py         | 论文爬取、下载、元数据等   |
| PDF解析        | tests/test_pdf_parser.py       | PDF文本提取、结构识别等    |
| 创新点提取      | tests/test_innovation_extractor.py | AI创新点提取、解析等       |
| 创新点组合生成  | tests/test_idea_generator.py   | 创新点组合、AI生成新想法   |

每个测试文件均覆盖了模块的主要功能、边界情况和异常处理。

### 示例：运行某个模块的测试
```bash
pytest tests/test_pdf_parser.py
```

