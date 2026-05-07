<template>
  <div class="auth-layout">
    <div class="auth-container" :class="{ 'auth-container-enter': true }">
      <div class="auth-header">
        <div class="auth-logo-wrapper">
          <el-icon class="title-icon"><Monitor /></el-icon>
        </div>
        <h1 class="auth-title">mdserver-web</h1>
        <p class="auth-subtitle">Linux 服务器管理面板</p>
      </div>
      <router-view />
    </div>
    <div class="auth-footer">
      <span>&copy; {{ currentYear }} mdserver-web. All rights reserved.</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const currentYear = computed(() => new Date().getFullYear());
</script>

<style lang="scss" scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    pointer-events: none;
  }
}

.auth-container {
  width: 420px;
  max-width: 90vw;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-logo-wrapper {
  width: 64px;
  height: 64px;
  margin: 0 auto 12px;
  background: linear-gradient(135deg, #409eff 0%, #6366f1 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.3);
}

.title-icon {
  font-size: 36px;
  color: #ffffff;
}

.auth-title {
  font-size: 26px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 6px;
}

.auth-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.auth-footer {
  position: relative;
  z-index: 1;
  margin-top: 24px;
  text-align: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

@media (max-width: 480px) {
  .auth-container {
    padding: 24px;
    border-radius: 12px;
  }

  .auth-title {
    font-size: 22px;
  }
}
</style>
