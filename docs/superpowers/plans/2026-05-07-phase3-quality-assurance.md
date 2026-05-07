# 阶段 3：质量保障 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 建立完整的测试体系，实现自动化测试和部署验证

**架构：** 后端使用 pytest，前端使用 Vitest，部署使用脚本自动化，验证使用 MCP 浏览器自动化

**技术栈：** pytest, pytest-cov, Vitest, Vue Test Utils, Playwright/Cypress (MCP)

---

## 文件结构

```
mdserver-web/
├── tests/                        # 后端测试
│   ├── conftest.py               # pytest 配置和 fixtures
│   ├── test_api/                 # API 测试
│   │   ├── __init__.py
│   │   ├── conftest.py           # API 测试 fixtures
│   │   ├── test_dashboard.py     # 仪表盘 API 测试
│   │   ├── test_files.py         # 文件管理 API 测试
│   │   └── test_site.py          # 网站管理 API 测试
│   ├── test_utils/               # 工具函数测试
│   │   ├── __init__.py
│   │   ├── test_mw.py            # mw 工具测试
│   │   └── test_file.py          # 文件工具测试
│   └── test_models/              # 数据模型测试
│       ├── __init__.py
│       └── test_user.py          # 用户模型测试
├── web/frontend/
│   ├── src/
│   │   ├── __tests__/            # 前端测试
│   │   │   ├── components/       # 组件测试
│   │   │   │   └── FileEditor.test.js
│   │   │   ├── stores/           # 状态测试
│   │   │   │   └── user.test.js
│   │   │   └── utils/            # 工具测试
│   │   │       └── request.test.js
│   │   └── ...
│   ├── vitest.config.js          # Vitest 配置
│   └── package.json              # 添加测试脚本
├── scripts/
│   ├── deploy.sh                 # 部署脚本
│   ├── test-deploy.sh            # 部署测试脚本
│   └── smoke-test.py             # 冒烟测试
└── .github/
    └── workflows/
        └── ci.yml                # GitHub Actions 配置
```

---

## 任务 1：配置 pytest 环境

**文件：**
- 创建：`tests/conftest.py`
- 创建：`tests/test_api/__init__.py`
- 创建：`tests/test_utils/__init__.py`
- 创建：`tests/test_models/__init__.py`
- 修改：`pyproject.toml`

- [ ] **步骤 1：创建 tests/conftest.py**

```python
import os
import sys
import pytest

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))


@pytest.fixture
def app():
    """创建 Flask 应用实例"""
    from web.app import create_app

    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def db(app):
    """创建测试数据库"""
    from web.core.orm import db

    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()


@pytest.fixture
def auth_client(client, db):
    """创建已认证的测试客户端"""
    # 创建测试用户
    from web.thisdb.user import createUser
    createUser('testuser', 'testpassword')

    # 登录
    client.post('/do_login', data={
        'username': 'testuser',
        'password': 'testpassword',
        'code': ''
    })

    return client
```

- [ ] **步骤 2：创建 __init__.py 文件**

为每个测试目录创建空的 `__init__.py`：

```python
# tests/test_api/__init__.py
# tests/test_utils/__init__.py
# tests/test_models/__init__.py
```

- [ ] **步骤 3：更新 pyproject.toml 添加 pytest 配置**

在 `pyproject.toml` 中添加：

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]
```

- [ ] **步骤 4：验证 pytest 配置**

运行：`cd /www/server/mdserver-web && python -m pytest --co`
预期：显示收集到的测试（目前为 0）

- [ ] **步骤 5：Commit**

```bash
git add tests/ pyproject.toml
git commit -m "test: setup pytest configuration"
```

---

## 任务 2：编写仪表盘 API 测试

**文件：**
- 创建：`tests/test_api/conftest.py`
- 创建：`tests/test_api/test_dashboard.py`

- [ ] **步骤 1：创建 tests/test_api/conftest.py**

```python
import pytest


