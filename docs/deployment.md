# 部署文档

## 概述

本文档介绍如何在 Linux 服务器上部署 mdserver-web 面板。

## 系统要求

### 操作系统
- CentOS 7+
- Ubuntu 18.04+
- Debian 9+
- 其他主流 Linux 发行版

### 硬件要求
- CPU: 1 核+
- 内存: 1GB+ (推荐 2GB+)
- 磁盘: 20GB+ 可用空间

### 软件要求
- Python 3.6+
- pip3
- git
- curl/wget

## 快速安装

### 一键安装脚本

```bash
# CentOS/RHEL
yum install -y wget && wget -O install.sh https://cdn.jsdelivr.net/gh/midoks/mdserver-web@latest/scripts/install.sh && bash install.sh

# Ubuntu/Debian
apt install -y wget && wget -O install.sh https://cdn.jsdelivr.net/gh/midoks/mdserver-web@latest/scripts/install.sh && bash install.sh
```

### 国内加速安装

```bash
# 使用国内镜像
yum install -y wget && wget -O install.sh https://gitee.com/midoks/mdserver-web/raw/master/scripts/install.sh && bash install.sh
```

## 手动安装

### 1. 安装依赖

**CentOS/RHEL:**
```bash
yum install -y python3-devel gcc make wget curl git
yum install -y openssl-devel bzip2-devel libffi-devel
```

**Ubuntu/Debian:**
```bash
apt update
apt install -y python3-dev gcc make wget curl git
apt install -y libssl-dev libffi-dev libbz2-dev
```

### 2. 克隆代码

```bash
cd /www/server
git clone https://github.com/midoks/mdserver-web.git
cd mdserver-web
```

### 3. 安装 Python 依赖

```bash
pip3 install -r requirements.txt
```

如果国内下载慢，可以使用镜像:
```bash
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 创建必要目录

```bash
mkdir -p /www/server
mkdir -p /www/wwwroot
mkdir -p /www/backup
mkdir -p /www/wwwlogs
```

### 5. 启动面板

```bash
cd /www/server/mdserver-web
bash cli.sh start
```

## 启动脚本说明

`cli.sh` 提供以下命令:

```bash
# 启动面板 (包含后台任务)
bash cli.sh start

# 停止面板
bash cli.sh stop

# 重启面板
bash cli.sh restart

# 调试模式启动
bash cli.sh debug

# 仅启动面板 (不含后台任务)
bash cli.sh panel

# 仅启动后台任务
bash cli.sh task
```

## 配置说明

### 面板端口

默认端口随机生成，存储在 `data/port.pl` 文件中。

首次启动时会:
1. 随机生成 10000-65530 之间的端口
2. 自动放行防火墙端口
3. 将端口保存到 `data/port.pl`

### 面板地址

启动后会显示面板访问地址和初始账号密码:
```
==================================================================
mdserver-web 0.18.5
面板地址: http://your-ip:7200
初始用户名: admin
初始密码: xxxxxxxx
==================================================================
```

### 修改端口

```bash
# 停止面板
bash cli.sh stop

# 修改端口
echo "8080" > data/port.pl

# 启动面板
bash cli.sh start
```

### IPv6 支持

```bash
# 启用 IPv6
touch data/ipv6.pl

# 禁用 IPv6
rm -f data/ipv6.pl
```

### SSL 配置

面板支持 HTTPS 访问，可在面板设置中开启:
1. 登录面板
2. 进入 面板设置
3. 配置面板 SSL

## 目录结构

部署后的目录结构:

```
/www/server/
├── mdserver-web/           # 面板目录
│   ├── web/               # Web 应用
│   ├── plugins/           # 插件目录
│   ├── data/              # 数据目录
│   │   ├── panel.db       # SQLite 数据库
│   │   ├── port.pl        # 面板端口
│   │   └── default.pl     # 初始密码
│   ├── logs/              # 日志目录
│   │   ├── panel.log      # 访问日志
│   │   ├── panel_error.log # 错误日志
│   │   └── panel_task.log # 任务日志
│   ├── cli.sh             # 启动脚本
│   └── panel_task.py      # 后台任务
├── openresty/             # OpenResty (插件安装)
├── mysql/                 # MySQL (插件安装)
├── redis/                 # Redis (插件安装)
└── php/                   # PHP (插件安装)

/www/
├── wwwroot/               # 网站根目录
├── backup/                # 备份目录
└── wwwlogs/               # 网站日志
```

## Gunicorn 配置

面板使用 Gunicorn 作为 WSGI 服务器，配置文件 `web/setting.py`:

```python
# 工作进程数 (自动根据 CPU 核心数设置)
workers = cpu_count
if workers > 2:
    workers = 2

