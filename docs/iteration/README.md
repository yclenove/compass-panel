# 自动迭代框架

自动化代码质量改进迭代框架，用于持续扫描、修复和报告项目中的代码问题。

## 目录结构

```
scripts/iterate.sh                    # 主控入口脚本
scripts/iteration/
  ├── iteration-config.json           # 迭代配置文件
  ├── scan-issues.sh                  # 问题扫描脚本
  ├── fix-issue.py                    # 问题自动修复脚本
  ├── generate-report.py              # 迭代报告生成脚本
  ├── run-iteration.sh                # 单次迭代执行脚本
  ├── status.sh                       # 迭代状态查看脚本
  └── init.sh                         # 环境初始化脚本
docs/iteration/
  ├── README.md                       # 本文档
  └── reports/                        # 迭代报告输出目录
```

## 快速开始

### 1. 初始化环境

```bash
bash scripts/iterate.sh init
```

初始化脚本会：
- 创建必要的目录结构
- 检查 Python3、flake8、git、pytest 等依赖
- 设置脚本可执行权限

### 2. 执行一次迭代

```bash
bash scripts/iterate.sh run
```

### 3. 查看当前状态

```bash
bash scripts/iterate.sh status
```

## 可用命令

| 命令 | 说明 |
|------|------|
| `init` | 初始化迭代环境 |
| `run` | 执行一次完整迭代 |
| `status` | 查看迭代状态 |
| `scan` | 仅扫描项目问题 |
| `fix` | 仅自动修复问题 |
| `report` | 仅生成迭代报告 |
| `help` | 显示帮助信息 |

## 迭代流程

每次迭代包含以下步骤：

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  扫描   │───▶│  修复   │───▶│  测试   │───▶│  提交   │───▶│  报告   │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

### 步骤 1: 扫描问题

运行 `scan-issues.sh` 扫描以下类型的问题：

- **flake8 检查**: 代码风格和质量问题
- **TODO/FIXME 注释**: 待处理的代码标记
- **安全检查**: 硬编码密码、eval、exec 等风险代码

扫描结果输出到 `scripts/iteration/issues.json`。

### 步骤 2: 自动修复

运行 `fix-issue.py` 自动修复可修复的问题。

支持修复的 flake8 规则：

| 规则 | 说明 |
|------|------|
| E301 | 嵌套定义前缺少空行 |
| E302 | 函数/类定义前缺少 2 个空行 |
| E303 | 空行过多 |
| E501 | 行过长（>120 字符） |
| E711 | 与 None 比较（应使用 is/is not） |
| E712 | 与 True/False 比较 |
| W291 | 行尾有多余空格 |
| W292 | 文件末尾缺少换行 |
| W293 | 冒号前有多余空格 |
| W391 | 文件末尾有多余空行 |

### 步骤 3: 运行测试

根据 `iteration-config.json` 中配置的测试命令运行测试。

### 步骤 4: 提交代码

将修复后的代码变更提交到 git。

### 步骤 5: 生成报告

在 `docs/iteration/reports/` 目录生成 Markdown 格式的迭代报告。

## 配置说明

配置文件: `scripts/iteration/iteration-config.json`

```json
{
  "version": "1.0.0",
  "max_iterations": 100,
  "current_iteration": 0,
  "priorities": {
    "bug": 1,
    "security": 1,
    "tech_debt": 2,
    "performance": 3,
    "feature": 4,
    "documentation": 5
  },
  "issue_sources": [
    {
      "name": "flake8",
      "command": "flake8 web/ --count --statistics",
      "type": "tech_debt",
      "priority": 2
    }
  ],
  "test_commands": [
    "python -m pytest tests/ -v"
  ],
  "report_dir": "docs/iteration/reports"
}
```

### 主要配置项

| 配置项 | 说明 |
|--------|------|
| `max_iterations` | 最大迭代次数 |
| `current_iteration` | 当前迭代编号（自动更新） |
| `priorities` | 问题类型优先级（数字越小优先级越高） |
| `issue_sources` | 问题扫描来源配置 |
| `test_commands` | 测试命令列表 |
| `report_dir` | 报告输出目录 |

## 问题优先级

| 优先级 | 类型 | 说明 |
|--------|------|------|
| 1 | bug, security | 最高优先级，立即修复 |
| 2 | tech_debt | 技术债务，尽快处理 |
| 3 | performance | 性能问题，计划处理 |
| 4 | feature | 功能需求，按计划实施 |
| 5 | documentation | 文档更新，低优先级 |

## 使用场景

### 场景 1: 日常代码质量改进

```bash
# 扫描并查看当前问题
bash scripts/iterate.sh scan
bash scripts/iterate.sh status

# 自动修复可修复的问题
bash scripts/iterate.sh fix

# 生成报告
bash scripts/iterate.sh report
```

### 场景 2: CI/CD 集成

```bash
# 在 CI 中执行完整迭代
bash scripts/iterate.sh run
```

### 场景 3: 定期质量审查

```bash
# 仅扫描和生成报告，不自动修复
bash scripts/iterate.sh scan
bash scripts/iterate.sh report
```

## 依赖要求

- Python 3.6+
- flake8（可选，用于代码质量检查）
- pytest（可选，用于运行测试）
- git（可选，用于代码提交）

安装 flake8:
```bash
pip install flake8
```

安装 pytest:
```bash
pip install pytest
```

## 注意事项

1. 自动修复仅处理明确的格式问题，不会改变代码逻辑
2. 安全扫描为简易检查，不能替代专业的安全审计工具
3. 建议在运行迭代前先备份代码或在分支上操作
4. 迭代报告会保存历史记录，便于追踪改进趋势
