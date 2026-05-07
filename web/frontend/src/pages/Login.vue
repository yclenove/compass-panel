<template>
  <div class="login-page">
    <el-form
      ref="loginFormRef"
      :model="loginForm"
      :rules="loginRules"
      size="large"
      @keyup.enter="handleLogin"
    >
      <el-form-item prop="username">
        <el-input
          v-model="loginForm.username"
          placeholder="请输入用户名"
          :prefix-icon="User"
          clearable
          autofocus
        />
      </el-form-item>

      <el-form-item prop="password">
        <el-input
          v-model="loginForm.password"
          type="password"
          placeholder="请输入密码"
          :prefix-icon="Lock"
          show-password
          clearable
          @keydown="checkCapsLock"
        />
        <transition name="fade">
          <span v-if="capsLockOn" class="caps-lock-warning">
            <el-icon><Warning /></el-icon> 大写锁定已开启
          </span>
        </transition>
      </el-form-item>

      <el-form-item v-if="showVerifyCode" prop="code">
        <div class="verify-code-row">
          <el-input
            v-model="loginForm.code"
            placeholder="请输入验证码"
            :prefix-icon="Key"
            clearable
            class="verify-input"
          />
          <div class="verify-code-img" @click="refreshCode">
            <img
              v-if="verifyCodeUrl"
              :src="verifyCodeUrl"
              alt="验证码"
              @error="onCodeImgError"
            />
            <span v-else class="loading-text">加载中...</span>
          </div>
        </div>
      </el-form-item>

      <el-form-item>
        <div class="login-options">
          <el-checkbox v-model="rememberMe">记住我</el-checkbox>
        </div>
        <el-button
          type="primary"
          :loading="loading"
          class="login-btn"
          @click="handleLogin"
        >
          {{ loading ? '登录中...' : '登 录' }}
        </el-button>
      </el-form-item>
    </el-form>

    <div class="login-footer">
      <span>{{ currentTime }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User, Lock, Key } from '@element-plus/icons-vue';
import { useUserStore } from '@/stores/user';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const loginFormRef = ref(null);
const loading = ref(false);
const showVerifyCode = ref(false);
const verifyCodeUrl = ref('');
const capsLockOn = ref(false);
const rememberMe = ref(false);
const currentTime = ref('');

const loginForm = reactive({
  username: '',
  password: '',
  code: '',
});

// 动态验证规则：验证码字段仅在显示时必填
const loginRules = computed(() => ({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  code: showVerifyCode.value
    ? [{ required: true, message: '请输入验证码', trigger: 'blur' }]
    : [],
}));

// Caps Lock 检测
function checkCapsLock(e) {
  capsLockOn.value = e.getModifierState('CapsLock');
}

// 当前时间
let timeTimer = null;
function updateTime() {
  const now = new Date();
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}

function refreshCode() {
  verifyCodeUrl.value = '/code?t=' + Date.now();
}

function onCodeImgError() {
  showVerifyCode.value = false;
  verifyCodeUrl.value = '';
}

async function handleLogin() {
  if (!loginFormRef.value) return;

  try {
    await loginFormRef.value.validate();
  } catch {
    return;
  }

  loading.value = true;
  try {
    await userStore.login(loginForm);
    ElMessage.success('登录成功');

    // 记住用户名
    if (rememberMe.value) {
      localStorage.setItem('mw_remember_user', loginForm.username);
    } else {
      localStorage.removeItem('mw_remember_user');
    }

    const redirect = route.query.redirect || '/dashboard';
    router.push(redirect);
  } catch (error) {
    ElMessage.error(error.message || '登录失败，请检查用户名和密码');
    if (showVerifyCode.value) {
      refreshCode();
    }
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  showVerifyCode.value = true;
  refreshCode();
  updateTime();
  timeTimer = setInterval(updateTime, 1000);

  // 恢复记住的用户名
  const savedUser = localStorage.getItem('mw_remember_user');
  if (savedUser) {
    loginForm.username = savedUser;
    rememberMe.value = true;
  }
});

onBeforeUnmount(() => {
  if (timeTimer) clearInterval(timeTimer);
});
</script>

<style lang="scss" scoped>
.login-page {
  width: 100%;

  .login-footer {
    text-align: center;
    margin-top: 16px;
    font-size: 12px;
    color: #c0c4cc;
  }
}

.caps-lock-warning {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 12px;
  color: #e6a23c;
}

.login-options {
  margin-bottom: 12px;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.verify-code-row {
  display: flex;
  gap: 12px;
  width: 100%;

  .verify-input {
    flex: 1;
  }

  .verify-code-img {
    width: 120px;
    height: 40px;
    cursor: pointer;
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid #dcdfe6;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .loading-text {
      font-size: 12px;
      color: #909399;
    }
  }
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  letter-spacing: 4px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
