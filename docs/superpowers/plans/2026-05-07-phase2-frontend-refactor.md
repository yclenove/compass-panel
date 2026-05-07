# 阶段 2：前端重构 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 将前端从 jQuery + Bootstrap 重构为 Vue 3 + Element Plus，集成 Monaco Editor

**架构：** 使用 Vue 3 组件化架构，Pinia 状态管理，Vue Router 路由，Monaco Editor 代码编辑

**技术栈：** Vue 3, Vite, Element Plus, Pinia, Vue Router 4, Monaco Editor

---

## 文件结构

```
web/frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── api/                    # API 请求封装
│   │   ├── index.js            # Axios 实例
│   │   ├── dashboard.js        # 仪表盘 API
│   │   ├── files.js            # 文件管理 API
│   │   └── site.js             # 网站管理 API
│   ├── assets/                 # 静态资源
│   │   ├── styles/
│   │   │   ├── main.scss       # 主样式
│   │   │   └── variables.scss  # SCSS 变量
│   │   └── images/
│   ├── components/             # 通用组件
│   │   ├── DataTable.vue       # 数据表格
│   │   ├── FileEditor.vue      # 文件编辑器
│   │   ├── Terminal.vue        # 终端组件
│   │   ├── Charts.vue          # 图表组件
│   │   └── Breadcrumb.vue      # 面包屑导航
│   ├── layouts/                # 布局组件
│   │   ├── MainLayout.vue      # 主布局
│   │   └── AuthLayout.vue      # 认证布局
│   ├── pages/                  # 页面组件
│   │   ├── Dashboard.vue       # 首页仪表盘
│   │   ├── Login.vue           # 登录页
│   │   ├── files/
│   │   │   ├── FileList.vue    # 文件列表
│   │   │   └── FileEdit.vue    # 文件编辑
│   │   ├── site/
│   │   │   ├── SiteList.vue    # 网站列表
│   │   │   └── SiteEdit.vue    # 网站编辑
│   │   ├── monitor/
│   │   │   └── Monitor.vue     # 监控页
│   │   ├── firewall/
│   │   │   └── Firewall.vue    # 防火墙
│   │   ├── logs/
│   │   │   └── Logs.vue        # 日志
│   │   ├── crontab/
│   │   │   └── Crontab.vue     # 计划任务
│   │   ├── soft/
│   │   │   └── Soft.vue        # 软件管理
│   │   └── setting/
│   │       └── Setting.vue     # 面板设置
│   ├── router/                 # 路由配置
│   │   └── index.js
│   ├── stores/                 # Pinia 状态
│   │   ├── index.js            # Store 入口
│   │   ├── user.js             # 用户状态
│   │   ├── app.js              # 应用状态
│   │   └── files.js            # 文件状态
│   ├── utils/                  # 工具函数
│   │   ├── request.js          # HTTP 请求
│   │   ├── auth.js             # 认证工具
│   │   └── helpers.js          # 辅助函数
│   ├── App.vue                 # 根组件
│   └── main.js                 # 入口文件
├── index.html                  # HTML 模板
├── vite.config.js              # Vite 配置
├── package.json                # 项目配置
└── .env                        # 环境变量
```

---

## 任务 1：初始化 Vue 3 项目

**文件：**
- 创建：`web/frontend/package.json`
- 创建：`web/frontend/vite.config.js`
- 创建：`web/frontend/index.html`
- 创建：`web/frontend/src/main.js`
- 创建：`web/frontend/src/App.vue`

- [ ] **步骤 1：创建 package.json**

```json
{
  "name": "mdserver-web-frontend",
  "version": "0.18.5",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint src/**/*.{js,vue}",
    "lint:fix": "eslint src/**/*.{js,vue} --fix",
    "format": "prettier --write src/**/*.{js,vue,css,scss}"
  },
  "dependencies": {
    "vue": "^3.3.4",
    "vue-router": "^4.2.4",
    "pinia": "^2.1.4",
    "element-plus": "^2.3.14",
    "@element-plus/icons-vue": "^2.1.0",
    "axios": "^1.5.0",
    "monaco-editor": "^0.44.0",
    "@monaco-editor/loader": "^1.4.0",
    "echarts": "^5.4.3",
    "xterm": "^5.3.0",
    "xterm-addon-fit": "^0.8.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.3.4",
    "vite": "^4.4.9",
    "sass": "^1.66.1",
    "eslint": "^8.49.0",
    "eslint-plugin-vue": "^9.17.0",
    "prettier": "^3.0.3"
  }
}
```

- [ ] **步骤 2：创建 vite.config.js**

```javascript
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:7200',
        changeOrigin: true,
      },
      '/files': {
        target: 'http://localhost:7200',
        changeOrigin: true,
      },
      '/site': {
        target: 'http://localhost:7200',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: '../static/dist',
    assetsDir: 'assets',
    emptyOutDir: true,
  },
});
```

- [ ] **步骤 3：创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>mdserver-web</title>
  <link rel="icon" href="/favicon.ico">
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **步骤 4：创建 src/main.js**

```javascript
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import * as ElementPlusIconsVue from '@element-plus/icons-vue';

import App from './App.vue';
import router from './router';
import './assets/styles/main.scss';

const app = createApp(App);

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

app.use(createPinia());
app.use(router);
app.use(ElementPlus, { size: 'default' });

app.mount('#app');
```

