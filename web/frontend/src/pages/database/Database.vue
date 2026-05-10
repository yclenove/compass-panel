<template>
  <div class="page-container">
    <div class="page-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="MySQL" name="mysql">
          <!-- MySQL 未安装引导 -->
          <el-card v-if="!mysqlRunning && !mysqlChecked" class="install-guide-card" shadow="hover">
            <div class="install-guide">
              <el-icon :size="48" color="#4479A1"><Coin /></el-icon>
              <h2>MySQL 未安装或未运行</h2>
              <p>MySQL 是流行的开源关系型数据库。请先安装 MySQL 后再使用。</p>
              <el-space style="margin-top: 16px">
                <el-button type="primary" size="large" @click="installDatabase('mysql')" :loading="mysqlInstalling">
                  <el-icon><Download /></el-icon> 一键安装 MySQL
                </el-button>
                <el-button size="large" @click="mysqlCheckStatus" :loading="mysqlStatusLoading">
                  <el-icon><Refresh /></el-icon> 检查状态
                </el-button>
              </el-space>
              <div v-if="mysqlInstallMsg" style="margin-top:12px;color:#409eff">{{ mysqlInstallMsg }}</div>
            </div>
          </el-card>

          <div v-else>
          <div class="toolbar">
            <el-tag :type="mysqlRunning ? 'success' : 'danger'">{{ mysqlRunning ? '运行中 v'+mysqlVersion : '未运行' }}</el-tag>
            <el-button type="primary" @click="mysqlShowCreate=true">创建数据库</el-button>
            <el-button @click="mysqlLoadUsers">用户管理</el-button>
            <el-button @click="mysqlLoadDbs">刷新</el-button>
          </div>
          <el-table :data="mysqlDbs" stripe v-loading="mysqlLoading" empty-text="暂无数据库">
            <el-table-column prop="name" label="数据库名" min-width="150" />
            <el-table-column label="操作" width="300" align="center">
              <template #default="{ row }">
                <el-button size="small" @click="mysqlBackup(row)">备份</el-button>
                <el-popconfirm title="确定删除此数据库?" @confirm="mysqlDrop(row)">
                  <template #reference><el-button size="small" type="danger">删除</el-button></template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
          <el-dialog v-model="mysqlShowCreate" title="创建MySQL数据库" width="400px">
            <el-form label-width="80px">
              <el-form-item label="数据库名" required><el-input v-model="mysqlNew.name" placeholder="mydb" /></el-form-item>
              <el-form-item label="字符集"><el-select v-model="mysqlNew.charset"><el-option label="utf8mb4" value="utf8mb4" /><el-option label="utf8" value="utf8" /><el-option label="gbk" value="gbk" /></el-select></el-form-item>
              <el-form-item label="创建用户"><el-input v-model="mysqlNew.username" placeholder="可选" /></el-form-item>
              <el-form-item label="用户密码"><el-input v-model="mysqlNew.password" type="password" placeholder="可选" show-password /></el-form-item>
            </el-form>
            <template #footer><el-button @click="mysqlShowCreate=false">取消</el-button><el-button type="primary" @click="mysqlCreate" :loading="mysqlSaving">创建</el-button></template>
          </el-dialog>
          <el-dialog v-model="mysqlShowUsers" title="MySQL用户管理" width="500px">
            <el-table :data="mysqlUsers" stripe><el-table-column prop="User" label="用户名" /><el-table-column prop="Host" label="主机" />
              <el-table-column label="操作" width="120"><template #default="{ row }"><el-popconfirm title="确定删除?" @confirm="mysqlDelUser(row)"><template #reference><el-button size="small" type="danger">删除</el-button></template></el-popconfirm></template></el-table-column>
            </el-table>
            <div style="margin-top:12px"><el-input v-model="mysqlNewUser.name" placeholder="用户名" style="width:120px" /><el-input v-model="mysqlNewUser.pwd" type="password" placeholder="密码" style="width:150px;margin-left:8px" show-password /><el-button style="margin-left:8px" @click="mysqlCreateUser">创建用户</el-button></div>
          </el-dialog>
          </div>
        </el-tab-pane>
        <el-tab-pane label="PostgreSQL" name="pgsql">
          <!-- PostgreSQL 未安装引导 -->
          <el-card v-if="!pgsqlRunning && !pgsqlChecked" class="install-guide-card" shadow="hover">
            <div class="install-guide">
              <el-icon :size="48" color="#336791"><Coin /></el-icon>
              <h2>PostgreSQL 未安装或未运行</h2>
              <p>PostgreSQL 是强大的开源对象关系型数据库。请先安装后再使用。</p>
              <el-button type="primary" size="large" @click="installDatabase('postgresql')" :loading="pgsqlInstalling">
                <el-icon><Download /></el-icon> 一键安装 PostgreSQL
              </el-button>
            </div>
          </el-card>

          <div v-else>
          <div class="toolbar">
            <el-button type="primary" @click="pgsqlCreate">创建数据库</el-button>
            <el-button @click="pgsqlListUsers">用户管理</el-button>
            <el-tag :type="pgsqlRunning ? 'success' : 'danger'">{{ pgsqlRunning ? '运行中' : '未运行' }}</el-tag>
            <span v-if="pgsqlVersion" class="version">v{{ pgsqlVersion }}</span>
          </div>
          <el-table :data="pgsqlDbs" stripe>
            <el-table-column prop="name" label="数据库名" />
            <el-table-column label="操作" width="300">
              <template #default="{ row }">
                <el-button size="small" @click="pgsqlBackup(row)">备份</el-button>
                <el-button size="small" type="danger" @click="pgsqlDrop(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          </div>
        </el-tab-pane>
        <el-tab-pane label="Redis" name="redis">
          <!-- Redis 未安装引导 -->
          <el-card v-if="!redisRunning && !redisChecked" class="install-guide-card" shadow="hover">
            <div class="install-guide">
              <el-icon :size="48" color="#DC382D"><Coin /></el-icon>
              <h2>Redis 未安装或未运行</h2>
              <p>Redis 是高性能的内存键值数据库，常用于缓存和会话存储。</p>
              <el-button type="primary" size="large" style="margin-top: 16px" @click="installDatabase('redis')" :loading="redisInstalling">
                <el-icon><Download /></el-icon> 一键安装 Redis
              </el-button>
            </div>
          </el-card>

          <div v-else>
          <div class="toolbar">
            <el-tag :type="redisRunning ? 'success' : 'danger'">{{ redisRunning ? '运行中' : '未运行' }}</el-tag>
            <span v-if="redisInfo.memory">内存: {{ redisInfo.memory }}</span>
            <span v-if="redisInfo.keys">键数: {{ redisInfo.keys }}</span>
            <el-button @click="redisScan">扫描Key</el-button>
            <el-button @click="redisFlush" type="danger">清空数据库</el-button>
          </div>
          <div class="redis-ops">
            <el-input v-model="redisKey" placeholder="Key" style="width:200px" />
            <el-input v-model="redisValue" placeholder="Value" style="width:300px" />
            <el-button @click="redisGet">获取</el-button>
            <el-button @click="redisSet" type="primary">设置</el-button>
            <el-button @click="redisDel">删除</el-button>
          </div>
          <el-input v-model="redisResult" type="textarea" :rows="6" readonly />
          </div>
        </el-tab-pane>
        <el-tab-pane label="MongoDB" name="mongo">
          <!-- MongoDB 未安装引导 -->
          <el-card v-if="!mongoRunning && !mongoChecked" class="install-guide-card" shadow="hover">
            <div class="install-guide">
              <el-icon :size="48" color="#47A248"><Coin /></el-icon>
              <h2>MongoDB 未安装或未运行</h2>
              <p>MongoDB 是流行的 NoSQL 文档数据库。</p>
              <el-button type="primary" size="large" style="margin-top: 16px" @click="installDatabase('mongodb')" :loading="mongoInstalling">
                <el-icon><Download /></el-icon> 一键安装 MongoDB
              </el-button>
            </div>
          </el-card>

          <div v-else>
          <div class="toolbar">
            <el-tag :type="mongoRunning ? 'success' : 'danger'">{{ mongoRunning ? '运行中' : '未运行' }}</el-tag>
            <el-button type="primary" @click="mongoCreate">创建数据库</el-button>
          </div>
          <el-table :data="mongoDbs" stripe>
            <el-table-column prop="name" label="数据库" />
            <el-table-column prop="size" label="大小" :formatter="sizeFmt" />
            <el-table-column label="操作" width="250">
              <template #default="{ row }">
                <el-button size="small" @click="mongoListCols(row)">集合</el-button>
                <el-button size="small" @click="mongoBackup(row)">备份</el-button>
                <el-button size="small" type="danger" @click="mongoDrop(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          </div>
        </el-tab-pane>
        <el-tab-pane label="phpMyAdmin" name="pma">
          <div class="toolbar">
            <el-tag :type="pmaInstalled ? 'success' : 'info'">{{ pmaInstalled ? '已安装 v'+pmaVersion : '未安装' }}</el-tag>
            <el-select v-model="pmaInstallVer" placeholder="版本" style="width:120px">
              <el-option v-for="v in pmaVersions" :key="v" :label="v" :value="v" />
            </el-select>
            <el-button type="primary" @click="pmaInstall" :disabled="pmaInstalled">安装</el-button>
            <el-button type="danger" @click="pmaUninstall" :disabled="!pmaInstalled">卸载</el-button>
          </div>
          <div v-if="pmaInstalled" class="pma-config">
            <el-input v-model="pmaProxyConfig" type="textarea" :rows="10" readonly />
            <el-button @click="pmaGetConfig">生成Nginx代理配置</el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 安装进度对话框 -->
    <el-dialog v-model="installDialogVisible" :title="`安装 ${installingName}`" width="600px" :close-on-click-modal="false" :close-on-press-escape="!installRunning">
      <div class="install-progress-panel">
        <el-steps :active="installStep" align-center finish-status="success" style="margin-bottom: 20px">
          <el-step title="初始化" />
          <el-step title="下载安装" />
          <el-step title="配置" />
          <el-step title="启动完成" />
        </el-steps>
        <el-progress
          :percentage="installProgress"
          :status="installFailed ? 'exception' : installProgress >= 100 ? 'success' : ''"
          :stroke-width="20"
          :text-inside="true"
        />
        <p style="text-align: center; margin: 16px 0; color: #606266; min-height: 24px">{{ installMsg }}</p>
        <div v-if="installLogs.length > 0" class="install-log">
          <div class="log-header">
            <span><el-icon><Document /></el-icon> 安装日志</span>
            <el-button link size="small" @click="installLogs = []">清屏</el-button>
          </div>
          <div class="log-content" ref="logContainer">
            <div v-for="(line, i) in installLogs" :key="i" class="log-line" :class="line.type">{{ line.text }}</div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="cancelInstall" :disabled="installRunning && installProgress < 100">取消</el-button>
        <el-button type="primary" @click="installDialogVisible = false" :disabled="installRunning && installProgress < 100">
          {{ installProgress >= 100 ? '完成' : installFailed ? '关闭' : '安装中...' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import request from '@/utils/request';
import { installPlugin } from '@/api/index';

const activeTab = ref('mysql');

// 安装进度相关
const installDialogVisible = ref(false);
const installingName = ref('');
const installingKey = ref('');
const installStep = ref(0);
const installProgress = ref(0);
const installMsg = ref('');
const installRunning = ref(false);
const installFailed = ref(false);
const installLogs = reactive([]);
const logContainer = ref(null);
let installPollTimer = null;
// MySQL
const mysqlRunning = ref(false); const mysqlChecked = ref(false); const mysqlVersion = ref(''); const mysqlDbs = ref([]);
const mysqlLoading = ref(false); const mysqlSaving = ref(false); const mysqlStatusLoading = ref(false); const mysqlInstalling = ref(false); const mysqlInstallMsg = ref('');
const mysqlShowCreate = ref(false); const mysqlShowUsers = ref(false);
const mysqlNew = ref({ name: '', charset: 'utf8mb4', username: '', password: '' });
const mysqlUsers = ref([]); const mysqlNewUser = ref({ name: '', pwd: '' });
async function mysqlLoadStatus() { try { const d = await api('/database/mysql/status'); mysqlRunning.value = d?.running; mysqlVersion.value = d?.version; mysqlChecked.value = true; } catch(e) { mysqlChecked.value = true; } }
async function mysqlCheckStatus() { mysqlStatusLoading.value = true; await mysqlLoadStatus(); mysqlStatusLoading.value = false; if (mysqlRunning.value) mysqlLoadDbs(); }
async function mysqlLoadDbs() { mysqlLoading.value=true; try { const d = await api('/database/mysql/databases'); mysqlDbs.value = (d?.databases||[]).map(n=>({name:n})); } finally { mysqlLoading.value=false; } }
async function mysqlCreate() { if(!mysqlNew.value.name) return ElMessage.warning('请输入数据库名'); mysqlSaving.value=true; try { await api('/database/mysql/create_database',{...mysqlNew.value}); ElMessage.success('创建成功'); mysqlShowCreate.value=false; mysqlLoadDbs(); } catch(e) { ElMessage.error(e.message); } finally { mysqlSaving.value=false; } }
async function mysqlDrop(row) { try { await api('/database/mysql/delete_database',{name:row.name}); ElMessage.success('已删除'); mysqlLoadDbs(); } catch(e) { ElMessage.error(e.message); } }
async function mysqlBackup(row) { try { await api('/database/mysql/backup',{name:row.name}); ElMessage.success('备份完成'); } catch(e) { ElMessage.error('备份失败: ' + (e.message || '未知错误')); } }
async function mysqlLoadUsers() { try { const d=await api('/database/mysql/users'); mysqlUsers.value=d?.users||[]; mysqlShowUsers.value=true; } catch(e) { console.error('加载MySQL用户失败:', e); } }
async function mysqlCreateUser() { if(!mysqlNewUser.value.name) { ElMessage.warning('请输入用户名'); return; } if(!mysqlNewUser.value.pwd) { ElMessage.warning('请输入密码'); return; } if(mysqlNewUser.value.pwd.length < 5) { ElMessage.warning('密码至少5个字符'); return; } try { await api('/database/mysql/create_user',{username:mysqlNewUser.value.name,password:mysqlNewUser.value.pwd}); ElMessage.success('用户创建成功'); mysqlNewUser.value = { name: '', pwd: '' }; mysqlLoadUsers(); } catch(e) { ElMessage.error('创建用户失败: ' + (e.message || '未知错误')); } }
async function mysqlDelUser(row) { try { await api('/database/mysql/delete_user',{username:row.User,host:row.Host}); ElMessage.success('用户已删除'); mysqlLoadUsers(); } catch(e) { ElMessage.error('删除失败: ' + (e.message || '未知错误')); } }
// PgSQL
const pgsqlRunning = ref(false); const pgsqlChecked = ref(false); const pgsqlVersion = ref(''); const pgsqlDbs = ref([]); const pgsqlInstalling = ref(false);
const redisRunning = ref(false); const redisChecked = ref(false); const redisInfo = ref({}); const redisKey = ref(''); const redisValue = ref(''); const redisResult = ref(''); const redisInstalling = ref(false);
const mongoRunning = ref(false); const mongoChecked = ref(false); const mongoDbs = ref([]); const mongoInstalling = ref(false);
const pmaInstalled = ref(false); const pmaVersion = ref(''); const pmaVersions = ref(['5.2.1','4.9.11','4.4.15']); const pmaInstallVer = ref('5.2.1'); const pmaProxyConfig = ref('');

const labelMap = { mysql: 'MySQL', postgresql: 'PostgreSQL', redis: 'Redis', mongodb: 'MongoDB' };
const loadMap = { mysql: mysqlLoadStatus, postgresql: loadPgsql, redis: loadRedis, mongodb: loadMongo };

function addLog(text, type = 'info') {
  installLogs.push({ text: `[${new Date().toLocaleTimeString()}] ${text}`, type });
  nextTick(() => {
    if (logContainer.value) logContainer.value.scrollTop = logContainer.value.scrollHeight;
  });
}

async function installDatabase(name) {
  const label = labelMap[name] || name;
  installingName.value = label;
  installingKey.value = name;
  installDialogVisible.value = true;
  installStep.value = 0;
  installProgress.value = 0;
  installMsg.value = '正在初始化...';
  installRunning.value = true;
  installFailed.value = false;
  installLogs.length = 0;

  try {
    addLog(`开始安装 ${label}...`, 'info');
    installStep.value = 1;
    installMsg.value = '正在提交安装任务...';
    addLog('提交安装任务到后台...', 'info');

    const res = await installPlugin(name);
    const taskId = res?.data?.task_id || res?.data?.data?.task_id;

    if (!taskId) {
      installMsg.value = '安装任务已提交（无法获取进度）';
      addLog('安装任务已提交，请在软件管理中查看进度', 'warn');
      installStep.value = 2;
      installProgress.value = 50;
      setTimeout(checkStatus, 8000);
      return;
    }

    addLog(`任务已创建 (ID: ${taskId})`, 'success');
    installStep.value = 2;
    installMsg.value = '正在下载安装...';

    // Poll progress
    const poll = async () => {
      if (!installRunning.value) return;
      try {
        const progressRes = await request.post('/plugins/install_progress', { task_id: taskId });
        const data = progressRes.data?.data || progressRes.data || {};

        const newProgress = Math.max(0, Math.min(100, data.progress || 0));
        if (newProgress > installProgress.value) {
          installProgress.value = newProgress;
        }
        installMsg.value = data.message || data.msg || '安装中...';

        // Log important status changes
        if (data.message && data.message !== installMsg._lastMsg) {
          addLog(data.message, 'info');
          installMsg._lastMsg = data.message;
        }

        if (data.status === 'completed' || (data.progress && data.progress >= 100)) {
          installProgress.value = 100;
          installMsg.value = `${label} 安装完成！`;
          installStep.value = 4;
          installRunning.value = false;
          addLog(`${label} 安装成功！`, 'success');
          ElMessage.success(`${label} 安装成功`);
          setTimeout(checkStatus, 2000);
          return;
        } else if (data.status === 'failed') {
          installFailed.value = true;
          installRunning.value = false;
          installMsg.value = data.message || '安装失败';
          addLog(`安装失败: ${data.message || '未知错误'}`, 'error');
          ElMessage.error(`${label} 安装失败`);
          setTimeout(checkStatus, 3000);
          return;
        }

        installPollTimer = setTimeout(poll, 2000);
      } catch {
        installPollTimer = setTimeout(poll, 3000);
      }
    };

    installPollTimer = setTimeout(poll, 1000);
  } catch (e) {
    installFailed.value = true;
    installRunning.value = false;
    installMsg.value = `安装启动失败: ${e.message || '未知错误'}`;
    addLog(`启动安装失败: ${e.message}`, 'error');
    ElMessage.error(`安装失败: ${e.message || '未知错误'}`);
  }

  async function checkStatus() {
    const loader = loadMap[name];
    if (loader) {
      try { await loader(); } catch {}
    }
    const btnInstalling = installingKey.value === 'mysql' ? mysqlInstalling :
      installingKey.value === 'postgresql' ? pgsqlInstalling :
      installingKey.value === 'redis' ? redisInstalling : mongoInstalling;
    btnInstalling.value = false;
  }
}

function cancelInstall() {
  if (installRunning.value && installProgress.value < 100) return;
  if (installPollTimer) clearTimeout(installPollTimer);
  installRunning.value = false;
  installDialogVisible.value = false;
}

async function api(url, data = {}) { const r = await request.post(url, data); return r.data?.data || r.data; }
function sizeFmt(row, col, val) { return val ? (val < 1024**3 ? (val/1024**2).toFixed(1)+' MB' : (val/1024**3).toFixed(1)+' GB') : '-'; }

// PgSQL
async function loadPgsql() { try { const d = await api('/database/pgsql/status'); pgsqlRunning.value = d?.running; pgsqlVersion.value = d?.version; } catch(e) { console.error('PostgreSQL状态检查失败:', e); } finally { pgsqlChecked.value = true; } }
async function pgsqlCreate() {
  const { value: name } = await ElMessageBox.prompt('数据库名'); if (!name) return;
  await api('/database/pgsql/create', { name }); ElMessage.success('创建成功'); pgsqlList();
}
async function pgsqlList() { const d = await api('/database/pgsql/list_databases'); pgsqlDbs.value = (d?.databases || []).map(n => ({ name: n })); }
async function pgsqlDrop(row) { try { await ElMessageBox.confirm('确定删除?'); await api('/database/pgsql/delete', { name: row.name }); ElMessage.success('已删除'); pgsqlList(); } catch(e) { if (e !== 'cancel') ElMessage.error('删除失败: ' + (e.message || '未知错误')); } }
async function pgsqlBackup(row) { const d = await api('/database/pgsql/backup', { name: row.name }); ElMessage.success('备份完成: ' + (d?.file || '')); }
async function pgsqlListUsers() { const d = await api('/database/pgsql/list_users'); ElMessage.info('用户: ' + (d?.users || []).join(', ')); }

// Redis
async function loadRedis() { try { const d = await api('/database/redis/status'); redisRunning.value = d?.running; redisInfo.value = d?.info || {}; } catch(e) { console.error('Redis状态检查失败:', e); } finally { redisChecked.value = true; } }
async function redisGet() { const d = await api('/database/redis/get', { key: redisKey.value }); redisResult.value = JSON.stringify(d, null, 2); }
async function redisSet() { await api('/database/redis/set', { key: redisKey.value, value: redisValue.value }); ElMessage.success('OK'); }
async function redisDel() { await api('/database/redis/delete', { keys: redisKey.value }); ElMessage.success('OK'); }
async function redisScan() { const d = await api('/database/redis/scan', { pattern: redisKey.value || '*' }); redisResult.value = d?.result || ''; }
async function redisFlush() { await ElMessageBox.confirm('清空所有数据?', '危险操作', { type: 'error' }); await api('/database/redis/flush', { confirm: 'YES_I_KNOW' }); }

// MongoDB
async function loadMongo() { try { const d = await api('/database/mongodb/status'); mongoRunning.value = d?.running; } catch(e) { console.error('MongoDB状态检查失败:', e); } finally { mongoChecked.value = true; } }
async function mongoCreate() { const { value: name } = await ElMessageBox.prompt('数据库名'); if (!name) return; await api('/database/mongodb/create', { name }); ElMessage.success('OK'); mongoList(); }
async function mongoList() { const d = await api('/database/mongodb/list_databases'); mongoDbs.value = d?.databases || []; }
async function mongoDrop(row) { try { await ElMessageBox.confirm('确定删除?'); await api('/database/mongodb/delete', { name: row.name }); ElMessage.success('OK'); mongoList(); } catch(e) { if (e !== 'cancel') ElMessage.error('删除失败: ' + (e.message || '未知错误')); } }
async function mongoBackup(row) { await api('/database/mongodb/backup', { name: row.name }); ElMessage.success('备份完成'); }
async function mongoListCols(row) { const d = await api('/database/mongodb/list_collections', { database: row.name }); ElMessage.info('集合: ' + (d?.collections || []).join(', ')); }

// phpMyAdmin
async function loadPma() { const d = await api('/database/pma/status'); pmaInstalled.value = d?.installed; pmaVersion.value = d?.version; }
async function pmaInstall() { await api('/database/pma/install', { version: pmaInstallVer.value }); ElMessage.success('安装完成'); loadPma(); }
async function pmaUninstall() { await api('/database/pma/uninstall'); ElMessage.success('已卸载'); loadPma(); }
async function pmaGetConfig() { const d = await api('/database/pma/get_proxy_config', { php_version: '74' }); pmaProxyConfig.value = d?.config || ''; }

onMounted(() => { mysqlLoadStatus(); mysqlLoadDbs(); loadPgsql(); pgsqlList(); loadRedis(); loadMongo(); mongoList(); loadPma(); });
</script>

<style lang="scss" scoped>
.toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.version { color: #909399; font-size: 13px; }
.redis-ops { display: flex; gap: 8px; margin-bottom: 12px; }
.pma-config { margin-top: 12px; }
.install-guide-card { margin-bottom: 16px; }
.install-guide { text-align: center; padding: 24px 0;
  h2 { margin: 16px 0 8px; color: #303133; }
  p { color: #909399; margin-bottom: 8px; }
}
.install-progress-panel {
  .install-log {
    margin-top: 16px;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    overflow: hidden;
    .log-header {
      display: flex; justify-content: space-between; align-items: center;
      padding: 8px 12px; background: #f5f7fa; border-bottom: 1px solid #ebeef5;
      font-size: 13px; font-weight: 500;
    }
    .log-content {
      max-height: 240px; overflow-y: auto; padding: 8px 12px;
      background: #1e1e1e; font-family: 'JetBrains Mono', 'Menlo', monospace; font-size: 12px;
      .log-line {
        line-height: 1.6; white-space: pre-wrap; word-break: break-all;
        color: #d4d4d4;
        &.success { color: #4ec9b0; }
        &.error { color: #f44747; }
        &.warn { color: #e6a23c; }
      }
    }
  }
}
</style>
