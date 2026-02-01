# AI Pulse - AI 脉动

一站式 AI 行业前沿深度情报扫描与自动化摘要系统，将碎片化原始信息转化为结构化深度情报。

## 功能特性

- **多源信息采集**：自动爬取 HuggingFace Papers、OpenAI Blog、Anthropic News、Google AI Blog、TechCrunch、机器之心、量子位等 AI 领域权威信息源
- **智能分类**：基于阿里云百炼大模型（Qwen）自动对文章进行三大类分类
  - 技术创新：模型架构、训练方法、算法改进
  - 模型评测：评估标准、Benchmark、安全性测试
  - 产品动态：产品发布、功能更新、商业动态
- **AI 摘要生成**：自动生成中文摘要，突出核心观点和技术创新点
- **每日趋势总结**：AI 自动分析当日收集的文章，生成趋势洞察和要点
- **收藏功能**：支持收藏感兴趣的文章
- **定时采集**：每日自动执行数据采集任务

## 技术架构

```
┌─────────────────────────────────────────────────────┐
│                    前端 (React)                      │
│  React 18 + TypeScript + Vite + TailwindCSS         │
└─────────────────────┬───────────────────────────────┘
                      │ Nginx 反向代理
┌─────────────────────▼───────────────────────────────┐
│                   后端 (FastAPI)                     │
│  Python 3.11 + SQLAlchemy + APScheduler             │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌──────────┐
   │ SQLite  │  │ 爬虫模块 │  │ 百炼 API │
   │ 数据库  │  │ Crawler  │  │ (Qwen)   │
   └─────────┘  └──────────┘  └──────────┘
```

## 快速开始

### 前置条件

- Docker & Docker Compose
- 阿里云百炼 API Key（用于 AI 功能）

### 部署步骤

1. **克隆代码**
```bash
git clone https://github.com/Aierwins2/AI-Pulse.git
cd AI-Pulse
```

2. **配置环境变量**
```bash
cp backend/.env.example .env
# 编辑 .env，填入你的 Dashscope API Key
nano .env
```

3. **启动服务**
```bash
docker-compose up -d --build
```

4. **访问网站**
- 前端：http://localhost
- API：http://localhost:8000

### 手动触发数据采集

```bash
curl -X POST http://localhost:8000/api/crawl
```

## 项目结构

```
AI-Pulse/
├── src/                    # 前端源码
│   ├── api/               # API 客户端
│   ├── components/        # React 组件
│   ├── pages/             # 页面组件
│   └── types/             # TypeScript 类型
├── backend/               # 后端源码
│   ├── crawler/           # 爬虫模块
│   │   ├── base.py       # 基础爬虫类
│   │   ├── huggingface.py # HuggingFace 爬虫
│   │   ├── media.py      # 媒体网站爬虫
│   │   └── manager.py    # 爬虫管理器
│   ├── ai_processor.py    # AI 处理（分类、摘要）
│   ├── database.py        # 数据库操作
│   ├── scheduler.py       # 定时任务
│   ├── main.py           # FastAPI 入口
│   └── config.py         # 配置管理
├── docker-compose.yml     # Docker 编排
├── Dockerfile.frontend    # 前端 Docker 镜像
├── Dockerfile.backend     # 后端 Docker 镜像
└── nginx.conf            # Nginx 配置
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/articles` | GET | 获取文章列表 |
| `/api/articles/{id}` | GET | 获取单篇文章 |
| `/api/articles/{id}/favorite` | POST | 切换收藏状态 |
| `/api/trend` | GET | 获取每日趋势总结 |
| `/api/stats` | GET | 获取统计信息 |
| `/api/crawl` | POST | 手动触发爬取 |
| `/api/categories` | GET | 获取分类列表 |

## 配置说明

环境变量（`.env` 文件）：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DASHSCOPE_API_KEY` | 阿里云百炼 API Key | 必填 |
| `DATABASE_URL` | 数据库连接 | sqlite+aiosqlite:///./data/aipulse.db |
| `DATA_RETENTION_DAYS` | 数据保留天数 | 7 |
| `CRAWLER_SCHEDULE_HOUR` | 定时爬取小时 | 9 |
| `CRAWLER_SCHEDULE_MINUTE` | 定时爬取分钟 | 0 |
| `AI_MODEL` | AI 模型 | qwen-plus |

## 信息源

| 来源 | 类型 | 说明 |
|------|------|------|
| HuggingFace Papers | 论文 | 每日 AI 研究论文 |
| OpenAI Blog | 博客 | OpenAI 官方博客 |
| Anthropic News | 新闻 | Anthropic 官方新闻 |
| Google AI Blog | 博客 | Google AI 博客 |
| TechCrunch AI | 新闻 | TechCrunch AI 频道 |
| 机器之心 | 媒体 | 中文 AI 媒体 |
| 量子位 | 媒体 | 中文 AI 媒体 |

## 开发

### 本地开发

```bash
# 前端
npm install
npm run dev

# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 构建镜像

```bash
docker-compose build
```

## 许可证

MIT License