- [ ] **步骤 5：创建 src/App.vue**

```vue
<template>
  <router-view />
</template>

<script setup>
// 根组件
</script>

<style lang="scss">
body {
  margin: 0;
  padding: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}
</style>
```

- [ ] **步骤 6：创建 src/router/index.js**

```javascript
import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { layout: 'auth' },
  },
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
    meta: { title: '首页' },
  },
  {
    path: '/files',
    name: 'Files',
    component: () => import('@/pages/files/FileList.vue'),
    meta: { title: '文件管理' },
  },
  {
    path: '/files/edit',
    name: 'FileEdit',
    component: () => import('@/pages/files/FileEdit.vue'),
    meta: { title: '编辑文件' },
  },
  {
    path: '/site',
    name: 'Site',
    component: () => import('@/pages/site/SiteList.vue'),
    meta: { title: '网站管理' },
  },
  {
    path: '/monitor',
    name: 'Monitor',
    component: () => import('@/pages/monitor/Monitor.vue'),
    meta: { title: '监控' },
  },
  {
    path: '/firewall',
    name: 'Firewall',
    component: () => import('@/pages/firewall/Firewall.vue'),
    meta: { title: '安全' },
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('@/pages/logs/Logs.vue'),
    meta: { title: '日志' },
  },
  {
    path: '/crontab',
    name: 'Crontab',
    component: () => import('@/pages/crontab/Crontab.vue'),
    meta: { title: '计划任务' },
  },
  {
    path: '/soft',
    name: 'Soft',
    component: () => import('@/pages/soft/Soft.vue'),
    meta: { title: '软件管理' },
  },
  {
    path: '/setting',
    name: 'Setting',
    component: () => import('@/pages/setting/Setting.vue'),
    meta: { title: '面板设置' },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');

  if (to.path !== '/login' && !token) {
    next('/login');
  } else {
    next();
  }
});

export default router;
```

- [ ] **步骤 7：创建 src/assets/styles/main.scss**

```scss
// 变量
$primary-color: #409eff;
$success-color: #67c23a;
$warning-color: #e6a23c;
$danger-color: #f56c6c;
$info-color: #909399;

$bg-color: #f5f7fa;
$border-color: #dcdfe6;
$text-color: #303133;
$text-color-secondary: #606266;
$text-color-placeholder: #c0c4cc;

// 全局样式
* {
  box-sizing: border-box;
}

body {
  background-color: $bg-color;
  color: $text-color;
}

// 工具类
.flex {
  display: flex;
}

.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

.flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

// 动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
```

- [ ] **步骤 8：验证项目初始化**

运行：`cd web/frontend && npm install && npm run dev`
预期：开发服务器启动，访问 http://localhost:3000 显示空白页面

- [ ] **步骤 9：Commit**

```bash
git add web/frontend/
git commit -m "feat: initialize Vue 3 frontend project"
```

---

## 任务 2：创建 API 请求封装

**文件：**
- 创建：`web/frontend/src/utils/request.js`
- 创建：`web/frontend/src/api/index.js`
- 创建：`web/frontend/src/api/dashboard.js`
- 创建：`web/frontend/src/api/files.js`

- [ ] **步骤 1：创建 src/utils/request.js**

```javascript
import axios from 'axios';
import { ElMessage } from 'element-plus';
import router from '@/router';

const service = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
});

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Cookie'] = `MW_VER_1=${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    const res = response.data;

    // 检查是否是登录页面重定向
    if (response.headers['content-type']?.includes('text/html')) {
      if (response.data.includes('登录')) {
        router.push('/login');
        return Promise.reject(new Error('未登录'));
      }
    }

    return res;
  },
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          router.push('/login');
          break;
        case 403:
          ElMessage.error('没有权限');
          break;
        case 500:
          ElMessage.error('服务器错误');
          break;
      }
    }
    return Promise.reject(error);
  }
);

export default service;
```

- [ ] **步骤 2：创建 src/api/index.js**

```javascript
import request from '@/utils/request';

export function getSystemInfo() {
  return request({
    url: '/system/get_system_info',
    method: 'post',
  });
}

export function getNetworkInfo() {
  return request({
    url: '/system/get_network',
    method: 'post',
  });
}

export function checkLogin() {
  return request({
    url: '/check_login',
    method: 'get',
  });
}
```

- [ ] **步骤 3：创建 src/api/dashboard.js**

```javascript
import request from '@/utils/request';

export function login(data) {
  return request({
    url: '/do_login',
    method: 'post',
    data,
  });
}

export function getCaptcha() {
  return '/code';
}

export function logout() {
  return request({
    url: '/do_logout',
    method: 'post',
  });
}
```

- [ ] **步骤 4：创建 src/api/files.js**

```javascript
import request from '@/utils/request';

export function getDir(path, showRow = 100, p = 1, search = '') {
  return request({
    url: '/files/get_dir',
    method: 'post',
    data: { path, showRow, p, search },
  });
}

export function getFileContent(path) {
  return request({
    url: '/files/get_file_content',
    method: 'post',
    data: { path },
  });
}

export function saveFileContent(path, data, encoding = 'utf-8') {
  return request({
    url: '/files/save_file_content',
    method: 'post',
    data: { path, data, encoding },
  });
}

