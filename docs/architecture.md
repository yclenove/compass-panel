# MW-Linux 面板项目架构文档

## 项目概述

mdserver-web (MW-Linux面板) 是一个基于 Python Flask 框架开发的 Linux 服务器管理面板，提供 Web 界面来管理服务器、网站、数据库、插件等功能。

- **版本**: 0.18.5
- **Python 版本**: 3.6+
- **Web 框架**: Flask + Gunicorn
- **数据库**: SQLite (面板数据) + MySQL (可选)
- **实时通信**: Flask-SocketIO

## 目录结构

```
mdserver-web/
├── web/                    # Web 应用主目录
│   ├── app.py             # 应用入口
│   ├── config.py          # 配置文件
│   ├── setting.py         # Gunicorn 配置
│   ├── branding.py        # 品牌信息
│   ├── version.py         # 版本信息
│   ├── admin/             # 管理后台模块
│   │   ├── __init__.py    # Flask 应用初始化
│   │   ├── submodules.py  # 蓝图模块注册
│   │   ├── common.py      # 公共工具
│   │   ├── user_login_check.py  # 登录验证装饰器
│   │   ├── dashboard/     # 仪表盘模块
│   │   ├── site/          # 站点管理模块
│   │   ├── files/         # 文件管理模块
│   │   ├── soft/          # 软件管理模块
│   │   ├── plugins/       # 插件管理模块
│   │   ├── setting/       # 面板设置模块
│   │   ├── crontab/       # 计划任务模块
│   │   ├── firewall/      # 防火墙模块
│   │   ├── logs/          # 日志模块
│   │   ├── monitor/       # 监控模块
│   │   ├── system/        # 系统信息模块
│   │   ├── task/          # 任务队列模块
│   │   └── setup/         # 初始化设置
│   ├── core/              # 核心库
│   │   ├── mw.py          # 核心工具函数
│   │   ├── orm.py         # MySQL ORM
│   │   └── db.py          # 数据库工具
│   ├── thisdb/            # 数据库操作层
│   │   ├── __init__.py    # 导入所有模块
│   │   ├── init.py        # 数据库初始化
│   │   ├── user.py        # 用户表操作
│   │   ├── sites.py       # 站点表操作
│   │   ├── option.py      # 配置表操作
│   │   ├── logs.py        # 日志表操作
│   │   ├── crontab.py     # 计划任务表操作
│   │   ├── firewall.py    # 防火墙表操作
│   │   ├── tasks.py       # 任务队列表操作
│   │   └── ...
│   ├── utils/             # 工具类库
│   │   ├── plugin.py      # 插件管理工具
│   │   ├── site.py        # 站点管理工具
│   │   ├── file.py        # 文件操作工具
│   │   ├── firewall.py    # 防火墙工具
│   │   ├── crontab.py     # 计划任务工具
│   │   ├── task.py        # 任务队列工具
│   │   ├── config.py      # 配置工具
│   │   ├── setting.py     # 设置工具
│   │   ├── ssh/           # SSH 相关
│   │   ├── system/        # 系统信息工具
│   │   ├── php/           # PHP 相关工具
│   │   └── cert/          # 证书工具
│   └── templates/         # 模板文件
├── plugins/               # 插件目录
│   ├── openresty/         # OpenResty 插件
│   ├── mysql/             # MySQL 插件
│   ├── redis/             # Redis 插件
│   ├── php/               # PHP 插件
│   └── ...                # 其他插件
├── data/                  # 数据目录
│   └── panel.db           # SQLite 数据库
├── logs/                  # 日志目录
├── cli.sh                 # 启动脚本
├── panel_task.py          # 后台任务进程
└── requirements.txt       # Python 依赖
```

## 核心架构

### 1. Flask 应用初始化

应用入口 `web/app.py` 负责:
- 初始化 Flask 应用
- 配置压缩 (brotli/zstd/gzip)
- 配置缓存 (Flask-Caching)
- 配置 Session
- 注册蓝图模块
- 初始化 SocketIO
- 配置日志

### 2. 蓝图模块系统

所有功能模块通过 Flask Blueprint 组织，在 `admin/submodules.py` 中统一注册:

```python
# 已注册的蓝图模块
DashboardModule   # 仪表盘 (/)
SiteModule        # 站点管理 (/site)
TaskModule        # 任务队列 (/task)
SettingModule     # 面板设置 (/setting)
LogsModule        # 日志管理 (/logs)
FilesModule       # 文件管理 (/files)
SoftModule        # 软件管理 (/soft)
PluginsModule     # 插件管理 (/plugins)
CrontabModule     # 计划任务 (/crontab)
FirewallModule    # 防火墙 (/firewall)
MonitorModule     # 监控 (/monitor)
SystemModule      # 系统信息 (/system)
```

### 3. 数据库层

#### SQLite (面板数据)
- 存储路径: `data/panel.db`
- 用于存储面板配置、用户信息、站点信息等
- 通过 `thisdb/` 模块封装数据库操作

#### MySQL ORM
- `core/orm.py` 提供 MySQL 连接和操作
- 用于管理用户安装的 MySQL 数据库

### 4. 插件系统

每个插件是一个独立目录，包含:
- `info.json`: 插件元信息
- `index.py`: 插件主逻辑
- `index.html`: 插件设置页面
- `install.sh`: 安装脚本
- `init.d/`: 服务管理脚本
- `conf/`: 配置文件模板
- `js/`: 前端 JavaScript

### 5. 任务队列

- `panel_task.py`: 后台任务进程，独立运行
- 用于执行耗时操作: 插件安装、文件下载、备份等
- 通过数据库任务表进行任务调度

## 请求处理流程

```
客户端请求
    ↓
Gunicorn (多线程)
    ↓
Flask before_request (认证检查)
    ↓
Blueprint 路由处理
    ↓
业务逻辑 (utils/thisdb)
    ↓
响应返回
```

## 认证机制

1. **Session 认证**: 基于 Flask Session，存储登录状态
2. **安全入口**: 可设置自定义管理路径
3. **Basic Auth**: 可选的 HTTP 基础认证
4. **两步验证**: 支持 TOTP 两步验证
5. **临时登录**: 支持临时 Token 登录
6. **验证码**: 登录验证码保护

## 配置管理

### 环境变量
- `MW_ENV`: 运行环境 (development/production)

### 配置文件
- `web/config.py`: 应用配置
- `web/setting.py`: Gunicorn 配置
- `data/port.pl`: 面板端口
- `data/ipv6.pl`: IPv6 配置

## 核心依赖

| 依赖 | 用途 |
|------|------|
| Flask | Web 框架 |
| Gunicorn | WSGI 服务器 |
| Flask-SocketIO | WebSocket 支持 |
| Flask-Caching | 缓存 |
| Flask-Compress | 响应压缩 |
| PyMySQL | MySQL 连接 |
| psutil | 系统监控 |
| paramiko | SSH 连接 |
| pyotp | 两步验证 |
| cryptography | 加密工具 |

## 目录约定

| 目录 | 用途 |
|------|------|
| `/www/server/` | 软件安装目录 |
| `/www/wwwroot/` | 网站根目录 |
| `/www/backup/` | 备份目录 |
| `/www/wwwlogs/` | 日志目录 |
| `data/` | 面板数据目录 |
| `logs/` | 面板日志目录 |
| `plugins/` | 插件目录 |
| `tmp/` | 临时文件目录 |