# 线程数
threads = workers * 2

# 工作模式
worker_class = 'gthread'

# 超时时间
timeout = 600

# 保持连接时间
keepalive = 60

# 日志级别
loglevel = 'info'

# 日志文件
errorlog = 'logs/panel_error.log'
accesslog = 'logs/panel.log'
```

## 防火墙配置

面板会自动配置防火墙，如需手动配置:

**firewalld:**
```bash
firewall-cmd --permanent --add-port=7200/tcp
firewall-cmd --reload
```

**iptables:**
```bash
iptables -A INPUT -p tcp --dport 7200 -j ACCEPT
service iptables save
```

**ufw:**
```bash
ufw allow 7200/tcp
```

## 进程管理

### 查看进程

```bash
# 查看面板进程
ps aux | grep app:app

# 查看任务进程
ps aux | grep panel_task.py
```

### 手动停止

```bash
# 停止所有面板进程
bash cli.sh stop

# 或手动 kill
pkill -f app:app
pkill -f panel_task.py
```

## 日志说明

| 日志文件 | 说明 |
|----------|------|
| logs/panel.log | Gunicorn 访问日志 |
| logs/panel_error.log | 错误日志 |
| logs/panel_task.log | 后台任务日志 |
| logs/panel_exec.log | 任务执行输出 |
| logs/panel.pid | 进程 PID 文件 |

### 查看日志

```bash
# 实时查看访问日志
tail -f logs/panel.log

# 查看错误日志
tail -f logs/panel_error.log

# 查看任务日志
tail -f logs/panel_task.log
```

## 升级面板

### 在线升级

面板内置升级功能，可在面板界面中直接升级。

### 手动升级

```bash
cd /www/server/mdserver-web

# 停止面板
bash cli.sh stop

# 拉取最新代码
git pull

# 更新依赖
pip3 install -r requirements.txt

# 启动面板
bash cli.sh start
```

## 卸载面板

```bash
# 停止面板
bash cli.sh stop

# 删除面板目录
rm -rf /www/server/mdserver-web

# 删除数据目录 (可选)
rm -rf /www/server
rm -rf /www/wwwroot
rm -rf /www/backup
rm -rf /www/wwwlogs
```

## 常见问题

### Q: 面板无法访问?

A: 检查以下几点:
1. 防火墙是否放行端口
2. 面板进程是否正常运行
3. 查看错误日志排查问题

### Q: 忘记面板密码?

A: 使用以下命令重置:
```bash
cd /www/server/mdserver-web
python3 -c "
import sys
sys.path.insert(0, 'web')
import core.mw as mw
import thisdb
thisdb.setUserByRoot(password='new_password')
print('密码已重置')
"
```

### Q: 如何修改面板用户名?

A: 使用以下命令:
```bash
cd /www/server/mdserver-web
python3 -c "
import sys
sys.path.insert(0, 'web')
import core.mw as mw
import thisdb
thisdb.setUserByRoot(name='new_username')
print('用户名已修改')
"
```

### Q: 面板启动失败?

A: 检查以下几点:
1. Python 版本是否 >= 3.6
2. 依赖是否安装完整
3. 端口是否被占用
4. 查看错误日志: `cat logs/panel_error.log`

### Q: 如何配置反向代理?

A: 使用 Nginx 反向代理示例:
```nginx
server {
    listen 80;
    server_name panel.example.com;

    location / {
        proxy_pass http://127.0.0.1:7200;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 性能优化

### 1. 调整 Gunicorn 配置

根据服务器配置调整 `web/setting.py`:
```python
# CPU 核心数较多时
workers = 4
threads = 8
```

### 2. 启用缓存

面板默认启用 Flask-Caching，可通过配置优化缓存策略。

### 3. 日志轮转

日志自动轮转，配置在 `web/config.py`:
```python
LOG_ROTATION_SIZE = 1  # MB
LOG_ROTATION_AGE = 1440  # 分钟
LOG_ROTATION_MAX_LOG_FILES = 5  # 保留数量
```

## 安全建议

1. **修改默认端口**: 避免使用常见端口
2. **设置安全入口**: 在面板设置中配置安全路径
3. **开启 HTTPS**: 配置面板 SSL 证书
4. **启用两步验证**: 增强账户安全
5. **限制登录尝试**: 面板自带登录失败锁定
6. **定期备份**: 备份面板数据和网站数据
7. **及时更新**: 保持面板和插件最新版本
