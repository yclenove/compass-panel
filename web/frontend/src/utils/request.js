import axios from 'axios';
import { ElMessage } from 'element-plus';

// 检测安全入口路径
function getAdminPath() {
  // 从当前 URL 路径中提取安全入口
  const path = window.location.pathname;
  // 匹配 /<8位安全入口>/vue/... 模式
  const match = path.match(/^\/([a-zA-Z0-9]{8})\//);
  if (match) {
    return '/' + match[1];
  }
  return '';
}

const adminPath = getAdminPath();

// 创建 Axios 实例
// API 路由不需要安全入口前缀，直接使用根路径
const service = axios.create({
  baseURL: '/',
  timeout: 30000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
});

// 请求拦截器：添加 token
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('mw_token');
    if (token) {
      if (config.data instanceof URLSearchParams) {
        config.data.append('token', token);
      } else if (config.data && typeof config.data === 'object' && !(config.data instanceof FormData)) {
        config.data.token = token;
      } else if (!config.data) {
        const params = new URLSearchParams();
        params.append('token', token);
        config.data = params;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理错误
service.interceptors.response.use(
  (response) => {
    const res = response.data;

    // 后端返回错误状态处理 (status === false 或 status === -1)
    if (res.status === false || res.status === -1 || res.code === -1) {
      ElMessage.error(res.msg || res.data || '请求失败');
      return Promise.reject(new Error(res.msg || '请求失败'));
    }

    // 401 未授权，跳转登录
    if (res.status === 401 || res.code === 401) {
      ElMessage.error('登录已过期，请重新登录');
      localStorage.removeItem('mw_token');
      localStorage.removeItem('mw_username');
      window.location.href = adminPath + '/vue/login';
      return Promise.reject(new Error('未授权'));
    }

    return res;
  },

  (error) => {
    if (error.response) {
      const status = error.response.status;
      switch (status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录');
          localStorage.removeItem('mw_token');
          localStorage.removeItem('mw_username');
          window.location.href = adminPath + '/vue/login';
          break;
        case 403:
          // 面板未登录返回 403，重定向到登录页
          localStorage.removeItem('mw_token');
          localStorage.removeItem('mw_username');
          window.location.href = adminPath + '/vue/login';
          break;
        case 404:
          ElMessage.error('请求的资源不存在');
          break;
        case 500:
          ElMessage.error('服务器内部错误');
          break;
        default:
          ElMessage.error(`请求错误: ${status}`);
      }
    } else if (error.message.includes('timeout')) {
      ElMessage.error('请求超时，请稍后重试');
    } else {
      ElMessage.error('网络异常，请检查网络连接');
    }
    return Promise.reject(error);
  }
);

export default service;
