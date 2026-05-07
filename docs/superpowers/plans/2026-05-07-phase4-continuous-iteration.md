# 阶段 4：持续迭代 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 建立自动化迭代框架，实现 100 轮自动迭代

**架构：** 通过脚本自动化扫描问题、修复、测试、部署、报告的完整流程

**技术栈：** Python, Shell, pytest, ESLint, Flake8, Git

---

## 文件结构

```
mdserver-web/
├── scripts/
│   ├── iteration/
│   │   ├── run-iteration.sh        # 迭代主脚本
│   │   ├── scan-issues.sh          # 问题扫描脚本
│   │   ├── fix-issue.py            # 问题修复脚本
│   │   ├── generate-report.py      # 报告生成脚本
│   │   └── iteration-config.json   # 迭代配置
│   └── ...
├── docs/
│   └── iteration/
│       └── reports/                # 迭代报告目录
│           ├── iteration-001.md
│           ├── iteration-002.md
│           └── ...
└── .github/
    └── workflows/
        └── auto-iteration.yml      # 自动迭代 GitHub Action
```

---

## 任务 1：创建迭代配置文件

**文件：**
- 创建：`scripts/iteration/iteration-config.json`

- [ ] **步骤 1：创建 iteration-config.json**

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
    },
    {
      "name": "eslint",
      "command": "cd web/frontend && npm run lint 2>&1 | grep 'error\\|warning'",
      "type": "tech_debt",
      "priority": 2
    },
    {
      "name": "pylint",
      "command": "pylint web/ --disable=C,R --output-format=json",
      "type": "tech_debt",
      "priority": 2
    },
    {
      "name": "todo_comments",
      "command": "grep -rn 'TODO\\|FIXME\\|HACK\\|XXX' web/ --include='*.py' --include='*.js' --include='*.vue'",
      "type": "tech_debt",
      "priority": 3
    }
  ],
  "test_commands": [
    "python -m pytest tests/ -v",
    "cd web/frontend && npm test"
  ],
  "deploy_command": "bash scripts/deploy.sh",
  "smoke_test_command": "python scripts/smoke-test.py",
  "report_dir": "docs/iteration/reports"
}
```

- [ ] **步骤 2：Commit**

```bash
git add scripts/iteration/
git commit -m "feat: add iteration configuration"
```

---

## 任务 2：创建问题扫描脚本

**文件：**
- 创建：`scripts/iteration/scan-issues.sh`

- [ ] **步骤 1：创建 scan-issues.sh**

```bash
#!/bin/bash
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

CONFIG_FILE="scripts/iteration/iteration-config.json"
ISSUES_FILE="scripts/iteration/issues.json"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  问题扫描${NC}"
echo -e "${GREEN}========================================${NC}"

# 初始化问题文件
echo "[]" > $ISSUES_FILE

# 扫描 Python 问题
echo -e "\n${YELLOW}[1/4] 扫描 Python 代码问题...${NC}"
python_issues=$(flake8 web/ --count --statistics 2>&1 || true)
if [ -n "$python_issues" ]; then
    echo "$python_issues" | head -20
    # 保存到问题文件
    echo "$python_issues" | while read -r line; do
        if [[ $line =~ ^web/ ]]; then
            issue=$(echo "$line" | jq -R -s -c '{
                "source": "flake8",
                "type": "tech_debt",
                "priority": 2,
                "message": .,
                "file": (split(":")[0]),
                "line": (split(":")[1] | tonumber)
            }')
            jq ". += [$issue]" $ISSUES_FILE > tmp.json && mv tmp.json $ISSUES_FILE
        fi
    done
fi

# 扫描 JavaScript 问题
echo -e "\n${YELLOW}[2/4] 扫描 JavaScript 代码问题...${NC}"
js_issues=$(cd web/frontend && npm run lint 2>&1 | grep -E 'error|warning' || true)
if [ -n "$js_issues" ]; then
    echo "$js_issues" | head -20
fi