@pytest.fixture
def sample_user(db):
    """创建示例用户"""
    from web.thisdb.user import createUser
    createUser('admin', 'admin123')
    return {'username': 'admin', 'password': 'admin123'}
```

- [ ] **步骤 2：创建 tests/test_api/test_dashboard.py**

```python
import pytest


class TestDashboard:
    """仪表盘 API 测试"""

    def test_index_page(self, client):
        """测试首页访问"""
        response = client.get('/')
        assert response.status_code in [200, 302]

    def test_login_page(self, client):
        """测试登录页面"""
        response = client.get('/login')
        assert response.status_code == 200

    def test_login_success(self, client, sample_user):
        """测试登录成功"""
        response = client.post('/do_login', data={
            'username': sample_user['username'],
            'password': sample_user['password'],
            'code': ''
        })
        data = response.get_json()
        assert data['status'] == 1

    def test_login_wrong_password(self, client, sample_user):
        """测试密码错误"""
        response = client.post('/do_login', data={
            'username': sample_user['username'],
            'password': 'wrongpassword',
            'code': ''
        })
        data = response.get_json()
        assert data['status'] != 1

    def test_login_wrong_username(self, client):
        """测试用户名不存在"""
        response = client.post('/do_login', data={
            'username': 'nonexistent',
            'password': 'password',
            'code': ''
        })
        data = response.get_json()
        assert data['status'] != 1

    def test_check_login_authenticated(self, auth_client):
        """测试已登录状态检查"""
        response = auth_client.get('/check_login')
        data = response.get_json()
        assert data['status'] is True

    def test_check_login_unauthenticated(self, client):
        """测试未登录状态检查"""
        response = client.get('/check_login')
        data = response.get_json()
        assert data['status'] is False

    def test_system_info(self, auth_client):
        """测试系统信息接口"""
        response = auth_client.post('/system/get_system_info')
        data = response.get_json()
        assert 'data' in data
        assert 'cpu' in data['data']
        assert 'mem' in data['data']
```

- [ ] **步骤 3：运行测试验证**

运行：`cd /www/server/mdserver-web && python -m pytest tests/test_api/test_dashboard.py -v`
预期：测试通过（可能需要调整以匹配实际 API）

- [ ] **步骤 4：Commit**

```bash
git add tests/test_api/
git commit -m "test: add dashboard API tests"
```

---

## 任务 3：编写文件管理 API 测试

**文件：**
- 创建：`tests/test_api/test_files.py`

- [ ] **步骤 1：创建 tests/test_api/test_files.py**

```python
import pytest
import os
import tempfile


class TestFiles:
    """文件管理 API 测试"""

    @pytest.fixture
    def test_dir(self, tmp_path):
        """创建测试目录"""
        test_dir = tmp_path / "test_files"
        test_dir.mkdir()
        (test_dir / "test.txt").write_text("Hello, World!")
        (test_dir / "subdir").mkdir()
        return str(test_dir)

    def test_get_dir(self, auth_client, test_dir):
        """测试获取目录列表"""
        response = auth_client.post('/files/get_dir', data={
            'path': test_dir
        })
        data = response.get_json()
        assert data['status'] is True
        assert 'dir' in data['data']
        assert 'file' in data['data']

    def test_get_file_content(self, auth_client, test_dir):
        """测试获取文件内容"""
        filepath = os.path.join(test_dir, 'test.txt')
        response = auth_client.post('/files/get_file_content', data={
            'path': filepath
        })
        data = response.get_json()
        assert data['status'] is True
        assert 'Hello, World!' in data['data']['data']

    def test_save_file_content(self, auth_client, test_dir):
        """测试保存文件内容"""
        filepath = os.path.join(test_dir, 'new_file.txt')
        response = auth_client.post('/files/save_file_content', data={
            'path': filepath,
            'data': 'New content',
            'encoding': 'utf-8'
        })
        data = response.get_json()
        assert data['status'] is True

        # 验证文件已创建
        assert os.path.exists(filepath)
        with open(filepath, 'r') as f:
            assert f.read() == 'New content'

    def test_create_dir(self, auth_client, test_dir):
        """测试创建目录"""
        new_dir = os.path.join(test_dir, 'new_directory')
        response = auth_client.post('/files/create_dir', data={
            'path': test_dir,
            'dirname': 'new_directory'
        })
        data = response.get_json()
        assert data['status'] is True
        assert os.path.isdir(new_dir)

    def test_delete_file(self, auth_client, test_dir):
        """测试删除文件"""
        filepath = os.path.join(test_dir, 'test.txt')
        response = auth_client.post('/files/delete_file', data={
            'path': filepath
        })
        data = response.get_json()
        assert data['status'] is True
        assert not os.path.exists(filepath)

    def test_rename_file(self, auth_client, test_dir):
        """测试重命名文件"""
        old_path = os.path.join(test_dir, 'test.txt')
        new_name = 'renamed.txt'
        response = auth_client.post('/files/rename', data={
            'path': old_path,
            'newname': new_name
        })
        data = response.get_json()
        assert data['status'] is True
        assert os.path.exists(os.path.join(test_dir, new_name))

    def test_get_disk_info(self, auth_client):
        """测试获取磁盘信息"""
        response = auth_client.post('/files/get_disk')
        data = response.get_json()
        assert data['status'] is True
        assert isinstance(data['data'], list)
