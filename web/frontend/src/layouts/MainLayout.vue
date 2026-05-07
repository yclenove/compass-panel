<template>
  <el-container class="main-layout">
    <!-- 移动端遮罩 -->
    <div
      v-if="isMobile && !appStore.sidebarCollapsed"
      class="sidebar-overlay"
      @click="appStore.toggleSidebar"
    />

    <!-- 侧边栏 -->
    <el-aside
      :width="appStore.sidebarCollapsed ? '64px' : '210px'"
      class="sidebar"
      :class="{ 'mobile-sidebar': isMobile }"
    >
      <div class="sidebar-header">
        <el-icon class="logo-icon"><Monitor /></el-icon>
        <span v-show="!appStore.sidebarCollapsed" class="logo-text">mdserver-web</span>
      </div>

      <el-menu
        :default-active="currentRoute"
        :collapse="appStore.sidebarCollapsed"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#ffffff"
        :collapse-transition="false"
        router
        @select="handleMenuSelect"
      >
        <template v-for="route in menuRoutes" :key="route.path">
          <el-menu-item :index="'/' + route.path">
            <el-icon><component :is="route.meta.icon" /></el-icon>
            <template #title>{{ route.meta.title }}</template>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <!-- 右侧主内容区 -->
    <el-container class="main-container">
      <!-- 顶部导航 -->
      <el-header class="top-header">
        <div class="header-left">
          <el-icon
            class="collapse-btn"
            @click="appStore.toggleSidebar"
          >
            <Fold v-if="!appStore.sidebarCollapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/" class="breadcrumb-hide-mobile">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentMeta.title">
              {{ currentMeta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <el-tooltip content="刷新" placement="bottom">
            <el-icon class="header-action" @click="handleRefresh"><Refresh /></el-icon>
          </el-tooltip>

          <el-tooltip content="全屏" placement="bottom">
            <el-icon class="header-action" @click="toggleFullscreen"><FullScreen /></el-icon>
          </el-tooltip>

          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-dropdown">
              <el-avatar :size="28" class="user-avatar">
                {{ userStore.username ? userStore.username[0].toUpperCase() : 'A' }}
              </el-avatar>
              <span class="username">{{ userStore.username || 'Admin' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="setting">
                  <el-icon><Setting /></el-icon>面板设置
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="$route.fullPath" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAppStore } from '@/stores/app';
import { useUserStore } from '@/stores/user';

const route = useRoute();
const router = useRouter();
const appStore = useAppStore();
const userStore = useUserStore();

// 移动端检测
const isMobile = ref(window.innerWidth < 768);

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768;
  if (isMobile.value && !appStore.sidebarCollapsed) {
    appStore.toggleSidebar();
  }
};

onMounted(() => {
  window.addEventListener('resize', checkMobile);
  checkMobile();
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkMobile);
});

// 移动端菜单选择后自动收起
const handleMenuSelect = () => {
  if (isMobile.value) {
    appStore.toggleSidebar();
  }
};

// 获取当前路由路径，用于菜单高亮
const currentRoute = computed(() => {
  const path = route.path;
  // 处理子路由，如 /files/edit -> /files
  const segments = path.split('/').filter(Boolean);
  return segments.length > 1 ? `/${segments[0]}` : path;
});

const currentMeta = computed(() => route.meta || {});

// 获取需要显示在菜单中的路由（排除隐藏的）
const menuRoutes = computed(() => {
  const mainRoute = router.options.routes.find((r) => r.path === '/');
  if (!mainRoute || !mainRoute.children) return [];
  return mainRoute.children.filter((r) => !r.meta?.hidden);
});

function handleRefresh() {
  window.location.reload();
}


function toggleFullscreen() {
  if (document.fullscreenElement) {
    document.exitFullscreen();
  } else {
    document.documentElement.requestFullscreen();
  }
}

function handleCommand(command) {
  switch (command) {
    case 'setting':
      router.push('/setting');
      break;
    case 'logout':
      userStore.logout();
      break;
  }
}
</script>

<style lang="scss" scoped>
.main-layout {
  height: 100vh;
  overflow: hidden;
}

// 移动端遮罩
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

// 侧边栏
.sidebar {
  background-color: #304156;
  overflow-y: auto;
  overflow-x: hidden;
  transition: width 0.3s ease;

  &::-webkit-scrollbar {
    width: 0;
  }

  .el-menu {
    border-right: none;
  }

  &.mobile-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 1000;
  }
}

.sidebar-header {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 0 16px;
  background-color: #263445;
  color: #ffffff;
  overflow: hidden;

  .logo-icon {
    font-size: 26px;
    color: #409eff;
    flex-shrink: 0;
  }

  .logo-text {
    font-size: 16px;
    font-weight: 600;
    white-space: nowrap;
    letter-spacing: 0.5px;
  }
}

// 主内容容器
.main-container {
  overflow: hidden;
  background-color: #f0f2f5;
}

// 顶部导航
.top-header {
  height: 50px;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;

  .collapse-btn {
    font-size: 20px;
    cursor: pointer;
    color: #606266;
    transition: color 0.2s;

    &:hover {
      color: #409eff;
    }
  }

  .breadcrumb-hide-mobile {
    @media (max-width: 767px) {
      display: none;
    }
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;

  .header-action {
    font-size: 18px;
    cursor: pointer;
    color: #606266;
    transition: color 0.2s;
    padding: 4px;
    border-radius: 4px;

    &:hover {
      color: #409eff;
      background: rgba(64, 158, 255, 0.1);
    }
  }
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #606266;

  .user-avatar {
    background: #409eff;
    color: #fff;
    font-size: 14px;
    font-weight: 600;
  }

  .username {
    font-size: 14px;
    max-width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;

    @media (max-width: 767px) {
      display: none;
    }
  }
}

// 内容区
.main-content {
  padding: 16px;
  overflow-y: auto;
  height: calc(100vh - 50px);
  background-color: #f0f2f5;
}

// 路由切换动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// 菜单项样式微调
:deep(.el-menu-item) {
  &:hover {
    background-color: #263445 !important;
  }

  &.is-active {
    background-color: #1890ff !important;
  }
}

:deep(.el-menu-item .el-icon) {
  font-size: 18px;
}
</style>
