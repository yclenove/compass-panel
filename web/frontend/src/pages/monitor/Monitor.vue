<template>
  <div class="monitor-page">
    <!-- 实时监控卡片 -->
    <el-row :gutter="16" class="realtime-cards">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="monitor-card cpu-card">
          <div class="card-header">
            <el-icon :size="24"><Cpu /></el-icon>
            <span>CPU 使用率</span>
          </div>
          <div class="card-body">
            <el-progress
              type="dashboard"
              :percentage="cpuUsage"
              :color="getProgressColor(cpuUsage)"
              :width="120"
            >
              <template #default>
                <span class="progress-text">{{ cpuUsage }}%</span>
              </template>
            </el-progress>
          </div>
          <div class="card-footer">
            <span>核心数: {{ cpuCores }}</span>
            <span>
              负载:
              <el-tooltip :content="`1分钟: ${loadAvg[0]} / 5分钟: ${loadAvg[1]} / 15分钟: ${loadAvg[2]}`" placement="top">
                <el-tag :type="getLoadType()" size="small" class="load-tag">{{ loadAvg[0] }}</el-tag>
              </el-tooltip>
            </span>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="monitor-card memory-card">
          <div class="card-header">
            <el-icon :size="24"><Coin /></el-icon>
            <span>内存使用率</span>
          </div>
          <div class="card-body">
            <el-progress
              type="dashboard"
              :percentage="memoryUsage"
              :color="getProgressColor(memoryUsage)"
              :width="120"
            >
              <template #default>
                <span class="progress-text">{{ memoryUsage }}%</span>
              </template>
            </el-progress>
          </div>
          <div class="card-footer">
            <span>已用: {{ formatBytes(memoryUsed) }}</span>
            <span>总计: {{ formatBytes(memoryTotal) }}</span>
          </div>
          <div v-if="swapTotal > 0" class="swap-bar">
            <div class="swap-label">Swap: {{ formatBytes(swapUsed) }} / {{ formatBytes(swapTotal) }}</div>
            <el-progress :percentage="swapUsage" :stroke-width="6" :show-text="false" :color="getProgressColor(swapUsage)" />
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="monitor-card disk-card">
          <div class="card-header">
            <el-icon :size="24"><Box /></el-icon>
            <span>磁盘使用率</span>
          </div>
          <div class="card-body">
            <el-progress
              type="dashboard"
              :percentage="diskUsage"
              :color="getProgressColor(diskUsage)"
              :width="120"
            >
              <template #default>
                <span class="progress-text">{{ diskUsage }}%</span>
              </template>
            </el-progress>
          </div>
          <div class="card-footer">
            <span>已用: {{ formatBytes(diskUsed) }}</span>
            <span>总计: {{ formatBytes(diskTotal) }}</span>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="monitor-card network-card">
          <div class="card-header">
            <el-icon :size="24"><Connection /></el-icon>
            <span>网络流量</span>
          </div>
          <div class="card-body">
            <div class="network-stats">
              <div class="network-item">
                <el-icon><Top /></el-icon>
                <span class="network-label">上行</span>
                <span class="network-value">{{ formatBytes(networkUp) }}/s</span>
              </div>
              <div class="network-item">
                <el-icon><Bottom /></el-icon>
                <span class="network-label">下行</span>
                <span class="network-value">{{ formatBytes(networkDown) }}/s</span>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <span>TCP连接: {{ tcpConnections }}</span>
            <span>运行: {{ systemInfo.uptime || '-' }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>CPU 使用趋势</span>
              <el-radio-group v-model="cpuTimeRange" size="small">
                <el-radio-button label="1h">1小时</el-radio-button>
                <el-radio-button label="6h">6小时</el-radio-button>
                <el-radio-button label="24h">24小时</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="cpuChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>内存使用趋势</span>
              <el-radio-group v-model="memoryTimeRange" size="small">
                <el-radio-button label="1h">1小时</el-radio-button>
                <el-radio-button label="6h">6小时</el-radio-button>
                <el-radio-button label="24h">24小时</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="memoryChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>磁盘 I/O 趋势</span>
              <el-radio-group v-model="diskTimeRange" size="small">
                <el-radio-button label="1h">1小时</el-radio-button>
                <el-radio-button label="6h">6小时</el-radio-button>
                <el-radio-button label="24h">24小时</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="diskChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>网络流量趋势</span>
              <el-radio-group v-model="networkTimeRange" size="small">
                <el-radio-button label="1h">1小时</el-radio-button>
                <el-radio-button label="6h">6小时</el-radio-button>
                <el-radio-button label="24h">24小时</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="networkChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 进程监控 -->
    <el-card class="process-card">
      <template #header>
        <div class="chart-header">
          <span>
            进程监控
            <el-tag size="small" type="info" style="margin-left: 8px">{{ filteredProcesses.length }} 个进程</el-tag>
          </span>
          <div class="process-actions">
            <el-input
              v-model="processSearch"
              placeholder="搜索进程"
              clearable
              prefix-icon="Search"
              style="width: 180px"
              size="small"
            />
            <el-select v-model="processSortBy" style="width: 120px" size="small">
              <el-option label="CPU 降序" value="cpu_desc" />
              <el-option label="内存 降序" value="mem_desc" />
              <el-option label="PID 升序" value="pid_asc" />
              <el-option label="名称" value="name_asc" />
            </el-select>
            <el-button icon="Refresh" size="small" @click="refreshProcesses">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- Top 5 资源消耗 -->
      <div class="top-processes" v-if="topProcesses.length > 0">
        <span class="top-label">Top 5 资源消耗:</span>
        <el-tag
          v-for="(p, idx) in topProcesses"
          :key="p.pid"
          :type="idx === 0 ? 'danger' : idx < 3 ? 'warning' : 'info'"
          size="small"
          class="top-tag"
        >
          {{ p.name }} ({{ p.cpu }}% CPU, {{ p.memory }}% 内存)
        </el-tag>
      </div>

      <el-table :data="filteredProcesses" stripe max-height="400" v-loading="processLoading">
        <el-table-column prop="pid" label="PID" width="70" />
        <el-table-column prop="name" label="进程名称" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span :class="{ 'hot-process': parseFloat(row.cpu) > 50 }">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="user" label="用户" width="90" />
        <el-table-column prop="cpu" label="CPU %" width="140" sortable>
          <template #default="{ row }">
            <div class="progress-cell">
              <el-progress
                :percentage="parseFloat(row.cpu)"
                :stroke-width="10"
                :show-text="false"
                :color="getProgressColor(parseFloat(row.cpu))"
              />
              <span class="progress-value" :style="{ color: getProgressColor(parseFloat(row.cpu)) }">{{ row.cpu }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="memory" label="内存 %" width="140" sortable>
          <template #default="{ row }">
            <div class="progress-cell">
              <el-progress
                :percentage="parseFloat(row.memory)"
                :stroke-width="10"
                :show-text="false"
                :color="getProgressColor(parseFloat(row.memory))"
              />
              <span class="progress-value" :style="{ color: getProgressColor(parseFloat(row.memory)) }">{{ row.memory }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'running' ? 'success' : 'info'" size="small">
              {{ row.status === 'running' ? '运行中' : '睡眠' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="启动时间" width="150" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-popconfirm title="确定要终止此进程吗？" @confirm="killProcess(row)">
              <template #reference>
                <el-button type="danger" link size="small">终止</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 监控设置 -->
    <el-card class="monitor-settings-card">
      <template #header>
        <div class="chart-header">
          <span>监控设置</span>
          <el-button icon="Refresh" @click="fetchMonitorSettings" size="small">刷新</el-button>
        </div>
      </template>
      <el-row :gutter="16">
        <el-col :xs="24" :sm="8">
          <div class="setting-item">
            <span class="setting-label">监控记录</span>
            <el-switch v-model="monitorEnabled" @change="toggleMonitor" active-text="开启" inactive-text="关闭" />
          </div>
        </el-col>
        <el-col :xs="24" :sm="8">
          <div class="setting-item">
            <span class="setting-label">保留天数</span>
            <el-input-number v-model="monitorDays" :min="1" :max="365" style="width: 120px" />
            <el-button type="primary" size="small" style="margin-left: 8px" @click="saveMonitorDays">保存</el-button>
          </div>
        </el-col>
        <el-col :xs="24" :sm="8">
          <div class="setting-item">
            <span class="setting-label">仅统计外网</span>
            <el-switch v-model="monitorOnlyNet" @change="toggleOnlyNet" active-text="开启" inactive-text="关闭" />
          </div>
        </el-col>
      </el-row>
      <el-divider />
      <el-button type="danger" @click="clearMonitorData" :loading="clearingData">清空监控记录</el-button>
    </el-card>

    <!-- 系统信息 -->
    <el-card class="system-info-card">
      <template #header>
        <div class="chart-header">
          <span>系统信息</span>
          <div>
            <el-button type="warning" size="small" @click="handleRestartPanel">
              <el-icon><RefreshRight /></el-icon> 重启面板
            </el-button>
            <el-button type="danger" size="small" @click="handleRestartServer">
              <el-icon><SwitchButton /></el-icon> 重启服务器
            </el-button>
          </div>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="主机名">{{ systemInfo.hostname || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作系统">{{ systemInfo.os || '-' }}</el-descriptions-item>
        <el-descriptions-item label="内核版本">{{ systemInfo.kernel || '-' }}</el-descriptions-item>
        <el-descriptions-item label="系统架构">{{ systemInfo.arch || '-' }}</el-descriptions-item>
        <el-descriptions-item label="运行时间">{{ systemInfo.uptime || '-' }}</el-descriptions-item>
        <el-descriptions-item label="面板版本">{{ systemInfo.version || '-' }}</el-descriptions-item>
        <el-descriptions-item label="CPU 型号">{{ systemInfo.cpu_model || '-' }}</el-descriptions-item>
        <el-descriptions-item label="CPU 核心">{{ systemInfo.cpu_cores || '-' }} 核</el-descriptions-item>
        <el-descriptions-item label="总内存">{{ formatBytes(systemInfo.memory_total) }}</el-descriptions-item>
        <el-descriptions-item label="总磁盘">{{ formatBytes(systemInfo.disk_total) }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import * as echarts from 'echarts';
import { useAppStore } from '@/stores/app';
import { getSystemInfo, getSystemNetwork, getDiskInfo, getCpuIo, getDiskIo, getNetworkIo, getMonitorControl, setMonitorControl, restartPanelApi, restartServerApi } from '@/api/index';

const appStore = useAppStore();

// 实时数据
const cpuUsage = ref(0);
const cpuCores = ref(0);
const cpuTemp = ref(0);
const memoryUsage = ref(0);
const memoryUsed = ref(0);
const memoryTotal = ref(0);
const swapUsage = ref(0);
const swapUsed = ref(0);
const swapTotal = ref(0);
const diskUsage = ref(0);
const diskUsed = ref(0);
const diskTotal = ref(0);
const networkUp = ref(0);
const networkDown = ref(0);
const tcpConnections = ref(0);
const activeConnections = ref(0);
const loadAvg = ref([0, 0, 0]);

// 历史数据（用于图表）
const MAX_HISTORY = 60;
const cpuHistory = reactive([]);
const memHistory = reactive([]);
const diskReadHistory = reactive([]);
const diskWriteHistory = reactive([]);
const netUpHistory = reactive([]);
const netDownHistory = reactive([]);
const timeLabels = reactive([]);

// 图表引用
const cpuChartRef = ref(null);
const memoryChartRef = ref(null);
const diskChartRef = ref(null);
const networkChartRef = ref(null);

// 图表实例
let cpuChart = null;
let memoryChart = null;
let diskChart = null;
let networkChart = null;

// 进程列表
const processList = ref([]);
const processLoading = ref(false);
const processSearch = ref('');
const processSortBy = ref('cpu_desc');

// Top 5 processes by resource usage
const topProcesses = computed(() => {
  return [...processList.value]
    .sort((a, b) => (parseFloat(b.cpu) + parseFloat(b.memory)) - (parseFloat(a.cpu) + parseFloat(a.memory)))
    .slice(0, 5);
});

// Filtered and sorted processes
const filteredProcesses = computed(() => {
  let list = [...processList.value];

  if (processSearch.value) {
    const q = processSearch.value.toLowerCase();
    list = list.filter(p =>
      (p.name || '').toLowerCase().includes(q) ||
      String(p.pid).includes(q) ||
      (p.user || '').toLowerCase().includes(q)
    );
  }

  switch (processSortBy.value) {
    case 'cpu_desc':
      list.sort((a, b) => parseFloat(b.cpu) - parseFloat(a.cpu));
      break;
    case 'mem_desc':
      list.sort((a, b) => parseFloat(b.memory) - parseFloat(a.memory));
      break;
    case 'pid_asc':
      list.sort((a, b) => a.pid - b.pid);
      break;
    case 'name_asc':
      list.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
      break;
  }

  return list;
});

// 系统信息
const systemInfo = ref({
  hostname: '',
  os: '',
  kernel: '',
  arch: '',
  uptime: '',
  version: '',
  cpu_model: '',
  cpu_cores: 0,
  memory_total: 0,
  disk_total: 0
});

// 监控设置
const monitorEnabled = ref(true);
const monitorDays = ref(30);
const monitorOnlyNet = ref(true);
const clearingData = ref(false);

let refreshTimer = null;

function getProgressColor(value) {
  if (value >= 90) return '#f56c6c';
  if (value >= 70) return '#e6a23c';
  return '#67c23a';
}

function getLoadType() {
  const load = parseFloat(loadAvg.value[0]) || 0;
  const cores = cpuCores.value || 1;
  const ratio = load / cores;
  if (ratio > 1.5) return 'danger';
  if (ratio > 0.8) return 'warning';
  return 'success';
}

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const k = 1024;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + units[i];
}

function formatUptime(timeStr) {
  if (!timeStr) return '-';
  return timeStr;
}

function getTimeLabel() {
  const now = new Date();
  return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
}

function pushHistory(arr, value) {
  arr.push(value);
  if (arr.length > MAX_HISTORY) arr.shift();
}

function initChart(chartRef, title, color1, color2, data, yMax = 100, unit = '%') {
  if (!chartRef) return null;
  const chart = echarts.init(chartRef);
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      borderWidth: 1,
      textStyle: { color: '#303133' },
      formatter: (params) => {
        const p = params[0];
        return `${p.axisValue}<br/>${p.marker} ${p.seriesName}: ${p.value}${unit}`;
      }
    },
    grid: {
      left: '3%',
      right: '3%',
      top: '10%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [...timeLabels],
      axisLine: { lineStyle: { color: '#dcdfe6' } },
      axisLabel: { color: '#909399', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      max: yMax === 100 ? 100 : undefined,
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#f0f2f5' } },
      axisLabel: { color: '#909399', formatter: `{value}${unit}` }
    },
    series: [{
      name: title,
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 2, color: color1 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: `rgba(${color2}, 0.3)` },
          { offset: 1, color: `rgba(${color2}, 0.05)` }
        ])
      },
      data: [...data]
    }]
  };
  chart.setOption(option);
  return chart;
}

function initNetworkChart(dataUp, dataDown) {
  if (!networkChartRef.value) return;
  networkChart = echarts.init(networkChartRef.value);
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      borderWidth: 1,
      textStyle: { color: '#303133' },
      formatter: (params) => {
        let html = `${params[0].axisValue}<br/>`;
        params.forEach(p => {
          html += `${p.marker} ${p.seriesName}: ${formatBytes(p.value)}/s<br/>`;
        });
        return html;
      }
    },
    legend: {
      data: ['上行', '下行'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '3%',
      top: '10%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [...timeLabels],
      axisLine: { lineStyle: { color: '#dcdfe6' } },
      axisLabel: { color: '#909399', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#f0f2f5' } },
      axisLabel: {
        color: '#909399',
        formatter: (value) => formatBytes(value) + '/s'
      }
    },
    series: [
      {
        name: '上行',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: '#f56c6c' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0.05)' }
          ])
        },
        data: [...dataUp]
      },
      {
        name: '下行',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: '#67c23a' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
          ])
        },
        data: [...dataDown]
      }
    ]
  };
  networkChart.setOption(option);
}