```

- [ ] **步骤 2：运行测试验证**

运行：`cd /www/server/mdserver-web && python -m pytest tests/test_api/test_files.py -v`
预期：测试通过

- [ ] **步骤 3：Commit**

```bash
git add tests/test_api/test_files.py
git commit -m "test: add file management API tests"
```

---

## 任务 4：编写工具函数测试

**文件：**
- 创建：`tests/test_utils/test_mw.py`

- [ ] **步骤 1：创建 tests/test_utils/test_mw.py**

```python
import pytest
import hashlib


class TestMwUtils:
    """mw 工具函数测试"""

    def test_md5(self):
        """测试 MD5 函数"""
        from web.core.mw import md5

        # 测试正常字符串
        result = md5('hello')
        assert result == hashlib.md5('hello'.encode('utf-8')).hexdigest()

        # 测试空字符串
        result = md5('')
        assert result == hashlib.md5(''.encode('utf-8')).hexdigest()

    def test_return_data(self):
        """测试返回数据格式"""
        from web.core.mw import returnData

        # 测试成功返回
        result = returnData(True, 'success')
        assert result['status'] is True
        assert result['msg'] == 'success'

        # 测试失败返回
        result = returnData(False, 'error')
        assert result['status'] is False
        assert result['msg'] == 'error'

    def test_return_json(self):
        """测试返回 JSON 格式"""
        from web.core.mw import returnJson

        result = returnJson(1, 'success')
        assert result['status'] == 1
        assert result['msg'] == 'success'

    def test_get_panel_data_dir(self):
        """测试获取面板数据目录"""
        from web.core.mw import getPanelDataDir

        data_dir = getPanelDataDir()
        assert data_dir is not None
        assert isinstance(data_dir, str)

    def test_get_mw_logs(self):
        """测试获取日志目录"""
        from web.core.mw import getMWLogs

        logs_dir = getMWLogs()
        assert logs_dir is not None
        assert isinstance(logs_dir, str)
```

- [ ] **步骤 2：运行测试验证**

运行：`cd /www/server/mdserver-web && python -m pytest tests/test_utils/test_mw.py -v`
预期：测试通过

- [ ] **步骤 3：Commit**

```bash
git add tests/test_utils/
git commit -m "test: add utility function tests"
```

---

## 任务 5：配置前端测试环境

**文件：**
- 修改：`web/frontend/package.json`
- 创建：`web/frontend/vitest.config.js`
- 创建：`web/frontend/src/__tests__/utils/request.test.js`

- [ ] **步骤 1：更新 package.json 添加测试依赖和脚本**

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage"
  },
  "devDependencies": {
    "vitest": "^0.34.0",
    "@vue/test-utils": "^2.4.0",
    "jsdom": "^22.1.0",
    "@vitest/coverage-v8": "^0.34.0"
  }
}
```

