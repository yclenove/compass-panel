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
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/pages/Dashboard.vue'),
        meta: { title: '仪表盘', icon: 'Odometer', requiresAuth: true },
      },
      {
        path: 'site',
        name: 'SiteList',
        component: () => import('@/pages/site/SiteList.vue'),
        meta: { title: '网站管理', icon: 'ChromeFilled', requiresAuth: true },
      },
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
        path: 'monitor',
        name: 'Monitor',
        component: () => import('@/pages/monitor/Monitor.vue'),
        meta: { title: '系统监控', icon: 'DataLine', requiresAuth: true },
      },
      {
        path: 'firewall',
        name: 'Firewall',
        component: () => import('@/pages/firewall/Firewall.vue'),
        meta: { title: '安全', icon: 'Shield', requiresAuth: true },
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('@/pages/logs/Logs.vue'),
        meta: { title: '日志', icon: 'Tickets', requiresAuth: true },
      },
      {
        path: 'crontab',
        name: 'Crontab',
        component: () => import('@/pages/crontab/Crontab.vue'),
        meta: { title: '计划任务', icon: 'Timer', requiresAuth: true },
      },
      {
        path: 'soft',
        name: 'Soft',
        component: () => import('@/pages/soft/Soft.vue'),
        meta: { title: '软件管理', icon: 'Box', requiresAuth: true },
      },
      {
        path: 'setting',
        name: 'Setting',
        component: () => import('@/pages/setting/Setting.vue'),
        meta: { title: '面板设置', icon: 'Setting', requiresAuth: true },
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
    ? `${to.meta.title} - mdserver-web`
    : 'mdserver-web';

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
