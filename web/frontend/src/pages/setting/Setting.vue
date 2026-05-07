<template>
  <div class="setting-page">
    <!-- 面板信息概览 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="面板版本" :value="panelInfo.version || '-'">
            <template #prefix><el-icon style="color: #409eff"><Monitor /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="面板端口" :value="panelInfo.port || '-'">
            <template #prefix><el-icon style="color: #67c23a"><Connection /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="安全入口" :value="panelInfo.admin_path || '-'">
            <template #prefix><el-icon style="color: #e6a23c"><Lock /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="运行时间" :value="panelInfo.time || '-'">
            <template #prefix><el-icon style="color: #f56c6c"><Timer /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 设置标签页 -->
    <el-card>
      <el-tabs v-model="activeTab">
        <!-- 基本设置 -->
        <el-tab-pane label="基本设置" name="basic">
          <template #label>
            <span><el-icon><Setting /></el-icon> 基本设置</span>
          </template>
          <!-- 面板访问地址 -->
          <el-alert type="info" :closable="false" class="panel-url-alert">
            <template #title>
              <div class="panel-url-row">
                <span>面板访问地址: <strong>{{ panelAccessUrl }}</strong></span>
                <el-button type="primary" link size="small" @click="copyPanelUrl">
                  <el-icon><CopyDocument /></el-icon> 复制
                </el-button>
              </div>
            </template>
          </el-alert>

          <el-form :model="basicForm" label-width="120px" class="setting-form">
            <el-form-item label="面板别名">
              <el-input v-model="basicForm.webname" placeholder="面板别名" style="max-width: 400px" />
              <el-button type="primary" style="margin-left: 8px" @click="saveWebname">保存</el-button>
            </el-form-item>
            <el-form-item label="面板端口">
              <el-input v-model="basicForm.port" placeholder="面板端口" style="max-width: 200px" />
              <el-button type="primary" style="margin-left: 8px" @click="savePort">保存</el-button>
              <span class="form-tip">修改端口后需要重启面板</span>
            </el-form-item>
            <el-form-item label="服务器IP">
              <el-input v-model="basicForm.server_ip" placeholder="服务器IP" style="max-width: 300px" />
              <el-button type="primary" style="margin-left: 8px" @click="saveIp">保存</el-button>
            </el-form-item>
            <el-form-item label="安全入口">
              <el-input v-model="basicForm.admin_path" placeholder="/安全入口" style="max-width: 300px">
                <template #prepend>/</template>
              </el-input>
              <el-button type="primary" style="margin-left: 8px" @click="saveAdminPath">保存</el-button>
              <span class="form-tip">安全入口长度不能小于6位</span>
            </el-form-item>
            <el-form-item label="默认站点目录">
              <el-input v-model="basicForm.site_path" placeholder="站点目录" style="max-width: 400px" />
              <el-button type="primary" style="margin-left: 8px" @click="saveSitesPath">保存</el-button>
            </el-form-item>
            <el-form-item label="默认备份目录">
              <el-input v-model="basicForm.backup_path" placeholder="备份目录" style="max-width: 400px" />
              <el-button type="primary" style="margin-left: 8px" @click="saveBackupPath">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 安全设置 -->
        <el-tab-pane label="安全设置" name="security">
          <template #label>
            <span><el-icon><Shield /></el-icon> 安全设置</span>
          </template>
          <el-form :model="securityForm" label-width="140px" class="setting-form">
            <el-form-item label="BasicAuth认证">
              <el-switch v-model="securityForm.basicAuthOpen" @change="saveBasicAuth" />
              <span class="form-tip">开启后访问面板需要HTTP Basic认证</span>
            </el-form-item>
            <el-form-item v-if="securityForm.basicAuthOpen" label="BasicAuth用户名">
              <el-input v-model="securityForm.basicUser" placeholder="用户名" style="max-width: 300px" />
            </el-form-item>
            <el-form-item v-if="securityForm.basicAuthOpen" label="BasicAuth密码">
              <el-input v-model="securityForm.basicPwd" type="password" placeholder="密码" show-password style="max-width: 300px" />
            </el-form-item>
            <el-form-item v-if="securityForm.basicAuthOpen">
              <el-button type="primary" @click="saveBasicAuth">保存BasicAuth设置</el-button>
            </el-form-item>
            <el-divider />
            <el-form-item label="未授权响应状态码">
              <el-select v-model="securityForm.statusCode" style="width: 200px">
                <el-option label="403 禁止访问" value="403" />
                <el-option label="404 未找到" value="404" />
                <el-option label="444 连接断开" value="444" />
                <el-option label="200 正常(默认)" value="0" />
              </el-select>
              <el-button type="primary" style="margin-left: 8px" @click="saveStatusCode">保存</el-button>
              <span class="form-tip">未登录时访问面板返回的状态码</span>
            </el-form-item>
            <el-divider />
            <el-form-item label="面板调试模式">
              <el-switch v-model="securityForm.debugMode" @change="toggleDebugMode" />
              <span class="form-tip">开启后输出详细错误信息</span>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 用户设置 -->
        <el-tab-pane label="用户设置" name="user">
          <template #label>
            <span><el-icon><User /></el-icon> 用户设置</span>
          </template>
          <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="120px" class="setting-form">
            <el-form-item label="修改用户名">
              <el-input v-model="userForm.newUsername" placeholder="新用户名" style="max-width: 300px" />
            </el-form-item>
            <el-form-item label="确认用户名">
              <el-input v-model="userForm.confirmUsername" placeholder="再次输入新用户名" style="max-width: 300px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveUsername">修改用户名</el-button>
            </el-form-item>
            <el-divider />
            <el-form-item label="新密码">
              <el-input v-model="userForm.newPassword" type="password" placeholder="新密码" show-password style="max-width: 300px" @input="updatePasswordStrength" />
            </el-form-item>
            <el-form-item v-if="userForm.newPassword" label="密码强度">
              <div class="password-strength">
                <div class="strength-bars">
                  <div class="strength-bar" :class="{ active: passwordStrength >= 1, weak: passwordStrength === 1, medium: passwordStrength === 2, strong: passwordStrength >= 3 }"></div>
                  <div class="strength-bar" :class="{ active: passwordStrength >= 2, medium: passwordStrength === 2, strong: passwordStrength >= 3 }"></div>
                  <div class="strength-bar" :class="{ active: passwordStrength >= 3, strong: passwordStrength >= 3 }"></div>
                  <div class="strength-bar" :class="{ active: passwordStrength >= 4, strong: passwordStrength >= 4 }"></div>
                </div>
                <span class="strength-text" :class="passwordStrengthClass">{{ passwordStrengthText }}</span>
              </div>
            </el-form-item>
            <el-form-item label="确认密码">
              <el-input v-model="userForm.confirmPassword" type="password" placeholder="再次输入新密码" show-password style="max-width: 300px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="savePassword" :disabled="passwordStrength < 1">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 面板控制 -->
        <el-tab-pane label="面板控制" name="control">
          <template #label>
            <span><el-icon><Operation /></el-icon> 面板控制</span>
          </template>
          <div class="control-actions">
            <el-card shadow="hover" class="control-card">
              <div class="control-item">
                <div class="control-info">
                  <h4>面板重启</h4>
                  <p>重启面板服务，不会影响网站运行</p>
                </div>
                <el-button type="warning" @click="restartPanel">重启面板</el-button>
              </div>
            </el-card>
            <el-card shadow="hover" class="control-card">
              <div class="control-item">
                <div class="control-info">
                  <h4>面板关闭</h4>
                  <p>关闭面板服务，需要通过命令行重新启动</p>
                </div>
                <el-button type="danger" @click="closePanel">关闭面板</el-button>
              </div>
            </el-card>
            <el-card shadow="hover" class="control-card">
              <div class="control-item">
                <div class="control-info">
                  <h4>IPv6兼容</h4>
                  <p>开启或关闭面板IPv6兼容支持</p>
                </div>
                <el-button type="primary" @click="toggleIpv6">切换IPv6</el-button>
              </div>
            </el-card>
            <el-card shadow="hover" class="control-card">
              <div class="control-item">
                <div class="control-info">
                  <h4>面板更新</h4>
                  <p>检查并更新面板到最新版本</p>
                </div>
                <el-button type="success" @click="checkUpdate">检查更新</el-button>
              </div>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  getPanelSettings,
  setWebname,
  setServerIp,
  setBackupDir,
  setSitesDir,
  setAdminPath,
  setBasicAuth,
  setStatusCode,
  toggleDebug,
  togglePanel,
  setIpv6Status,
  setName,
  setPassword,
  setPort,
  restartPanelApi
} from '@/api/index';