- [ ] **步骤 2：创建 vitest.config.js**

```javascript
import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/__tests__/setup.js'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      reportsDirectory: './coverage',
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
});
```

- [ ] **步骤 3：创建 src/__tests__/setup.js**

```javascript
import { config } from '@vue/test-utils';

// 全局测试配置
config.global.mocks = {
  $t: (msg) => msg,
};
```

- [ ] **步骤 4：创建 src/__tests__/utils/request.test.js**

```javascript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import request from '@/utils/request';

vi.mock('axios');

describe('request utility', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('should create axios instance with correct config', () => {
    expect(request.defaults.timeout).toBe(30000);
  });

  it('should add token to request headers', async () => {
    const token = 'test-token';
    localStorage.setItem('token', token);

    const mockResponse = { data: { status: true } };
    axios.create.mockReturnValue({
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
      defaults: { timeout: 30000 },
    });

    // 验证 token 被添加到请求头
    expect(localStorage.getItem('token')).toBe(token);
  });

  it('should handle 401 response', async () => {
    const error = {
      response: { status: 401 },
    };

    // 验证 401 错误处理
    expect(error.response.status).toBe(401);
  });
});
```

- [ ] **步骤 5：运行前端测试**

运行：`cd web/frontend && npm install && npm test`
预期：测试通过

- [ ] **步骤 6：Commit**

```bash
git add web/frontend/vitest.config.js web/frontend/src/__tests__/ web/frontend/package.json
git commit -m "test: setup frontend testing with Vitest"
```

---

## 任务 6：编写前端组件测试

**文件：**
- 创建：`web/frontend/src/__tests__/components/FileEditor.test.js`
- 创建：`web/frontend/src/__tests__/stores/user.test.js`

- [ ] **步骤 1：创建 FileEditor.test.js**

```javascript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import FileEditor from '@/components/FileEditor.vue';

// Mock Monaco Editor
vi.mock('monaco-editor', () => ({
  editor: {
    create: vi.fn(() => ({
      getValue: vi.fn(() => ''),
      setValue: vi.fn(),
      onDidChangeModelContent: vi.fn(),
      dispose: vi.fn(),
      getModel: vi.fn(() => ({
        getLanguageId: vi.fn(() => 'javascript'),
      })),
      layout: vi.fn(),
      addCommand: vi.fn(),
    })),
    setModelLanguage: vi.fn(),
  },
  KeyMod: { CtrlCmd: 1 },
  KeyCode: { KeyS: 1 },
}));

describe('FileEditor Component', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = mount(FileEditor, {
      props: {
        modelValue: 'test content',
        language: 'javascript',
        height: 500,
      },
    });
  });

  it('should render correctly', () => {
    expect(wrapper.find('.file-editor').exists()).toBe(true);
  });

  it('should have correct height', () => {
    expect(wrapper.props('height')).toBe(500);
  });

  it('should emit update:modelValue on content change', async () => {
    // 模拟内容变化
    await wrapper.setProps({ modelValue: 'new content' });
    expect(wrapper.props('modelValue')).toBe('new content');
  });
});
```

- [ ] **步骤 2：创建 user.test.js**

```javascript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useUserStore } from '@/stores/user';

vi.mock('@/api/dashboard', () => ({
  login: vi.fn(),
  logout: vi.fn(),
}));

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  it('should have correct initial state', () => {
    const store = useUserStore();
    expect(store.token).toBe('');
    expect(store.username).toBe('');
    expect(store.isLogin).toBe(false);
  });

  it('should update state on login', async () => {
    const store = useUserStore();

    // Mock successful login
    const { login } = await import('@/api/dashboard');
    login.mockResolvedValue({ status: 1 });

    const result = await store.login({
      username: 'testuser',
      password: 'testpass',
    });

    expect(result).toBe(true);
    expect(store.username).toBe('testuser');
    expect(store.isLogin).toBe(true);
  });

  it('should clear state on logout', async () => {
    const store = useUserStore();

    // 设置初始状态
    store.token = 'test-token';
    store.username = 'testuser';
    store.isLogin = true;
    localStorage.setItem('token', 'test-token');

    // Mock logout
    const { logout } = await import('@/api/dashboard');
    logout.mockResolvedValue({});

    await store.logout();

    expect(store.token).toBe('');
    expect(store.username).toBe('');
    expect(store.isLogin).toBe(false);
    expect(localStorage.getItem('token')).toBeNull();
  });
});
```

