#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  mdserver-web 部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"

WSL_DISTRO="${1:-Debian}"
DEPLOY_DIR="/www/server/mdserver-web"

# 步骤 1：构建前端
echo -e "\n${YELLOW}[1/5] 构建前端...${NC}"
if [ -d "web/frontend" ]; then
    cd web/frontend
    npm install
    npm run build
    cd ../..
fi

# 步骤 2：运行测试
echo -e "\n${YELLOW}[2/5] 运行测试...${NC}"
python -m pytest tests/ -v --tb=short || echo "测试未通过，继续部署..."

# 步骤 3：复制代码到 WSL
echo -e "\n${YELLOW}[3/5] 复制代码到 WSL...${NC}"
wsl -d $WSL_DISTRO -- bash -c "sudo mkdir -p $DEPLOY_DIR"
wsl -d $WSL_DISTRO -- bash -c "sudo cp -r . $DEPLOY_DIR/"

# 步骤 4：修复行尾符
echo -e "\n${YELLOW}[4/5] 修复行尾符...${NC}"
wsl -d $WSL_DISTRO -- bash -c "sudo find $DEPLOY_DIR -name '*.sh' -exec sed -i 's/\r$//' {} \;"
wsl -d $WSL_DISTRO -- bash -c "sudo find $DEPLOY_DIR -name '*.py' -exec sed -i 's/\r$//' {} \;"

# 步骤 5：重启服务
echo -e "\n${YELLOW}[5/5] 重启服务...${NC}"
wsl -d $WSL_DISTRO -- bash -c "cd $DEPLOY_DIR && sudo bash cli.sh restart"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
