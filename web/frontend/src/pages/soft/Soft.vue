<template>
  <div class="soft-page">
    <!-- 统计概览 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="可用软件" :value="softList.length">
            <template #prefix><el-icon style="color: #409eff"><Box /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="已安装" :value="installedCount">
            <template #prefix><el-icon style="color: #67c23a"><CircleCheck /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="可更新" :value="updateCount">
            <template #prefix><el-icon style="color: #e6a23c"><Top /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="分类数" :value="categoryCount">
            <template #prefix><el-icon style="color: #909399"><Grid /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分类标签 + 搜索栏 -->
    <el-card class="category-card">
      <el-row :gutter="16" align="middle">
        <el-col :xs="24" :sm="24" :md="16">
          <el-tabs v-model="activeCategory" @tab-change="handleCategoryChange">
            <el-tab-pane label="全部" name="all" />
            <el-tab-pane label="Web服务器" name="web" />
            <el-tab-pane label="数据库" name="database" />
            <el-tab-pane label="编程语言" name="language" />
            <el-tab-pane label="缓存/NoSQL" name="cache" />
            <el-tab-pane label="FTP/存储" name="storage" />
            <el-tab-pane label="其他工具" name="tools" />
          </el-tabs>
        </el-col>
        <el-col :xs="24" :sm="24" :md="8" class="filter-actions">
          <el-input
            v-model="searchQuery"
            placeholder="搜索软件"
            clearable
            prefix-icon="Search"
            style="width: 160px"
          />
          <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 100px">
            <el-option label="全部" value="" />
            <el-option label="已安装" value="installed" />
            <el-option label="未安装" value="not_installed" />
          </el-select>
          <el-select v-model="sortBy" placeholder="排序" style="width: 100px">
            <el-option label="默认" value="default" />
            <el-option label="名称" value="name" />
            <el-option label="已安装优先" value="installed" />
          </el-select>
          <el-button-group>
            <el-button :type="viewMode === 'grid' ? 'primary' : ''" @click="viewMode = 'grid'" icon="Grid" />
            <el-button :type="viewMode === 'list' ? 'primary' : ''" @click="viewMode = 'list'" icon="List" />
          </el-button-group>
        </el-col>
      </el-row>
    </el-card>

    <!-- 网格视图 -->
    <el-row :gutter="16" v-loading="loading" v-if="viewMode === 'grid'">
      <el-col
        v-for="soft in filteredSoftList"
        :key="soft.id"
        :xs="24" :sm="12" :md="8" :lg="6"
      >
        <el-card shadow="hover" class="soft-card" @click="soft.installed ? manageSoft(soft) : installSoft(soft)">
          <div class="soft-header">
            <div class="soft-icon" :style="{ background: getIconBg(soft) }">
              <el-icon :size="36" :style="{ color: soft.icon_color || '#409eff' }">
                <component :is="soft.icon || 'Box'" />
              </el-icon>
            </div>
            <div class="soft-info">
              <h3 class="soft-name">{{ soft.name }}</h3>
              <span class="soft-version">v{{ soft.version }}</span>
            </div>
            <el-tag v-if="soft.installed" type="success" size="small" effect="dark">已安装</el-tag>
          </div>
          <p class="soft-desc">{{ soft.description }}</p>
          <div class="soft-footer">
            <span class="soft-category">{{ getCategoryLabel(soft.category) }}</span>
            <div class="soft-actions" @click.stop>
              <el-button
                v-if="soft.installed"
                type="primary"
                size="small"
                @click="manageSoft(soft)"
              >
                管理
              </el-button>
              <el-button
                v-else
                type="success"
                size="small"
                @click="installSoft(soft)"
              >
                安装
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 列表视图 -->
    <el-card v-if="viewMode === 'list'" v-loading="loading">
      <el-table :data="filteredSoftList" stripe>
        <el-table-column prop="name" label="软件名称" min-width="150">
          <template #default="{ row }">
            <div class="list-name-cell">
              <el-icon :size="20" :style="{ color: row.icon_color || '#409eff' }">
                <component :is="row.icon || 'Box'" />
              </el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="100" />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ getCategoryLabel(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.installed ? 'success' : 'info'" size="small">
              {{ row.installed ? '已安装' : '未安装' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.installed" type="primary" size="small" @click="manageSoft(row)">管理</el-button>
            <el-button v-else type="success" size="small" @click="installSoft(row)">安装</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-empty v-if="filteredSoftList.length === 0 && !loading" description="暂无软件" />

    <!-- 软件管理对话框 -->
    <el-dialog v-model="manageDialogVisible" :title="currentSoft.name + ' 管理'" width="650px">
      <el-tabs v-model="manageActiveTab">
        <!-- 概览标签 -->
        <el-tab-pane label="概览" name="overview">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="软件名称">{{ currentSoft.name }}</el-descriptions-item>
            <el-descriptions-item label="版本">
              {{ currentSoft.version }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="currentSoft.status === 'running' ? 'success' : 'danger'" effect="dark">
                <el-icon v-if="currentSoft.status === 'running'"><VideoPlay /></el-icon>
                <el-icon v-else><VideoPause /></el-icon>
                {{ currentSoft.status === 'running' ? '运行中' : '已停止' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="分类">{{ getCategoryLabel(currentSoft.category) }}</el-descriptions-item>
            <el-descriptions-item label="安装路径" :span="2">{{ currentSoft.install_path || '/www/server' }}</el-descriptions-item>
            <el-descriptions-item label="配置文件" :span="2">{{ currentSoft.config_path || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <!-- 控制标签 -->
        <el-tab-pane label="控制" name="control">
          <div class="soft-manage-actions">
            <el-button type="success" size="large" @click="startSoft" :disabled="currentSoft.status === 'running'">
              <el-icon><VideoPlay /></el-icon> 启动
            </el-button>
            <el-button type="warning" size="large" @click="stopSoft" :disabled="currentSoft.status !== 'running'">
              <el-icon><VideoPause /></el-icon> 停止
            </el-button>
            <el-button type="info" size="large" @click="restartSoft">
              <el-icon><RefreshRight /></el-icon> 重启
            </el-button>
            <el-button type="primary" size="large" @click="editConfig">
              <el-icon><Edit /></el-icon> 编辑配置
            </el-button>
            <el-button type="danger" size="large" @click="uninstallSoft">
              <el-icon><Delete /></el-icon> 卸载
            </el-button>
          </div>
        </el-tab-pane>

        <!-- 日志标签 -->
        <el-tab-pane label="日志" name="logs">
          <div class="log-actions">
            <el-button size="small" @click="refreshSoftLogs">
              <el-icon><Refresh /></el-icon> 刷新日志
            </el-button>
          </div>
          <el-input
            v-model="softLogs"
            type="textarea"
            :rows="10"
            readonly
            placeholder="暂无日志，点击刷新获取最新日志"
            class="soft-log-textarea"
          />
        </el-tab-pane>
      </el-tabs>
    </el-dialog>

    <!-- 安装对话框 -->
    <el-dialog v-model="installDialogVisible" title="安装软件" width="500px">
      <el-steps :active="installStep" finish-status="success" align-center style="margin-bottom: 24px">
        <el-step title="选择版本" />
        <el-step title="确认安装" />
        <el-step title="安装中" />
      </el-steps>

      <el-form :model="installForm" label-width="100px" v-if="installStep === 0">
        <el-form-item label="软件名称">
          <el-input :value="installForm.name" disabled />
        </el-form-item>
        <el-form-item label="版本选择">
          <el-select v-model="installForm.version" placeholder="选择版本">
            <el-option
              v-for="v in installForm.versions"
              :key="v"
              :label="v"
              :value="v"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="安装路径">
          <el-input v-model="installForm.path" placeholder="安装路径" />
        </el-form-item>
      </el-form>

      <div v-if="installStep === 1" class="install-confirm">
        <el-alert type="info" :closable="false" show-icon>
          <template #title>即将安装 {{ installForm.name }} v{{ installForm.version }}</template>
          <p>安装路径: {{ installForm.path }}</p>
          <p>安装过程可能需要几分钟，请耐心等待。</p>
        </el-alert>
      </div>

      <div v-if="installStep === 2" class="install-progress">
        <el-progress :percentage="installProgress" :status="installProgress >= 100 ? 'success' : ''" />
        <p class="progress-text">{{ installProgressText }}</p>
      </div>

      <template #footer>
        <el-button @click="installDialogVisible = false" :disabled="installStep === 2 && installProgress < 100 && installProgress > 0">
          {{ installStep === 2 && installProgress >= 100 ? '完成' : '取消' }}
        </el-button>
        <el-button v-if="installStep === 0" type="primary" @click="installStep = 1">下一步</el-button>
        <el-button v-if="installStep === 1" type="primary" @click="confirmInstall" :loading="installing">开始安装</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getPluginList, installPlugin, uninstallPlugin, runPlugin } from '@/api/index';

const softList = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const statusFilter = ref('');
const sortBy = ref('default');
const viewMode = ref('grid');
const activeCategory = ref('all');
const manageDialogVisible = ref(false);
const manageActiveTab = ref('overview');
const installDialogVisible = ref(false);
const installing = ref(false);
const installStep = ref(0);
const installProgress = ref(0);
const installProgressText = ref('');
const currentSoft = ref({});
const softLogs = ref('');

const installForm = ref({
  name: '',
  version: '',
  versions: [],
  path: '/www/server'
});

// 统计数据
const installedCount = computed(() => softList.value.filter(s => s.installed).length);
const updateCount = computed(() => softList.value.filter(s => s.installed && s.hasUpdate).length);
const categoryCount = computed(() => {
  const cats = new Set(softList.value.map(s => s.category));
  return cats.size;
});

const filteredSoftList = computed(() => {
  let list = [...softList.value];

  if (activeCategory.value !== 'all') {
    list = list.filter(s => s.category === activeCategory.value);
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    list = list.filter(s =>
      s.name.toLowerCase().includes(query) ||
      (s.description && s.description.toLowerCase().includes(query))
    );
  }

  if (statusFilter.value === 'installed') {
    list = list.filter(s => s.installed);
  } else if (statusFilter.value === 'not_installed') {
    list = list.filter(s => !s.installed);
  }

  // 排序
  if (sortBy.value === 'name') {
    list.sort((a, b) => a.name.localeCompare(b.name));
  } else if (sortBy.value === 'installed') {
    list.sort((a, b) => (b.installed ? 1 : 0) - (a.installed ? 1 : 0));
  }

  return list;
});

// 软件分类映射
const categoryMap = {
  'openresty': 'web', 'nginx': 'web', 'apache': 'web', 'caddy': 'web',
  'mysql': 'database', 'mariadb': 'database', 'pgsql': 'database', 'mongodb': 'database', 'sqlite': 'database',
  'php': 'language', 'node': 'language', 'golang': 'language', 'java': 'language', 'python': 'language',
  'redis': 'cache', 'memcached': 'cache',
  'ftp': 'storage', 'rsync': 'storage', 's3': 'storage',
};

const categoryIcons = {
  'web': { icon: 'Monitor', color: '#409eff' },
  'database': { icon: 'Coin', color: '#67c23a' },
  'language': { icon: 'Promotion', color: '#e6a23c' },
  'cache': { icon: 'DataLine', color: '#f56c6c' },
  'storage': { icon: 'Box', color: '#909399' },
  'tools': { icon: 'Setting', color: '#606266' },
};

const categoryLabels = {
  'web': 'Web服务器',
  'database': '数据库',
  'language': '编程语言',
  'cache': '缓存/NoSQL',
  'storage': 'FTP/存储',
  'tools': '其他工具',
};

function getCategory(name) {
  const lower = (name || '').toLowerCase();
  for (const [key, cat] of Object.entries(categoryMap)) {
    if (lower.includes(key)) return cat;
  }
  return 'tools';
}

function getCategoryLabel(cat) {
  return categoryLabels[cat] || cat || '其他';
}

function getIconBg(soft) {
  const catInfo = categoryIcons[soft.category] || categoryIcons['tools'];
  return `${catInfo.color}15`;
}

const fetchSoftList = async () => {
  loading.value = true;
  try {
    const res = await getPluginList({ type: '0', p: '1' });
    if (res && res.data) {
      softList.value = (Array.isArray(res.data) ? res.data : []).map((item, idx) => {
        const cat = getCategory(item.name);
        const catInfo = categoryIcons[cat] || categoryIcons['tools'];
        return {
          id: idx + 1,
          name: item.title || item.name || 'Unknown',
          version: item.versions ? item.versions[item.versions.length - 1] : '-',
          description: item.description || item.ps || '',
          category: cat,
          icon: catInfo.icon,
          icon_color: catInfo.color,
          installed: !!item.setup,
          status: item.setup ? 'running' : 'stopped',
          install_path: item.install_path || '',
          config_path: item.config_path || '',
          hasUpdate: false, // TODO: implement version check
          _raw: item,
        };
      });
    }
  } catch {
    softList.value = [];
  } finally {
    loading.value = false;
  }
};

const handleCategoryChange = () => {};

const manageSoft = (soft) => {
  currentSoft.value = soft;
  manageActiveTab.value = 'overview';
  softLogs.value = '';
  manageDialogVisible.value = true;
  refreshSoftLogs();
};

const refreshSoftLogs = async () => {
  try {
    const raw = currentSoft.value._raw || {};
    const res = await runPlugin(raw.name, 'run_logs', raw.version || '');
    if (res && res.data && typeof res.data === 'string') {
      softLogs.value = res.data;
    } else {
      softLogs.value = `[${new Date().toLocaleString()}] ${currentSoft.value.name} 暂无运行日志`;
    }
  } catch {
    softLogs.value = `[${new Date().toLocaleString()}] ${currentSoft.value.name} 暂无运行日志`;
  }
};

const installSoft = (soft) => {
  currentSoft.value = soft;
  installStep.value = 0;
  installProgress.value = 0;
  installProgressText.value = '';
  const raw = soft._raw || {};
  installForm.value = {
    name: soft.name,
    version: raw.default_ver || soft.version,
    versions: raw.versions || [soft.version],
    path: '/www/server'
  };
  installDialogVisible.value = true;
};

const confirmInstall = async () => {
  installing.value = true;
  installStep.value = 2;
  installProgress.value = 0;
  installProgressText.value = '正在准备安装...';

  // 模拟安装进度
  const progressInterval = setInterval(() => {
    if (installProgress.value < 90) {
      installProgress.value += Math.random() * 15;
      if (installProgress.value < 30) installProgressText.value = '正在下载安装包...';
      else if (installProgress.value < 60) installProgressText.value = '正在解压安装...';
      else if (installProgress.value < 90) installProgressText.value = '正在配置环境...';
    }
  }, 500);

  try {
    const raw = currentSoft.value._raw || {};
    await installPlugin(raw.name || installForm.value.name, installForm.value.version);
    installProgress.value = 100;
    installProgressText.value = '安装完成！';
    ElMessage.success(`${installForm.value.name} 安装任务已提交`);
    clearInterval(progressInterval);
    setTimeout(() => {
      installDialogVisible.value = false;
      fetchSoftList();
    }, 1500);
  } catch {
    clearInterval(progressInterval);
    installProgress.value = 0;
    installProgressText.value = '安装失败';
    installStep.value = 1;
    ElMessage.error('安装失败');
  } finally {
    installing.value = false;
  }
};

const startSoft = async () => {
  try {
    const raw = currentSoft.value._raw || {};
    await runPlugin(raw.name, 'start', raw.version || '');
    currentSoft.value.status = 'running';
    ElMessage.success(`${currentSoft.value.name} 已启动`);
    refreshSoftLogs();
  } catch {
    ElMessage.error('启动失败');
  }
};

const stopSoft = async () => {
  try {
    await ElMessageBox.confirm(`确定要停止 ${currentSoft.value.name} 吗？`, '停止确认');
    const raw = currentSoft.value._raw || {};
    await runPlugin(raw.name, 'stop', raw.version || '');
    currentSoft.value.status = 'stopped';
    ElMessage.success(`${currentSoft.value.name} 已停止`);
    refreshSoftLogs();
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('停止失败');
  }
};

const restartSoft = async () => {
  try {
    const raw = currentSoft.value._raw || {};
    await runPlugin(raw.name, 'restart', raw.version || '');
    ElMessage.success(`${currentSoft.value.name} 已重启`);
    refreshSoftLogs();
  } catch {
    ElMessage.error('重启失败');
  }
};

const editConfig = async () => {
  try {
    const raw = currentSoft.value._raw || {};
    const res = await runPlugin(raw.name, 'conf', raw.version || '');
    if (res && res.data) {
      ElMessage.success('配置已获取');
      if (typeof res.data === 'string') {
        softLogs.value = res.data;
        manageActiveTab.value = 'logs';
      }
    } else {
      ElMessage.info('该插件暂无配置接口');
    }
  } catch {
    ElMessage.info('该插件暂无配置接口');
  }
};

const uninstallSoft = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要卸载 ${currentSoft.value.name} 吗？此操作不可恢复！`,
      '卸载确认',
      { type: 'warning' }
    );
    const raw = currentSoft.value._raw || {};
    await uninstallPlugin(raw.name, raw.version || '');
    ElMessage.success(`${currentSoft.value.name} 已卸载`);
    manageDialogVisible.value = false;
    fetchSoftList();
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('卸载失败');
  }
};

onMounted(() => fetchSoftList());
</script>

<style lang="scss" scoped>
.soft-page {
  .stats-row {
    margin-bottom: 16px;

    .stat-card {
      text-align: center;
      margin-bottom: 8px;
    }
  }

  .category-card {
    margin-bottom: 16px;

    .filter-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      justify-content: flex-end;
      margin-top: 8px;

      @media (min-width: 992px) {
        margin-top: 0;
      }
    }
  }

  .soft-card {
    margin-bottom: 16px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .soft-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;

      .soft-icon {
        width: 52px;
        height: 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        flex-shrink: 0;
      }

      .soft-info {
        flex: 1;
        min-width: 0;

        .soft-name {
          font-size: 15px;
          font-weight: 600;
          margin: 0 0 2px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .soft-version {
          font-size: 12px;
          color: #909399;
        }
      }
    }

    .soft-desc {
      font-size: 13px;
      color: #606266;
      margin: 0 0 12px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      line-height: 1.5;
    }

    .soft-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .soft-category {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .list-name-cell {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .soft-manage-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding: 16px 0;
  }

  .log-actions {
    margin-bottom: 12px;
  }

  .soft-log-textarea {
    :deep(textarea) {
      font-family: 'Consolas', 'Monaco', monospace;
      font-size: 13px;
      line-height: 1.6;
    }
  }

  .install-confirm {
    p {
      margin: 4px 0;
      font-size: 13px;
    }
  }

  .install-progress {
    text-align: center;
    padding: 24px 0;

    .progress-text {
      margin-top: 12px;
      color: #606266;
      font-size: 14px;
    }
  }
}
</style>