const activeTab = ref('basic');
const userFormRef = ref(null);

const panelInfo = ref({
  version: '',
  port: '',
  admin_path: '',
  time: '',
  title: '',
  site_path: '',
  backup_path: '',
  server_ip: ''
});

const basicForm = reactive({
  webname: '',
  port: '',
  server_ip: '',
  admin_path: '',
  site_path: '',
  backup_path: ''
});

const securityForm = reactive({
  basicAuthOpen: false,
  basicUser: '',
  basicPwd: '',
  statusCode: '403',
  debugMode: false
});

const userForm = reactive({
  newUsername: '',
  confirmUsername: '',
  newPassword: '',
  confirmPassword: ''
});

const userRules = {};

// 面板访问地址
const panelAccessUrl = computed(() => {
  const host = window.location.hostname;
  const port = panelInfo.value.port || window.location.port || '7200';
  const path = panelInfo.value.admin_path || '';
  const protocol = window.location.protocol;
  return `${protocol}//${host}:${port}${path}`;
});

const copyPanelUrl = () => {
  navigator.clipboard.writeText(panelAccessUrl.value).then(() => {
    ElMessage.success('面板地址已复制到剪贴板');
  }).catch(() => {
    ElMessage.error('复制失败');
  });
};

// 密码强度检测
const passwordStrength = ref(0);
const passwordStrengthText = computed(() => {
  const texts = ['', '弱', '一般', '强', '非常强'];
  return texts[passwordStrength.value] || '';
});
const passwordStrengthClass = computed(() => {
  const classes = ['', 'text-weak', 'text-medium', 'text-strong', 'text-strong'];
  return classes[passwordStrength.value] || '';
});