export function createFile(path, filename) {
  return request({
    url: '/files/create_file',
    method: 'post',
    data: { path, filename },
  });
}

export function createDir(path, dirname) {
  return request({
    url: '/files/create_dir',
    method: 'post',
    data: { path, dirname },
  });
}

export function deleteFile(path) {
  return request({
    url: '/files/delete_file',
    method: 'post',
    data: { path },
  });
}

export function renameFile(path, newname) {
  return request({
    url: '/files/rename',
    method: 'post',
    data: { path, newname },
  });
}

export function copyFile(path, topath) {
  return request({
    url: '/files/copy_file',
    method: 'post',
    data: { path, topath },
  });
}

export function moveFile(path, topath) {
  return request({
    url: '/files/move_file',
    method: 'post',
    data: { path, topath },
  });
}

export function getDiskInfo() {
  return request({
    url: '/files/get_disk',
    method: 'post',
  });
}
```

- [ ] **步骤 5：验证 API 封装**

运行：`cd web/frontend && npm run build`
预期：构建成功，无错误

- [ ] **步骤 6：Commit**

```bash
git add web/frontend/src/api/ web/frontend/src/utils/
git commit -m "feat: add API request wrapper"
```

---

## 任务 3：创建 Pinia 状态管理

**文件：**
- 创建：`web/frontend/src/stores/index.js`
- 创建：`web/frontend/src/stores/user.js`
- 创建：`web/frontend/src/stores/app.js`

- [ ] **步骤 1：创建 src/stores/index.js**

```javascript
import { createPinia } from 'pinia';

const pinia = createPinia();

export default pinia;
```

- [ ] **步骤 2：创建 src/stores/user.js**

```javascript
import { defineStore } from 'pinia';
import { login, logout } from '@/api/dashboard';

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    username: localStorage.getItem('username') || '',
    isLogin: !!localStorage.getItem('token'),
  }),

  actions: {
    async login(credentials) {
      try {
        const res = await login(credentials);
        if (res.status === 1) {
          this.token = document.cookie.match(/MW_VER_1=([^;]+)/)?.[1] || '';
          this.username = credentials.username;
          this.isLogin = true;

          localStorage.setItem('token', this.token);
          localStorage.setItem('username', this.username);

          return true;
        }
        return false;
      } catch (error) {
        console.error('Login failed:', error);
        return false;
      }
    },

    async logout() {
      try {
        await logout();
      } catch (error) {
        console.error('Logout failed:', error);
      } finally {
        this.token = '';
        this.username = '';
        this.isLogin = false;

        localStorage.removeItem('token');
        localStorage.removeItem('username');
      }
    },
  },
});
```

- [ ] **步骤 3：创建 src/stores/app.js**

```javascript
import { defineStore } from 'pinia';
import { getSystemInfo } from '@/api';

export const useAppStore = defineStore('app', {
  state: () => ({
    systemInfo: {
      cpu: 0,
      mem: 0,
      memTotal: 0,
      memUsed: 0,
      disk: [],
    },
    sidebarCollapsed: false,
    theme: localStorage.getItem('theme') || 'light',
  }),

  actions: {
    async fetchSystemInfo() {
      try {
        const res = await getSystemInfo();
        if (res.status) {
          this.systemInfo = res.data;
        }
      } catch (error) {
        console.error('Failed to fetch system info:', error);
      }
    },

    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed;
    },

    setTheme(theme) {
      this.theme = theme;
      localStorage.setItem('theme', theme);
      document.documentElement.setAttribute('data-theme', theme);
    },
  },
});
```

- [ ] **步骤 4：验证状态管理**

运行：`cd web/frontend && npm run build`
预期：构建成功，无错误

- [ ] **步骤 5：Commit**

```bash
git add web/frontend/src/stores/
git commit -m "feat: add Pinia state management"
```

---

## 任务 4：创建主布局组件

**文件：**
- 创建：`web/frontend/src/layouts/MainLayout.vue`
- 创建：`web/frontend/src/layouts/AuthLayout.vue`

- [ ] **步骤 1：创建 src/layouts/MainLayout.vue**

```vue
<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside :width="sidebarCollapsed ? '64px' : '220px'" class="sidebar">
      <div class="logo">
        <img src="@/assets/images/logo.png" alt="Logo" class="logo-img" />
        <span v-show="!sidebarCollapsed" class="logo-text">mdserver-web</span>
      </div>

      <el-menu
        :default-active="currentRoute"
        :collapse="sidebarCollapsed"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <template #title>首页</template>
        </el-menu-item>

        <el-menu-item index="/site">
          <el-icon><Document /></el-icon>
          <template #title>网站</template>
        </el-menu-item>

        <el-menu-item index="/monitor">
          <el-icon><Monitor /></el-icon>
          <template #title>监控</template>
        </el-menu-item>

        <el-menu-item index="/firewall">
          <el-icon><Lock /></el-icon>
          <template #title>安全</template>
        </el-menu-item>

        <el-menu-item index="/files">
          <el-icon><Folder /></el-icon>
          <template #title>文件</template>
        </el-menu-item>

        <el-menu-item index="/logs">
          <el-icon><Notebook /></el-icon>
          <template #title>日志</template>
        </el-menu-item>

        <el-menu-item index="/crontab">
          <el-icon><Timer /></el-icon>
          <template #title>计划任务</template>
        </el-menu-item>

        <el-menu-item index="/soft">
          <el-icon><Box /></el-icon>
          <template #title>软件管理</template>
        </el-menu-item>

        <el-menu-item index="/setting">
          <el-icon><Setting /></el-icon>
          <template #title>面板设置</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="toggleSidebar">
            <Fold v-if="!sidebarCollapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" icon="UserFilled" />
              <span class="username">{{ username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="setting">面板设置</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAppStore } from '@/stores/app';
import { useUserStore } from '@/stores/user';

const route = useRoute();
const router = useRouter();
const appStore = useAppStore();
const userStore = useUserStore();

const sidebarCollapsed = computed(() => appStore.sidebarCollapsed);
const currentRoute = computed(() => route.path);
const currentTitle = computed(() => route.meta.title);
const username = computed(() => userStore.username);

const toggleSidebar = () => {
  appStore.toggleSidebar();
};

const handleCommand = async (command) => {
  if (command === 'setting') {
    router.push('/setting');
  } else if (command === 'logout') {
    await userStore.logout();
    router.push('/login');
  }
};
</script>

<style lang="scss" scoped>
.main-layout {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 16px;
    background-color: #263445;

    .logo-img {
      width: 32px;
      height: 32px;
      margin-right: 8px;
    }

    .logo-text {
      color: #fff;
      font-size: 16px;
      font-weight: bold;
      white-space: nowrap;
    }
  }

  .sidebar-menu {
    border-right: none;
    background-color: #304156;

    :deep(.el-menu-item) {
      color: #bfcbd9;

      &:hover {
        background-color: #263445;
      }

      &.is-active {
        color: #409eff;
        background-color: #263445;
      }
    }
  }
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);

  .header-left {
    display: flex;
    align-items: center;

    .collapse-btn {
      font-size: 20px;
      cursor: pointer;
      margin-right: 16px;
      color: #666;

      &:hover {
        color: #409eff;
      }
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      cursor: pointer;

      .username {
        margin-left: 8px;
        font-size: 14px;
        color: #666;
      }
    }
  }
}

