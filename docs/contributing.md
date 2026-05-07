# 贡献指南

感谢您对 mdserver-web 项目的关注！本文档将指导您如何为项目做出贡献。

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请通过 GitHub Issues 提交:

1. 访问 [Issues 页面](https://github.com/midoks/mdserver-web/issues)
2. 搜索是否已有相关问题
3. 如果没有，点击 "New Issue" 创建新问题
4. 填写问题模板，提供详细信息

### 问题报告模板

```markdown
## 问题描述
简要描述问题

## 复现步骤
1. 第一步
2. 第二步
3. ...

## 期望行为
描述您期望的行为

## 实际行为
描述实际发生的行为

## 环境信息
- 操作系统: CentOS 7.9
- Python 版本: 3.8.10
- 面板版本: 0.18.5

## 日志信息
```
粘贴相关日志
```

## 截图
如果适用，添加截图帮助说明
```

## 提交代码

### 1. Fork 项目

点击项目页面右上角的 "Fork" 按钮，将项目复制到您的 GitHub 账号。

### 2. 克隆代码

```bash
git clone https://github.com/your-username/mdserver-web.git
cd mdserver-web
```

### 3. 创建分支

```bash
# 创建并切换到新分支
git checkout -b feature/your-feature-name

# 或修复 bug
git checkout -b fix/your-bug-fix
```

### 4. 修改代码

进行您的修改，确保:
- 代码风格一致
- 添加必要的注释
- 不引入新的 bug

### 5. 测试修改

```bash
# 启动面板测试
bash cli.sh debug

# 测试您的修改是否正常工作
```

### 6. 提交更改

```bash
# 添加修改的文件
git add .

# 提交更改
git commit -m "feat: 添加新功能描述"

# 推送到您的 Fork
git push origin feature/your-feature-name
```

### 7. 创建 Pull Request

1. 访问您的 Fork 页面
2. 点击 "New Pull Request"
3. 填写 PR 描述
4. 等待审核

## Commit 规范

使用语义化提交信息:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复 bug |
| docs | 文档更新 |
| style | 代码格式调整 (不影响功能) |
| refactor | 重构 (不是新功能也不是修复) |
| perf | 性能优化 |
| test | 测试相关 |
| chore | 构建/工具相关 |

### 示例

```bash
# 新功能
git commit -m "feat(plugins): 添加插件自动更新功能"

# 修复 bug
git commit -m "fix(login): 修复验证码验证失败问题"

# 文档更新
git commit -m "docs: 更新插件开发文档"

# 重构
git commit -m "refactor(core): 重构数据库连接模块"
```

## 代码规范

### Python 代码风格

遵循 PEP 8 规范:

```python
# 使用 4 空格缩进
def my_function():
    pass

# 类名使用驼峰命名
class MyClass:
    pass

# 函数和变量使用下划线命名
def my_function():
    my_variable = 1

# 常量使用大写
MY_CONSTANT = 100
```

### 命名规范

```python
# 模块名: 小写 + 下划线
my_module.py

# 类名: 驼峰命名
class MyPlugin:

# 函数名: 小写 + 下划线
def get_plugin_list():

# 常量: 大写 + 下划线
MAX_RETRY_COUNT = 3
```

### 注释规范

```python
def get_sites_list(page=1, size=10):
    """
    获取站点列表

    Args:
        page (int): 页码，默认 1
        size (int): 每页数量，默认 10

    Returns:
        dict: 包含站点列表的字典
            - list (list): 站点列表
            - count (int): 总数
    """
    pass
```

### 文件头部

每个 Python 文件应包含标准头部:

```python
# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------
```

## 开发环境

### 1. 搭建开发环境

```bash
# 克隆代码
git clone https://github.com/midoks/mdserver-web.git
cd mdserver-web

# 创建虚拟环境 (可选)
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip3 install -r requirements.txt

# 启动调试模式
bash cli.sh debug
```

### 2. 项目结构

```
mdserver-web/
├── web/                    # Web 应用
│   ├── app.py             # 入口
│   ├── admin/             # 后台模块
│   ├── core/              # 核心库
│   ├── thisdb/            # 数据库操作
│   ├── utils/             # 工具库
│   └── templates/         # 模板
├── plugins/               # 插件
├── data/                  # 数据
├── logs/                  # 日志
└── cli.sh                 # 启动脚本
```

### 3. 添加新模块

1. 在 `web/admin/` 下创建模块目录
2. 创建 `__init__.py` 和路由文件
3. 在 `web/admin/submodules.py` 中注册蓝图

```python
# web/admin/mymodule/__init__.py
from flask import Blueprint

blueprint = Blueprint('mymodule', __name__, url_prefix='/mymodule')

@blueprint.route('/index')
def index():
    return 'My Module'
```

```python
# web/admin/submodules.py 中添加
from .mymodule import blueprint as MyModule

def get_submodules():
    return [
        # ... 其他模块
        MyModule,
    ]
```

## 提交插件

### 插件目录结构

```
plugins/
└── my_plugin/
    ├── info.json          # 必需
    ├── index.py           # 必需
    ├── index.html         # 必需
    ├── install.sh         # 必需
    ├── ico.png            # 推荐
    ├── init.d/            # 推荐
    ├── conf/              # 按需
    └── js/                # 按需
```

### 插件提交要求

1. **info.json**: 完整填写插件信息
2. **index.py**: 实现标准接口函数
3. **install.sh**: 实现安装/卸载逻辑
4. **index.html**: 提供管理界面
5. **测试**: 确保插件可正常安装运行

## 文档贡献

### 文档目录

```
docs/
├── architecture.md        # 项目架构
├── deployment.md          # 部署文档
├── contributing.md        # 贡献指南
├── api/                   # API 文档
│   ├── dashboard.md
│   └── files.md
└── plugins/               # 插件文档
    └── getting-started.md
```

### 文档编写规范

1. 使用中文编写
2. 使用 Markdown 格式
3. 代码示例要完整可运行
4. 保持文档与代码同步更新

## 版本发布

### 版本号规则

采用语义化版本: `主版本.次版本.修订号`

- **主版本**: 不兼容的 API 变更
- **次版本**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

当前版本: `0.18.5`

### 发布流程

1. 更新 `web/version.py` 中的版本号
2. 更新 `CHANGELOG.md`
3. 创建 Git Tag
4. 发布 Release

## 社区

### 交流渠道

- GitHub Issues: 问题反馈和功能建议
- GitHub Discussions: 技术交流和讨论

### 行为准则

- 尊重他人
- 友善交流
- 建设性反馈
- 专注于技术讨论

## 常见问题

### Q: 如何快速开始开发?

A: 使用 `bash cli.sh debug` 启动调试模式，代码修改后会自动重载。

### Q: 如何调试插件?

A: 插件通过 `/plugins/run` 接口调用，可以在 `index.py` 中添加 print 输出调试信息。

### Q: 数据库如何操作?

A: 使用 `thisdb/` 模块中的函数，或直接使用 `mw.M('table_name')` 进行查询。

### Q: 如何添加新的 API 接口?

A: 在对应的 Blueprint 模块中添加路由函数，使用 `@panel_login_required` 装饰器进行认证。

## 致谢

感谢所有为 mdserver-web 做出贡献的开发者！

[![Contributors](https://contributors-img.web.app/image?repo=midoks/mdserver-web)](https://github.com/midoks/mdserver-web/graphs/contributors)
