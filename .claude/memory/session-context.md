# Compass Panel 项目上下文

## 项目信息
- **项目名称**: compass-panel
- **代码位置**: H:\aicoding\compass-panel
- **远程仓库**: https://github.com/yclenove/compass-panel
- **面板名称**: Compass 指南面板（从 mdserver-web 改名而来）
- **基于**: mdserver-web (midoks/mdserver-web) 深度改造

## 技术栈
- **后端**: Flask + Gunicorn + SQLAlchemy 2.0 + SQLite(WAL) + Socket.IO
- **前端**: Vue 3 + Vite + Element Plus + Pinia + ECharts + Monaco Editor + xterm.js
- **Python**: 3.13.5 (WSL Debian)
- **Node**: v20.20.2
- **UI**: Vue 3 前端在 `/vue/` 路径下，传统模板页面保留在根路径

## 25阶段迭代计划
详见 `docs/BAOTA_COMPARISON.md`
- S0: 数据层基础 (SQLAlchemy 2.0 + WAL + 多库分离 + Fernet加密 + Alembic)
- S1-S4: 项目类型/网站管理/安全/数据库
- S5-S9: 文件管理/备份/监控/Docker/SSL
- S10-S24: 各种功能模块
- S25: 面板迁移（快照/跨服务器迁移/环境克隆/版本回滚/灾难恢复）

## 品牌规范
详见 `docs/BRAND.md`
- CLI命令: `compass start/stop/status/reset/info`
- 安装: `curl -sSL compass.run | bash`
- 路径: `/www/server/compass-panel`, `/etc/compass/`
- 版本计划: v1.5(S0) → v2.0(S1-S4) → ... → v6.0(S20-S25)

## WSL 部署信息
- **WSL发行版**: Debian (Running, WSL2)
- **WSL用户**: root
- **面板目录**: /www/server/compass-panel
- **Python venv**: /www/server/compass-panel/venv
- **systemd服务**: compass.service (已创建并启用)
- **运行端口**: 7202 (端口7201被旧mdserver-web占用后改用)
- **admin_path**: ZeArJVCH
- **数据库**: /www/server/compass-panel/data/panel.db
- **前端dist**: /www/server/compass-panel/web/static/dist/ (已构建)
- **前端源码**: /www/server/compass-panel/web/frontend/

## 已知问题（待修复）
1. 内存单位显示 "undefined" — `31.23 undefined` 应显示 `GB`
2. 面板名称仍为 "夸父面板" — 需改为 "Compass 指南面板"
3. 面板版本显示 0.18.5/0.0.1 — 需更新版本号
4. admin_close 默认值为 "yes" — 导致API重定向到/close，默认应为 "no"
5. 端口显示 7200 — 数据库中默认值，实际应匹配运行端口
6. 系统监控页面空白 — 监控数据未采集（正常现象）
7. 部分 API 请求返回 302 到 /close — 已通过修改admin_close修复

## 数据库关键配置
```sql
-- option 表中的关键配置
admin_close = 'no'  -- 原来是 'yes'，导致所有API被重定向
panel_api = '{"open": true}'  -- 原来是 false
admin_path = 'ZeArJVCH'
title = '夸父面板'  -- 需改为 'Compass 指南面板'
```

## 代码中的关键文件
- `web/admin/__init__.py` — Flask应用初始化、路由注册、before_request拦截
- `web/admin/user_login_check.py` — 登录验证装饰器
- `web/admin/setup/__init__.py` — 面板初始化（数据库、用户、命令、定时任务）
- `web/admin/setup/init_cmd.py` — init.d脚本初始化（WSL下会卡住，已用try/except包裹）
- `web/admin/system/system.py` — 系统信息API
- `web/admin/setting/app.py` — 面板设置API
- `web/thisdb/option.py` — 数据库选项读取
- `web/static/dist/` — Vue前端构建产物
- `web/frontend/` — Vue前端源码

## Git 注意事项
- 之前有敏感信息泄露（Google OAuth/Azure secrets），已通过 filter-branch 清理
- 提交前检查 plugins/ 目录下的敏感文件
- .gitignore 已配置排除 __pycache__, node_modules, .venv, data/*.db, logs, *.key 等