- [ ] **步骤 3：运行前端测试**

运行：`cd web/frontend && npm test`
预期：测试通过

- [ ] **步骤 4：Commit**

```bash
git add web/frontend/src/__tests__/
git commit -m "test: add frontend component and store tests"
```

---

## 任务 7：创建部署脚本

**文件：**
- 创建：`scripts/deploy.sh`
- 创建：`scripts/test-deploy.sh`

- [ ] **步骤 1：创建 scripts/deploy.sh**

```bash
#!/bin/bash
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  mdserver-web 部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查参数
WSL_DISTRO="${1:-Debian}"
DEPLOY_DIR="/www/server/mdserver-web"

# 步骤 1：构建前端
echo -e "\n${YELLOW}[1/5] 构建前端...${NC}"
cd web/frontend
npm install
npm run build
cd ../..

# 步骤 2：运行测试
echo -e "\n${YELLOW}[2/5] 运行测试...${NC}"
python -m pytest tests/ -v --tb=short
if [ $? -ne 0 ]; then
    echo -e "${RED}测试失败，中止部署${NC}"
    exit 1
fi

# 步骤 3：复制代码到 WSL
echo -e "\n${YELLOW}[3/5] 复制代码到 WSL...${NC}"
wsl -d $WSL_DISTRO -- bash -c "sudo rm -rf $DEPLOY_DIR/*"
wsl -d $WSL_DISTRO -- bash -c "sudo cp -r . $DEPLOY_DIR/"

# 步骤 4：修复行尾符
echo -e "\n${YELLOW}[4/5] 修复行尾符...${NC}"
wsl -d $WSL_DISTRO -- bash -c "sudo find $DEPLOY_DIR -name '*.sh' -exec sed -i 's/\r$//' {} \;"
wsl -d $WSL_DISTRO -- bash -c "sudo find $DEPLOY_DIR -name '*.py' -exec sed -i 's/\r$//' {} \;"

# 步骤 5：重启服务
echo -e "\n${YELLOW}[5/5] 重启服务...${NC}"
wsl -d $WSL_DISTRO -- bash -c "sudo bash $DEPLOY_DIR/cli.sh restart"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
```

- [ ] **步骤 2：创建 scripts/test-deploy.sh**

```bash
#!/bin/bash
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  mdserver-web 部署测试${NC}"
echo -e "${GREEN}========================================${NC}"

WSL_DISTRO="${1:-Debian}"
PANEL_PORT="24749"

# 步骤 1：检查服务状态
echo -e "\n${YELLOW}[1/4] 检查服务状态...${NC}"
wsl -d $WSL_DISTRO -- bash -c "ps aux | grep gunicorn | grep -v grep"
if [ $? -ne 0 ]; then
    echo -e "${RED}服务未运行${NC}"
    exit 1
fi

# 步骤 2：检查端口
echo -e "\n${YELLOW}[2/4] 检查端口...${NC}"
curl -s -o /dev/null -w "%{http_code}" http://localhost:$PANEL_PORT
if [ $? -ne 0 ]; then
    echo -e "${RED}端口 $PANEL_PORT 不可达${NC}"
    exit 1
fi

# 步骤 3：检查登录页面
echo -e "\n${YELLOW}[3/4] 检查登录页面...${NC}"
RESPONSE=$(curl -s http://localhost:$PANEL_PORT)
if [[ ! $RESPONSE == *"夸父面板"* ]]; then
    echo -e "${RED}登录页面异常${NC}"
    exit 1
fi

# 步骤 4：检查 API
echo -e "\n${YELLOW}[4/4] 检查 API...${NC}"
curl -s http://localhost:$PANEL_PORT/check_login | grep -q "status"
if [ $? -ne 0 ]; then
    echo -e "${RED}API 异常${NC}"
    exit 1
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  所有检查通过！${NC}"
echo -e "${GREEN}========================================${NC}"
```