function initDiskIoChart() {
  if (!diskChartRef.value) return null;
  diskChart = echarts.init(diskChartRef.value);
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      borderWidth: 1,
      textStyle: { color: '#303133' },
      formatter: (params) => {
        let html = `${params[0].axisValue}<br/>`;
        params.forEach(p => {
          html += `${p.marker} ${p.seriesName}: ${formatBytes(p.value)}/s<br/>`;
        });
        return html;
      }
    },
    legend: {
      data: ['读取', '写入'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '3%',
      top: '10%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [...timeLabels],
      axisLine: { lineStyle: { color: '#dcdfe6' } },
      axisLabel: { color: '#909399', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#f0f2f5' } },
      axisLabel: {
        color: '#909399',
        formatter: (value) => formatBytes(value) + '/s'
      }
    },
    series: [
      {
        name: '读取',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: '#e6a23c' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(230, 162, 60, 0.3)' },
            { offset: 1, color: 'rgba(230, 162, 60, 0.05)' }
          ])
        },
        data: [...diskReadHistory]
      },
      {
        name: '写入',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: '#409eff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        },
        data: [...diskWriteHistory]
      }
    ]
  };
  diskChart.setOption(option);
  return diskChart;
}

function updateCharts() {
  const timeData = [...timeLabels];

  if (cpuChart) {
    cpuChart.setOption({
      xAxis: { data: timeData },
      series: [{ data: [...cpuHistory] }]
    });
  }

  if (memoryChart) {
    memoryChart.setOption({
      xAxis: { data: timeData },
      series: [{ data: [...memHistory] }]
    });
  }

  if (diskChart) {
    diskChart.setOption({
      xAxis: { data: timeData },
      series: [
        { data: [...diskReadHistory] },
        { data: [...diskWriteHistory] }
      ]
    });
  }

  if (networkChart) {
    networkChart.setOption({
      xAxis: { data: timeData },
      series: [
        { data: [...netUpHistory] },
        { data: [...netDownHistory] }
      ]
    });
  }
}

