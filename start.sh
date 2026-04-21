#!/bin/bash

# --- 颜色定义 ---
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}   My Codeforces 一键启动工具         ${NC}"
echo -e "${BLUE}=======================================${NC}"

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# --- 模式选择 ---
echo -e "请选择启动模式:"
echo -e "1) ${GREEN}Docker 模式${NC} (推荐，无需配置环境)"
echo -e "2) ${YELLOW}本地原生模式${NC} (需已安装 Python 和 Node.js)"
read -p "请输入数字 [1-2]: " choice

if [ "$choice" == "1" ]; then
    if ! command_exists docker; then
        echo -e "${RED}错误: 未检测到 Docker，请先安装 Docker。${NC}"
        exit 1
    fi
    echo -e "${GREEN}正在通过 Docker Compose 启动...${NC}"
    docker compose up --build
else
    # --- 本地原生模式 ---
    echo -e "${YELLOW}正在启动本地服务...${NC}"

    # 1. 启动后端
    echo -e "${BLUE}[1/2] 正在启动后端 (FastAPI)...${NC}"
    cd backend
    if [ ! -d ".venv" ]; then
        echo "正在创建虚拟环境..."
        python3 -m venv .venv
    fi
    source .venv/bin/activate
    pip install -r requirements.txt --quiet
    python3 main.py &
    BACKEND_PID=$!
    cd ..

    # 2. 启动前端
    echo -e "${BLUE}[2/2] 正在启动前端 (Vite)...${NC}"
    cd frontend
    npm install --silent
    npm run dev &
    FRONTEND_PID=$!
    cd ..

    echo -e "${GREEN}服务已全部启动！${NC}"
    echo -e "后端 API: ${BLUE}http://localhost:8000${NC}"
    echo -e "前端 UI: ${BLUE}http://localhost:5173${NC}"
    echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"

    # 监听退出信号
    trap "kill $BACKEND_PID $FRONTEND_PID; echo -e '\n${BLUE}服务已停止。${NC}'; exit" INT
    wait
fi