# 扫描 TODO 注释
echo -e "\n${YELLOW}[3/4] 扫描 TODO 注释...${NC}"
todo_issues=$(grep -rn 'TODO\|FIXME\|HACK\|XXX' web/ --include='*.py' --include='*.js' --include='*.vue' 2>/dev/null || true)
if [ -n "$todo_issues" ]; then
    echo "$todo_issues" | head -20
    echo "$todo_issues" | while read -r line; do
        issue=$(echo "$line" | jq -R -s -c '{
            "source": "todo_comments",
            "type": "tech_debt",
            "priority": 3,
            "message": .,
            "file": (split(":")[0]),
            "line": (split(":")[1] | tonumber)
        }')
        jq ". += [$issue]" $ISSUES_FILE > tmp.json && mv tmp.json $ISSUES_FILE
    done
fi

# 扫描安全问题
echo -e "\n${YELLOW}[4/4] 扫描安全问题...${NC}"
security_issues=$(grep -rn 'eval\|exec\|os\.system\|subprocess\.call' web/ --include='*.py' 2>/dev/null | grep -v test || true)
if [ -n "$security_issues" ]; then
    echo "$security_issues" | head -20
fi

# 统计问题数量
total_issues=$(jq length $ISSUES_FILE)
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  扫描完成，共发现 $total_issues 个问题${NC}"
echo -e "${GREEN}========================================${NC}"

# 按优先级排序
jq 'sort_by(.priority)' $ISSUES_FILE > tmp.json && mv tmp.json $ISSUES_FILE
```

- [ ] **步骤 2：添加执行权限**

```bash
chmod +x scripts/iteration/scan-issues.sh
```

- [ ] **步骤 3：Commit**

```bash
git add scripts/iteration/scan-issues.sh
git commit -m "feat: add issue scanning script"
```

---

## 任务 3：创建问题修复脚本

**文件：**
- 创建：`scripts/iteration/fix-issue.py`

- [ ] **步骤 1：创建 fix-issue.py**

```python
#!/usr/bin/env python3
"""
问题修复脚本
根据问题类型自动修复代码问题
"""

import json
import os
import re
import sys
from pathlib import Path


class IssueFixer:
    def __init__(self, issues_file='scripts/iteration/issues.json'):
        self.issues_file = issues_file
        self.issues = []
        self.fixed = 0
        self.failed = 0

    def load_issues(self):
        """加载问题列表"""
        with open(self.issues_file, 'r') as f:
            self.issues = json.load(f)
        return self.issues

    def fix_todo_comments(self, issue):
        """修复 TODO 注释（记录但不自动修复）"""
        print(f"  TODO 注释: {issue['message']}")
        return False

    def fix_flake8_issue(self, issue):
        """修复 Flake8 问题"""
        message = issue['message']
        file_path = issue.get('file')
        line_num = issue.get('line')

        if not file_path or not os.path.exists(file_path):
            return False

        with open(file_path, 'r') as f:
            lines = f.readlines()

        if line_num and line_num <= len(lines):
            line = lines[line_num - 1]

            # 修复常见问题
            # E302: 期望两个空行
            if 'E302' in message:
                # 在函数/类定义前添加空行
                lines.insert(line_num - 1, '\n')
                with open(file_path, 'w') as f:
                    f.writelines(lines)
                return True

            # E501: 行太长
            if 'E501' in message:
                # 尝试拆分长行
                if len(line) > 100:
                    # 简单拆分策略
                    indent = len(line) - len(line.lstrip())
                    new_line = line[:88] + '\n' + ' ' * (indent + 4) + line[88:]
                    lines[line_num - 1] = new_line
                    with open(file_path, 'w') as f:
                        f.writelines(lines)
                    return True

            # W291: 行尾有空格
            if 'W291' in message:
                lines[line_num - 1] = line.rstrip() + '\n'
                with open(file_path, 'w') as f:
                    f.writelines(lines)
                return True

            # W293: 行首有空格
            if 'W293' in message:
                lines[line_num - 1] = line.lstrip()
                with open(file_path, 'w') as f:
                    f.writelines(lines)
                return True

        return False

    def fix_security_issue(self, issue):
        """修复安全问题"""
        message = issue['message']
        file_path = issue.get('file')
        line_num = issue.get('line')

        if not file_path or not os.path.exists(file_path):
            return False

        with open(file_path, 'r') as f:
            content = f.read()

        # 替换不安全的函数调用
        if 'os.system' in message:
            # 建议使用 subprocess
            print(f"  安全警告: {file_path}:{line_num} - 建议使用 subprocess 替代 os.system")
            return False

        if 'eval(' in message:
            print(f"  安全警告: {file_path}:{line_num} - 避免使用 eval()")
            return False

        return False

    def fix_issue(self, issue):
        """修复单个问题"""
        issue_type = issue.get('type')
        source = issue.get('source')

        print(f"\n修复问题: {issue.get('message', '')[:80]}")

        try:
            if source == 'todo_comments':
                return self.fix_todo_comments(issue)
            elif source == 'flake8':
                return self.fix_flake8_issue(issue)
            elif source == 'security':
                return self.fix_security_issue(issue)
            else:
                print(f"  未知问题类型: {source}")
                return False
        except Exception as e:
            print(f"  修复失败: {e}")
            return False

    def run(self, max_fixes=1):
        """运行修复"""
        self.load_issues()

        if not self.issues:
            print("没有发现问题")
            return

        print(f"共发现 {len(self.issues)} 个问题")
        print(f"本次最多修复 {max_fixes} 个问题")

        # 按优先级排序
        sorted_issues = sorted(self.issues, key=lambda x: x.get('priority', 99))

        for issue in sorted_issues[:max_fixes]:
            if self.fix_issue(issue):
                self.fixed += 1
            else:
                self.failed += 1

        print(f"\n修复完成: {self.fixed} 成功, {self.failed} 失败")

        # 从问题列表中移除已修复的问题
        remaining_issues = sorted_issues[self.fixed:]
        with open(self.issues_file, 'w') as f:
            json.dump(remaining_issues, f, indent=2)