// 从后端获取进程列表
async function refreshProcesses() {
  processLoading.value = true;
  try {
    const res = await getSystemNetwork();
    if (res && res.process_list) {
      processList.value = res.process_list.map((p, idx) => ({
        pid: p.pid || p[0] || idx,
        name: p.name || p[1] || '-',
        user: p.user || p[6] || '-',
        cpu: parseFloat(p.cpu_percent || p[2] || 0).toFixed(1),
        memory: parseFloat(p.memory_percent || p[3] || 0).toFixed(1),
        status: (p.status || p[4] || 'sleeping').toLowerCase(),
        start_time: p.create_time || p[5] || '-'
      }));
    } else {
      // 如果 API 不返回进程列表，使用基础系统信息中的进程数
      processList.value = [];
    }
  } catch {
    processList.value = [];
  } finally {
    processLoading.value = false;
  }
}

async function killProcess(process) {
  try {
    // Try to kill via system API
    const res = await fetch('/system/kill_process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `pid=${process.pid}`
    }).catch(() => null);

    ElMessage.success(`进程 ${process.name} (PID: ${process.pid}) 终止请求已发送`);
    setTimeout(refreshProcesses, 1000);
  } catch (error) {
    ElMessage.error('终止进程失败');
  }
}

// 监控设置
async function fetchMonitorSettings() {
  try {
    const res = await getMonitorControl();
    if (res) {
      monitorEnabled.value = res.status !== false;
      monitorDays.value = parseInt(res.day) || 30;
      monitorOnlyNet.value = res.stat_all_status !== false;
    }
  } catch (e) {
    console.error('获取监控设置失败:', e);
  }
}