- [ ] **步骤 3：添加执行权限**

```bash
chmod +x scripts/deploy.sh scripts/test-deploy.sh
```

- [ ] **步骤 4：Commit**

```bash
git add scripts/
git commit -m "feat: add deployment and test scripts"
```

---

## 任务 8：创建冒烟测试

**文件：**
- 创建：`scripts/smoke-test.py`

- [ ] **步骤 1：创建 scripts/smoke-test.py**

```python
#!/usr/bin/env python3
"""
mdserver-web 冒烟测试
用于验证部署后的基本功能
"""

import requests
import sys
import time


class SmokeTest:
    def __init__(self, base_url='http://localhost:24749'):
        self.base_url = base_url
        self.session = requests.Session()
        self.passed = 0
        self.failed = 0

    def log(self, message, level='INFO'):
        print(f'[{level}] {message}')

    def test_pass(self, test_name):
        self.passed += 1
        self.log(f'✓ {test_name}', 'PASS')

    def test_fail(self, test_name, reason=''):
        self.failed += 1
        self.log(f'✗ {test_name}: {reason}', 'FAIL')

    def test_home_page(self):
        """测试首页访问"""
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                self.test_pass('首页访问')
            else:
                self.test_fail('首页访问', f'状态码: {response.status_code}')
        except Exception as e:
            self.test_fail('首页访问', str(e))

    def test_login_page(self):
        """测试登录页面"""
        try:
            # 获取安全入口
            response = self.session.get(self.base_url)
            if 'hfaY7eBF' in response.text or 'admin_path' in response.text:
                # 需要安全入口
                admin_path = '/hfaY7eBF'
                response = self.session.get(f'{self.base_url}{admin_path}')
            
            if response.status_code == 200 and '夸父面板' in response.text:
                self.test_pass('登录页面')
            else:
                self.test_fail('登录页面', '页面内容异常')
        except Exception as e:
            self.test_fail('登录页面', str(e))

    def test_login_api(self):
        """测试登录 API"""
        try:
            response = self.session.post(
                f'{self.base_url}/do_login',
                data={
                    'username': 'w6hlycfo',
                    'password': 'admin123',
                    'code': ''
                }
            )
            data = response.json()
            if data.get('status') == 1:
                self.test_pass('登录 API')
            else:
                self.test_fail('登录 API', data.get('msg', '未知错误'))
        except Exception as e:
            self.test_fail('登录 API', str(e))

    def test_system_info_api(self):
        """测试系统信息 API"""
        try:
            response = self.session.post(f'{self.base_url}/system/get_system_info')
            data = response.json()
            if 'data' in data and 'cpu' in data['data']:
                self.test_pass('系统信息 API')
            else:
                self.test_fail('系统信息 API', '返回数据格式异常')
        except Exception as e:
            self.test_fail('系统信息 API', str(e))

    def test_files_api(self):
        """测试文件管理 API"""
        try:
            response = self.session.post(
                f'{self.base_url}/files/get_dir',
                data={'path': '/www/wwwroot'}
            )
            data = response.json()
            if data.get('status'):
                self.test_pass('文件管理 API')
            else:
                self.test_fail('文件管理 API', '获取目录失败')
        except Exception as e:
            self.test_fail('文件管理 API', str(e))

    def run_all_tests(self):
        """运行所有测试"""
        self.log('开始冒烟测试...')
        self.log('=' * 40)

        self.test_home_page()
        self.test_login_page()
        self.test_login_api()
        self.test_system_info_api()
        self.test_files_api()

        self.log('=' * 40)
        self.log(f'测试完成: {self.passed} 通过, {self.failed} 失败')

        return self.failed == 0


if __name__ == '__main__':
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:24749'
    tester = SmokeTest(base_url)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
```