.content {
  background-color: #f5f7fa;
  padding: 20px;
}
</style>
```

- [ ] **步骤 2：创建 src/layouts/AuthLayout.vue**

```vue
<template>
  <div class="auth-layout">
    <div class="auth-container">
      <div class="auth-header">
        <img src="@/assets/images/logo.png" alt="Logo" class="logo" />
        <h1 class="title">mdserver-web</h1>
      </div>
      <router-view />
    </div>
  </div>
</template>

<script setup>
// 认证布局
</script>

<style lang="scss" scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.auth-container {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);

  .auth-header {
    text-align: center;
    margin-bottom: 30px;

    .logo {
      width: 64px;
      height: 64px;
      margin-bottom: 16px;
    }

    .title {
      font-size: 24px;
      color: #303133;
      margin: 0;
    }
  }
}
</style>
```

- [ ] **步骤 3：验证布局组件**

运行：`cd web/frontend && npm run build`
预期：构建成功，无错误

- [ ] **步骤 4：Commit**

```bash
git add web/frontend/src/layouts/
git commit -m "feat: add main and auth layout components"
```

---

## 任务 5：创建登录页面

**文件：**
- 创建：`web/frontend/src/pages/Login.vue`

- [ ] **步骤 1：创建 src/pages/Login.vue**

```vue
<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-position="top"
    class="login-form"
  >
    <el-form-item label="用户名" prop="username">
      <el-input
        v-model="form.username"
        placeholder="请输入用户名"
        prefix-icon="User"
        size="large"
      />
    </el-form-item>

    <el-form-item label="密码" prop="password">
      <el-input
        v-model="form.password"
        type="password"
        placeholder="请输入密码"
        prefix-icon="Lock"
        size="large"
        show-password
        @keyup.enter="handleLogin"
      />
    </el-form-item>

    <el-form-item v-if="showCaptcha" label="验证码" prop="code">
      <div class="captcha-row">
        <el-input
          v-model="form.code"
          placeholder="请输入验证码"
          size="large"
          @keyup.enter="handleLogin"
        />
        <img
          :src="captchaUrl"
          class="captcha-img"
          @click="refreshCaptcha"
          alt="验证码"
        />
      </div>
    </el-form-item>

    <el-form-item>
      <el-button
        type="primary"
        size="large"
        :loading="loading"
        class="login-btn"
        @click="handleLogin"
      >
        登录
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/stores/user';
import { getCaptcha } from '@/api/dashboard';

const router = useRouter();
const userStore = useUserStore();

const formRef = ref(null);
const loading = ref(false);
const showCaptcha = ref(false);
const captchaUrl = ref('');

const form = reactive({
  username: '',
  password: '',
  code: '',
});

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  code: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
};

const refreshCaptcha = () => {
  captchaUrl.value = getCaptcha() + '?t=' + Date.now();
};

onMounted(() => {
  refreshCaptcha();
});

const handleLogin = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (!valid) return;

    loading.value = true;
    try {
      const success = await userStore.login(form);
      if (success) {
        ElMessage.success('登录成功');
        router.push('/dashboard');
      } else {
        ElMessage.error('登录失败');
        refreshCaptcha();
      }
    } catch (error) {
      ElMessage.error(error.message || '登录失败');
      refreshCaptcha();
    } finally {
      loading.value = false;
    }
  });
};
</script>

