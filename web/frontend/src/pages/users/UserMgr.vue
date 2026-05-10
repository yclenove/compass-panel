<template>
  <div class="page-container">
    <div class="page-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="用户列表" name="users">
          <div class="toolbar">
            <el-button type="primary" @click="showAddUser = true">添加用户</el-button>
            <el-button @click="loadUsers" :loading="loading">刷新</el-button>
          </div>
          <el-table :data="users" stripe v-loading="loading" empty-text="暂无用户">
            <el-table-column prop="name" label="用户名" width="150" />
            <el-table-column prop="role" label="角色" width="100" />
            <el-table-column prop="email" label="邮箱" min-width="180" />
            <el-table-column label="操作" width="180" align="center">
              <template #default="{ row }">
                <el-button size="small" @click="onShowChangePwd(row)">改密</el-button>
                <el-popconfirm title="确定删除此用户?" @confirm="onDelUser(row)">
                  <template #reference><el-button size="small" type="danger">删除</el-button></template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="API密钥" name="apikeys">
          <div class="toolbar">
            <el-button type="primary" @click="showCreateApiKey = true">创建API密钥</el-button>
          </div>
          <el-table :data="apiKeys" stripe empty-text="暂无API密钥">
            <el-table-column prop="name" label="名称" width="180" />
            <el-table-column prop="app_id" label="App ID" min-width="200" />
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-popconfirm title="确定删除此密钥?" @confirm="onDelApiKey(row)">
                  <template #reference><el-button size="small" type="danger">删除</el-button></template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <!-- Add User Dialog -->
      <el-dialog v-model="showAddUser" title="添加用户" width="400px" @closed="resetAddUserForm">
        <el-form :model="addUserForm" label-width="80px">
          <el-form-item label="用户名" required><el-input v-model="addUserForm.name" placeholder="至少3个字符" /></el-form-item>
          <el-form-item label="密码" required>
            <el-input v-model="addUserForm.password" type="password" placeholder="至少5个字符" show-password @input="checkPwdStrength(addUserForm.password)" />
            <div class="pwd-strength" v-if="addUserForm.password">
              <div class="pwd-bar" :class="pwdStrengthClass"></div>
              <span class="pwd-text" :class="pwdStrengthClass">{{ pwdStrengthText }}</span>
            </div>
          </el-form-item>
          <el-form-item label="邮箱"><el-input v-model="addUserForm.email" placeholder="选填" /></el-form-item>
          <el-form-item label="角色"><el-select v-model="addUserForm.role"><el-option label="普通用户" value="user" /><el-option label="管理员" value="admin" /></el-select></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showAddUser = false">取消</el-button>
          <el-button type="primary" @click="onAddUser" :loading="saving">添加</el-button>
        </template>
      </el-dialog>

      <!-- Change Password Dialog -->
      <el-dialog v-model="showChangePwd" title="修改密码" width="350px" @closed="changePwdTarget = ''; changePwdNew = '';">
        <el-form label-width="80px">
          <el-form-item label="用户">{{ changePwdTarget }}</el-form-item>
          <el-form-item label="新密码" required><el-input v-model="changePwdNew" type="password" placeholder="至少5个字符" show-password /></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showChangePwd = false">取消</el-button>
          <el-button type="primary" @click="onChangePwd" :loading="saving">确认</el-button>
        </template>
      </el-dialog>

      <!-- Create API Key Dialog -->
      <el-dialog v-model="showCreateApiKey" title="创建API密钥" width="450px" @closed="resetApiKeyForm">
        <el-form :model="apiKeyForm" label-width="100px">
          <el-form-item label="名称" required><el-input v-model="apiKeyForm.name" placeholder="应用名称" /></el-form-item>
          <el-form-item label="IP白名单"><el-input v-model="apiKeyForm.ipWhitelist" placeholder="逗号分隔，留空不限制" /></el-form-item>
        </el-form>
        <div v-if="newApiKeyResult.app_id" class="key-result">
          <el-alert type="success" title="密钥创建成功！请保存以下信息，关闭后将无法查看Secret" :closable="false" />
          <p><strong>App ID:</strong> <code>{{ newApiKeyResult.app_id }}</code></p>
          <p><strong>App Secret:</strong> <code>{{ newApiKeyResult.app_secret }}</code></p>
        </div>
        <template #footer>
          <el-button @click="showCreateApiKey = false">关闭</el-button>
          <el-button v-if="!newApiKeyResult.app_id" type="primary" @click="onCreateApiKey" :loading="saving">创建</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';

async function api(url, data = {}) {
  const resp = await request.post(url, data);
  if (resp.data?.status === false) throw new Error(resp.data.msg || '请求失败');
  return resp.data?.data || resp.data || {};
}