async function toggleMonitor(val) {
  try {
    await setMonitorControl(val ? '1' : '0', monitorDays.value.toString());
    ElMessage.success(val ? '监控已开启' : '监控已关闭');
  } catch (e) {
    monitorEnabled.value = !val;
    ElMessage.error('设置失败');
  }
}

async function saveMonitorDays() {
  try {
    await setMonitorControl(monitorEnabled.value ? '1' : '0', monitorDays.value.toString());
    ElMessage.success('保留天数已保存');
  } catch (e) {
    ElMessage.error('保存失败');
  }
}

async function toggleOnlyNet(val) {
  try {
    await setMonitorControl(val ? '3' : '2', monitorDays.value.toString());
    ElMessage.success(val ? '已开启仅统计外网' : '已关闭仅统计外网');
  } catch (e) {
    monitorOnlyNet.value = !val;
    ElMessage.error('设置失败');
  }
}

async function clearMonitorData() {
  try {
    await ElMessageBox.confirm('确定要清空所有监控记录吗？此操作不可恢复！', '清空监控记录', {
      type: 'warning',
      confirmButtonText: '确定清空',
      cancelButtonText: '取消'
    });
    clearingData.value = true;
    await setMonitorControl('del', '');
    ElMessage.success('监控记录已清空');
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('清空失败');
  } finally {
    clearingData.value = false;
  }
}

