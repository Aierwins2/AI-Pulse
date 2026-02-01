# AI Pulse 阿里云部署指南

## 前置条件

根据您的阿里云资源：
- **轻量应用服务器**: 1 个实例 (用于部署应用)
- **大模型服务平台百炼**: 获取 API Key (用于 AI 功能)
- **域名与网站**: 1 个域名 (可选，用于访问)

---

## 第一步：获取 Dashscope API Key

1. 登录 [阿里云控制台](https://console.aliyun.com)
2. 搜索并进入 **大模型服务平台百炼**
3. 在左侧菜单找到 **API-KEY 管理**
4. 点击 **创建 API Key**
5. 复制生成的 API Key（请妥善保存）

---

## 第二步：连接轻量应用服务器

### 方式一：阿里云控制台
1. 进入轻量应用服务器控制台
2. 点击实例，选择 **远程连接**
3. 使用 Workbench 连接

### 方式二：SSH 连接
```bash
ssh root@<服务器公网IP>
```

---

## 第三步：上传代码到服务器

### 方式一：Git 克隆（推荐）
```bash
# 安装 Git（如果没有）
apt update && apt install -y git

# 克隆代码
cd /opt
git clone <你的仓库地址> ai-pulse
cd ai-pulse
```

### 方式二：SCP 上传
```bash
# 在本地执行
scp -r /path/to/AI-Pulse root@<服务器IP>:/opt/ai-pulse
```

---

## 第四步：配置环境变量

```bash
cd /opt/ai-pulse

# 创建环境配置文件
cp backend/.env.example .env

# 编辑配置文件
nano .env
```

修改以下内容：
```env
# 填入您的 Dashscope API Key（必填）
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxx

# 其他配置保持默认即可
DATABASE_URL=sqlite+aiosqlite:///./data/aipulse.db
DATA_RETENTION_DAYS=7
CRAWLER_SCHEDULE_HOUR=9
CRAWLER_SCHEDULE_MINUTE=0
AI_MODEL=qwen-plus
HOST=0.0.0.0
PORT=8000

# 如果配置了域名，添加您的域名
CORS_ORIGINS=http://localhost,http://your-domain.com
```

---

## 第五步：运行部署脚本

```bash
# 赋予执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh
```

脚本会自动：
- 安装 Docker 和 Docker Compose
- 创建数据目录
- 构建 Docker 镜像
- 启动所有服务

---

## 第六步：配置防火墙

### 阿里云控制台配置
1. 进入轻量应用服务器控制台
2. 点击 **防火墙** 设置
3. 添加规则：
   - **端口 80** (HTTP) - TCP
   - **端口 443** (HTTPS，如需) - TCP
   - **端口 8000** (API，可选) - TCP

### 或使用命令行
```bash
# 如果使用 ufw
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
```

---

## 第七步：配置域名（可选）

如果您有域名，需要配置 DNS 解析：

1. 进入 **云解析 DNS** 控制台
2. 选择您的域名
3. 添加解析记录：
   - **记录类型**: A
   - **主机记录**: @ 或 www
   - **记录值**: 轻量服务器的公网 IP

等待 DNS 生效（通常几分钟到几小时）。

---

## 第八步：配置 HTTPS（推荐）

### 使用 Let's Encrypt 免费证书

```bash
# 安装 certbot
apt install -y certbot

# 停止服务（释放 80 端口）
docker-compose down

# 获取证书
certbot certonly --standalone -d your-domain.com

# 证书路径
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

然后修改 `nginx.conf` 启用 HTTPS。

---

## 验证部署

部署完成后，可以通过以下方式验证：

```bash
# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 测试 API
curl http://localhost:8000/

# 手动触发爬取
curl -X POST http://localhost:8000/api/crawl
```

访问地址：
- **前端**: `http://<服务器IP>` 或 `http://your-domain.com`
- **API**: `http://<服务器IP>:8000` 或 `http://your-domain.com/api`

---

## 常用运维命令

```bash
# 查看所有服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 只看后端日志
docker-compose logs -f backend

# 重启所有服务
docker-compose restart

# 停止所有服务
docker-compose down

# 更新代码后重新部署
git pull
docker-compose build
docker-compose up -d

# 清理 Docker 缓存
docker system prune -f
```

---

## 故障排查

### 问题：服务无法启动
```bash
# 查看详细日志
docker-compose logs

# 检查端口占用
netstat -tlnp | grep -E '80|8000'
```

### 问题：API Key 无效
1. 确认 API Key 已正确配置在 `.env` 文件
2. 确认百炼平台账户余额充足
3. 重启后端服务：`docker-compose restart backend`

### 问题：无法访问网站
1. 检查防火墙规则是否放行 80 端口
2. 检查阿里云安全组配置
3. 确认服务已启动：`docker-compose ps`

### 问题：爬取没有数据
```bash
# 手动触发爬取
curl -X POST http://localhost:8000/api/crawl

# 查看爬取日志
docker-compose logs backend | grep -i crawl
```

---

## 架构说明

```
                    ┌─────────────────────────────────────┐
                    │          阿里云轻量服务器            │
                    │                                     │
 用户访问 ──────────►│  ┌─────────┐      ┌─────────────┐  │
 http://域名        │  │  Nginx  │─────►│   FastAPI   │  │
                    │  │ (前端)  │      │   (后端)    │  │
                    │  │ :80     │      │   :8000     │  │
                    │  └─────────┘      └──────┬──────┘  │
                    │                          │         │
                    │                   ┌──────▼──────┐  │
                    │                   │   SQLite    │  │
                    │                   │  数据库     │  │
                    │                   └─────────────┘  │
                    └─────────────────────────────────────┘
                                       │
                                       │ API 调用
                                       ▼
                    ┌─────────────────────────────────────┐
                    │      阿里云大模型平台百炼            │
                    │         (Qwen-Plus)                 │
                    └─────────────────────────────────────┘
```

---

## 费用说明

- **轻量应用服务器**: 按实例规格计费
- **百炼平台 API**: 按调用量计费（首次注册有免费额度）
- **域名**: 按年计费
- **云解析 DNS**: 免费版足够使用

建议关注百炼平台的 API 使用量，避免超出免费额度。
