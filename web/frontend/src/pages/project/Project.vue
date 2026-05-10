<template>
  <div class="page-container">
    <div class="page-card">
      <el-tabs v-model="activeTab">
        <!-- Python 项目 -->
        <el-tab-pane label="Python项目" name="python">
          <div class="toolbar">
            <el-button type="primary" @click="pyShowCreate = true">创建Python项目</el-button>
            <el-button @click="loadPy" :loading="pyLoading">刷新</el-button>
          </div>
          <el-table :data="pyProjects" stripe v-loading="pyLoading" empty-text="暂无Python项目">
            <el-table-column prop="name" label="项目名称" min-width="150" />
            <el-table-column prop="path" label="路径" min-width="250" show-overflow-tooltip />
            <el-table-column label="大小" width="100">
              <template #default="{ row }">{{ formatSize(row.size) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="250" align="center">
              <template #default="{ row }">
                <el-button size="small" type="success" @click="pyStart(row)">启动</el-button>
                <el-button size="small" type="warning" @click="pyStop(row)">停止</el-button>
                <el-popconfirm title="确定删除此项目及其所有文件?" @confirm="pyDelete(row)">
                  <template #reference><el-button size="small" type="danger">删除</el-button></template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>

          <!-- Python 创建对话框 -->
          <el-dialog v-model="pyShowCreate" title="创建Python项目" width="500px" @closed="resetPyForm">
            <el-form :model="pyForm" label-width="100px">
              <el-form-item label="项目名称" required>
                <el-input v-model="pyForm.name" placeholder="my-python-app" />
              </el-form-item>
              <el-form-item label="项目路径">
                <el-input v-model="pyForm.path" placeholder="留空自动生成: /www/python_project/{名称}" />
              </el-form-item>
              <el-form-item label="启动方式">
                <el-select v-model="pyForm.startup" style="width: 100%">
                  <el-option label="Gunicorn (推荐)" value="gunicorn" />
                  <el-option label="Python直接运行" value="python" />
                  <el-option label="Uvicorn" value="uvicorn" />
                </el-select>
              </el-form-item>
              <el-form-item label="监听端口">
                <el-input v-model="pyForm.port" placeholder="8000" />
              </el-form-item>
              <el-form-item label="创建虚拟环境">
                <el-switch v-model="pyForm.createVenv" />
                <span class="form-hint">推荐创建独立虚拟环境</span>
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="pyShowCreate = false">取消</el-button>
              <el-button type="primary" @click="onCreatePy" :loading="pySaving">创建</el-button>
            </template>
          </el-dialog>
        </el-tab-pane>

        <!-- Go 项目 -->
        <el-tab-pane label="Go项目" name="go">
          <div class="toolbar">
            <el-button type="primary" @click="goShowCreate = true">创建Go项目</el-button>
            <el-button @click="loadGo" :loading="goLoading">刷新</el-button>
          </div>
          <el-table :data="goProjects" stripe v-loading="goLoading" empty-text="暂无Go项目">
            <el-table-column prop="name" label="项目名称" min-width="150" />
            <el-table-column prop="path" label="路径" min-width="250" show-overflow-tooltip />
            <el-table-column prop="port" label="端口" width="80" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'running' ? 'success' : 'info'" size="small">
                  {{ row.status === 'running' ? '运行中' : '已停止' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="280" align="center">
              <template #default="{ row }">
                <el-button size="small" @click="goBuild(row)">编译</el-button>
                <el-button size="small" type="success" @click="goStart(row)">启动</el-button>
                <el-button size="small" type="warning" @click="goStop(row)">停止</el-button>
                <el-popconfirm title="确定删除此项目?" @confirm="goDelete(row)">
                  <template #reference><el-button size="small" type="danger">删除</el-button></template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>

          <!-- Go 创建对话框 -->
          <el-dialog v-model="goShowCreate" title="创建Go项目" width="500px" @closed="resetGoForm">
            <el-form :model="goForm" label-width="100px">
              <el-form-item label="项目名称" required>
                <el-input v-model="goForm.name" placeholder="my-go-app" />
              </el-form-item>
              <el-form-item label="项目路径">
                <el-input v-model="goForm.path" placeholder="留空自动生成: /www/go_project/{名称}" />
              </el-form-item>
              <el-form-item label="编译命令">
                <el-input v-model="goForm.buildCmd" placeholder="go build -o app ." />
              </el-form-item>
              <el-form-item label="可执行文件">
                <el-input v-model="goForm.binary" placeholder="./app" />
              </el-form-item>
              <el-form-item label="监听端口">
                <el-input v-model="goForm.port" placeholder="8080" />
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="goShowCreate = false">取消</el-button>
              <el-button type="primary" @click="onCreateGo" :loading="goSaving">创建</el-button>
            </template>
          </el-dialog>
        </el-tab-pane>

        <!-- 反向代理 -->
        <el-tab-pane label="反向代理" name="proxy">
          <div class="toolbar">
            <el-button type="primary" @click="proxyShowCreate = true">创建反向代理</el-button>
            <el-button @click="loadProxy" :loading="proxyLoading">刷新</el-button>
          </div>
          <el-table :data="proxies" stripe v-loading="proxyLoading" empty-text="暂无反向代理">
            <el-table-column prop="name" label="名称" min-width="120" />
            <el-table-column prop="domain" label="域名" min-width="150" />
            <el-table-column prop="target_url" label="目标URL" min-width="200" show-overflow-tooltip />
            <el-table-column prop="port" label="端口" width="80" />
            <el-table-column label="操作" width="180" align="center">
              <template #default="{ row }">
                <el-button size="small" @click="editProxy(row)">编辑</el-button>
                <el-popconfirm title="确定删除此代理?" @confirm="proxyDelete(row)">
                  <template #reference><el-button size="small" type="danger">删除</el-button></template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>

          <!-- Proxy 创建对话框 -->
          <el-dialog v-model="proxyShowCreate" title="创建反向代理" width="500px" @closed="resetProxyForm">
            <el-form :model="proxyForm" label-width="100px">
              <el-form-item label="代理名称" required>
                <el-input v-model="proxyForm.name" placeholder="my-proxy" />
              </el-form-item>
              <el-form-item label="域名">
                <el-input v-model="proxyForm.domain" placeholder="example.com (可选)" />
              </el-form-item>
              <el-form-item label="目标地址" required>
                <el-input v-model="proxyForm.target_url" placeholder="http://127.0.0.1:3000" />
              </el-form-item>
              <el-form-item label="监听端口">
                <el-input v-model="proxyForm.port" placeholder="80" />
              </el-form-item>
              <el-form-item label="WebSocket支持">
                <el-switch v-model="proxyForm.ws_support" />
              </el-form-item>
              <el-form-item label="启用缓存">
                <el-switch v-model="proxyForm.cache_enabled" />
              </el-form-item>
              <el-form-item label="缓存时间" v-if="proxyForm.cache_enabled">
                <el-input v-model="proxyForm.cache_time" placeholder="1h" />
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="proxyShowCreate = false">取消</el-button>
              <el-button type="primary" @click="onCreateProxy" :loading="proxySaving">创建</el-button>
            </template>
          </el-dialog>
        </el-tab-pane>

        <!-- 静态网站 -->
        <el-tab-pane label="静态网站" name="static">
          <div class="toolbar">
            <el-button type="primary" @click="staticShowCreate = true">创建静态网站</el-button>
            <el-button @click="loadStatic" :loading="staticLoading">刷新</el-button>
          </div>
          <el-table :data="staticSites" stripe v-loading="staticLoading" empty-text="暂无静态网站">
            <el-table-column prop="name" label="名称" min-width="120" />
            <el-table-column prop="domain" label="域名" min-width="150" />
            <el-table-column prop="path" label="路径" min-width="250" show-overflow-tooltip />
            <el-table-column prop="port" label="端口" width="80" />
            <el-table-column label="操作" width="180" align="center">
              <template #default="{ row }">
                <el-button size="small" @click="viewStatic(row)">查看</el-button>
                <el-popconfirm title="确定删除此站点及其文件?" @confirm="staticDelete(row)">
                  <template #reference><el-button size="small" type="danger">删除</el-button></template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>

          <!-- Static 创建对话框 -->
          <el-dialog v-model="staticShowCreate" title="创建静态网站" width="500px" @closed="resetStaticForm">
            <el-form :model="staticForm" label-width="100px">
              <el-form-item label="站点名称" required>
                <el-input v-model="staticForm.name" placeholder="my-website" />
              </el-form-item>
              <el-form-item label="域名">
                <el-input v-model="staticForm.domain" placeholder="example.com (可选)" />
              </el-form-item>
              <el-form-item label="站点路径">
                <el-input v-model="staticForm.path" placeholder="留空自动生成: /www/wwwroot/{名称}" />
              </el-form-item>
              <el-form-item label="监听端口">
                <el-input v-model="staticForm.port" placeholder="80" />
              </el-form-item>
              <el-form-item label="默认文档">
                <el-input v-model="staticForm.index_page" placeholder="index.html" />
              </el-form-item>
              <el-form-item label="Gzip压缩">
                <el-switch v-model="staticForm.gzip_enabled" />
              </el-form-item>
              <el-form-item label="静态资源缓存">
                <el-switch v-model="staticForm.cache_enabled" />
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="staticShowCreate = false">取消</el-button>
              <el-button type="primary" @click="onCreateStatic" :loading="staticSaving">创建</el-button>
            </template>
          </el-dialog>
        </el-tab-pane>
      </el-tabs>
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

const activeTab = ref('python');

function formatSize(bytes) {
  if (!bytes) return '-';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  if (bytes < 1024 * 1024 * 1024) return (bytes / 1024 / 1024).toFixed(1) + ' MB';
  return (bytes / 1024 / 1024 / 1024).toFixed(1) + ' GB';
}

// ========== Python ==========
const pyProjects = ref([]);
const pyLoading = ref(false);
const pySaving = ref(false);
const pyShowCreate = ref(false);
const pyForm = reactive({ name: '', path: '', startup: 'gunicorn', port: '8000', createVenv: true });
function resetPyForm() { pyForm.name = ''; pyForm.path = ''; pyForm.startup = 'gunicorn'; pyForm.port = '8000'; pyForm.createVenv = true; }

async function loadPy() {
  pyLoading.value = true;
  try { const d = await api('/project/python/list'); pyProjects.value = d?.projects || []; }
  finally { pyLoading.value = false; }
}

async function onCreatePy() {
  if (!pyForm.name) { ElMessage.warning('请输入项目名称'); return; }
  pySaving.value = true;
  try {
    await api('/project/python/create', {
      name: pyForm.name, path: pyForm.path, startup: pyForm.startup,
      port: pyForm.port, create_venv: pyForm.createVenv ? '1' : '0'
    });
    ElMessage.success('Python项目创建成功');
    pyShowCreate.value = false;
    await loadPy();
  } catch (e) { ElMessage.error(e.message); }
  finally { pySaving.value = false; }
}

async function pyStart(row) {
  try { await api('/project/python/start', { path: row.path }); ElMessage.success('已启动'); }
  catch (e) { ElMessage.error(e.message); }
}
async function pyStop(row) {
  try { await api('/project/python/stop', { port: '8000' }); ElMessage.success('已停止'); }
  catch (e) { ElMessage.error(e.message); }
}
async function pyDelete(row) {
  try { await api('/project/python/delete', { path: row.path, name: row.name }); ElMessage.success('已删除'); await loadPy(); }
  catch (e) { ElMessage.error(e.message); }
}

// ========== Go ==========
const goProjects = ref([]);
const goLoading = ref(false);
const goSaving = ref(false);
const goShowCreate = ref(false);
const goForm = reactive({ name: '', path: '', buildCmd: 'go build -o app .', binary: './app', port: '8080' });
function resetGoForm() { goForm.name = ''; goForm.path = ''; goForm.buildCmd = 'go build -o app .'; goForm.binary = './app'; goForm.port = '8080'; }

async function loadGo() {
  goLoading.value = true;
  try { const d = await api('/project/golang/list'); goProjects.value = d?.projects || []; }
  finally { goLoading.value = false; }
}

async function onCreateGo() {
  if (!goForm.name) { ElMessage.warning('请输入项目名称'); return; }
  goSaving.value = true;
  try {
    await api('/project/golang/create', {
      name: goForm.name, path: goForm.path, build_cmd: goForm.buildCmd,
      binary: goForm.binary, port: goForm.port
    });
    ElMessage.success('Go项目创建成功');
    goShowCreate.value = false;
    await loadGo();
  } catch (e) { ElMessage.error(e.message); }
  finally { goSaving.value = false; }
}

async function goBuild(row) {
  try { await api('/project/golang/build', { path: row.path }); ElMessage.success('编译完成'); }
  catch (e) { ElMessage.error(e.message); }
}
async function goStart(row) {
  try { await api('/project/golang/start', { path: row.path }); ElMessage.success('已启动'); await loadGo(); }
  catch (e) { ElMessage.error(e.message); }
}
async function goStop(row) {
  try { await api('/project/golang/stop', { name: row.name }); ElMessage.success('已停止'); await loadGo(); }
  catch (e) { ElMessage.error(e.message); }
}
async function goDelete(row) {
  try { await api('/project/golang/delete', { path: row.path, name: row.name }); ElMessage.success('已删除'); await loadGo(); }
  catch (e) { ElMessage.error(e.message); }
}

// ========== Proxy ==========
const proxies = ref([]);
const proxyLoading = ref(false);
const proxySaving = ref(false);
const proxyShowCreate = ref(false);
const proxyForm = reactive({ name: '', domain: '', target_url: '', port: '80', ws_support: false, cache_enabled: false, cache_time: '1h' });
function resetProxyForm() { proxyForm.name = ''; proxyForm.domain = ''; proxyForm.target_url = ''; proxyForm.port = '80'; proxyForm.ws_support = false; proxyForm.cache_enabled = false; proxyForm.cache_time = '1h'; }

async function loadProxy() {
  proxyLoading.value = true;
  try { const d = await api('/project/proxy/list'); proxies.value = d?.proxies || []; }
  finally { proxyLoading.value = false; }
}

async function onCreateProxy() {
  if (!proxyForm.name) { ElMessage.warning('请输入代理名称'); return; }
  if (!proxyForm.target_url) { ElMessage.warning('请输入目标地址'); return; }
  proxySaving.value = true;
  try {
    await api('/project/proxy/create', {
      name: proxyForm.name, domain: proxyForm.domain, target_url: proxyForm.target_url,
      port: proxyForm.port, ws_support: proxyForm.ws_support ? '1' : '0',
      cache_enabled: proxyForm.cache_enabled ? '1' : '0', cache_time: proxyForm.cache_time
    });
    ElMessage.success('反向代理创建成功');
    proxyShowCreate.value = false;
    await loadProxy();
  } catch (e) { ElMessage.error(e.message); }
  finally { proxySaving.value = false; }
}

function editProxy(row) {
  proxyForm.name = row.name;
  proxyForm.domain = row.domain || '';
  proxyForm.target_url = row.target_url || '';
  proxyForm.port = String(row.port || '80');
  proxyForm.ws_support = row.ws_support || false;
  proxyForm.cache_enabled = row.cache_enabled || false;
  proxyForm.cache_time = row.cache_time || '1h';
  proxyShowCreate.value = true;
}
async function proxyDelete(row) {
  try { await api('/project/proxy/delete', { name: row.name }); ElMessage.success('已删除'); await loadProxy(); }
  catch (e) { ElMessage.error(e.message); }
}

// ========== Static ==========
const staticSites = ref([]);
const staticLoading = ref(false);
const staticSaving = ref(false);
const staticShowCreate = ref(false);
const staticForm = reactive({ name: '', domain: '', path: '', port: '80', index_page: 'index.html', gzip_enabled: true, cache_enabled: true });
function resetStaticForm() { staticForm.name = ''; staticForm.domain = ''; staticForm.path = ''; staticForm.port = '80'; staticForm.index_page = 'index.html'; staticForm.gzip_enabled = true; staticForm.cache_enabled = true; }

async function loadStatic() {
  staticLoading.value = true;
  try { const d = await api('/project/static/list'); staticSites.value = d?.sites || []; }
  finally { staticLoading.value = false; }
}

async function onCreateStatic() {
  if (!staticForm.name) { ElMessage.warning('请输入站点名称'); return; }
  staticSaving.value = true;
  try {
    await api('/project/static/create', {
      name: staticForm.name, domain: staticForm.domain, path: staticForm.path,
      port: staticForm.port, index_page: staticForm.index_page,
      gzip_enabled: staticForm.gzip_enabled ? '1' : '0',
      cache_enabled: staticForm.cache_enabled ? '1' : '0'
    });
    ElMessage.success('静态网站创建成功');
    staticShowCreate.value = false;
    await loadStatic();
  } catch (e) { ElMessage.error(e.message); }
  finally { staticSaving.value = false; }
}

function viewStatic(row) { ElMessage.info(`站点路径: ${row.path}`); }
async function staticDelete(row) {
  try { await api('/project/static/delete', { name: row.name, path: row.path }); ElMessage.success('已删除'); await loadStatic(); }
  catch (e) { ElMessage.error(e.message); }
}

onMounted(() => { loadPy(); loadGo(); loadProxy(); loadStatic(); });
</script>

<style lang="scss" scoped>
.toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.form-hint { margin-left: 8px; color: #909399; font-size: 12px; }
</style>
