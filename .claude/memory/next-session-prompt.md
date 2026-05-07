# 新 Session 启动提示词

复制以下内容到新 session 的 CLAUDE.md 或作为首条消息：

---

## Compass Panel 迭代开发 — 新Session启动

### 项目背景
compass-panel 是从 mdserver-web (midoks/mdserver-web) 深度改造的 Linux 服务器管理面板。目标是打造**超越宝塔面板**的完美产品。

### 当前状态
- 项目代码在 `H:\aicoding\compass-panel`
- Vue 3 前端已构建并可运行
- 后端 Flask + Gunicorn 在 WSL Debian 中运行
- 参考迭代计划: `docs/BAOTA_COMPARISON.md` (25阶段 S0-S25)
- 体验设计文档: `docs/EXPERIENCE_DESIGN.md`
- 品牌规范: `docs/BRAND.md`

### 立即要做的事
1. **修复已知Bug**:
   - 内存单位 "undefined" → 应显示 "GB"
   - 面板名称 "夸父面板" → "Compass 指南面板"
   - 版本号更新
   - admin_close 默认值改为 "no"

2. **开始 S0 数据层基础**:
   - SQLAlchemy 2.0 + WAL mode
   - 5库分离 (panel.db/security.db/monitor.db/task.db/log.db)
   - Fernet 字段加密
   - Alembic 迁移
   - Repository Pattern

3. **品牌改造**:
   - 所有页面标题、页脚、logo 改为 Compass 指南面板
   - CLI 工具: compass start/stop/status
   - 安装脚本: curl -sSL compass.run | bash

### 代码规范
- Python: PEP8 + Black (行宽88) + Flake8
- Vue: Composition API (`<script setup>`) + ESLint + Prettier
- 提交: `<type>(<scope>): <subject>` (feat/fix/docs/style/refactor/perf/test/chore)

### 迭代优先级
先做 S0（数据层），再做 S1-S4（核心功能），再做 S5-S9（运维功能），最后做 S10-S25（高级功能）。
每个阶段完成后提交到 GitHub。
