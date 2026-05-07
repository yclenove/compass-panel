# mdserver-web 迭代设计方案

## 背景

mdserver-web 是一个 Linux 面板管理工具，当前存在以下问题：
- 前端技术栈老旧（jQuery 1.10 + Bootstrap 3.3.5）
- 缺乏代码质量规范
- 文档不完善
- 没有正式测试
- 文本编辑器体验差

本迭代计划通过 4 个阶段，全面提升项目质量。

## 技术选型

| 类别 | 选择 | 理由 |
|------|------|------|
| 代码规范 | PEP8 + Black + Flake8 | Python 社区标准 |
| 前端框架 | Vue 3 + Vite + Element Plus | 现代化、组件化、生态丰富 |
| 状态管理 | Pinia | Vue 3 官方推荐 |
| 路由 | Vue Router 4 | Vue 3 官方路由 |
| 文本编辑器 | Monaco Editor | VS Code 同款，功能强大 |
| 测试框架 | pytest + Vitest | 简单易用，社区标准 |
| CSS 框架 | Element Plus + UnoCSS | 组件库 + 原子化 CSS |

## 阶段 1：基础建设

### 1.1 代码质量规则

**Python 配置**
- `pyproject.toml`：Black 格式化配置
- `.flake8`：Flake8 检查规则
- `pre-commit`：Git hooks 自动格式化

**JavaScript 配置**
- `.eslintrc.js`：ESLint 规则
- `.prettierrc`：Prettier 格式化配置
- `package.json`：添加 lint 脚本

**通用配置**
- `.editorconfig`：编辑器统一配置
- `.gitignore`：完善忽略规则

### 1.2 补全文档

**文档结构**
```
docs/
├── architecture.md      # 项目架构
├── api/                 # API 文档
│   ├── dashboard.md
│   ├── files.md
│   ├── site.md
│   └── ...
├── plugins/             # 插件开发指南
│   ├── getting-started.md
│   └── api-reference.md
├── deployment.md        # 部署文档
└── contributing.md      # 贡献指南
```

**文档内容**
- 项目架构图
- API 接口说明（参数、返回值、示例）
- 插件开发流程
- 部署步骤

### 1.3 开发模式

**实现方式**
- 环境变量 `MW_ENV=development`
- 开发模式行为：
  - 关闭验证码
  - 开启热重载
  - 显示调试信息
  - 允许跨域请求
  - 详细错误日志

**配置文件**
- `web/config.py`：读取环境变量
- `.env.example`：环境变量示例

---

## 阶段 2：前端重构

### 2.1 Vue 3 全面重写

**项目结构**
```
web/frontend/
├── src/
│   ├── assets/          # 静态资源
│   ├── components/      # 通用组件
│   ├── layouts/         # 布局组件
│   ├── pages/           # 页面组件
│   ├── stores/          # Pinia 状态
│   ├── router/          # 路由配置
│   ├── utils/           # 工具函数
│   └── App.vue
├── public/
├── index.html
├── vite.config.js
└── package.json
```

**页面拆分**
- 首页仪表盘
- 网站管理
- 文件管理
- 数据库管理
- 监控
- 安全
- 日志
- 计划任务
- 软件管理
- 面板设置

**组件设计**
- `Layout.vue`：主布局（侧边栏 + 内容区）
- `DataTable.vue`：数据表格组件
- `FileEditor.vue`：文件编辑器组件
- `Terminal.vue`：终端组件
- `Charts.vue`：图表组件

### 2.2 Monaco Editor 集成

**功能特性**
- 多语言语法高亮
- 代码补全
- Emmet 支持
- 多光标编辑
- 搜索替换
- 代码折叠
- 缩进指南
- 小地图

**集成方式**
- `monaco-editor` npm 包
- `@monaco-editor/loader` 动态加载
- 自定义主题

### 2.3 UI/UX 优化

**设计语言**
- 现代化卡片布局
- 圆角设计
- 渐变色彩
- 阴影效果
- 动画过渡

**响应式设计**
- 移动端适配
- 平板适配
- 桌面适配

**暗色主题**
- Element Plus 暗色模式
- 自定义暗色变量
- 主题切换

**快捷键**
- `Ctrl+S`：保存
- `Ctrl+F`：搜索
- `Ctrl+Z`：撤销
- `Ctrl+Shift+P`：命令面板

---

## 阶段 3：质量保障

### 3.1 单元测试

**后端测试**
```
tests/
├── conftest.py          # pytest 配置
├── test_api/            # API 测试
│   ├── test_dashboard.py
│   ├── test_files.py
│   └── ...
├── test_utils/          # 工具测试
└── test_models/         # 模型测试
```

**前端测试**
```
web/frontend/src/
├── __tests__/           # 组件测试
├── stores/__tests__/    # 状态测试
└── utils/__tests__/     # 工具测试
```

**覆盖率目标**
- 后端：80%+
- 前端：70%+

### 3.2 部署测试

**自动化流程**
1. 代码提交触发测试
2. 测试通过后构建
3. 部署到 WSL
4. MCP 浏览器自动化测试
5. 生成测试报告

**冒烟测试**
- 面板登录
- 文件管理
- 网站管理
- 软件安装

---

## 阶段 4：持续迭代

### 4.1 自动迭代 100 轮

**迭代策略**
- 每轮修复 1-3 个问题
- 优先级：bug > 技术债 > 性能优化 > 功能增强

**问题来源**
- 代码扫描（ESLint、Flake8）
- 已知 issue
- 技术债清单
- 性能瓶颈

**自动化流程**
1. 扫描问题
2. 选择优先级最高的问题
3. 修复问题
4. 运行测试
5. 部署验证
6. 生成报告
7. 提交代码

---

## 验证方案

### 阶段 1 验证
- 运行 `black --check .` 确认格式化
- 运行 `flake8` 确认无错误
- 运行 `npm run lint` 确认前端规范
- 检查文档完整性

### 阶段 2 验证
- 前端构建成功
- 页面正常加载
- 功能正常运行
- 响应式布局正常

### 阶段 3 验证
- `pytest` 测试通过
- `vitest` 测试通过
- 覆盖率达标
- MCP 自动化测试通过

### 阶段 4 验证
- 每轮迭代报告
- 问题修复确认
- 无回归问题

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Vue 3 重写工作量大 | 高 | 分模块渐进式迁移 |
| Monaco Editor 包体积大 | 中 | 动态加载，按需引入 |
| 测试覆盖率不足 | 中 | 优先测试核心功能 |
| 自动迭代引入新 bug | 中 | 每轮运行完整测试 |

## 时间估算

| 阶段 | 预计时间 | 说明 |
|------|----------|------|
| 阶段 1 | 2-3 天 | 基础建设 |
| 阶段 2 | 5-7 天 | 前端重构 |
| 阶段 3 | 2-3 天 | 质量保障 |
| 阶段 4 | 持续进行 | 100 轮迭代 |
| **总计** | **10-15 天 + 持续** | |

## 下一步

1. 用户批准设计
2. 编写实现计划
3. 开始阶段 1 实现