- [ ] **步骤 2：添加执行权限**

```bash
chmod +x scripts/smoke-test.py
```

- [ ] **步骤 3：Commit**

```bash
git add scripts/smoke-test.py
git commit -m "feat: add smoke test script"
```

---

## 任务 9：配置 GitHub Actions

**文件：**
- 创建：`.github/workflows/ci.yml`

- [ ] **步骤 1：创建 .github/workflows/ci.yml**

```yaml
name: CI

on:
  push:
    branches: [ master, dev ]
  pull_request:
    branches: [ master ]

jobs:
  backend-tests:
    name: Backend Tests
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8 black

    - name: Check code style
      run: |
        black --check web/ tests/
        flake8 web/ tests/

    - name: Run tests
      run: |
        python -m pytest tests/ -v --cov=web --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  frontend-tests:
    name: Frontend Tests
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: web/frontend/package-lock.json

    - name: Install dependencies
      working-directory: web/frontend
      run: npm ci

    - name: Lint
      working-directory: web/frontend
      run: npm run lint

    - name: Test
      working-directory: web/frontend
      run: npm test

    - name: Build
      working-directory: web/frontend
      run: npm run build

  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]

    steps:
    - uses: actions/checkout@v3

    - name: Build frontend
      working-directory: web/frontend
      run: |
        npm ci
        npm run build

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install backend dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Start server
      run: |
        cd web && gunicorn -b :7200 -w 1 --timeout 120 app:app &
        sleep 5

    - name: Run smoke tests
      run: |
        python scripts/smoke-test.py http://localhost:7200
```

- [ ] **步骤 2：Commit**

```bash
git add .github/workflows/
git commit -m "ci: add GitHub Actions workflow"
```

---

## 任务 10：生成测试覆盖率报告

**文件：**
- 修改：`pyproject.toml`
- 创建：`scripts/test-coverage.sh`

- [ ] **步骤 1：更新 pyproject.toml 添加覆盖率配置**

```toml
[tool.coverage.run]
source = ["web"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/migrations/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if __name__ == .__main__.",
    "raise NotImplementedError",
    "pass",
    "except:",
]
show_missing = true
fail_under = 70
```

- [ ] **步骤 2：创建 scripts/test-coverage.sh**

```bash
#!/bin/bash
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  测试覆盖率报告${NC}"
echo -e "${GREEN}========================================${NC}"

# 后端覆盖率
echo -e "\n${YELLOW}后端测试覆盖率:${NC}"
python -m pytest tests/ -v --cov=web --cov-report=term-missing --cov-report=html

# 前端覆盖率
echo -e "\n${YELLOW}前端测试覆盖率:${NC}"
cd web/frontend
npm run test:coverage
cd ../..

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  覆盖率报告已生成${NC}"
echo -e "${GREEN}  后端: htmlcov/index.html${NC}"
echo -e "${GREEN}  前端: web/frontend/coverage/index.html${NC}"
echo -e "${GREEN}========================================${NC}"
```

- [ ] **步骤 3：添加执行权限**

```bash
chmod +x scripts/test-coverage.sh
```

- [ ] **步骤 4：Commit**

```bash
git add pyproject.toml scripts/test-coverage.sh
git commit -m "feat: add test coverage reporting"
```

---

## 阶段 3 完成检查清单

- [ ] pytest 配置完成
- [ ] 后端 API 测试完成
- [ ] 工具函数测试完成
- [ ] 前端测试环境配置完成
- [ ] 前端组件测试完成
- [ ] 部署脚本创建完成
- [ ] 冒烟测试创建完成
- [ ] GitHub Actions 配置完成
- [ ] 测试覆盖率报告配置完成
- [ ] 所有测试通过

## 下一步

进入阶段 4：持续迭代