async function refreshData() {
  try {
    const [basicRes, networkRes, diskRes, loadRes] = await Promise.all([
      getSystemInfo(),
      getSystemNetwork(),
      getDiskInfo().catch(() => null),
      getSystemLoad().catch(() => null)
    ]);

    const basic = basicRes || {};
    const net = networkRes || {};

    // CPU
    const cpuArr = net.cpu || [];
    const usage = basic.cpuRealUsed ?? cpuArr[0] ?? 0;
    const cores = basic.cpuNum ?? cpuArr[1] ?? 0;
    cpuUsage.value = Math.round(usage);
    cpuCores.value = cores;
    cpuTemp.value = 0;

    // Load Average
    if (loadRes && loadRes.data) {
      const ld = loadRes.data;
      loadAvg.value = [
        parseFloat(ld.one || ld[0] || 0).toFixed(2),
        parseFloat(ld.five || ld[1] || 0).toFixed(2),
        parseFloat(ld.fifteen || ld[2] || 0).toFixed(2)
      ];
    } else if (net.load) {
      const ld = net.load;
      loadAvg.value = [
        parseFloat(ld.one || ld[0] || 0).toFixed(2),
        parseFloat(ld.five || ld[1] || 0).toFixed(2),
        parseFloat(ld.fifteen || ld[2] || 0).toFixed(2)
      ];
    }

    // Memory
    const mem = net.mem || basic;
    const memTotal = mem.memTotal || basic.memTotal || 0;
    const memUsed = mem.memRealUsed || basic.memRealUsed || 0;
    memoryTotal.value = memTotal * 1024 * 1024; // MB -> bytes
    memoryUsed.value = memUsed * 1024 * 1024;
    memoryUsage.value = memTotal ? Math.round((memUsed / memTotal) * 100) : 0;

    // Swap
    const swpTotal = mem.swapTotal || mem.memBuffers || 0;
    const swpUsed = mem.swapUsed || 0;
    swapTotal.value = swpTotal * 1024 * 1024;
    swapUsed.value = swpUsed * 1024 * 1024;
    swapUsage.value = swpTotal ? Math.round((swpUsed / swpTotal) * 100) : 0;

    // Disk
    let dTotal = 0, dUsed = 0, dUsage = 0;
    if (diskRes?.data) {
      const rootDisk = diskRes.data.find(d => d.path === '/');
      if (rootDisk?.size) {
        dTotal = parseSizeStr(rootDisk.size[0]);
        dUsed = parseSizeStr(rootDisk.size[1]);
        dUsage = parseInt(rootDisk.size[3]) || 0;
      }
    }
    diskTotal.value = dTotal;
    diskUsed.value = dUsed;
    diskUsage.value = dUsage;

    // Network
    const netAll = net.network?.ALL || {};
    networkUp.value = Math.round(netAll.up || 0);
    networkDown.value = Math.round(netAll.down || 0);
    tcpConnections.value = net.tcpCount || net.isession || 0;

    // System info
    systemInfo.value = {
      hostname: basic.hostname || '',
      os: basic.system || '',
      kernel: basic.kernel || '',
      arch: basic.arch || '',
      uptime: basic.time || '',
      version: basic.version || '',
      cpu_model: cpuArr[3] || '',
      cpu_cores: cores,
      memory_total: memoryTotal.value,
      disk_total: diskTotal.value
    };

    // 更新图表历史数据
    const label = getTimeLabel();
    pushHistory(timeLabels, label);
    pushHistory(cpuHistory, cpuUsage.value);
    pushHistory(memHistory, memoryUsage.value);
    pushHistory(netUpHistory, networkUp.value);
    pushHistory(netDownHistory, networkDown.value);

    // 同步到 appStore
    await appStore.fetchSystemInfo().catch(() => {});
  } catch (error) {
    console.error('刷新监控数据失败:', error);
  }
}