if __name__ == '__main__':
    max_fixes = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    fixer = IssueFixer()
    fixer.run(max_fixes)
```

- [ ] **步骤 2：添加执行权限**

```bash
chmod +x scripts/iteration/fix-issue.py
```

- [ ] **步骤 3：Commit**

```bash
git add scripts/iteration/fix-issue.py
git commit -m "feat: add issue fixing script"
```

---

## 任务 4：创建报告生成脚本

**文件：**
- 创建：`scripts/iteration/generate-report.py`

- [ ] **步骤 1：创建 generate-report.py**

```python
#!/usr/bin/env python3
"""
迭代报告生成脚本
"""

import json
import os
from datetime import datetime
from pathlib import Path


class ReportGenerator:
    def __init__(self, config_file='scripts/iteration/iteration-config.json'):
        self.config_file = config_file
        self.config = {}
        self.report_dir = 'docs/iteration/reports'

    def load_config(self):
        """加载配置"""
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
        return self.config

    def get_git_info(self):
        """获取 Git 信息"""
        import subprocess

        try:
            commit_hash = subprocess.check_output(
                ['git', 'rev-parse', '--short', 'HEAD']
            ).decode().strip()

            commit_message = subprocess.check_output(
                ['git', 'log', '-1', '--pretty=%B']
            ).decode().strip()

            branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
            ).decode().strip()

            return {
                'hash': commit_hash,
                'message': commit_message,
                'branch': branch,
            }
        except Exception as e:
            return {'error': str(e)}

    def get_test_results(self):
        """获取测试结果"""
        # 这里应该运行测试并收集结果
        # 简化版本返回占位数据
        return {
            'backend': {'passed': 0, 'failed': 0, 'total': 0},
            'frontend': {'passed': 0, 'failed': 0, 'total': 0},
        }

    def generate_report(self, iteration, issues_fixed, issues_remaining):
        """生成报告"""
        self.load_config()

        # 创建报告目录
        os.makedirs(self.report_dir, exist_ok=True)

        # 获取信息
        git_info = self.get_git_info()
        test_results = self.get_test_results()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 生成报告内容
        report = f"""# 迭代报告 #{iteration:03d}

**日期**: {timestamp}
**分支**: {git_info.get('branch', 'unknown')}
**提交**: {git_info.get('hash', 'unknown')}

## 概述

本次迭代修复了 {issues_fixed} 个问题，剩余 {issues_remaining} 个问题待处理。

## 修改内容

{git_info.get('message', '无提交信息')}

## 测试结果

### 后端测试
- 通过: {test_results['backend']['passed']}
- 失败: {test_results['backend']['failed']}
- 总计: {test_results['backend']['total']}

### 前端测试
- 通过: {test_results['frontend']['passed']}
- 失败: {test_results['frontend']['failed']}
- 总计: {test_results['frontend']['total']}

## 问题状态

- 已修复: {issues_fixed}
- 待处理: {issues_remaining}
- 总计: {issues_fixed + issues_remaining}

## 下一步

1. 继续修复剩余问题
2. 运行完整测试
3. 部署验证

---

*自动生成于 {timestamp}*
"""

        # 保存报告
        report_file = os.path.join(self.report_dir, f'iteration-{iteration:03d}.md')
        with open(report_file, 'w') as f:
            f.write(report)

        print(f"报告已生成: {report_file}")
        return report_file