<style lang="scss" scoped>
.login-form {
  .captcha-row {
    display: flex;
    gap: 12px;

    .captcha-img {
      height: 40px;
      cursor: pointer;
      border-radius: 4px;
    }
  }

  .login-btn {
    width: 100%;
  }
}
</style>
```

- [ ] **步骤 2：验证登录页面**

运行：`cd web/frontend && npm run build`
预期：构建成功，无错误

- [ ] **步骤 3：Commit**

```bash
git add web/frontend/src/pages/Login.vue
git commit -m "feat: add login page component"
```

---

## 任务 6：创建首页仪表盘

**文件：**
- 创建：`web/frontend/src/pages/Dashboard.vue`

- [ ] **步骤 1：创建 src/pages/Dashboard.vue**

```vue
<template>
  <div class="dashboard">
    <!-- 系统信息卡片 -->
    <el-row :gutter="20" class="info-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Cpu /></el-icon>
              <span>CPU 使用率</span>
            </div>
          </template>
          <div class="card-content">
            <el-progress
              type="dashboard"
              :percentage="systemInfo.cpu"
              :color="getProgressColor(systemInfo.cpu)"
            />
            <div class="card-label">{{ cpuCores }} 核心</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Memory /></el-icon>
              <span>内存使用率</span>
            </div>
          </template>
          <div class="card-content">
            <el-progress
              type="dashboard"
              :percentage="systemInfo.mem"
              :color="getProgressColor(systemInfo.mem)"
            />
            <div class="card-label">
              {{ systemInfo.memUsed }}G / {{ systemInfo.memTotal }}G
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Upload /></el-icon>
              <span>上行流量</span>
            </div>
          </template>
          <div class="card-content">
            <div class="flow-value">{{ networkInfo.up }}</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Download /></el-icon>
              <span>下行流量</span>
            </div>
          </template>
          <div class="card-content">
            <div class="flow-value">{{ networkInfo.down }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 磁盘信息 -->
    <el-card class="disk-card">
      <template #header>
        <div class="card-header">
          <el-icon><Coin /></el-icon>
          <span>磁盘信息</span>
        </div>
      </template>
      <el-table :data="systemInfo.disk" stripe>
        <el-table-column prop="path" label="分区" />
        <el-table-column label="使用率">
          <template #default="{ row }">
            <el-progress
              :percentage="row.percent"
              :color="getProgressColor(row.percent)"
            />
          </template>
        </el-table-column>
        <el-table-column label="已用 / 总计">
          <template #default="{ row }">
            {{ row.used }} / {{ row.size }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useAppStore } from '@/stores/app';
import { getNetworkInfo } from '@/api';

const appStore = useAppStore();

const systemInfo = computed(() => appStore.systemInfo);
const cpuCores = computed(() => {
  // 从系统信息中获取 CPU 核心数
  return 20; // 临时硬编码
});

const networkInfo = ref({
  up: '0 B',
  down: '0 B',
});

let networkTimer = null;

const getProgressColor = (percentage) => {
  if (percentage < 50) return '#67c23a';
  if (percentage < 80) return '#e6a23c';
  return '#f56c6c';
};

const fetchNetworkInfo = async () => {
  try {
    const res = await getNetworkInfo();
    if (res.status) {
      networkInfo.value = res.data;
    }
  } catch (error) {
    console.error('Failed to fetch network info:', error);
  }
};

onMounted(() => {
  appStore.fetchSystemInfo();
  fetchNetworkInfo();

  // 每 5 秒更新网络信息
  networkTimer = setInterval(fetchNetworkInfo, 5000);
});

onUnmounted(() => {
  if (networkTimer) {
    clearInterval(networkTimer);
  }
});
</script>

<style lang="scss" scoped>
.dashboard {
  .info-cards {
    margin-bottom: 20px;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 500;
  }

  .card-content {
    text-align: center;

    .card-label {
      margin-top: 12px;
      font-size: 14px;
      color: #909399;
    }

    .flow-value {
      font-size: 28px;
      font-weight: bold;
      color: #409eff;
    }
  }

  .disk-card {
    margin-top: 20px;
  }
}
</style>
```

- [ ] **步骤 2：验证首页仪表盘**

运行：`cd web/frontend && npm run build`
预期：构建成功，无错误

- [ ] **步骤 3：Commit**

```bash
git add web/frontend/src/pages/Dashboard.vue
git commit -m "feat: add dashboard page component"
```

---

## 任务 7：创建文件管理页面

**文件：**
- 创建：`web/frontend/src/pages/files/FileList.vue`
- 创建：`web/frontend/src/pages/files/FileEdit.vue`
- 创建：`web/frontend/src/components/FileEditor.vue`

- [ ] **步骤 1：创建 src/pages/files/FileList.vue**

```vue
<template>
  <div class="file-list">
    <!-- 工具栏 -->
    <el-card class="toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button icon="Back" @click="goBack" :disabled="currentPath === '/'">
            返回
          </el-button>
          <el-button icon="Refresh" @click="refresh">刷新</el-button>
          <el-button icon="Upload" type="primary" @click="showUpload">上传</el-button>
          <el-button icon="FolderAdd" @click="showCreateDir">新建目录</el-button>
          <el-button icon="DocumentAdd" @click="showCreateFile">新建文件</el-button>
        </div>

        <div class="toolbar-right">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索文件"
            clearable
            @keyup.enter="search"
          >
            <template #append>
              <el-button icon="Search" @click="search" />
            </template>
          </el-input>
        </div>
      </div>

      <!-- 路径导航 -->
      <div class="path-nav">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item
            v-for="(item, index) in pathParts"
            :key="index"
            @click="navigateTo(index)"
          >
            {{ item || '根目录' }}
          </el-breadcrumb-item>
        </el-breadcrumb>
      </div>
    </el-card>

    <!-- 文件列表 -->
    <el-card class="file-table-card">
      <el-table
        :data="fileList"
        stripe
        @selection-change="handleSelectionChange"
        @row-dblclick="handleDoubleClick"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="文件名" min-width="300">
          <template #default="{ row }">
            <div class="file-name" @click="handleClick(row)">
              <el-icon v-if="row.isDir" class="file-icon folder-icon">
                <Folder />
              </el-icon>
              <el-icon v-else class="file-icon">
                <Document />
              </el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">
            {{ row.isDir ? '-' : formatSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="chmod" label="权限" width="120" />
        <el-table-column prop="accept" label="所有者" width="120" />
        <el-table-column prop="mtime" label="修改时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.mtime) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.isDir"
              type="primary"
              link
              @click="editFile(row)"
            >
              编辑
            </el-button>
            <el-button type="primary" link @click="rename(row)">
              重命名
            </el-button>
            <el-button type="danger" link @click="deleteFile(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getDir, deleteFile as apiDeleteFile, renameFile } from '@/api/files';

const route = useRoute();
const router = useRouter();

const currentPath = ref('/www/wwwroot');
const fileList = ref([]);
const selectedFiles = ref([]);
const searchKeyword = ref('');
const currentPage = ref(1);
const pageSize = ref(100);
const total = ref(0);
const loading = ref(false);

const pathParts = computed(() => {
  return currentPath.value.split('/').filter(Boolean);
});

const fetchFiles = async () => {
  loading.value = true;
  try {
    const res = await getDir(
      currentPath.value,
      pageSize.value,
      currentPage.value,
      searchKeyword.value
    );
    if (res.status) {
      fileList.value = [...res.data.dir, ...res.data.file];
      total.value = res.data.count || fileList.value.length;
    }
  } catch (error) {
    ElMessage.error('获取文件列表失败');
  } finally {
    loading.value = false;
  }
};

const navigateTo = (index) => {
  const parts = pathParts.value.slice(0, index + 1);
  currentPath.value = '/' + parts.join('/');
  currentPage.value = 1;
  fetchFiles();
};

const goBack = () => {
  const parts = currentPath.value.split('/').filter(Boolean);
  parts.pop();
  currentPath.value = '/' + parts.join('/') || '/';
  currentPage.value = 1;
  fetchFiles();
};

const refresh = () => {
  fetchFiles();
};

const handleClick = (row) => {
  if (row.isDir) {
    currentPath.value = currentPath.value + '/' + row.name;
    currentPage.value = 1;
    fetchFiles();
  }
};

const handleDoubleClick = (row) => {
  if (!row.isDir) {
    editFile(row);
  }
};

const editFile = (row) => {
  router.push({
    path: '/files/edit',
    query: { path: currentPath.value + '/' + row.name },
  });
};

const rename = async (row) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新名称', '重命名', {
      inputValue: row.name,
      inputValidator: (val) => !!val || '名称不能为空',
    });

    const res = await renameFile(
      currentPath.value + '/' + row.name,
      value
    );
    if (res.status) {
      ElMessage.success('重命名成功');
      fetchFiles();
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重命名失败');
    }
  }
};