// 解析 "1007G" "18G" 等格式为字节
function parseSizeStr(str) {
  if (!str || str === '-') return 0;
  str = str.toString().trim();
  const match = str.match(/^([\d.]+)\s*([KMGTP]?B?)$/i);
  if (!match) return 0;
  const num = parseFloat(match[1]);
  const unit = match[2].toUpperCase();
  const multipliers = { '': 1, 'B': 1, 'K': 1024, 'KB': 1024, 'M': 1024**2, 'MB': 1024**2, 'G': 1024**3, 'GB': 1024**3, 'T': 1024**4, 'TB': 1024**4 };
  return Math.round(num * (multipliers[unit] || 1));
}

// 从后端获取历史IO数据
async function fetchHistoricalData() {
  try {
    const [cpuIoRes, diskIoRes, netIoRes] = await Promise.all([
      getCpuIo().catch(() => null),
      getDiskIo().catch(() => null),
      getNetworkIo().catch(() => null)
    ]);

    // 如果后端有历史数据，用它来初始化图表
    if (cpuIoRes?.data && Array.isArray(cpuIoRes.data) && cpuIoRes.data.length > 0) {
      cpuIoRes.data.forEach(item => {
        const time = item.add_time ? item.add_time.split(' ')[1]?.substring(0, 5) : getTimeLabel();
        pushHistory(timeLabels, time);
        pushHistory(cpuHistory, parseFloat(item.cpu_io) || 0);
      });
    }

    if (diskIoRes?.data && Array.isArray(diskIoRes.data) && diskIoRes.data.length > 0) {
      diskIoRes.data.forEach(item => {
        pushHistory(diskReadHistory, parseFloat(item.read_bytes) || 0);
        pushHistory(diskWriteHistory, parseFloat(item.write_bytes) || 0);
      });
    }

    if (netIoRes?.data && Array.isArray(netIoRes.data) && netIoRes.data.length > 0) {
      netIoRes.data.forEach(item => {
        pushHistory(netUpHistory, parseFloat(item.up) || 0);
        pushHistory(netDownHistory, parseFloat(item.down) || 0);
      });
    }
  } catch {
    // 历史数据获取失败，使用实时数据
  }
}