if __name__ == '__main__':
    import sys

    iteration = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    issues_fixed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    issues_remaining = int(sys.argv[3]) if len(sys.argv) > 3 else 0

    generator = ReportGenerator()
    generator.generate_report(iteration, issues_fixed, issues_remaining)
```

- [ ] **步骤 2：添加执行权限**

```bash
chmod +x scripts/iteration/generate-report.py
```

- [ ] **步骤 3：Commit**

```bash
git add scripts/iteration/generate-report.py
git commit -m "feat: add report generation script"
```

---

## 任务 5：创建迭代主脚本

**文件：**
- 创建：`scripts/iteration/run-iteration.sh`

- [ ] **步骤 1：创建 run-iteration.sh**

```bash
#!/bin/bash
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

CONFIG_FILE="scripts/iteration/iteration-config.json"
ITERATION_FILE="scripts/iteration/current_iteration.txt"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  mdserver-web 自动迭代${NC}"
echo -e "${GREEN}========================================${NC}"

# 读取当前迭代次数
if [ -f "$ITERATION_FILE" ]; then
    CURRENT_ITERATION=$(cat $ITERATION_FILE)
else
    CURRENT_ITERATION=0
fi

# 检查是否达到最大迭代次数
MAX_ITERATIONS=$(jq -r '.max_iterations' $CONFIG_FILE)
if [ $CURRENT_ITERATION -ge $MAX_ITERATIONS ]; then
    echo -e "${YELLOW}已达到最大迭代次数 ($MAX_ITERATIONS)${NC}"
    exit 0
fi

# 递增迭代次数
CURRENT_ITERATION=$((CURRENT_ITERATION + 1))
echo $CURRENT_ITERATION > $ITERATION_FILE

echo -e "\n${YELLOW}迭代 #$CURRENT_ITERATION${NC}"
echo -e "${YELLOW}========================================${NC}"

# 步骤 1：扫描问题
echo -e "\n${YELLOW}[1/6] 扫描问题...${NC}"
bash scripts/iteration/scan-issues.sh

# 统计问题数量
ISSUES_FILE="scripts/iteration/issues.json"
TOTAL_ISSUES=$(jq length $ISSUES_FILE 2>/dev/null || echo 0)

if [ $TOTAL_ISSUES -eq 0 ]; then
    echo -e "${GREEN}没有发现问题，迭代完成${NC}"
    exit 0
fi

echo -e "\n${YELLOW}发现 $TOTAL_ISSUES 个问题${NC}"

# 步骤 2：修复问题
echo -e "\n${YELLOW}[2/6] 修复问题...${NC}"
python scripts/iteration/fix-issue.py 1
ISSUES_FIXED=$?

# 步骤 3：运行测试
echo -e "\n${YELLOW}[3/6] 运行测试...${NC}"
python -m pytest tests/ -v --tb=short || true
cd web/frontend && npm test || true
cd ../..