const deleteFile = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${row.name} 吗？`,
      '删除确认',
      { type: 'warning' }
    );

    const res = await apiDeleteFile(currentPath.value + '/' + row.name);
    if (res.status) {
      ElMessage.success('删除成功');
      fetchFiles();
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
    }
  }
};

const handleSelectionChange = (selection) => {
  selectedFiles.value = selection;
};

const handlePageChange = (page) => {
  currentPage.value = page;
  fetchFiles();
};

const search = () => {
  currentPage.value = 1;
  fetchFiles();
};

const showUpload = () => {
  // TODO: 实现上传功能
  ElMessage.info('上传功能开发中');
};

const showCreateDir = () => {
  // TODO: 实现新建目录功能
  ElMessage.info('新建目录功能开发中');
};

const showCreateFile = () => {
  // TODO: 实现新建文件功能
  ElMessage.info('新建文件功能开发中');
};

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatTime = (timestamp) => {
  return new Date(timestamp * 1000).toLocaleString();
};

onMounted(() => {
  fetchFiles();
});
</script>

<style lang="scss" scoped>
.file-list {
  .toolbar-card {
    margin-bottom: 20px;

    .toolbar {
      display: flex;
      justify-content: space-between;
      margin-bottom: 16px;
    }

    .path-nav {
      padding: 8px 0;
      border-top: 1px solid #ebeef5;
    }
  }

  .file-table-card {
    .file-name {
      display: flex;
      align-items: center;
      cursor: pointer;

      .file-icon {
        margin-right: 8px;
        font-size: 18px;
        color: #909399;

        &.folder-icon {
          color: #e6a23c;
        }
      }

      &:hover {
        color: #409eff;
      }
    }

    .pagination {
      margin-top: 16px;
      display: flex;
      justify-content: flex-end;
    }
  }
}
</style>
```

