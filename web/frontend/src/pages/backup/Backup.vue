<template>
  <div class="page-container">
    <div class="page-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="备份列表" name="list">
          <div class="toolbar">
            <el-button type="primary" @click="showCreate = true">创建备份</el-button>
            <el-select v-model="filterType" @change="loadBackups" placeholder="全部类型" clearable style="width:120px">
              <el-option label="网站" value="site" /><el-option label="数据库" value="database" /><el-option label="目录" value="directory" />
            </el-select>
            <el-button @click="loadBackups" :loading="loading">刷新</el-button>
          </div>
          <el-table :data="backups" stripe v-loading="loading" empty-text="暂无备份">
            <el-table-column prop="name" label="文件名" min-width="250" show-overflow-tooltip />
            <el-table-column label="大小" width="100">
              <template #default="{ row }">{{ row.size ? (row.size / 1024 / 1024).toFixed(1) + ' MB' : '-' }}</template>
            </el-table-column>
            <el-table-column prop="mtime" label="时间" width="170" />
            <el-table-column label="操作" width="180" align="center">
              <template #default="{ row }">
                <el-button size="small" @click="onShowRestore(row)">恢复</el-button>
                <el-popconfirm title="确定删除此备份?" @confirm="onDelete(row)">
                  <template #reference><el-button size="small" type="danger">删除</el-button></template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="云存储" name="cloud">
          <el-table :data="cloudProviders" stripe empty-text="暂无云存储配置">
            <el-table-column prop="name" label="提供商" width="160" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="small" @click="onShowCloudConfig(row)">配置</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <!-- Create Backup Dialog -->
      <el-dialog v-model="showCreate" title="创建备份" width="450px" @closed="resetCreateForm">
        <el-form :model="createForm" label-width="80px">
          <el-form-item label="类型" required>
            <el-select v-model="createForm.type"><el-option label="网站" value="site" /><el-option label="数据库" value="database" /><el-option label="目录" value="directory" /></el-select>
          </el-form-item>
          <el-form-item label="目标" required>
            <el-select v-if="createForm.type === 'site'" v-model="createForm.target" filterable placeholder="选择站点" style="width:100%">
              <el-option v-for="s in siteList" :key="s" :label="s" :value="s" />
            </el-select>
            <el-select v-else-if="createForm.type === 'database'" v-model="createForm.target" filterable placeholder="选择数据库" style="width:100%">
              <el-option v-for="d in dbList" :key="d" :label="d" :value="d" />
            </el-select>
            <div v-else class="dir-picker">
              <el-input v-model="createForm.target" placeholder="目录路径，如 /www/wwwroot" />
              <el-button @click="browseDir('createForm')" style="margin-left:8px">浏览</el-button>
            </div>
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="createForm.remark" placeholder="备份说明（可选）" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showCreate = false">取消</el-button>
          <el-button type="primary" @click="onCreate" :loading="creating">创建备份</el-button>
        </template>
      </el-dialog>

      <!-- Restore Dialog -->
      <el-dialog v-model="showRestore" title="恢复备份" width="400px">
        <el-form label-width="80px">
          <el-form-item label="备份文件">{{ restoreFile }}</el-form-item>
          <el-form-item label="恢复到" required>
            <el-input v-model="restorePath" placeholder="输入目标路径" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showRestore = false">取消</el-button>
          <el-button type="primary" @click="onRestore" :loading="restoring">恢复</el-button>
        </template>
      </el-dialog>

      <!-- Cloud Config Dialog -->
      <el-dialog v-model="showCloudConfig" :title="'配置云存储 - ' + cloudConfigName" width="500px">
        <el-form label-width="120px">
          <el-form-item v-for="key in cloudConfigKeys" :key="key" :label="key" required>
            <el-input v-model="cloudConfigValues[key]" :placeholder="'输入' + key" :type="key.includes('secret') || key.includes('key') || key.includes('password') ? 'password' : 'text'" show-password />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showCloudConfig = false">取消</el-button>
          <el-button type="primary" @click="onSaveCloudConfig" :loading="cloudSaving">保存</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';

async function api(url, data = {}) {
  const resp = await request.post(url, data);
  if (resp.data?.status === false) throw new Error(resp.data.msg || '请求失败');
  return resp.data?.data || resp.data || {};
}

const activeTab = ref('list');
const loading = ref(false);
const backups = ref([]);
const filterType = ref('');
const cloudProviders = ref([]);
const siteList = ref([]);
const dbList = ref([]);

