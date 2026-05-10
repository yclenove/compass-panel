import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { ElMessage } from 'element-plus';

// 检测安全入口路径，构建正确的 base 路径
function getRouterBase() {
  const path = window.location.pathname;
  const match = path.match(/^\/([a-zA-Z0-9]{8})\//);
  if (match) {
    return '/' + match[1] + '/vue/';
  }
  return '/vue/';
}

// 布局组件
import MainLayout from '@/layouts/MainLayout.vue';
import AuthLayout from '@/layouts/AuthLayout.vue';

const routes = [
  {
    path: '/login',
    component: AuthLayout,
    children: [
      {
        path: '',
        name: 'Login',
        component: () => import('@/pages/Login.vue'),
        meta: { title: '登录', requiresAuth: false },
      },
    ],
  },
  {
    path: '/',
    component: MainLayout,
    redirect: '/dashboard',
    children: [
      // === 概览 ===
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/pages/Dashboard.vue'),
        meta: { title: '仪表盘', icon: 'Odometer', requiresAuth: true },
      },
      // === 网站与应用 ===
      {
        path: 'site',
        name: 'SiteList',
        component: () => import('@/pages/site/SiteList.vue'),
        meta: { title: '网站管理', icon: 'ChromeFilled', requiresAuth: true },
      },
      {
        path: 'database',
        name: 'Database',
        component: () => import('@/pages/database/Database.vue'),
        meta: { title: '数据库', icon: 'Coin', requiresAuth: true },
      },
      {
        path: 'ssl',
        name: 'SslCert',
        component: () => import('@/pages/ssl/SslCert.vue'),
        meta: { title: 'SSL证书', icon: 'Lock', requiresAuth: true },
      },
      // === 服务器管理 ===
      {
        path: 'files',
        name: 'FileList',
        component: () => import('@/pages/files/FileList.vue'),
        meta: { title: '文件管理', icon: 'FolderOpened', requiresAuth: true },
      },
      {
        path: 'files/edit',
        name: 'FileEdit',
        component: () => import('@/pages/files/FileEdit.vue'),
        meta: { title: '编辑文件', icon: 'Document', requiresAuth: true, hidden: true },
      },
      {
        path: 'terminal',
        name: 'Terminal',
        component: () => import('@/pages/terminal/Terminal.vue'),
        meta: { title: '终端', icon: 'Promotion', requiresAuth: true },
      },
      {
        path: 'monitor',
        name: 'Monitor',
        component: () => import('@/pages/monitor/Monitor.vue'),
        meta: { title: '系统监控', icon: 'DataLine', requiresAuth: true },
      },
      {
        path: 'webserver',
        name: 'WebServer',
        component: () => import('@/pages/webserver/WebServer.vue'),
        meta: { title: 'Web服务器', icon: 'Monitor', requiresAuth: true },
      },
      // === 运维工具 ===
      {
        path: 'soft',
        name: 'Soft',
        component: () => import('@/pages/soft/Soft.vue'),
        meta: { title: '软件管理', icon: 'Box', requiresAuth: true },
      },
      {
        path: 'docker',
        name: 'Docker',
        component: () => import('@/pages/docker/DockerMgr.vue'),
        meta: { title: 'Docker', icon: 'Box', requiresAuth: true },
      },
      {
        path: 'crontab',
        name: 'Crontab',
        component: () => import('@/pages/crontab/Crontab.vue'),
        meta: { title: '计划任务', icon: 'Timer', requiresAuth: true },
      },
      {
        path: 'backup',
        name: 'Backup',
        component: () => import('@/pages/backup/Backup.vue'),
        meta: { title: '备份管理', icon: 'CopyDocument', requiresAuth: true },
      },
      // === 安全 ===
      {
        path: 'security',
        name: 'Security',
        component: () => import('@/pages/security/Security.vue'),
        meta: { title: '安全加固', icon: 'Shield', requiresAuth: true },
      },
      {
        path: 'firewall',
        name: 'Firewall',
        component: () => import('@/pages/firewall/Firewall.vue'),
        meta: { title: '防火墙', icon: 'Warning', requiresAuth: true },
      },
      // === 系统管理 ===
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('@/pages/logs/Logs.vue'),
        meta: { title: '操作日志', icon: 'Tickets', requiresAuth: true },
      },
      {
        path: 'users',
        name: 'UserMgr',
        component: () => import('@/pages/users/UserMgr.vue'),
        meta: { title: '用户管理', icon: 'User', requiresAuth: true },
      },
      {
        path: 'plugins',
        name: 'PluginMgr',
        component: () => import('@/pages/plugins/PluginMgr.vue'),
        meta: { title: '插件管理', icon: 'Box', requiresAuth: true },
      },
      {
        path: 'migration',
        name: 'Migration',
        component: () => import('@/pages/migration/Migration.vue'),
        meta: { title: '面板迁移', icon: 'Connection', requiresAuth: true },
      },
      {
        path: 'setting',
        name: 'Setting',
        component: () => import('@/pages/setting/Setting.vue'),
        meta: { title: '面板设置', icon: 'Setting', requiresAuth: true },
      },
      // === 隐藏路由 ===
      {
        path: 'project',
        name: 'Project',
        component: () => import('@/pages/project/Project.vue'),
        meta: { title: '项目管理', icon: 'FolderOpened', requiresAuth: true, hidden: true },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/pages/NotFound.vue'),
    meta: { title: '页面未找到', requiresAuth: false },
  },
];

const routerBase = getRouterBase();
// v4 route config - organized menu with logical grouping
const router = createRouter({
  history: createWebHistory(routerBase),
  routes,
});

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  const requiresAuth = to.meta.requiresAuth !== false;

  // 设置页面标题
  document.title = to.meta.title
    ? `${to.meta.title} - Compass`
    : 'Compass 指南面板';

  if (requiresAuth && !userStore.isLogin) {
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if (to.name === 'Login' && userStore.isLogin) {
    next({ name: 'Dashboard' });
  } else {
    next();
  }
});

// 路由错误处理
router.onError((error) => {
  console.error('路由错误:', error);
  if (error.message.includes('Failed to fetch dynamically imported module')) {
    ElMessage.error('页面加载失败，请刷新重试');
  }
});

export default router;