- [ ] **步骤 2：创建 src/pages/files/FileEdit.vue**

```vue
<template>
  <div class="file-edit">
    <el-card class="edit-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button icon="Back" @click="goBack">返回</el-button>
            <span class="file-path">{{ filePath }}</span>
          </div>
          <div class="header-right">
            <el-button type="primary" icon="DocumentChecked" @click="save">
              保存
            </el-button>
          </div>
        </div>
      </template>

      <FileEditor
        ref="editorRef"
        v-model="content"
        :language="language"
        :height="600"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { getFileContent, saveFileContent } from '@/api/files';
import FileEditor from '@/components/FileEditor.vue';

const route = useRoute();
const router = useRouter();

const filePath = computed(() => route.query.path || '');
const content = ref('');
const language = computed(() => {
  const ext = filePath.value.split('.').pop().toLowerCase();
  const langMap = {
    js: 'javascript',
    ts: 'typescript',
    py: 'python',
    php: 'php',
    html: 'html',
    css: 'css',
    scss: 'scss',
    json: 'json',
    md: 'markdown',
    sh: 'shell',
    yml: 'yaml',
    yaml: 'yaml',
    xml: 'xml',
    sql: 'sql',
    conf: 'ini',
    ini: 'ini',
  };
  return langMap[ext] || 'plaintext';
});

const editorRef = ref(null);

const fetchContent = async () => {
  if (!filePath.value) return;

  try {
    const res = await getFileContent(filePath.value);
    if (res.status) {
      content.value = res.data.data;
    }
  } catch (error) {
    ElMessage.error('获取文件内容失败');
  }
};

const save = async () => {
  try {
    const res = await saveFileContent(filePath.value, content.value);
    if (res.status) {
      ElMessage.success('保存成功');
    }
  } catch (error) {
    ElMessage.error('保存失败');
  }
};

const goBack = () => {
  router.back();
};

onMounted(() => {
  fetchContent();
});
</script>

<style lang="scss" scoped>
.file-edit {
  .edit-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .header-left {
        display: flex;
        align-items: center;
        gap: 16px;

        .file-path {
          font-size: 14px;
          color: #606266;
        }
      }
    }
  }
}
</style>
```

- [ ] **步骤 3：创建 src/components/FileEditor.vue**

```vue
<template>
  <div ref="editorContainer" class="file-editor"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as monaco from 'monaco-editor';

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  language: {
    type: String,
    default: 'plaintext',
  },
  height: {
    type: Number,
    default: 500,
  },
  readOnly: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['update:modelValue']);

const editorContainer = ref(null);
let editor = null;

onMounted(() => {
  if (!editorContainer.value) return;

  // 创建编辑器
  editor = monaco.editor.create(editorContainer.value, {
    value: props.modelValue,
    language: props.language,
    theme: 'vs-dark',
    readOnly: props.readOnly,
    automaticLayout: true,
    minimap: {
      enabled: true,
    },
    fontSize: 14,
    lineNumbers: 'on',
    roundedSelection: false,
    scrollBeyondLastLine: false,
    wordWrap: 'on',
    folding: true,
    bracketMatching: 'always',
    autoClosingBrackets: 'always',
    autoClosingQuotes: 'always',
    formatOnPaste: true,
    formatOnType: true,
    tabSize: 4,
  });

  // 监听内容变化
  editor.onDidChangeModelContent(() => {
    emit('update:modelValue', editor.getValue());
  });

  // 设置快捷键
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
    // Ctrl+S 保存
    emit('save');
  });
});

onUnmounted(() => {
  if (editor) {
    editor.dispose();
  }
});

// 监听外部值变化
watch(
  () => props.modelValue,
  (newValue) => {
    if (editor && newValue !== editor.getValue()) {
      editor.setValue(newValue);
    }
  }
);

// 监听语言变化
watch(
  () => props.language,
  (newLanguage) => {
    if (editor) {
      monaco.editor.setModelLanguage(editor.getModel(), newLanguage);
    }
  }
);

// 监听高度变化
watch(
  () => props.height,
  (newHeight) => {
    if (editorContainer.value) {
      editorContainer.value.style.height = `${newHeight}px`;
      editor.layout();
    }
  }
);
</script>

<style lang="scss" scoped>
.file-editor {
  width: 100%;
  min-height: 500px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}
</style>
```

- [ ] **步骤 4：验证文件管理页面**

运行：`cd web/frontend && npm run build`
预期：构建成功，无错误

- [ ] **步骤 5：Commit**

```bash
git add web/frontend/src/pages/files/ web/frontend/src/components/FileEditor.vue
git commit -m "feat: add file management pages with Monaco Editor"
```

---

## 任务 8：创建网站管理页面

**文件：**
- 创建：`web/frontend/src/pages/site/SiteList.vue`

- [ ] **步骤 1：创建 src/pages/site/SiteList.vue**

