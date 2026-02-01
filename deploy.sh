#!/bin/bash

# AI Pulse 部署脚本
# 适用于阿里云 ECS (Ubuntu/CentOS)

set -e

echo "=========================================="
echo "   AI Pulse 部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}建议使用 root 用户运行此脚本${NC}"
fi

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}Docker 未安装，正在安装...${NC}"
        curl -fsSL https://get.docker.com | sh
        systemctl start docker
        systemctl enable docker
        echo -e "${GREEN}Docker 安装完成${NC}"
    else
        echo -e "${GREEN}Docker 已安装${NC}"
    fi
}

# 检查 Docker Compose 是否安装
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${YELLOW}Docker Compose 未安装，正在安装...${NC}"
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        echo -e "${GREEN}Docker Compose 安装完成${NC}"
    else
        echo -e "${GREEN}Docker Compose 已安装${NC}"
    fi
}

# 配置环境变量
setup_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}创建 .env 配置文件...${NC}"
        cp backend/.env.example .env
        echo ""
        echo -e "${RED}请编辑 .env 文件，填入您的 DASHSCOPE_API_KEY${NC}"
        echo "运行: nano .env 或 vim .env"
        echo ""
        read -p "按 Enter 继续（确保已配置 API Key）..."
    fi
}

# 创建数据目录
setup_dirs() {
    mkdir -p data
    echo -e "${GREEN}数据目录已创建${NC}"
}

# 构建并启动服务
start_services() {
    echo -e "${YELLOW}构建 Docker 镜像...${NC}"
    docker-compose build

    echo -e "${YELLOW}启动服务...${NC}"
    docker-compose up -d

    echo -e "${GREEN}服务已启动！${NC}"
}

# 显示状态
show_status() {
    echo ""
    echo "=========================================="
    echo "   部署完成！"
    echo "=========================================="
    echo ""
    echo "服务状态:"
    docker-compose ps
    echo ""
    echo "访问地址:"
    echo "  - 前端: http://<服务器IP>"
    echo "  - 后端 API: http://<服务器IP>:8000"
    echo ""
    echo "常用命令:"
    echo "  - 查看日志: docker-compose logs -f"
    echo "  - 停止服务: docker-compose down"
    echo "  - 重启服务: docker-compose restart"
    echo "  - 手动触发爬取: curl -X POST http://localhost:8000/api/crawl"
    echo ""
}

# 主流程
main() {
    check_docker
    check_docker_compose
    setup_env
    setup_dirs
    start_services
    show_status
}

main
