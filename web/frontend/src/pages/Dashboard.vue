<template>
  <div class="dashboard-page">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="welcome-content">
        <div class="welcome-left">
          <h2 class="welcome-greeting">{{ greeting }}，管理员</h2>
          <p class="welcome-date">{{ currentDate }} | 运行时间: {{ formatUptime(systemInfo.uptime) }}</p>
        </div>
        <div class="welcome-right">
          <div class="health-score" :class="healthClass">
            <svg viewBox="0 0 36 36" class="health-ring">
              <path class="health-ring-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
              <path class="health-ring-fg" :stroke-dasharray="`${healthScore}, 100`" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            </svg>
            <div class="health-text">
              <span class="health-number">{{ healthScore }}</span>
              <span class="health-label">健康度</span>
            </div>
          </div>
          <div class="refresh-control">
            <el-switch v-model="autoRefresh" size="small" active-text="自动刷新" inactive-text="" />
            <span v-if="autoRefresh" class="refresh-countdown">{{ refreshCountdown }}s</span>
            <el-button size="small" :icon="Refresh" circle @click="manualRefresh" title="手动刷新" />
          </div>
        </div>
      </div>
    </div>

    <!-- 资源告警 -->
    <transition-group name="alert-slide" tag="div" class="alerts-container">
      <el-alert
        v-for="alert in activeAlerts"
        :key="alert.key"
        :title="alert.title"
        :description="alert.description"
        :type="alert.type"
        :closable="true"
        show-icon
        class="resource-alert"
        @close="dismissAlert(alert.key)"
      />
    </transition-group>

    <!-- 信息卡片 -->
    <el-row :gutter="16" class="info-cards">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="info-card cpu-card">
          <div class="card-icon">
            <el-icon :size="36"><Cpu /></el-icon>
          </div>
          <div class="card-info">
            <div class="card-label">CPU 使用率</div>
            <div class="card-value">{{ systemInfo.cpu.usage || 0 }}%</div>
            <el-progress
              :percentage="systemInfo.cpu.usage || 0"
              :stroke-width="6"
              :show-text="false"
              :color="getProgressColor(systemInfo.cpu.usage)"
            />
            <div class="card-detail">{{ systemInfo.cpu.cores || '-' }} 核 {{ systemInfo.cpu.model || '' }}</div>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <div class="info-card memory-card">
          <div class="card-icon">
            <el-icon :size="36"><Coin /></el-icon>
          </div>
          <div class="card-info">
            <div class="card-label">内存使用率</div>
            <div class="card-value">{{ systemInfo.memory.usage || 0 }}%</div>
            <el-progress
              :percentage="systemInfo.memory.usage || 0"
              :stroke-width="6"
              :show-text="false"
              :color="getProgressColor(systemInfo.memory.usage)"
            />
            <div class="card-detail">
              {{ formatBytes(systemInfo.memory.used) }} / {{ formatBytes(systemInfo.memory.total) }}
            </div>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <div class="info-card disk-card">
          <div class="card-icon">
            <el-icon :size="36"><Box /></el-icon>
          </div>
          <div class="card-info">
            <div class="card-label">磁盘使用率</div>
            <div class="card-value">{{ systemInfo.disk.usage || 0 }}%</div>
            <el-progress
              :percentage="systemInfo.disk.usage || 0"
              :stroke-width="6"
              :show-text="false"
              :color="getProgressColor(systemInfo.disk.usage)"
            />
            <div class="card-detail">
              {{ formatBytes(systemInfo.disk.used) }} / {{ formatBytes(systemInfo.disk.total) }}
            </div>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <div class="info-card network-card">
          <div class="card-icon">
            <el-icon :size="36"><Connection /></el-icon>
          </div>
          <div class="card-info">
            <div class="card-label">网络流量</div>
            <div class="card-value">{{ formatBytes(systemInfo.network.down) }}/s</div>
            <div class="network-detail">
              <span class="upload">
                <el-icon><Top /></el-icon>
                {{ formatBytes(systemInfo.network.up) }}/s
              </span>
              <span class="download">
                <el-icon><Bottom /></el-icon>
                {{ formatBytes(systemInfo.network.down) }}/s
              </span>
            </div>
            <div class="card-detail">运行时间: {{ formatUptime(systemInfo.uptime) }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 系统负载和进程信息 -->
    <el-row :gutter="16" class="info-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="page-card mini-card">
          <div class="mini-card-header">
            <el-icon><Monitor /></el-icon>
            <span>系统负载</span>
          </div>
          <div class="mini-card-body">
            <div class="load-avg">
              <div class="load-item">
                <span class="load-label">1分钟</span>
                <span class="load-value">{{ systemInfo.load?.one ?? '-' }}</span>
              </div>
              <div class="load-item">
                <span class="load-label">5分钟</span>
                <span class="load-value">{{ systemInfo.load?.five ?? '-' }}</span>
              </div>
              <div class="load-item">
                <span class="load-label">15分钟</span>
                <span class="load-value">{{ systemInfo.load?.fifteen ?? '-' }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="page-card mini-card">
          <div class="mini-card-header">
            <el-icon><Setting /></el-icon>
            <span>进程信息</span>
          </div>
          <div class="mini-card-body">
            <div class="process-info">
              <div class="process-item">
                <span class="process-label">总进程数</span>
                <span class="process-value">{{ systemInfo.process?.total || '-' }}</span>
              </div>
              <div class="process-item">
                <span class="process-label">运行中</span>
                <span class="process-value text-success">{{ systemInfo.process?.running || '-' }}</span>
              </div>
              <div class="process-item">
                <span class="process-label">睡眠中</span>
                <span class="process-value">{{ systemInfo.process?.sleeping || '-' }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="page-card mini-card">
          <div class="mini-card-header">
            <el-icon><Coin /></el-icon>
            <span>Swap 内存</span>
          </div>
          <div class="mini-card-body">
            <div class="swap-info">
              <el-progress
                :percentage="systemInfo.swap?.usage || 0"
                :stroke-width="8"
                :color="getProgressColor(systemInfo.swap?.usage)"
              />
              <div class="swap-detail">
                <span>{{ formatBytes(systemInfo.swap?.used || 0) }} / {{ formatBytes(systemInfo.swap?.total || 0) }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="page-card mini-card">
          <div class="mini-card-header">
            <el-icon><Connection /></el-icon>
            <span>网络连接</span>
          </div>
          <div class="mini-card-body">
            <div class="network-conn">
              <div class="conn-item">
                <span class="conn-label">TCP 连接</span>
                <span class="conn-value">{{ systemInfo.network?.tcp || '-' }}</span>
              </div>
              <div class="conn-item">
                <span class="conn-label">活动连接</span>
                <span class="conn-value text-primary">{{ systemInfo.network?.established || '-' }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 服务状态 -->
    <el-row :gutter="16" class="service-row">
      <el-col :xs="24">
        <div class="page-card">
          <div class="page-header">
            <h3 class="page-title">服务状态</h3>
            <el-button icon="Refresh" size="small" @click="refreshServices">刷新</el-button>
          </div>
          <div class="service-grid">
            <div
              v-for="svc in serviceList"
              :key="svc.name"
              class="service-item"
              :class="{ 'service-running': svc.running, 'service-stopped': !svc.running }"
            >
              <div class="service-icon">
                <el-icon :size="20"><component :is="svc.icon || 'Box'" /></el-icon>
              </div>
              <div class="service-info">
                <span class="service-name">{{ svc.name }}</span>
                <span class="service-status">{{ svc.running ? '运行中' : '未运行' }}</span>
                <span v-if="svc.version" class="service-version">v{{ svc.version }}</span>
              </div>
              <div class="service-actions">
                <el-button-group size="small">
                  <el-button
                    v-if="!svc.running"
                    type="success"
                    :icon="VideoPlay"
                    @click.stop="controlService(svc, 'start')"
                    :loading="svc.loading"
                  />
                  <el-button
                    v-if="svc.running"
                    type="warning"
                    :icon="VideoPause"
                    @click.stop="controlService(svc, 'restart')"
                    :loading="svc.loading"
                  />
                  <el-button
                    v-if="svc.running"
                    type="danger"
                    :icon="SwitchButton"
                    @click.stop="controlService(svc, 'stop')"
                    :loading="svc.loading"
                  />
                </el-button-group>
              </div>
              <div class="service-dot" :class="svc.running ? 'dot-green' : 'dot-red'"></div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-row :gutter="16" class="quick-actions-row">
      <el-col :xs="24">
        <div class="page-card">
          <div class="page-header">
            <h3 class="page-title">快捷操作</h3>
          </div>
          <div class="quick-actions-grid">
            <el-tooltip content="重启面板服务，不影响网站运行" placement="top">
              <el-button class="quick-action-btn" @click="quickAction('restart_panel')">
                <el-icon><RefreshRight /></el-icon>
                <span>重启面板</span>
              </el-button>
            </el-tooltip>
            <el-tooltip content="清空面板操作日志" placement="top">
              <el-button class="quick-action-btn" @click="quickAction('clear_logs')">
                <el-icon><Delete /></el-icon>
                <span>清空日志</span>
              </el-button>
            </el-tooltip>
            <el-tooltip content="检查面板是否有新版本" placement="top">
              <el-button class="quick-action-btn" @click="quickAction('check_update')">
                <el-icon><Upload /></el-icon>
                <span>检查更新</span>
              </el-button>
            </el-tooltip>
            <el-tooltip content="管理服务器文件 (快捷键: F)" placement="top">
              <el-button class="quick-action-btn" @click="$router.push('/files')">
                <el-icon><FolderOpened /></el-icon>
                <span>文件管理</span>
              </el-button>
            </el-tooltip>
            <el-tooltip content="管理网站站点" placement="top">
              <el-button class="quick-action-btn" @click="$router.push('/site')">
                <el-icon><ChromeFilled /></el-icon>
                <span>网站管理</span>
              </el-button>
            </el-tooltip>
            <el-tooltip content="查看系统监控数据 (快捷键: M)" placement="top">
              <el-button class="quick-action-btn" @click="$router.push('/monitor')">
                <el-icon><Monitor /></el-icon>
                <span>系统监控</span>
              </el-button>
            </el-tooltip>
            <el-tooltip content="配置防火墙规则" placement="top">
              <el-button class="quick-action-btn" @click="$router.push('/firewall')">
                <el-icon><Shield /></el-icon>
                <span>防火墙</span>
              </el-button>
            </el-tooltip>
            <el-tooltip content="面板全局设置 (快捷键: S)" placement="top">
              <el-button class="quick-action-btn" @click="$router.push('/setting')">
                <el-icon><Setting /></el-icon>
                <span>面板设置</span>
              </el-button>
            </el-tooltip>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :lg="16">
        <div class="page-card">
          <div class="page-header">
            <h3 class="page-title">资源使用趋势</h3>
            <el-radio-group v-model="chartTimeRange" size="small">
              <el-radio-button label="1h">1小时</el-radio-button>
              <el-radio-button label="6h">6小时</el-radio-button>
              <el-radio-button label="24h">24小时</el-radio-button>
            </el-radio-group>
          </div>
          <div ref="trendChartRef" class="chart-container"></div>
        </div>
      </el-col>

      <el-col :xs="24" :lg="8">
        <div class="page-card">
          <div class="page-header">
            <h3 class="page-title">系统信息</h3>
          </div>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="主机名">{{ systemInfo.hostname || '-' }}</el-descriptions-item>
            <el-descriptions-item label="操作系统">{{ systemInfo.os || '-' }}</el-descriptions-item>
            <el-descriptions-item label="内核版本">{{ systemInfo.kernel || '-' }}</el-descriptions-item>
            <el-descriptions-item label="运行时间">{{ formatUptime(systemInfo.uptime) }}</el-descriptions-item>
            <el-descriptions-item label="CPU 型号">{{ systemInfo.cpu.model || '-' }}</el-descriptions-item>
            <el-descriptions-item label="CPU 核心">{{ systemInfo.cpu.cores || '-' }} 核</el-descriptions-item>
            <el-descriptions-item label="总内存">{{ formatBytes(systemInfo.memory.total) }}</el-descriptions-item>
            <el-descriptions-item label="总磁盘">{{ formatBytes(systemInfo.disk.total) }}</el-descriptions-item>
            <el-descriptions-item label="系统架构">{{ systemInfo.arch || '-' }}</el-descriptions-item>
            <el-descriptions-item label="面板版本">{{ systemInfo.version || '-' }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { VideoPlay, VideoPause, SwitchButton, Refresh } from '@element-plus/icons-vue';
import { useAppStore } from '@/stores/app';
import * as echarts from 'echarts';
import { getIndexPluginList, restartPanelApi, clearLogs as apiClearLogs, runPlugin } from '@/api/index';

const router = useRouter();
const appStore = useAppStore();
const systemInfo = ref(appStore.systemInfo);

// 服务列表
const serviceList = ref([]);

// 欢迎横幅
const autoRefresh = ref(true);
const refreshCountdown = ref(30);
const dismissedAlerts = ref(new Set());

const greeting = computed(() => {
  const h = new Date().getHours();
  if (h < 6) return '夜深了';
  if (h < 9) return '早上好';
  if (h < 12) return '上午好';
  if (h < 14) return '中午好';
  if (h < 18) return '下午好';
  if (h < 22) return '晚上好';
  return '夜深了';
});

const currentDate = computed(() => {
  const now = new Date();
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
  return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日 ${weekdays[now.getDay()]}`;
});

// 系统健康度评分 (0-100)
const healthScore = computed(() => {
  const cpu = systemInfo.value.cpu.usage || 0;
  const mem = systemInfo.value.memory.usage || 0;
  const disk = systemInfo.value.disk.usage || 0;
  // 权重: CPU 40%, Memory 35%, Disk 25%
  const cpuScore = Math.max(0, 100 - cpu * 1.2);
  const memScore = Math.max(0, 100 - mem * 1.1);
  const diskScore = Math.max(0, 100 - disk * 1.0);
  return Math.round(cpuScore * 0.4 + memScore * 0.35 + diskScore * 0.25);
});

const healthClass = computed(() => {
  if (healthScore.value >= 80) return 'health-good';
  if (healthScore.value >= 60) return 'health-warning';
  return 'health-danger';
});

// 资源告警
const activeAlerts = computed(() => {
  const alerts = [];
  const cpu = systemInfo.value.cpu.usage || 0;
  const mem = systemInfo.value.memory.usage || 0;
  const disk = systemInfo.value.disk.usage || 0;

  if (cpu > 90 && !dismissedAlerts.value.has('cpu')) {
    alerts.push({ key: 'cpu', title: 'CPU 使用率过高', description: `当前 CPU 使用率 ${cpu}%，建议检查高负载进程`, type: 'error' });
  } else if (cpu > 80 && !dismissedAlerts.value.has('cpu')) {
    alerts.push({ key: 'cpu', title: 'CPU 使用率偏高', description: `当前 CPU 使用率 ${cpu}%，请关注系统负载`, type: 'warning' });
  }

  if (mem > 90 && !dismissedAlerts.value.has('mem')) {
    alerts.push({ key: 'mem', title: '内存使用率过高', description: `当前内存使用率 ${mem}%，可能存在内存泄漏`, type: 'error' });
  } else if (mem > 80 && !dismissedAlerts.value.has('mem')) {
    alerts.push({ key: 'mem', title: '内存使用率偏高', description: `当前内存使用率 ${mem}%，建议清理缓存或增加内存`, type: 'warning' });
  }

  if (disk > 95 && !dismissedAlerts.value.has('disk')) {
    alerts.push({ key: 'disk', title: '磁盘空间严重不足', description: `当前磁盘使用率 ${disk}%，请立即清理空间`, type: 'error' });
  } else if (disk > 85 && !dismissedAlerts.value.has('disk')) {
    alerts.push({ key: 'disk', title: '磁盘空间不足', description: `当前磁盘使用率 ${disk}%，建议清理日志和临时文件`, type: 'warning' });
  }

  return alerts;
});

function dismissAlert(key) {
  dismissedAlerts.value.add(key);
}

function manualRefresh() {
  refreshData();
  refreshCountdown.value = 30;
}

const serviceIcons = {
  'openresty': 'Monitor',
  'nginx': 'Monitor',
  'mysql': 'Coin',
  'mariadb': 'Coin',
  'pgsql': 'Coin',
  'mongodb': 'Coin',
  'php': 'Document',
  'redis': 'Connection',
  'memcached': 'Connection',
  'node': 'Promotion',
  'ftp': 'Upload',
};

async function refreshServices() {
  try {
    const res = await getIndexPluginList();
    if (res && Array.isArray(res.data)) {
      serviceList.value = res.data.map(item => ({
        name: item.title || item.name,
        running: !!item.setup,
        icon: serviceIcons[item.name?.toLowerCase()] || 'Box',
        version: item.version || '',
        loading: false
      }));
    }
  } catch {
    serviceList.value = [];
  }
}

async function controlService(svc, action) {
  const actionNames = { start: '启动', stop: '停止', restart: '重启' };
  try {
    await ElMessageBox.confirm(`确定要${actionNames[action]} ${svc.name} 吗？`, '操作确认', { type: 'warning' });
    svc.loading = true;
    await runPlugin(svc.name, action, svc.version);
    ElMessage.success(`${svc.name} ${actionNames[action]}命令已执行`);
    setTimeout(() => refreshServices(), 2000);
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(`${actionNames[action]}失败`);
    }
  } finally {
    svc.loading = false;
  }
}

async function quickAction(action) {
  switch (action) {
    case 'restart_panel':
      try {
        await ElMessageBox.confirm('确定要重启面板服务吗？', '重启确认', { type: 'warning' });
        await restartPanelApi();
        ElMessage.success('面板正在重启...');
        setTimeout(() => window.location.reload(), 3000);
      } catch {
        // cancelled
      }
      break;
    case 'clear_logs':
      try {
        await ElMessageBox.confirm('确定要清空面板日志吗？', '清空确认', { type: 'warning' });
        await apiClearLogs();
        ElMessage.success('日志已清空');
      } catch {
        // cancelled or error
      }
      break;
    case 'check_update':
      ElMessage.info('当前已是最新版本');
      break;
  }
}
const trendChartRef = ref(null);
const chartTimeRange = ref('1h');

let trendChart = null;
let refreshTimer = null;
let countdownTimer = null;

// 历史数据用于图表
const MAX_HISTORY = 60;
const cpuHistory = reactive([]);
const memHistory = reactive([]);
const diskHistory = reactive([]);
const timeLabels = reactive([]);

function getProgressColor(value) {
  if (value >= 90) return '#f56c6c';
  if (value >= 70) return '#e6a23c';
  return '#67c23a';
}

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const k = 1024;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + units[i];
}

function formatUptime(uptime) {
  if (!uptime) return '-';
  if (typeof uptime === 'string') {
    const match = uptime.match(/(\d+天\d+小时\d+分钟)/);
    if (match) return match[1];
    if (uptime.includes('天') || uptime.includes('小时') || uptime.includes('分钟')) {
      return uptime.replace('已不间断运行: ', '');
    }
    return uptime;
  }
  const days = Math.floor(uptime / 86400);
  const hours = Math.floor((uptime % 86400) / 3600);
  const mins = Math.floor((uptime % 3600) / 60);
  const parts = [];
  if (days > 0) parts.push(`${days}天`);
  if (hours > 0) parts.push(`${hours}小时`);
  parts.push(`${mins}分钟`);
  return parts.join('');
}

function getTimeLabel() {
  const now = new Date();
  return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
}

function pushHistory(arr, value) {
  arr.push(value);
  if (arr.length > MAX_HISTORY) arr.shift();
}

function initTrendChart() {
  if (!trendChartRef.value) return;

  trendChart = echarts.init(trendChartRef.value);

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      borderWidth: 1,
      textStyle: { color: '#303133' },
    },
    legend: {
      data: ['CPU', '内存', '磁盘'],
      bottom: 0,
    },
    grid: {
      left: '3%',
      right: '3%',
      top: '10%',
      bottom: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [...timeLabels],
      axisLine: { lineStyle: { color: '#dcdfe6' } },
      axisLabel: { color: '#909399', fontSize: 10 },
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#f0f2f5' } },
      axisLabel: { color: '#909399', formatter: '{value}%' },
    },
    series: [
      {
        name: 'CPU',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: '#409eff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' },
          ]),
        },
        data: [...cpuHistory],
      },
      {
        name: '内存',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: '#67c23a' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' },
          ]),
        },
        data: [...memHistory],
      },
      {
        name: '磁盘',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: '#e6a23c' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(230, 162, 60, 0.3)' },
            { offset: 1, color: 'rgba(230, 162, 60, 0.05)' },
          ]),
        },
        data: [...diskHistory],
      },
    ],
  };

  trendChart.setOption(option);
}

function updateTrendChart() {
  if (!trendChart) return;
  trendChart.setOption({
    xAxis: { data: [...timeLabels] },
    series: [
      { data: [...cpuHistory] },
      { data: [...memHistory] },
      { data: [...diskHistory] },
    ],
  });
}

async function refreshData() {
  try {
    await appStore.fetchSystemInfo();
    systemInfo.value = appStore.systemInfo;

    // 更新图表历史
    const label = getTimeLabel();
    pushHistory(timeLabels, label);
    pushHistory(cpuHistory, systemInfo.value.cpu.usage || 0);
    pushHistory(memHistory, systemInfo.value.memory.usage || 0);
    pushHistory(diskHistory, systemInfo.value.disk.usage || 0);

    updateTrendChart();
  } catch {
    // 静默处理
  }
}

// 键盘快捷键
function handleKeydown(e) {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
  if (e.key === 'r' || e.key === 'R') {
    e.preventDefault();
    manualRefresh();
  }
}

// 自动刷新控制
watch(autoRefresh, (val) => {
  if (val) {
    refreshCountdown.value = 30;
    startAutoRefresh();
  } else {
    stopAutoRefresh();
  }
});

function startAutoRefresh() {
  stopAutoRefresh();
  refreshTimer = setInterval(() => {
    refreshData();
    refreshCountdown.value = 30;
  }, 30000);
  countdownTimer = setInterval(() => {
    if (refreshCountdown.value > 0) refreshCountdown.value--;
  }, 1000);
}

function stopAutoRefresh() {
  if (refreshTimer) { clearInterval(refreshTimer); refreshTimer = null; }
  if (countdownTimer) { clearInterval(countdownTimer); countdownTimer = null; }
}

onMounted(async () => {
  await refreshData();
  refreshServices();
  await nextTick();
  initTrendChart();

  // 启动自动刷新
  startAutoRefresh();

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize);
  window.addEventListener('keydown', handleKeydown);
});

onBeforeUnmount(() => {
  stopAutoRefresh();
  if (trendChart) trendChart.dispose();
  window.removeEventListener('resize', handleResize);
  window.removeEventListener('keydown', handleKeydown);
});

function handleResize() {
  if (trendChart) trendChart.resize();
}
</script>

<style lang="scss" scoped>
.dashboard-page {
  // 欢迎横幅
  .welcome-banner {
    background: linear-gradient(135deg, #409eff 0%, #6366f1 50%, #764ba2 100%);
    border-radius: 12px;
    padding: 24px 28px;
    margin-bottom: 16px;
    color: #fff;
    position: relative;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      top: -50%;
      right: -20%;
      width: 300px;
      height: 300px;
      background: rgba(255, 255, 255, 0.06);
      border-radius: 50%;
    }

    &::after {
      content: '';
      position: absolute;
      bottom: -60%;
      right: 10%;
      width: 200px;
      height: 200px;
      background: rgba(255, 255, 255, 0.04);
      border-radius: 50%;
    }

    .welcome-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: relative;
      z-index: 1;

      .welcome-left {
        .welcome-greeting {
          margin: 0 0 6px;
          font-size: 22px;
          font-weight: 700;
        }

        .welcome-date {
          margin: 0;
          font-size: 13px;
          opacity: 0.85;
        }
      }

      .welcome-right {
        display: flex;
        align-items: center;
        gap: 20px;

        .health-score {
          position: relative;
          width: 72px;
          height: 72px;

          .health-ring {
            width: 72px;
            height: 72px;
            transform: rotate(-90deg);

            .health-ring-bg {
              fill: none;
              stroke: rgba(255, 255, 255, 0.2);
              stroke-width: 3;
            }

            .health-ring-fg {
              fill: none;
              stroke: #67c23a;
              stroke-width: 3;
              stroke-linecap: round;
              transition: stroke-dasharray 0.6s ease;
            }
          }

          .health-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;

            .health-number {
              display: block;
              font-size: 18px;
              font-weight: 700;
              line-height: 1;
            }

            .health-label {
              font-size: 9px;
              opacity: 0.8;
            }
          }

          &.health-good .health-ring-fg { stroke: #67c23a; }
          &.health-warning .health-ring-fg { stroke: #e6a23c; }
          &.health-danger .health-ring-fg { stroke: #f56c6c; }
        }

        .refresh-control {
          display: flex;
          align-items: center;
          gap: 8px;

          .refresh-countdown {
            font-size: 12px;
            opacity: 0.8;
            min-width: 28px;
          }

          .el-button {
            background: rgba(255, 255, 255, 0.15);
            border-color: rgba(255, 255, 255, 0.3);
            color: #fff;

            &:hover {
              background: rgba(255, 255, 255, 0.25);
            }
          }
        }
      }
    }
  }

  // 资源告警
  .alerts-container {
    margin-bottom: 12px;
  }

  .resource-alert {
    margin-bottom: 8px;
    border-radius: 8px;
  }

  .alert-slide-enter-active,
  .alert-slide-leave-active {
    transition: all 0.3s ease;
  }

  .alert-slide-enter-from {
    opacity: 0;
    transform: translateY(-10px);
  }

  .alert-slide-leave-to {
    opacity: 0;
    transform: translateX(30px);
  }

  .info-cards {
    margin-bottom: 16px;
  }

  .info-card {
    background: #ffffff;
    border-radius: 8px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    margin-bottom: 16px;
    transition: transform 0.2s, box-shadow 0.2s;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }

    .card-icon {
      width: 60px;
      height: 60px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      flex-shrink: 0;
    }

    .card-info {
      flex: 1;
      min-width: 0;

      .card-label {
        font-size: 13px;
        color: #909399;
        margin-bottom: 4px;
      }

      .card-value {
        font-size: 24px;
        font-weight: 700;
        color: #303133;
        margin-bottom: 8px;
      }

      .card-detail {
        font-size: 12px;
        color: #909399;
        margin-top: 6px;
      }
    }
  }

  .cpu-card .card-icon { background: linear-gradient(135deg, #409eff, #66b1ff); }
  .memory-card .card-icon { background: linear-gradient(135deg, #67c23a, #85ce61); }
  .disk-card .card-icon { background: linear-gradient(135deg, #e6a23c, #ebb563); }
  .network-card .card-icon { background: linear-gradient(135deg, #f56c6c, #f89898); }

  .network-detail {
    display: flex;
    gap: 16px;
    margin-bottom: 4px;

    .upload, .download {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 13px;
      color: #606266;
    }

    .upload .el-icon { color: #f56c6c; }
    .download .el-icon { color: #67c23a; }
  }

  .info-row {
    margin-bottom: 16px;

    .mini-card {
      margin-bottom: 16px;

      .mini-card-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 12px;

        .el-icon {
          color: #409eff;
        }
      }

      .mini-card-body {
        .load-avg {
          display: flex;
          justify-content: space-between;

          .load-item {
            text-align: center;

            .load-label {
              display: block;
              font-size: 12px;
              color: #909399;
              margin-bottom: 4px;
            }

            .load-value {
              font-size: 18px;
              font-weight: 600;
              color: #303133;
            }
          }
        }

        .process-info {
          display: flex;
          justify-content: space-between;

          .process-item {
            text-align: center;

            .process-label {
              display: block;
              font-size: 12px;
              color: #909399;
              margin-bottom: 4px;
            }

            .process-value {
              font-size: 18px;
              font-weight: 600;
              color: #303133;

              &.text-success { color: #67c23a; }
              &.text-primary { color: #409eff; }
            }
          }
        }

        .swap-info {
          .swap-detail {
            margin-top: 8px;
            text-align: center;
            font-size: 13px;
            color: #606266;
          }
        }

        .network-conn {
          display: flex;
          justify-content: space-between;

          .conn-item {
            text-align: center;

            .conn-label {
              display: block;
              font-size: 12px;
              color: #909399;
              margin-bottom: 4px;
            }

            .conn-value {
              font-size: 18px;
              font-weight: 600;
              color: #303133;

              &.text-primary { color: #409eff; }
            }
          }
        }
      }
    }
  }

  .chart-row {
    .page-card {
      margin-bottom: 16px;
    }
  }

  .quick-actions-row {
    margin-bottom: 16px;

    .quick-actions-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      padding: 8px 0;

      .quick-action-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
        padding: 16px 24px;
        height: auto;
        border-radius: 8px;
        transition: all 0.2s;

        .el-icon {
          font-size: 20px;
        }

        span {
          font-size: 12px;
        }

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
      }
    }
  }

  .chart-container {
    width: 100%;
    height: 320px;
  }

  .service-row {
    margin-bottom: 16px;
  }

  .service-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
    padding: 8px 0;

    .service-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 12px 16px;
      border-radius: 8px;
      background: #f5f7fa;
      transition: all 0.2s;

      &:hover {
        background: #ecf5ff;
      }

      &.service-running {
        border-left: 3px solid #67c23a;
      }

      &.service-stopped {
        border-left: 3px solid #dcdfe6;
        opacity: 0.7;
      }

      .service-icon {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #e4e7ed;
        color: #606266;
        flex-shrink: 0;
      }

      .service-info {
        flex: 1;
        min-width: 0;

        .service-name {
          display: block;
          font-size: 13px;
          font-weight: 500;
          color: #303133;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .service-status {
          font-size: 11px;
          color: #909399;
        }

        .service-version {
          font-size: 11px;
          color: #409eff;
          margin-left: 4px;
        }
      }

      .service-actions {
        flex-shrink: 0;

        .el-button-group {
          .el-button {
            padding: 5px 8px;
          }
        }
      }

      .service-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;

        &.dot-green {
          background: #67c23a;
          box-shadow: 0 0 6px rgba(103, 194, 58, 0.5);
        }

        &.dot-red {
          background: #dcdfe6;
        }
      }
    }
  }

  @media (max-width: 768px) {
    .welcome-banner {
      padding: 16px 20px;

      .welcome-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 16px;

        .welcome-left {
          .welcome-greeting {
            font-size: 18px;
          }
        }

        .welcome-right {
          width: 100%;
          justify-content: space-between;
        }
      }
    }

    .quick-actions-grid {
      justify-content: center;

      .quick-action-btn {
        padding: 12px 18px;
      }
    }

    .service-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