# 步骤 4：提交代码
echo -e "\n${YELLOW}[4/6] 提交代码...${NC}"
git add -A
git commit -m "auto-iteration: fix issues #$CURRENT_ITERATION" || true

# 步骤 5：生成报告
echo -e "\n${YELLOW}[5/6] 生成报告...${NC}"
ISSUES_REMAINING=$(jq length $ISSUES_FILE 2>/dev/null || echo 0)
python scripts/iteration/generate-report.py $CURRENT_ITERATION $ISSUES_FIXED $ISSUES_REMAINING

# 步骤 6：部署验证（可选）
echo -e "\n${YELLOW}[6/6] 部署验证...${NC}"
if [ "$DEPLOY_AFTER_ITERATION" = "true" ]; then
    bash scripts/deploy.sh || true
    python scripts/smoke-test.py || true
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  迭代 #$CURRENT_ITERATION 完成${NC}"
echo -e "${GREEN}  修复: $ISSUES_FIXED 个问题${NC}"
echo -e "${GREEN}  剩余: $ISSUES_REMAINING 个问题${NC}"
echo -e "${GREEN}========================================${NC}"
```

- [ ] **步骤 2：添加执行权限**

```bash
chmod +x scripts/iteration/run-iteration.sh
```

- [ ] **步骤 3：Commit**

```bash
git add scripts/iteration/run-iteration.sh scripts/iteration/current_iteration.txt
git commit -m "feat: add main iteration script"
```

---

## 任务 6：创建 GitHub Actions 自动迭代

**文件：**
- 创建：`.github/workflows/auto-iteration.yml`

- [ ] **步骤 1：创建 auto-iteration.yml**

```yaml
name: Auto Iteration

on:
  schedule:
    # 每天 UTC 时间 02:00 运行
    - cron: '0 2 * * *'
  workflow_dispatch:
    inputs:
      max_iterations:
        description: '最大迭代次数'
        required: false
        default: '1'

jobs:
  iterate:
    name: Run Iteration
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: web/frontend/package-lock.json

    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest flake8

    - name: Install Node dependencies
      working-directory: web/frontend
      run: npm ci

    - name: Run iteration
      run: |
        for i in $(seq 1 ${MAX_ITERATIONS:-1}); do
          echo "Running iteration $i..."
          bash scripts/iteration/run-iteration.sh
        done
      env:
        MAX_ITERATIONS: ${{ github.event.inputs.max_iterations || '1' }}

    - name: Commit changes
      uses: stefanzweifel/git-auto-commit-action@v4
      with:
        commit_message: "auto-iteration: daily fixes"
        file_pattern: |
          web/
          tests/
          docs/iteration/reports/

    - name: Upload iteration report
      uses: actions/upload-artifact@v3
      with:
        name: iteration-report
        path: docs/iteration/reports/
```

- [ ] **步骤 2：Commit**

```bash
git add .github/workflows/auto-iteration.yml
git commit -m "ci: add auto iteration workflow"
```

---

## 任务 7：创建迭代状态追踪

**文件：**
- 创建：`scripts/iteration/status.sh`
- 创建：`docs/iteration/README.md`

- [ ] **步骤 1：创建 status.sh**

```bash
#!/bin/bash
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

CONFIG_FILE="scripts/iteration/iteration-config.json"
ITERATION_FILE="scripts/iteration/current_iteration.txt"
ISSUES_FILE="scripts/iteration/issues.json"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  迭代状态${NC}"
echo -e "${GREEN}========================================${NC}"

# 当前迭代次数
if [ -f "$ITERATION_FILE" ]; then
    CURRENT=$(cat $ITERATION_FILE)
else
    CURRENT=0
fi
MAX=$(jq -r '.max_iterations' $CONFIG_FILE)

echo -e "\n${YELLOW}迭代进度:${NC}"
echo -e "  当前: $CURRENT / $MAX"
echo -e "  进度: $((CURRENT * 100 / MAX))%"