const activeTab = ref('users');
const pwdStrength = ref(0);
const pwdStrengthText = computed(() => ['', '弱', '一般', '强', '非常强'][pwdStrength.value] || '');
const pwdStrengthClass = computed(() => ['', 'weak', 'medium', 'strong', 'very-strong'][pwdStrength.value] || '');
function checkPwdStrength(pwd) {
  if (!pwd) { pwdStrength.value = 0; return; }
  let s = 0;
  if (pwd.length >= 6) s++;
  if (pwd.length >= 10) s++;
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) s++;
  if (/\d/.test(pwd) && /[!@#$%^&*]/.test(pwd)) s++;
  pwdStrength.value = Math.min(s, 4);
}
const loading = ref(false);
const saving = ref(false);
const users = ref([]);
const apiKeys = ref([]);

async function loadUsers() {
  loading.value = true;
  try {
    const d = await api('/users/list');
    users.value = d?.users || [];
  } finally { loading.value = false; }
}
async function loadApiKeys() {
  try {
    const d = await api('/users/api_keys');
    apiKeys.value = d?.keys || [];
  } catch (e) { console.error('加载API密钥失败:', e); }
}

// Add user
const showAddUser = ref(false);
const addUserForm = reactive({ name: '', password: '', email: '', role: 'user' });
function resetAddUserForm() { addUserForm.name = ''; addUserForm.password = ''; addUserForm.email = ''; addUserForm.role = 'user'; }

async function onAddUser() {
  if (!addUserForm.name || addUserForm.name.length < 3) { ElMessage.warning('用户名至少3个字符'); return; }
  if (!addUserForm.password || addUserForm.password.length < 5) { ElMessage.warning('密码至少5个字符'); return; }
  saving.value = true;
  try {
    await api('/users/add', { username: addUserForm.name, password: addUserForm.password, email: addUserForm.email, role: addUserForm.role });
    ElMessage.success('用户添加成功');
    showAddUser.value = false;
    await loadUsers();
  } catch (e) { ElMessage.error(e.message); }
  finally { saving.value = false; }
}

// Delete user
async function onDelUser(row) {
  try {
    await api('/users/delete', { username: row.name });
    ElMessage.success('用户已删除');
    await loadUsers();
  } catch (e) { ElMessage.error(e.message); }
}

// Change password
const showChangePwd = ref(false);
const changePwdTarget = ref('');
const changePwdNew = ref('');

function onShowChangePwd(row) { changePwdTarget.value = row.name; changePwdNew.value = ''; showChangePwd.value = true; }
async function onChangePwd() {
  if (!changePwdNew.value || changePwdNew.value.length < 5) { ElMessage.warning('密码至少5个字符'); return; }
  saving.value = true;
  try {
    await api('/users/change_password', { username: changePwdTarget.value, password: changePwdNew.value });
    ElMessage.success('密码已修改');
    showChangePwd.value = false;
  } catch (e) { ElMessage.error(e.message); }
  finally { saving.value = false; }
}

// API keys
const showCreateApiKey = ref(false);
const apiKeyForm = reactive({ name: '', ipWhitelist: '' });
const newApiKeyResult = ref({});
function resetApiKeyForm() { apiKeyForm.name = ''; apiKeyForm.ipWhitelist = ''; newApiKeyResult.value = {}; }

async function onCreateApiKey() {
  if (!apiKeyForm.name) { ElMessage.warning('请输入名称'); return; }
  saving.value = true;
  try {
    const d = await api('/users/create_api_key', { name: apiKeyForm.name, ip_whitelist: apiKeyForm.ipWhitelist });
    newApiKeyResult.value = d;
    await loadApiKeys();
  } catch (e) { ElMessage.error(e.message); }
  finally { saving.value = false; }
}
async function onDelApiKey(row) {
  try {
    await api('/users/delete_api_key', { app_id: row.app_id });
    ElMessage.success('API密钥已删除');
    await loadApiKeys();
  } catch (e) { ElMessage.error(e.message); }
}

onMounted(() => { loadUsers(); loadApiKeys(); });
</script>

<style lang="scss" scoped>
.toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.key-result { margin-top: 12px; padding: 12px; background: #f0f9eb; border-radius: 4px; }
.key-result p { margin: 4px 0; word-break: break-all; }
.key-result code { background: #e6f7d4; padding: 2px 6px; border-radius: 2px; font-size: 12px; }
.pwd-strength { display: flex; align-items: center; gap: 8px; margin-top: 4px; }
.pwd-bar { width: 100px; height: 4px; border-radius: 2px; background: #e4e7ed; transition: all 0.3s;
  &.weak { width: 25px; background: #f56c6c; }
  &.medium { width: 50px; background: #e6a23c; }
  &.strong { width: 75px; background: #67c23a; }
  &.very-strong { width: 100px; background: #00b894; }
}
.pwd-text { font-size: 12px;
  &.weak { color: #f56c6c; }
  &.medium { color: #e6a23c; }
  &.strong { color: #67c23a; }
  &.very-strong { color: #00b894; }
}
</style>