// Load site and database lists for backup target selection
async function loadSiteNames() {
  try {
    const d = await api('/site/list', { p: '1', limit: '200' });
    siteList.value = (d?.data || d?.sites || []).map(s => s.name || s.site_name || s);
  } catch (e) { console.error('加载站点列表失败:', e); }
}
async function loadDbNames() {
  try {
    const d = await api('/database/mysql/databases');
    dbList.value = d?.databases || [];
  } catch (e) { console.error('加载数据库列表失败:', e); }
}
async function browseDir() {
  try {
    const d = await api('/files/get_dir', { path: createForm.target || '/www', showHidden: '0' });
    const dirs = (d?.dir || []).map(item => {
      const parts = typeof item === 'string' ? item.split(';') : [];
      return parts[0] || '';
    }).filter(n => n && n !== '.' && n !== '..');
    if (dirs.length > 0) {
      const currentPath = createForm.target || '/www';
      ElMessage.info(`当前目录: ${currentPath}, 子目录: ${dirs.slice(0, 10).join(', ')}${dirs.length > 10 ? '...' : ''}`);
    }
  } catch (e) { ElMessage.error('浏览目录失败'); }
}

async function loadBackups() {
  loading.value = true;
  try {
    const d = await api('/backup/list_backups', { type: filterType.value });
    backups.value = d?.backups || [];
  } finally { loading.value = false; }
}

// Create
const showCreate = ref(false);
const creating = ref(false);
const createForm = reactive({ type: 'site', target: '', cloud: '', remark: '' });
function resetCreateForm() { createForm.type = 'site'; createForm.target = ''; createForm.cloud = ''; createForm.remark = ''; }

async function onCreate() {
  if (!createForm.target) { ElMessage.warning('请输入备份目标'); return; }
  creating.value = true;
  try {
    await api('/backup/create_backup', { type: createForm.type, target: createForm.target, cloud: createForm.cloud });
    ElMessage.success('备份创建成功');
    showCreate.value = false;
    await loadBackups();
  } catch (e) { ElMessage.error(e.message); }
  finally { creating.value = false; }
}

// Delete
async function onDelete(row) {
  try {
    await api('/backup/delete_backup', { file: row.path });
    ElMessage.success('备份已删除');
    await loadBackups();
  } catch (e) { ElMessage.error(e.message); }
}

// Restore
const showRestore = ref(false);
const restoring = ref(false);
const restoreFile = ref('');
const restorePath = ref('');

function onShowRestore(row) {
  restoreFile.value = row.name;
  restorePath.value = '';
  showRestore.value = true;
}
async function onRestore() {
  if (!restorePath.value) { ElMessage.warning('请输入恢复路径'); return; }
  restoring.value = true;
  try {
    await api('/backup/restore', { file: restoreFile.value, path: restorePath.value, name: restoreFile.value });
    ElMessage.success('恢复完成');
    showRestore.value = false;
  } catch (e) { ElMessage.error(e.message); }
  finally { restoring.value = false; }
}

// Cloud
const showCloudConfig = ref(false);
const cloudConfigName = ref('');
const cloudConfigKeys = ref([]);
const cloudConfigValues = reactive({});
const cloudSaving = ref(false);

async function loadCloud() {
  try {
    const d = await api('/backup/providers');
    cloudProviders.value = Object.entries(d?.providers || {}).map(([k, v]) => ({ key: k, ...v }));
  } catch (e) { console.error('加载云存储提供商失败:', e); }
}
function onShowCloudConfig(row) {
  cloudConfigName.value = row.name;
  cloudConfigKeys.value = row.config_keys || [];
  for (const k of cloudConfigKeys.value) cloudConfigValues[k] = '';
  showCloudConfig.value = true;
}
async function onSaveCloudConfig() {
  cloudSaving.value = true;
  try {
    const provider = cloudProviders.value.find(p => p.name === cloudConfigName.value);
    if (!provider) throw new Error('提供商不存在');
    const data = { provider: provider.key };
    for (const k of cloudConfigKeys.value) data[k] = cloudConfigValues[k] || '';
    await api('/backup/save_config', data);
    ElMessage.success('云存储配置已保存');
    showCloudConfig.value = false;
  } catch (e) { ElMessage.error(e.message); }
  finally { cloudSaving.value = false; }
}

onMounted(() => { loadBackups(); loadCloud(); loadSiteNames(); loadDbNames(); });
</script>

<style lang="scss" scoped>
.toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.dir-picker { display: flex; align-items: center; width: 100%; }
</style>