async function handleRestartPanel() {
  try {
    await ElMessageBox.confirm('确定要重启面板服务吗？', '重启面板', { type: 'warning' });
    await restartPanelApi();
    ElMessage.success('面板正在重启...');
    setTimeout(() => window.location.reload(), 3000);
  } catch {
    // cancelled
  }
}

async function handleRestartServer() {
  try {
    await ElMessageBox.confirm('确定要重启服务器吗？这将中断所有服务！', '重启服务器', {
      type: 'warning',
      confirmButtonText: '确定重启',
      cancelButtonText: '取消'
    });
    await restartServerApi();
    ElMessage.success('服务器正在重启，请稍后刷新页面...');
  } catch {
    // cancelled
  }
}

function handleResize() {
  if (cpuChart) cpuChart.resize();
  if (memoryChart) memoryChart.resize();
  if (diskChart) diskChart.resize();
  if (networkChart) networkChart.resize();
}

onMounted(async () => {
  // 先获取历史数据和实时数据
  await Promise.all([refreshData(), fetchHistoricalData()]);
  await nextTick();

  // 初始化图表（使用已收集的历史数据）
  cpuChart = initChart(cpuChartRef.value, 'CPU', '#409eff', '64, 158, 255', cpuHistory);
  memoryChart = initChart(memoryChartRef.value, '内存', '#67c23a', '103, 194, 58', memHistory);
  diskChart = initDiskIoChart();
  initNetworkChart(netUpHistory, netDownHistory);

  // 获取进程列表
  refreshProcesses();

  // 获取监控设置
  fetchMonitorSettings();

  // 每 5 秒刷新数据
  refreshTimer = setInterval(() => {
    refreshData();
  }, 5000);

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize);
});