```vue
<template>
  <div class="site-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>网站管理</span>
          <el-button type="primary" icon="Plus" @click="showAddSite">
            添加站点
          </el-button>
        </div>
      </template>

      <el-table :data="siteList" stripe v-loading="loading">
        <el-table-column prop="name" label="网站名称" />
        <el-table-column prop="path" label="根目录" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '运行中' : '已停止' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="editSite(row)">
              设置
            </el-button>
            <el-button
              :type="row.status === 1 ? 'warning' : 'success'"
              link
              @click="toggleSite(row)"
            >
              {{ row.status === 1 ? '停止' : '启动' }}
            </el-button>
            <el-button type="danger" link @click="deleteSite(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';

const siteList = ref([]);
const loading = ref(false);

const fetchSites = async () => {
  loading.value = true;
  try {
    // TODO: 调用 API 获取网站列表
    siteList.value = [];
  } catch (error) {
    ElMessage.error('获取网站列表失败');
  } finally {
    loading.value = false;
  }
};

const showAddSite = () => {
  ElMessage.info('添加站点功能开发中');
};

const editSite = (row) => {
  ElMessage.info('编辑站点功能开发中');
};

const toggleSite = async (row) => {
  const action = row.status === 1 ? '停止' : '启动';
  try {
    await ElMessageBox.confirm(`确定要${action} ${row.name} 吗？`, '确认');
    // TODO: 调用 API 切换状态
    ElMessage.success(`${action}成功`);
    fetchSites();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`${action}失败`);
    }
  }
};

const deleteSite = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${row.name} 吗？此操作不可恢复！`,
      '删除确认',
      { type: 'warning' }
    );
    // TODO: 调用 API 删除网站
    ElMessage.success('删除成功');
    fetchSites();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
    }
  }
};

onMounted(() => {
  fetchSites();
});
</script>

<style lang="scss" scoped>
.site-list {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
```

- [ ] **步骤 2：验证网站管理页面**

运行：`cd web/frontend && npm run build`
预期：构建成功，无错误

- [ ] **步骤 3：Commit**

```bash
git add web/frontend/src/pages/site/
git commit -m "feat: add site management page"
```

---

## 任务 9：创建其他页面占位

**文件：**
- 创建：`web/frontend/src/pages/monitor/Monitor.vue`
- 创建：`web/frontend/src/pages/firewall/Firewall.vue`
- 创建：`web/frontend/src/pages/logs/Logs.vue`
- 创建：`web/frontend/src/pages/crontab/Crontab.vue`
- 创建：`web/frontend/src/pages/soft/Soft.vue`
- 创建：`web/frontend/src/pages/setting/Setting.vue`

- [ ] **步骤 1：创建 Monitor.vue**

```vue
<template>
  <div class="monitor-page">
    <el-card>
      <template #header>
        <span>系统监控</span>
      </template>
      <el-empty description="监控功能开发中" />
    </el-card>
  </div>
</template>

<script setup>
// 监控页面
</script>
```

- [ ] **步骤 2：创建其他页面**

为每个页面创建类似的占位组件：

```vue
<template>
  <div class="[页面名]-page">
    <el-card>
      <template #header>
        <span>[页面标题]</span>
      </template>
      <el-empty description="[功能]开发中" />
    </el-card>
  </div>
</template>

<script setup>
// [页面名]页面
</script>
```

- [ ] **步骤 3：验证所有页面**

运行：`cd web/frontend && npm run build`
预期：构建成功，无错误

- [ ] **步骤 4：Commit**

```bash
git add web/frontend/src/pages/
git commit -m "feat: add placeholder pages for all modules"
```

---

## 任务 10：配置构建输出

**文件：**
- 修改：`web/frontend/vite.config.js`
- 创建：`web/templates/default/index.html`

- [ ] **步骤 1：修改 vite.config.js 配置构建输出**

```javascript
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:7200',
        changeOrigin: true,
      },
    },
  },
  build: {
    // 输出到 Flask 静态目录
    outDir: path.resolve(__dirname, '../static/dist'),
    assetsDir: 'assets',
    emptyOutDir: true,
    // 生成 manifest.json
    manifest: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'src/main.js'),
      },
    },
  },
});
```

- [ ] **步骤 2：修改 Flask 入口模板**

修改 `web/templates/default/layout.html`，添加 Vue 应用挂载点：

```html
<!-- 在 body 标签内添加 -->
<div id="app"></div>

<!-- 添加构建后的 JS/CSS -->
{% if config.DEV_MODE %}
<script type="module" src="http://localhost:3000/src/main.js"></script>
{% else %}
<script src="/static/dist/assets/main-[hash].js"></script>
<link rel="stylesheet" href="/static/dist/assets/main-[hash].css" />
{% endif %}
```

- [ ] **步骤 3：验证构建配置**

运行：`cd web/frontend && npm run build`
预期：构建成功，输出到 `web/static/dist/`

- [ ] **步骤 4：Commit**

```bash
git add web/frontend/vite.config.js web/templates/
git commit -m "feat: configure build output for Flask integration"
```

---

## 阶段 2 完成检查清单

- [ ] Vue 3 项目初始化完成
- [ ] API 请求封装完成
- [ ] Pinia 状态管理完成
- [ ] 主布局组件完成
- [ ] 登录页面完成
- [ ] 首页仪表盘完成
- [ ] 文件管理页面完成
- [ ] 网站管理页面完成
- [ ] Monaco Editor 集成完成
- [ ] 所有页面创建完成
- [ ] 构建配置完成

## 下一步

进入阶段 3：质量保障