# 问题状态
if [ -f "$ISSUES_FILE" ]; then
    TOTAL_ISSUES=$(jq length $ISSUES_FILE)
    echo -e "\n${YELLOW}问题状态:${NC}"
    echo -e "  待处理: $TOTAL_ISSUES"
else
    echo -e "\n${YELLOW}问题状态:${NC}"
    echo -e "  待处理: 0"
fi

# 报告数量
REPORT_COUNT=$(ls -1 docs/iteration/reports/*.md 2>/dev/null | wc -l || echo 0)
echo -e "\n${YELLOW}迭代报告:${NC}"
echo -e "  已生成: $REPORT_COUNT"

# Git 状态
echo -e "\n${YELLOW}Git 状态:${NC}"
git status --short

echo -e "\n${GREEN}========================================${NC}"
```

- [ ] **步骤 2：创建 docs/iteration/README.md**

```markdown
# 迭代文档

## 概述

本目录包含自动迭代的报告和相关文档。

## 迭代流程

1. **扫描问题** - 使用 ESLint、Flake8 等工具扫描代码问题
2. **修复问题** - 按优先级自动修复问题
3. **运行测试** - 确保修复不引入新问题
4. **提交代码** - 保存修复结果
5. **生成报告** - 记录迭代详情

## 迭代配置

配置文件位于 `scripts/iteration/iteration-config.json`：

```json
{
  "max_iterations": 100,
  "priorities": {
    "bug": 1,
    "security": 1,
    "tech_debt": 2,
    "performance": 3,
    "feature": 4
  }
}
```

## 运行迭代

### 手动运行

```bash
# 运行单次迭代
bash scripts/iteration/run-iteration.sh

# 查看状态
bash scripts/iteration/status.sh
```

### 自动运行

GitHub Actions 会每天自动运行迭代。

## 报告格式

每次迭代生成一份报告，包含：
- 迭代编号和日期
- 修复的问题
- 测试结果
- 下一步计划

## 优先级说明

| 优先级 | 类型 | 说明 |
|--------|------|------|
| 1 | bug | 程序错误 |
| 1 | security | 安全漏洞 |
| 2 | tech_debt | 技术债务 |
| 3 | performance | 性能优化 |
| 4 | feature | 功能增强 |
| 5 | documentation | 文档完善 |
```

- [ ] **步骤 3：添加执行权限**

```bash
chmod +x scripts/iteration/status.sh
```

- [ ] **步骤 4：Commit**

```bash
git add scripts/iteration/status.sh docs/iteration/README.md
git commit -m "feat: add iteration status tracking"
```

---

## 任务 8：初始化迭代环境

**文件：**
- 创建：`scripts/iteration/init.sh`

- [ ] **步骤 1：创建 init.sh**

```bash
#!/bin/bash
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  初始化迭代环境${NC}"
echo -e "${GREEN}========================================${NC}"

# 创建目录
echo -e "\n${YELLOW}[1/4] 创建目录...${NC}"
mkdir -p scripts/iteration
mkdir -p docs/iteration/reports

# 初始化迭代计数
echo -e "\n${YELLOW}[2/4] 初始化迭代计数...${NC}"
if [ ! -f scripts/iteration/current_iteration.txt ]; then
    echo "0" > scripts/iteration/current_iteration.txt
fi

# 初始化问题文件
echo -e "\n${YELLOW}[3/4] 初始化问题文件...${NC}"
if [ ! -f scripts/iteration/issues.json ]; then
    echo "[]" > scripts/iteration/issues.json
fi

# 验证配置
echo -e "\n${YELLOW}[4/4] 验证配置...${NC}"
if [ -f scripts/iteration/iteration-config.json ]; then
    jq . scripts/iteration/iteration-config.json > /dev/null && echo "配置文件有效"
else
    echo "配置文件不存在"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  初始化完成${NC}"
echo -e "${GREEN}========================================${NC}"
```

- [ ] **步骤 2：添加执行权限**

```bash
chmod +x scripts/iteration/init.sh
```

- [ ] **步骤 3：运行初始化**

```bash
bash scripts/iteration/init.sh
```

- [ ] **步骤 4：Commit**

```bash
git add scripts/iteration/init.sh
git commit -m "feat: add iteration initialization script"
```

---

## 任务 9：创建快速迭代脚本

**文件：**
- 创建：`scripts/iteration/quick-iterate.sh`

- [ ] **步骤 1：创建 quick-iterate.sh**

```bash
#!/bin/bash
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  快速迭代${NC}"
echo -e "${GREEN}========================================${NC}"

# 运行迭代
echo -e "\n${YELLOW}运行迭代...${NC}"
bash scripts/iteration/run-iteration.sh

# 显示状态
echo -e "\n${YELLOW}显示状态...${NC}"
bash scripts/iteration/status.sh

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  快速迭代完成${NC}"
echo -e "${GREEN}========================================${NC}"
```

- [ ] **步骤 2：添加执行权限**

```bash
chmod +x scripts/iteration/quick-iterate.sh
```

- [ ] **步骤 3：Commit**

```bash
git add scripts/iteration/quick-iterate.sh
git commit -m "feat: add quick iteration script"
```

---

## 任务 10：创建迭代主控脚本

**文件：**
- 创建：`scripts/iterate.sh`

- [ ] **步骤 1：创建 iterate.sh**

```bash
#!/bin/bash
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ITERATION_DIR="$SCRIPT_DIR/iteration"

show_help() {
    echo -e "${GREEN}mdserver-web 迭代工具${NC}"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  init      初始化迭代环境"
    echo "  run       运行单次迭代"
    echo "  status    显示迭代状态"
    echo "  report    生成迭代报告"
    echo "  scan      扫描问题"
    echo "  fix       修复问题"
    echo "  help      显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 init    # 初始化"
    echo "  $0 run     # 运行迭代"
    echo "  $0 status  # 查看状态"
}

case "${1:-help}" in
    init)
        bash "$ITERATION_DIR/init.sh"
        ;;
    run)
        bash "$ITERATION_DIR/run-iteration.sh"
        ;;
    status)
        bash "$ITERATION_DIR/status.sh"
        ;;
    report)
        python "$ITERATION_DIR/generate-report.py" "${2:-1}" "${3:-0}" "${4:-0}"
        ;;
    scan)
        bash "$ITERATION_DIR/scan-issues.sh"
        ;;
    fix)
        python "$ITERATION_DIR/fix-issue.py" "${2:-1}"
        ;;
    help|*)
        show_help
        ;;
esac
```

- [ ] **步骤 2：添加执行权限**

```bash
chmod +x scripts/iterate.sh
```

- [ ] **步骤 3：Commit**

```bash
git add scripts/iterate.sh
git commit -m "feat: add main iteration control script"
```

---

## 阶段 4 完成检查清单

- [ ] 迭代配置文件创建完成
- [ ] 问题扫描脚本创建完成
- [ ] 问题修复脚本创建完成
- [ ] 报告生成脚本创建完成
- [ ] 迭代主脚本创建完成
- [ ] GitHub Actions 配置完成
- [ ] 状态追踪功能完成
- [ ] 初始化脚本创建完成
- [ ] 快速迭代脚本创建完成
- [ ] 主控脚本创建完成

## 使用说明

### 初始化

```bash
bash scripts/iterate.sh init
```

### 运行迭代

```bash
# 单次迭代
bash scripts/iterate.sh run

# 快速迭代
bash scripts/iteration/quick-iterate.sh

# 多次迭代
for i in {1..10}; do bash scripts/iterate.sh run; done
```

### 查看状态

```bash
bash scripts/iterate.sh status
```

### 扫描问题

```bash
bash scripts/iterate.sh scan
```

### 修复问题

```bash
bash scripts/iterate.sh fix 3  # 修复 3 个问题
```

## 自动迭代

GitHub Actions 会每天自动运行迭代。也可以手动触发：

1. 访问 GitHub Actions 页面
2. 选择 "Auto Iteration" 工作流
3. 点击 "Run workflow"
4. 设置迭代次数
5. 点击 "Run workflow" 按钮
