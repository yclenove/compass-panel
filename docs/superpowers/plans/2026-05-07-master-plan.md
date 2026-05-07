# mdserver-web 迭代主计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 全面提升 mdserver-web 项目质量，包括代码规范、前端重构、测试体系和持续迭代

**架构：** 分 4 个阶段实施，每个阶段独立可测试，逐步提升项目质量

**技术栈：** Python, Flask, Vue 3, Element Plus, Monaco Editor, pytest, Vitest

---

## 计划概览

| 阶段 | 目标 | 预计时间 | 计划文件 |
|------|------|----------|----------|
| 阶段 1 | 基础建设 | 2-3 天 | [phase1-basic-infrastructure.md](phase1-basic-infrastructure.md) |
| 阶段 2 | 前端重构 | 5-7 天 | [phase2-frontend-refactor.md](phase2-frontend-refactor.md) |
| 阶段 3 | 质量保障 | 2-3 天 | [phase3-quality-assurance.md](phase3-quality-assurance.md) |
| 阶段 4 | 持续迭代 | 持续进行 | [phase4-continuous-iteration.md](phase4-continuous-iteration.md) |

**总计：10-15 天 + 持续迭代**

---

## 阶段 1：基础建设

**目标：** 建立代码质量规范、补全项目文档、实现开发模式

**关键任务：**
1. 创建 Python 代码规范配置（pyproject.toml, .flake8, .pre-commit-config.yaml）
2. 创建 JavaScript 代码规范配置（package.json, .eslintrc.js, .prettierrc）
3. 实现开发模式（环境变量切换，关闭验证码）
4. 创建项目文档（架构、API、插件开发、部署、贡献指南）

**验收标准：**
- `black --check .` 通过
- `flake8` 无错误
- `npm run lint` 通过
- 文档完整

**详细计划：** [phase1-basic-infrastructure.md](phase1-basic-infrastructure.md)

---

## 阶段 2：前端重构

**目标：** 将前端从 jQuery + Bootstrap 重构为 Vue 3 + Element Plus，集成 Monaco Editor

**关键任务：**
1. 初始化 Vue 3 项目（Vite, Pinia, Vue Router）
2. 创建 API 请求封装（Axios）
3. 创建 Pinia 状态管理
4. 创建主布局组件（侧边栏、头部、内容区）
5. 创建登录页面
6. 创建首页仪表盘
7. 创建文件管理页面（Monaco Editor 集成）
8. 创建网站管理页面
9. 创建其他页面占位
10. 配置构建输出

**验收标准：**
- `npm run build` 成功
- 所有页面正常加载
- Monaco Editor 功能正常
- 响应式布局正常

**详细计划：** [phase2-frontend-refactor.md](phase2-frontend-refactor.md)

---

## 阶段 3：质量保障

**目标：** 建立完整的测试体系，实现自动化测试和部署验证

**关键任务：**
1. 配置 pytest 环境
2. 编写仪表盘 API 测试
3. 编写文件管理 API 测试
4. 编写工具函数测试
5. 配置前端测试环境（Vitest）
6. 编写前端组件测试
7. 创建部署脚本
8. 创建冒烟测试
9. 配置 GitHub Actions
10. 生成测试覆盖率报告

**验收标准：**
- `pytest` 测试通过
- `npm test` 通过
- 测试覆盖率 > 70%
- 冒烟测试通过

**详细计划：** [phase3-quality-assurance.md](phase3-quality-assurance.md)

---

## 阶段 4：持续迭代

**目标：** 建立自动化迭代框架，实现 100 轮自动迭代

**关键任务：**
1. 创建迭代配置文件
2. 创建问题扫描脚本
3. 创建问题修复脚本
4. 创建报告生成脚本
5. 创建迭代主脚本
6. 创建 GitHub Actions 自动迭代
7. 创建迭代状态追踪
8. 初始化迭代环境
9. 创建快速迭代脚本
10. 创建迭代主控脚本

**验收标准：**
- 迭代脚本可运行
- 问题扫描正常
- 报告生成正常
- GitHub Actions 配置正确

**详细计划：** [phase4-continuous-iteration.md](phase4-continuous-iteration.md)

---

## 执行顺序

### 第一周：基础建设
- [ ] 完成阶段 1 所有任务
- [ ] 验收阶段 1

### 第二周：前端重构
- [ ] 完成阶段 2 所有任务
- [ ] 验收阶段 2

### 第三周：质量保障
- [ ] 完成阶段 3 所有任务
- [ ] 验收阶段 3

### 持续：自动迭代
- [ ] 初始化迭代环境
- [ ] 运行首次迭代
- [ ] 配置自动迭代

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Vue 3 重写工作量大 | 高 | 分模块渐进式迁移 |
| Monaco Editor 包体积大 | 中 | 动态加载，按需引入 |
| 测试覆盖率不足 | 中 | 优先测试核心功能 |
| 自动迭代引入新 bug | 中 | 每轮运行完整测试 |

---

## 工具和命令

### 代码质量
```bash
# Python 格式化
black web/ tests/

# Python 检查
flake8 web/ tests/

# JavaScript 检查
cd web/frontend && npm run lint

# JavaScript 格式化
cd web/frontend && npm run format
```

### 测试
```bash
# 后端测试
python -m pytest tests/ -v

# 前端测试
cd web/frontend && npm test

# 测试覆盖率
bash scripts/test-coverage.sh
```

### 部署
```bash
# 部署到 WSL
bash scripts/deploy.sh

# 部署测试
bash scripts/test-deploy.sh

# 冒烟测试
python scripts/smoke-test.py
```

### 迭代
```bash
# 初始化
bash scripts/iterate.sh init

# 运行迭代
bash scripts/iterate.sh run

# 查看状态
bash scripts/iterate.sh status
```

---

## 下一步

1. **批准计划** - 用户确认计划
2. **开始执行** - 从阶段 1 开始
3. **定期检查** - 每个阶段完成后验收
4. **持续迭代** - 阶段 4 完成后进入自动迭代