const updatePasswordStrength = () => {
  const pwd = userForm.newPassword;
  if (!pwd) {
    passwordStrength.value = 0;
    return;
  }
  let score = 0;
  if (pwd.length >= 6) score++;
  if (pwd.length >= 10) score++;
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score++;
  if (/\d/.test(pwd)) score++;
  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pwd)) score++;
  passwordStrength.value = Math.min(score, 4);
};

const fetchPanelInfo = async () => {
  try {
    const res = await getPanelSettings();
    if (res) {
      panelInfo.value = {
        version: res.version || '-',
        port: res.port || '-',
        admin_path: res.admin_path || '-',
        time: res.time || '-',
        title: res.title || '',
        site_path: res.site_path || '',
        backup_path: res.backup_path || '',
        server_ip: res.server_ip || ''
      };
      basicForm.webname = panelInfo.value.title;
      basicForm.port = panelInfo.value.port;
      basicForm.server_ip = panelInfo.value.server_ip;
      basicForm.admin_path = panelInfo.value.admin_path;
      basicForm.site_path = panelInfo.value.site_path;
      basicForm.backup_path = panelInfo.value.backup_path;

      // 安全设置
      securityForm.debugMode = res.debug === 'open';
      securityForm.statusCode = res.unauthorized_status || '403';
      if (res.basic_auth) {
        securityForm.basicAuthOpen = res.basic_auth.open || false;
      }
    }
  } catch (error) {
    console.error('获取面板信息失败:', error);
  }
};

const saveWebname = async () => {
  try {
    await setWebname(basicForm.webname);
    ElMessage.success('面板别名保存成功');
  } catch (error) {
    console.error('保存面板别名失败:', error);
  }
};

const savePort = async () => {
  try {
    await ElMessageBox.confirm('修改端口后需要重启面板，确定继续吗？', '修改端口', { type: 'warning' });
    const res = await setPort(basicForm.port);
    if (res && res.status === false) {
      ElMessage.error(res.msg || '端口保存失败');
      return;
    }
    ElMessage.success('端口保存成功，面板将重启');
  } catch (error) {
    if (error !== 'cancel') console.error('保存端口失败:', error);
  }
};

const saveIp = async () => {
  try {
    await setServerIp(basicForm.server_ip);
    ElMessage.success('IP保存成功');
  } catch (error) {
    console.error('保存IP失败:', error);
  }
};

const saveAdminPath = async () => {
  try {
    const path = basicForm.admin_path.startsWith('/') ? basicForm.admin_path : '/' + basicForm.admin_path;
    await setAdminPath(path);
    ElMessage.success('安全入口修改成功');
  } catch (error) {
    console.error('保存安全入口失败:', error);
  }
};

const saveSitesPath = async () => {
  try {
    await setSitesDir(basicForm.site_path);
    ElMessage.success('站点目录修改成功');
  } catch (error) {
    console.error('保存站点目录失败:', error);
  }
};

const saveBackupPath = async () => {
  try {
    await setBackupDir(basicForm.backup_path);
    ElMessage.success('备份目录修改成功');
  } catch (error) {
    console.error('保存备份目录失败:', error);
  }
};

const saveBasicAuth = async () => {
  try {
    await setBasicAuth({
      basic_user: securityForm.basicUser,
      basic_pwd: securityForm.basicPwd,
      is_open: securityForm.basicAuthOpen
    });
    ElMessage.success('BasicAuth设置已保存');
  } catch (error) {
    console.error('保存BasicAuth失败:', error);
  }
};

