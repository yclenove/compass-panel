# Compass面板 品牌命名规范

## 基本信息

| 项目 | 值 |
|------|-----|
| **面板名称** | Compass 指南面板 |
| **英文名** | Compass Panel |
| **中文名** | 指南面板 |
| **项目名** | compass-panel |
| **CLI命令** | `compass` |
| **GitHub** | github.com/midoks/compass-panel |
| **口号** | 导航指引，运筹帷幄 |
| **定位** | 新一代Linux服务器管理面板 |

## 安装与路径

| 项目 | 值 |
|------|-----|
| **一键安装** | `curl -sSL compass.run \| bash` |
| **安装路径** | `/www/server/compass-panel` |
| **配置目录** | `/etc/compass/` |
| **数据目录** | `/var/lib/compass/` (或 `/www/server/compass-panel/data/`) |
| **日志目录** | `/var/log/compass/` |
| **备份目录** | `/www/backup/` |
| **站点目录** | `/www/wwwroot/` |
| **安装日志** | `/var/log/compass-install.log` |

## CLI命令

```bash
compass                    # 交互式TUI界面
compass start              # 启动面板
compass stop               # 停止面板
compass restart            # 重启面板
compass status             # 查看状态
compass info               # 查看面板信息(地址/端口/密码)
compass reset              # 重置密码
compass port 8888          # 修改端口
compass ssl                # 管理面板SSL
compass update             # 更新面板
compass update --check     # 检查更新
compass backup             # 备份面板
compass restore <file>     # 恢复面板
compass log                # 查看日志
compass log --error        # 只看错误日志
compass doctor             # 诊断问题
compass security           # 安全检查
compass performance        # 性能检查
compass uninstall          # 卸载面板
```

## 技术栈

| 层 | 技术 | 版本 |
|----|------|------|
| 后端框架 | Flask | 2.x+ |
| WSGI | Gunicorn | 21.x+ |
| ORM | SQLAlchemy | 2.0+ |
| 数据库 | SQLite (WAL模式) | 3.35+ |
| 数据库迁移 | Alembic | 1.x+ |
| 加密 | cryptography (Fernet) | 41.x+ |
| WebSocket | Flask-SocketIO | 5.x+ |
| SSH | paramiko | 3.x+ |
| 前端框架 | Vue 3 | 3.x+ |
| 构建工具 | Vite | 5.x+ |
| UI库 | Element Plus | 2.x+ |
| 状态管理 | Pinia | 2.x+ |
| 路由 | Vue Router | 4.x+ |
| 图表 | ECharts | 5.x+ |
| 编辑器 | Monaco Editor | 0.4x+ |
| 终端 | xterm.js | 5.x+ |
| CLI | rich | 13.x+ |
| 压缩 | zstd | 0.16+ |

## 版本规划

| 版本 | 阶段 | 内容 |
|------|------|------|
| v1.5 | S0 | 数据层基础设施 |
| v2.0 | S1-S4 | 核心功能(项目类型/网站管理/安全/数据库) |
| v3.0 | S5-S9 | 运维功能(文件/备份/监控/Docker/SSL) |
| v4.0 | S10-S14 | 扩展功能(计划任务/FTP/推送/用户/Web服务器) |
| v5.0 | S15-S19 | 高级功能(系统优化/伪静态/AI助手/插件/面板安全) |
| v6.0 | S20-S25 | 企业级(高级功能/主题/API/自动化/迁移) |

## 数据库文件

```
data/
├── panel.db        # 核心配置(站点/用户/配置/域名/备份记录)
├── security.db     # 安全相关(防火墙/登录日志/WAF规则/IP黑白名单)
├── monitor.db      # 监控数据(CPU/内存/网络/磁盘/进程/负载)
├── task.db         # 任务相关(计划任务/任务日志/任务状态)
└── log.db          # 操作日志(审计/操作记录/访问日志)
```

## 前端路由

```
/compass/                    # 面板根路径(安全入口)
/compass/vue/                # Vue SPA
/compass/vue/dashboard       # 仪表盘
/compass/vue/site            # 网站管理
/compass/vue/files           # 文件管理
/compass/vue/monitor         # 系统监控
/compass/vue/firewall        # 安全
/compass/vue/logs            # 日志
/compass/vue/crontab         # 计划任务
/compass/vue/soft            # 软件管理
/compass/vue/setting         # 面板设置
/compass/vue/terminal        # 终端(新增)
/compass/vue/docker          # Docker管理(新增)
/compass/vue/database        # 数据库管理(新增)
/compass/vue/ssl             # SSL管理(新增)
/compass/vue/backup          # 备份管理(新增)
/compass/vue/migration       # 面板迁移(新增)
/compass/vue/ai              # AI助手(新增)
```

## API路径

```
/api/v1/panel/               # 面板信息
/api/v1/site/                # 网站管理
/api/v1/file/                # 文件管理
/api/v1/database/            # 数据库管理
/api/v1/firewall/            # 防火墙
/api/v1/crontab/             # 计划任务
/api/v1/monitor/             # 监控
/api/v1/system/              # 系统
/api/v1/ssl/                 # SSL
/api/v1/backup/              # 备份
/api/v1/docker/              # Docker
/api/v1/terminal/            # 终端
/api/v1/ai/                  # AI助手
/api/v1/migration/           # 面板迁移
/api/v1/user/                # 用户管理
```

## 配置文件

```
config/
├── encryption.key           # 加密密钥(Fernet)
├── panel.conf               # 面板主配置
├── dns_api.json             # DNS API提供商
├── php_versions.json        # PHP版本列表
├── safe_autofix.json        # 安全自动修复
├── safe_categories.json     # 安全检查分类
├── weak_pass.txt            # 弱密码字典
├── crontab.json             # 计划任务配置
├── databases.json           # 数据库路由配置
└── menu.json                # 菜单配置
```

## 代码规范

### Python
- PEP8 + Black格式化(行宽88)
- 类型注解(Type Hints)
- Docstring(Google风格)
- SQLAlchemy 2.0声明式模型

### JavaScript/Vue
- ESLint + Prettier
- Vue 3 Composition API(`<script setup>`)
- TypeScript(可选，渐进式)

### 提交规范
```
feat(模块): 新功能描述
fix(模块): 修复描述
docs(模块): 文档描述
refactor(模块): 重构描述
perf(模块): 性能优化描述
test(模块): 测试描述
chore(模块): 构建/工具描述
```

## 文件头规范

```python
# coding: utf-8

# ---------------------------------------------------------------------------------
# Compass Panel - Linux Server Management
# ---------------------------------------------------------------------------------
# Copyright (c) 2026 compass-panel contributors. All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------
```
