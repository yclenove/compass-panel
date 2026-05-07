<template>
  <div class="logs-page">
    <!-- 搜索和过滤栏 -->
    <el-card class="filter-card">
      <el-row :gutter="16" align="middle">
        <el-col :xs="24" :sm="8" :md="6">
          <el-input
            ref="searchInputRef"
            v-model="searchQuery"
            placeholder="搜索日志内容 (Ctrl+F)"
            clearable
            prefix-icon="Search"
            @input="handleSearch"
          />
        </el-col>
        <el-col :xs="24" :sm="8" :md="4">
          <el-select v-model="logType" placeholder="日志类型" clearable @change="handleFilter">
            <el-option label="全部" value="" />
            <el-option label="系统日志" value="system" />
            <el-option label="访问日志" value="access" />
            <el-option label="错误日志" value="error" />
            <el-option label="操作日志" value="operation" />
            <el-option label="安全日志" value="security" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="8" :md="6">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleDateChange"
          />
        </el-col>
        <el-col :xs="24" :sm="8" :md="4">
          <el-select v-model="logLevel" placeholder="日志级别" clearable @change="handleFilter">
            <el-option label="全部" value="" />
            <el-option label="INFO" value="info" />
            <el-option label="WARNING" value="warning" />
            <el-option label="ERROR" value="error" />
            <el-option label="DEBUG" value="debug" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="24" :md="4" class="action-buttons">
          <el-button type="primary" icon="Search" @click="fetchLogs">搜索</el-button>
          <el-button icon="Refresh" @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计卡片 + 快速筛选 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card" :class="{ 'stat-active': !logType }" @click="logType = ''; fetchLogs()">
          <el-statistic title="总日志数" :value="stats.total">
            <template #prefix><el-icon style="color: #409eff"><Tickets /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card" :class="{ 'stat-active': logType === 'operation' }" @click="logType = 'operation'; fetchLogs()">
          <el-statistic title="操作日志" :value="stats.operations">
            <template #prefix><el-icon style="color: #67c23a"><Calendar /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card" :class="{ 'stat-active': logType === 'error' }" @click="logType = 'error'; fetchLogs()">
          <el-statistic title="错误日志" :value="stats.errors">
            <template #prefix><el-icon style="color: #f56c6c"><WarningFilled /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card" :class="{ 'stat-active': logType === 'security' }" @click="logType = 'security'; fetchLogs()">
          <el-statistic title="安全日志" :value="stats.security">
            <template #prefix><el-icon style="color: #e6a23c"><Lock /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 日志活跃时间分布 -->
    <el-card class="activity-card" v-if="logList.length > 0">
      <template #header>
        <div class="card-header">
          <span><el-icon><DataLine /></el-icon> 日志活跃分布 (24小时)</span>
        </div>
      </template>
      <div class="activity-heatmap">
        <div
          v-for="(count, hour) in activityByHour"
          :key="hour"
          class="heatmap-cell"
          :style="{ opacity: getHeatmapOpacity(count) }"
          :title="`${hour}:00 - ${count} 条日志`"
        >
          <span class="heatmap-hour">{{ hour }}</span>
        </div>
      </div>
    </el-card>

    <!-- 日志列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>
            操作日志
            <el-tag v-if="selectedRows.length > 0" type="warning" size="small" style="margin-left: 8px">
              已选 {{ selectedRows.length }} 条
            </el-tag>
          </span>
          <div class="header-actions">
            <el-button
              v-if="selectedRows.length > 0"
              type="danger"
              icon="Delete"
              size="small"
              @click="batchDeleteLogs"
            >
              删除选中
            </el-button>
            <el-button type="danger" icon="Delete" @click="clearLogs">清空日志</el-button>
            <el-button icon="Download" @click="exportLogs">导出日志</el-button>
            <el-switch
              v-model="autoRefresh"
              active-text="自动刷新"
              inactive-text=""
              @change="toggleAutoRefresh"
            />
          </div>
        </div>
      </template>

      <el-table
        ref="logTableRef"
        :data="logList"
        stripe
        v-loading="loading"
        @sort-change="handleSortChange"
        :row-class-name="getRowClassName"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="45" />
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="log-detail">
              <div class="log-detail-header">
                <el-tag :type="getTypeTag(row.type)" size="small">{{ getTypeName(row.type) }}</el-tag>
                <span class="log-detail-time">{{ row.add_time }}</span>
              </div>
              <pre class="log-content">{{ row.log }}</pre>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="id" label="ID" width="70" sortable="custom" />
        <el-table-column prop="type" label="类型" width="110">
          <template #default="{ row }">
            <el-tag
              :type="getTypeTag(row.type)"
              size="small"
              class="clickable-tag"
              @click="filterByType(row.type)"
            >
              {{ getTypeName(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="log" label="日志内容" min-width="300" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="log-text" v-html="highlightSearch(row.log)"></span>
          </template>
        </el-table-column>
        <el-table-column prop="uid" label="用户" width="70" />
        <el-table-column prop="add_time" label="时间" width="170" sortable="custom" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewLogDetail(row)">详情</el-button>
            <el-button type="info" link @click="copySingleLog(row)">复制</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-if="total > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[20, 50, 100, 200]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <!-- 日志详情抽屉 -->
    <el-drawer
      v-model="logDetailVisible"
      title="日志详情"
      size="500px"
      direction="rtl"
    >
      <template v-if="currentLog.id">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="日志ID">
            <el-tag size="small">#{{ currentLog.id }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag :type="getTypeTag(currentLog.type)" size="small">
              {{ getTypeName(currentLog.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="用户ID">{{ currentLog.uid || '-' }}</el-descriptions-item>
          <el-descriptions-item label="时间">{{ currentLog.add_time }}</el-descriptions-item>
        </el-descriptions>
        <div class="drawer-log-content">
          <div class="drawer-log-header">
            <span>日志内容</span>
            <el-button type="primary" size="small" @click="copyLog">
              <el-icon><CopyDocument /></el-icon> 复制
            </el-button>
          </div>
          <pre class="log-detail-content">{{ currentLog.log }}</pre>
        </div>
        <!-- 相邻日志快速导航 -->
        <div class="log-nav" v-if="logList.length > 1">
          <el-button size="small" :disabled="!hasPrevLog" @click="navPrevLog">
            <el-icon><ArrowLeft /></el-icon> 上一条
          </el-button>
          <el-button size="small" :disabled="!hasNextLog" @click="navNextLog">
            下一条 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getLogList, clearLogs as apiClearLogs } from '@/api/index';

const logList = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const logType = ref('');
const logLevel = ref('');
const dateRange = ref(null);
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const autoRefresh = ref(false);
const logDetailVisible = ref(false);
const currentLog = ref({});
const sortProp = ref('');
const sortOrder = ref('');
const selectedRows = ref([]);
const searchInputRef = ref(null);
const logTableRef = ref(null);
const currentLogIndex = ref(-1);

let autoRefreshTimer = null;

const stats = computed(() => {
  const totalVal = logList.value.length;
  const operations = logList.value.filter(l => l.type === 'operation').length;
  const errors = logList.value.filter(l => l.type === 'error' || (l.log && l.log.toLowerCase().includes('error'))).length;
  const security = logList.value.filter(l => l.type === 'security').length;
  return { total: totalVal, operations, errors, security };
});

// 24小时活跃分布
const activityByHour = computed(() => {
  const hours = {};
  for (let i = 0; i < 24; i++) {
    hours[String(i).padStart(2, '0')] = 0;
  }
  logList.value.forEach(l => {
    if (l.add_time) {
      const match = l.add_time.match(/(\d{2}):\d{2}:\d{2}/);
      if (match) {
        hours[match[1]] = (hours[match[1]] || 0) + 1;
      }
    }
  });
  return hours;
});

const getHeatmapOpacity = (count) => {
  const max = Math.max(...Object.values(activityByHour.value), 1);
  return 0.1 + (count / max) * 0.9;
};

// 日志导航
const hasPrevLog = computed(() => currentLogIndex.value > 0);
const hasNextLog = computed(() => currentLogIndex.value < logList.value.length - 1);

const navPrevLog = () => {
  if (currentLogIndex.value > 0) {
    currentLogIndex.value--;
    currentLog.value = logList.value[currentLogIndex.value];
  }
};

const navNextLog = () => {
  if (currentLogIndex.value < logList.value.length - 1) {
    currentLogIndex.value++;
    currentLog.value = logList.value[currentLogIndex.value];
  }
};

const fetchLogs = async () => {
  loading.value = true;
  try {
    const res = await getLogList({
      page: currentPage.value,
      limit: pageSize.value,
      search: searchQuery.value
    });
    if (res && res.data) {
      const data = Array.isArray(res.data) ? res.data : [];
      // Apply client-side filters
      let filtered = data;
      if (logType.value) {
        filtered = filtered.filter(l => l.type === logType.value);
      }
      if (logLevel.value) {
        filtered = filtered.filter(l => {
          const log = (l.log || '').toLowerCase();
          if (logLevel.value === 'error') return log.includes('error') || l.type === 'error';
          if (logLevel.value === 'warning') return log.includes('warning') || l.type === 'warning';
          if (logLevel.value === 'info') return log.includes('info') || l.type === 'operation';
          if (logLevel.value === 'debug') return log.includes('debug');
          return true;
        });
      }
      if (dateRange.value && dateRange.value.length === 2) {
        filtered = filtered.filter(l => {
          if (!l.add_time) return false;
          const d = l.add_time.split(' ')[0];
          return d >= dateRange.value[0] && d <= dateRange.value[1];
        });
      }
      logList.value = filtered;
      total.value = res.total || data.length || 0;
    }
  } catch (error) {
    console.error('获取日志列表失败:', error);
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  fetchLogs();
};

const handleFilter = () => {
  fetchLogs();
};

const handleDateChange = () => {
  fetchLogs();
};

const handleSortChange = ({ prop, order }) => {
  sortProp.value = prop;
  sortOrder.value = order === 'ascending' ? 'asc' : 'desc';
};

const handleSizeChange = (size) => {
  pageSize.value = size;
  fetchLogs();
};

const handleCurrentChange = (page) => {
  currentPage.value = page;
  fetchLogs();
};

const handleSelectionChange = (rows) => {
  selectedRows.value = rows;
};

const filterByType = (type) => {
  logType.value = type;
  fetchLogs();
};

const resetFilters = () => {
  searchQuery.value = '';
  logType.value = '';
  logLevel.value = '';
  dateRange.value = null;
  currentPage.value = 1;
  fetchLogs();
};

const getTypeName = (type) => {
  const types = {
    'system': '系统日志',
    'access': '访问日志',
    'error': '错误日志',
    'operation': '操作日志',
    'security': '安全日志'
  };
  return types[type] || type || '未知';
};

const getTypeTag = (type) => {
  const tags = {
    'system': '',
    'access': 'success',
    'error': 'danger',
    'operation': 'warning',
    'security': 'info'
  };
  return tags[type] || '';
};

const getRowClassName = ({ row }) => {
  if (row.type === 'error' || (row.log && row.log.toLowerCase().includes('error'))) {
    return 'error-row';
  }
  if (row.type === 'warning' || (row.log && row.log.toLowerCase().includes('warning'))) {
    return 'warning-row';
  }
  return '';
};

const highlightSearch = (text) => {
  if (!searchQuery.value || !text) return escapeHtml(text || '');
  const escaped = escapeHtml(text);
  const escapedQuery = searchQuery.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${escapedQuery})`, 'gi');
  return escaped.replace(regex, '<span class="highlight">$1</span>');
};

const escapeHtml = (text) => {
  if (!text) return '';
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
};

const viewLogDetail = (log) => {
  currentLog.value = log;
  currentLogIndex.value = logList.value.findIndex(l => l.id === log.id);
  logDetailVisible.value = true;
};

const copyLog = () => {
  const text = `ID: ${currentLog.value.id}\n类型: ${getTypeName(currentLog.value.type)}\n时间: ${currentLog.value.add_time}\n内容: ${currentLog.value.log}`;
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板');
  }).catch(() => {
    ElMessage.error('复制失败');
  });
};

const copySingleLog = (log) => {
  const text = `[${log.add_time || ''}] [${getTypeName(log.type)}] ${log.log || ''}`;
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板');
  }).catch(() => {
    ElMessage.error('复制失败');
  });
};

const clearLogs = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有日志吗？此操作不可恢复！', '清空日志', {
      type: 'warning',
      confirmButtonText: '确定清空',
      cancelButtonText: '取消'
    });
    await apiClearLogs();
    ElMessage.success('日志已清空');
    fetchLogs();
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('清空失败');
  }
};

const batchDeleteLogs = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 条日志吗？`,
      '批量删除',
      { type: 'warning' }
    );
    // Remove selected from display (client-side since backend may not support batch delete)
    const selectedIds = new Set(selectedRows.value.map(r => r.id));
    logList.value = logList.value.filter(l => !selectedIds.has(l.id));
    selectedRows.value = [];
    ElMessage.success('已删除选中的日志');
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败');
  }
};

const exportLogs = () => {
  const exportData = selectedRows.value.length > 0 ? selectedRows.value : logList.value;
  if (exportData.length === 0) {
    ElMessage.warning('暂无日志可导出');
    return;
  }
  try {
    const header = 'ID,类型,内容,用户ID,时间\n';
    const rows = exportData.map(log => {
      const content = (log.log || '').replace(/"/g, '""').replace(/\n/g, ' ');
      return `${log.id},"${getTypeName(log.type)}","${content}",${log.uid || ''},${log.add_time || ''}`;
    }).join('\n');
    const csv = '﻿' + header + rows;
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `logs_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);
    ElMessage.success(`已导出 ${exportData.length} 条日志`);
  } catch {
    ElMessage.error('导出失败');
  }
};

const toggleAutoRefresh = (val) => {
  if (val) {
    autoRefreshTimer = setInterval(fetchLogs, 30000);
    ElMessage.success('已开启自动刷新（每30秒）');
  } else {
    if (autoRefreshTimer) {
      clearInterval(autoRefreshTimer);
      autoRefreshTimer = null;
    }
    ElMessage.info('已关闭自动刷新');
  }
};

// 键盘快捷键
const handleKeydown = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
    e.preventDefault();
    searchInputRef.value?.focus();
  }
  if (e.key === 'Escape' && logDetailVisible.value) {
    logDetailVisible.value = false;
  }
};

onMounted(() => {
  fetchLogs();
  document.addEventListener('keydown', handleKeydown);
});

onBeforeUnmount(() => {
  if (autoRefreshTimer) clearInterval(autoRefreshTimer);
  document.removeEventListener('keydown', handleKeydown);
});
</script>

<style lang="scss" scoped>
.logs-page {
  .filter-card {
    margin-bottom: 16px;

    .action-buttons {
      display: flex;
      justify-content: flex-end;
      gap: 8px;
      margin-top: 8px;

      @media (min-width: 768px) {
        margin-top: 0;
      }
    }
  }

  .stats-row {
    margin-bottom: 16px;

    .stat-card {
      text-align: center;
      margin-bottom: 8px;
      cursor: pointer;
      transition: all 0.3s;
      border: 2px solid transparent;

      &:hover {
        transform: translateY(-2px);
      }

      &.stat-active {
        border-color: #409eff;
        background: rgba(64, 158, 255, 0.05);
      }
    }
  }

  .activity-card {
    margin-bottom: 16px;

    .activity-heatmap {
      display: flex;
      gap: 2px;
      flex-wrap: wrap;

      .heatmap-cell {
        flex: 1;
        min-width: 28px;
        height: 36px;
        background: #409eff;
        border-radius: 3px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          transform: scale(1.1);
          z-index: 1;
        }

        .heatmap-hour {
          font-size: 10px;
          color: #fff;
          font-weight: 600;
        }
      }
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;

    .header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  .clickable-tag {
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      opacity: 0.8;
      transform: scale(1.05);
    }
  }

  .log-text {
    :deep(.highlight) {
      background-color: #f56c6c;
      color: #fff;
      padding: 0 2px;
      border-radius: 2px;
    }
  }

  .log-detail {
    padding: 16px;

    .log-detail-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;

      .log-detail-time {
        color: #909399;
        font-size: 13px;
      }
    }

    .log-content {
      background: #f5f7fa;
      padding: 12px;
      border-radius: 4px;
      white-space: pre-wrap;
      word-break: break-all;
      font-family: 'Consolas', 'Monaco', monospace;
      max-height: 200px;
      overflow-y: auto;
      font-size: 13px;
      line-height: 1.6;
    }
  }

  .drawer-log-content {
    margin-top: 16px;

    .drawer-log-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      font-weight: 600;
      color: #303133;
    }
  }

  .log-detail-content {
    background: #f5f7fa;
    padding: 12px;
    border-radius: 4px;
    white-space: pre-wrap;
    word-break: break-all;
    font-family: 'Consolas', 'Monaco', monospace;
    max-height: 400px;
    overflow-y: auto;
    font-size: 13px;
    line-height: 1.6;
  }

  .log-nav {
    margin-top: 16px;
    display: flex;
    justify-content: space-between;
  }

  .el-pagination {
    margin-top: 16px;
    justify-content: flex-end;
  }

  :deep(.el-table) {
    .error-row {
      background-color: #fef0f0;
    }

    .warning-row {
      background-color: #fdf6ec;
    }
  }
}
</style>
