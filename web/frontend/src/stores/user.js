import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { login as loginApi, logout as logoutApi } from '@/api/dashboard';
import router from '@/router';

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('mw_token') || '');
  const username = ref(localStorage.getItem('mw_username') || '');

  const isLogin = computed(() => !!token.value);

  async function login(loginForm) {
    try {
      const res = await loginApi(loginForm.username, loginForm.password, loginForm.code);
      token.value = res.token || res.data?.token || 'logged_in';
      username.value = loginForm.username;
      localStorage.setItem('mw_token', token.value);
      localStorage.setItem('mw_username', username.value);
      return res;
    } catch (error) {
      throw error;
    }
  }

  async function logout() {
    try {
      await logoutApi();
    } catch {
      // 即使接口调用失败也继续清理
    }
    token.value = '';
    username.value = '';
    localStorage.removeItem('mw_token');
    localStorage.removeItem('mw_username');
    router.push('/login');
  }

  function resetState() {
    token.value = '';
    username.value = '';
    localStorage.removeItem('mw_token');
    localStorage.removeItem('mw_username');
  }

  return {
    token,
    username,
    isLogin,
    login,
    logout,
    resetState,
  };
});
