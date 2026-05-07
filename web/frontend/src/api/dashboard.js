import request from '@/utils/request';

// 登录
export function login(username, password, code) {
  const data = new URLSearchParams();
  data.append('username', username);
  data.append('password', password);
  if (code) {
    data.append('code', code);
  }
  return request({ url: '/do_login', method: 'post', data });
}

// 登出
export function logout() {
  return request({ url: '/do_logout', method: 'post' });
}

// 检查登录状态
export function checkLogin() {
  return request({ url: '/check_login', method: 'get' });
}

// 获取验证码
export function getVerifyCode() {
  return request({ url: '/code', method: 'get' });
}

// 修改密码
export function changePassword(password1, password2) {
  const data = new URLSearchParams();
  data.append('password1', password1);
  data.append('password2', password2);
  return request({ url: '/setting/set_password', method: 'post', data });
}
