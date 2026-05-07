#!/bin/bash
# mdserver-web 快速部署脚本 for WSL Debian
set -e

RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
BLUE='\033[34m'
PLAIN='\033[0m'

echo -e "${GREEN}========================================${PLAIN}"
echo -e "${GREEN}  mdserver-web WSL 快速部署脚本${PLAIN}"
echo -e "${GREEN}========================================${PLAIN}"

# 检查 root 权限
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用 sudo 运行此脚本${PLAIN}"
    exit 1
fi

# 检查是否已安装
if [ -d /www/server/mdserver-web ]; then
    echo -e "${YELLOW}检测到已有安装，是否覆盖？(y/n)${PLAIN}"
    read -r answer
    if [ "$answer" != "y" ]; then
        echo "取消安装"
        exit 0
    fi
    rm -rf /www/server/mdserver-web
fi

# 创建目录
echo -e "${BLUE}[1/5] 创建目录结构...${PLAIN}"
mkdir -p /www/server
mkdir -p /www/wwwroot
mkdir -p /www/wwwlogs
mkdir -p /www/backup/database
mkdir -p /www/backup/site

# 安装基础依赖
echo -e "${BLUE}[2/5] 安装系统依赖...${PLAIN}"
apt update -y
apt install -y wget curl zip unzip tar cron python3 python3-pip python3-venv

# 创建 www 用户
if ! id www &>/dev/null; then
    groupadd www
    useradd -g www -s /usr/sbin/nologin www
fi

# 下载代码
echo -e "${BLUE}[3/5] 下载 mdserver-web...${PLAIN}"
cd /tmp
if [ -f /mnt/h/aicoding/mdserver-web/scripts/install.sh ]; then
    echo "从本地 Windows 目录复制..."
    cp -r /mnt/h/aicoding/mdserver-web /www/server/mdserver-web
else
    echo "从 GitHub 下载..."
    wget --no-check-certificate -O /tmp/master.tar.gz https://github.com/midoks/mdserver-web/archive/refs/heads/master.tar.gz
    tar -zxf /tmp/master.tar.gz -C /tmp
    mv -f /tmp/mdserver-web-master /www/server/mdserver-web
    rm -f /tmp/master.tar.gz
fi

# 安装 Python 依赖
echo -e "${BLUE}[4/5] 安装 Python 依赖...${PLAIN}"
cd /www/server/mdserver-web
python3 -m venv .
source bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 安装 acme.sh
if [ ! -d /root/.acme.sh ]; then
    echo -e "${BLUE}安装 acme.sh...${PLAIN}"
    curl -fsSL https://get.acme.sh | bash
fi

# 执行系统特定安装脚本
echo -e "${BLUE}[5/5] 执行 Debian 安装脚本...${PLAIN}"
OSNAME='debian'
if [ -f scripts/install/${OSNAME}.sh ]; then
    bash scripts/install/${OSNAME}.sh
fi

# 启动服务
echo -e "${GREEN}========================================${PLAIN}"
echo -e "${GREEN}  启动 mdserver-web 面板${PLAIN}"
echo -e "${GREEN}========================================${PLAIN}"

cd /www/server/mdserver-web
bash cli.sh start

sleep 2

# 获取默认信息
if [ -f /www/server/mdserver-web/data/default.pl ]; then
    DEFAULT_PORT=$(cat /www/server/mdserver-web/data/port.pl 2>/dev/null || echo "7200")
    DEFAULT_PWD=$(cat /www/server/mdserver-web/data/default.pl)
    echo -e "\n${GREEN}安装完成！${PLAIN}"
    echo -e "${GREEN}========================================${PLAIN}"
    echo -e "面板地址: ${BLUE}http://localhost:${DEFAULT_PORT}${PLAIN}"
    echo -e "默认密码: ${BLUE}${DEFAULT_PWD}${PLAIN}"
    echo -e "${GREEN}========================================${PLAIN}"
    echo -e "\n常用命令:"
    echo -e "  启动: ${BLUE}cd /www/server/mdserver-web && bash cli.sh start${PLAIN}"
    echo -e "  停止: ${BLUE}cd /www/server/mdserver-web && bash cli.sh stop${PLAIN}"
    echo -e "  重启: ${BLUE}cd /www/server/mdserver-web && bash cli.sh restart${PLAIN}"
    echo -e "  调试: ${BLUE}cd /www/server/mdserver-web && bash cli.sh debug${PLAIN}"
fi

echo -e "\n${GREEN}部署完成！${PLAIN}"