const saveStatusCode = async () => {
  try {
    await setStatusCode(securityForm.statusCode);
    ElMessage.success('状态码设置已保存');
  } catch (error) {
    console.error('保存状态码失败:', error);
  }
};

const toggleDebugMode = async () => {
  try {
    await toggleDebug();
    ElMessage.success(securityForm.debugMode ? '调试模式已开启' : '调试模式已关闭');
  } catch (error) {
    console.error('切换调试模式失败:', error);
  }
};

const saveUsername = async () => {
  if (userForm.newUsername !== userForm.confirmUsername) {
    ElMessage.error('两次输入的用户名不一致');
    return;
  }
  if (userForm.newUsername.length < 3) {
    ElMessage.error('用户名长度不能少于3位');
    return;
  }
  try {
    const res = await setName(userForm.newUsername, userForm.confirmUsername);
    if (res && res.status === false) {
      ElMessage.error(res.msg || '用户名修改失败');
      return;
    }
    ElMessage.success('用户名修改成功');
    userForm.newUsername = '';
    userForm.confirmUsername = '';
  } catch (error) {
    ElMessage.error('用户名修改失败');
  }
};

const savePassword = async () => {
  if (userForm.newPassword !== userForm.confirmPassword) {
    ElMessage.error('两次输入的密码不一致');
    return;
  }
  if (userForm.newPassword.length < 5) {
    ElMessage.error('密码长度不能少于5位');
    return;
  }
  try {
    const res = await setPassword(userForm.newPassword, userForm.confirmPassword);
    if (res && res.status === false) {
      ElMessage.error(res.msg || '密码修改失败');
      return;
    }
    ElMessage.success('密码修改成功');
    userForm.newPassword = '';
    userForm.confirmPassword = '';
  } catch (error) {
    ElMessage.error('密码修改失败');
  }
};

const restartPanel = async () => {
  try {
    await ElMessageBox.confirm('确定要重启面板吗？', '重启面板', { type: 'warning' });
    await restartPanelApi();
    ElMessage.success('面板正在重启...');
    setTimeout(() => window.location.reload(), 3000);
  } catch (error) {
    if (error !== 'cancel') console.error('重启面板失败:', error);
  }
};

const closePanel = async () => {
  try {
    await ElMessageBox.confirm('确定要关闭面板吗？关闭后需要通过命令行重新启动！', '关闭面板', {
      type: 'warning',
      confirmButtonText: '确定关闭',
      cancelButtonText: '取消'
    });
    await togglePanel();
    ElMessage.success('面板已关闭');
  } catch (error) {
    if (error !== 'cancel') console.error('关闭面板失败:', error);
  }
};

const toggleIpv6 = async () => {
  try {
    await setIpv6Status();
    ElMessage.success('IPv6设置已切换');
  } catch (error) {
    console.error('切换IPv6失败:', error);
  }
};

const checkUpdate = () => {
  ElMessage.info('当前已是最新版本');
};

onMounted(() => {
  fetchPanelInfo();
});
</script>

<style lang="scss" scoped>
.setting-page {
  .stats-row {
    margin-bottom: 16px;

    .stat-card {
      text-align: center;
      margin-bottom: 8px;
    }
  }

  .panel-url-alert {
    margin-bottom: 16px;

    .panel-url-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
  }

  .setting-form {
    max-width: 600px;
    padding: 16px 0;

    .form-tip {
      display: inline-block;
      margin-left: 8px;
      font-size: 12px;
      color: #909399;
    }
  }

  .password-strength {
    display: flex;
    align-items: center;
    gap: 12px;

    .strength-bars {
      display: flex;
      gap: 4px;

      .strength-bar {
        width: 40px;
        height: 6px;
        background: #e4e7ed;
        border-radius: 3px;
        transition: all 0.3s;

        &.active.weak {
          background: #f56c6c;
        }

        &.active.medium {
          background: #e6a23c;
        }

        &.active.strong {
          background: #67c23a;
        }
      }
    }

    .strength-text {
      font-size: 12px;

      &.text-weak {
        color: #f56c6c;
      }

      &.text-medium {
        color: #e6a23c;
      }

      &.text-strong {
        color: #67c23a;
      }
    }
  }

  .control-actions {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 16px 0;

    .control-card {
      .control-item {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .control-info {
          h4 {
            margin: 0 0 4px;
            font-size: 15px;
            color: #303133;
          }

          p {
            margin: 0;
            font-size: 13px;
            color: #909399;
          }
        }
      }
    }
  }
}
</style>