onBeforeUnmount(() => {
  if (refreshTimer) clearInterval(refreshTimer);
  if (cpuChart) cpuChart.dispose();
  if (memoryChart) memoryChart.dispose();
  if (diskChart) diskChart.dispose();
  if (networkChart) networkChart.dispose();
  window.removeEventListener('resize', handleResize);
});
</script>

<style lang="scss" scoped>
.monitor-page {
  .realtime-cards {
    margin-bottom: 16px;

    .monitor-card {
      margin-bottom: 16px;

      .card-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 16px;

        .el-icon {
          color: #409eff;
        }
      }

      .card-body {
        text-align: center;
        padding: 16px 0;

        .progress-text {
          font-size: 24px;
          font-weight: 700;
        }

        .network-stats {
          display: flex;
          justify-content: space-around;

          .network-item {
            text-align: center;

            .el-icon {
              font-size: 24px;
              color: #409eff;
              margin-bottom: 8px;
            }

            .network-label {
              display: block;
              font-size: 12px;
              color: #909399;
              margin-bottom: 4px;
            }

            .network-value {
              font-size: 16px;
              font-weight: 600;
              color: #303133;
            }
          }
        }
      }

      .card-footer {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #909399;
        margin-top: 16px;
        padding-top: 12px;
        border-top: 1px solid #ebeef5;

        .load-tag {
          cursor: pointer;
        }
      }

      .swap-bar {
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px dashed #ebeef5;

        .swap-label {
          font-size: 11px;
          color: #909399;
          margin-bottom: 4px;
        }
      }
    }
  }

  .chart-row {
    margin-bottom: 16px;

    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .chart-container {
      width: 100%;
      height: 300px;
    }
  }

  .process-card {
    margin-bottom: 16px;

    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;

      .process-actions {
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }

    .top-processes {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
      margin-bottom: 12px;
      padding: 8px 12px;
      background: #fdf6ec;
      border-radius: 4px;

      .top-label {
        font-size: 12px;
        font-weight: 600;
        color: #e6a23c;
        white-space: nowrap;
      }

      .top-tag {
        font-size: 11px;
      }
    }

    .progress-cell {
      display: flex;
      align-items: center;
      gap: 8px;

      .el-progress {
        flex: 1;
      }

      .progress-value {
        font-size: 12px;
        font-weight: 600;
        min-width: 40px;
        text-align: right;
      }
    }

    .hot-process {
      color: #f56c6c;
      font-weight: 600;
    }
  }

  .monitor-settings-card {
    margin-bottom: 16px;

    .setting-item {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;

      .setting-label {
        font-size: 14px;
        color: #606266;
        min-width: 80px;
      }
    }
  }

  .system-info-card {
    margin-bottom: 16px;
  }
}
</style>
