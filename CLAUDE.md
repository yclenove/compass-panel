# mdserver-web 项目配置

## 项目概述

mdserver-web 是一个 Linux 服务器管理面板，提供 Web 界面管理服务器、网站、文件、数据库等功能。

## 技术栈

### 后端
- **框架**: Flask
- **数据库**: SQLAlchemy + SQLite
- **服务器**: Gunicorn
- **WebSocket**: Socket.IO

### 前端
- **框架**: Vue 3 + Vite
- **UI 库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **编辑器**: Monaco Editor
- **图表**: ECharts

## 目录结构

```
mdserver-web/
├── web/                    # Web 应用主目录
│   ├── admin/              # 后台管理模块（路由）
│   ├── core/               # 核心模块（mw.py, db.py, orm.py）
│   ├── static/             # 静态资源
│   ├── templates/          # Jinja2 模板
│   ├── thisdb/             # 数据库操作封装
│   ├── utils/              # 工具模块
│   ├── frontend/           # Vue 3 前端项目
│   ├── app.py              # Flask 应用入口
│   └── config.py           # 配置文件
├── plugins/                # 插件目录
├── scripts/                # 脚本目录
├── tests/                  # 测试目录
└── docs/                   # 文档目录
```

## 开发模式

设置环境变量 `MW_ENV=development` 启用开发模式：
- 关闭验证码
- 开启调试日志

```bash
export MW_ENV=development
```

## 常用命令

### 后端
```bash
# 启动服务
bash cli.sh start

# 开发模式启动
cd web && gunicorn -b :7200 -w 1 --reload app:app

# 运行测试
python -m pytest tests/ -v

# 代码检查
flake8 web/
black --check web/
```

### 前端
```bash
cd web/frontend

# 安装依赖
npm install

# 开发服务器
npm run dev

# 构建
npm run build

# 代码检查
npm run lint
```

### 迭代
```bash
# 初始化迭代环境
bash scripts/iterate.sh init

# 运行迭代
bash scripts/iterate.sh run

# 查看状态
bash scripts/iterate.sh status
```

## 代码规范

### Python
- PEP8 规范
- Black 格式化（行宽 88）
- Flake8 检查

### JavaScript/Vue
- ESLint 检查
- Prettier 格式化
- Vue 3 Composition API（`<script setup>`）

## 提交规范

```
<type>(<scope>): <subject>

类型: feat, fix, docs, style, refactor, perf, test, chore
```
