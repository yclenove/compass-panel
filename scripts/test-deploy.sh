#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  mdserver-web 部署测试${NC}"
echo -e "${GREEN}========================================${NC}"

WSL_DISTRO="${1:-Debian}"
PANEL_PORT="7200"

# 步骤 1：检查服务状态
echo -e "\n${YELLOW}[1/4] 检查服务状态...${NC}"
wsl -d $WSL_DISTRO -- bash -c "ps aux | grep gunicorn | grep -v grep" || {
    echo -e "${RED}服务未运行${NC}"
    exit 1
}

# 步骤 2：检查端口
echo -e "\n${YELLOW}[2/4] 检查端口...${NC}"
curl -s -o /dev/null -w "%{http_code}" http://localhost:$PANEL_PORT || {
    echo -e "${RED}端口 $PANEL_PORT 不可达${NC}"
    exit 1
}

# 步骤 3：运行冒烟测试
echo -e "\n${YELLOW}[3/4] 运行冒烟测试...${NC}"
python scripts/smoke-test.py http://localhost:$PANEL_PORT

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  所有检查通过！${NC}"
echo -e "${GREEN}========================================${NC}"
