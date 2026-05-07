<template>
  <div class="crontab-page">
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="总任务数" :value="stats.total">
            <template #prefix><el-icon style="color: #409eff"><Timer /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="运行中" :value="stats.running">
            <template #prefix><el-icon style="color: #67c23a"><VideoPlay /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="已暂停" :value="stats.paused">
            <template #prefix><el-icon style="color: #e6a23c"><VideoPause /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="今日执行" :value="stats.todayExecuted">
            <template #prefix><el-icon style="color: #909399"><Clock /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 计划任务列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>计划任务</span>
          <div class="header-actions">
            <el-input
              v-model="searchQuery"
              placeholder="搜索任务名称"
              clearable
              prefix-icon="Search"
              style="width: 200px; margin-right: 8px"
            />
            <el-button type="primary" icon="Plus" @click="showAddCrontab">添加任务</el-button>
            <el-button icon="Refresh" @click="fetchCrontabs">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredCrontabList" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="任务名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)" size="small">
              {{ getTypeName(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="执行周期" min-width="180">
          <template #default="{ row }">
            <span class="cron-expression">
              <el-icon><Clock /></el-icon>
              {{ formatCronExpression(row) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              :active-value="1"
              :inactive-value="0"
              @change="toggleStatus(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="add_time" label="创建时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="runTask(row)">执行</el-button>
            <el-button type="warning" link @click="editCrontab(row)">编辑</el-button>
            <el-button type="info" link @click="viewLogs(row)">日志</el-button>
            <el-button type="danger" link @click="deleteCrontab(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-if="total > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <!-- 添加/编辑任务对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑任务' : '添加任务'"
      width="600px"
    >
      <el-form :model="crontabForm" :rules="crontabRules" ref="crontabFormRef" label-width="100px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="crontabForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务类型" prop="type">
          <el-select v-model="crontabForm.type" placeholder="选择任务类型">
            <el-option label="Shell脚本" value="execshell" />
            <el-option label="备份任务" value="backup" />
            <el-option label="访问URL" value="visit" />
            <el-option label="日志切割" value="logsplit" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行周期" prop="period">
          <el-select v-model="crontabForm.period" placeholder="选择执行周期">
            <el-option label="每分钟" value="minute" />
            <el-option label="每小时" value="hour" />
            <el-option label="每天" value="day" />
            <el-option label="每周" value="week" />
            <el-option label="每月" value="month" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="crontabForm.period === 'custom'" label="Cron表达式" prop="cron_expression">
          <el-input v-model="crontabForm.cron_expression" placeholder="* * * * *" />
          <div class="cron-help">
            <span>分 时 日 月 周</span>
            <el-popover placement="right" :width="400" trigger="click">
              <template #reference>
                <el-button type="primary" link size="small">表达式帮助</el-button>
              </template>
              <div class="cron-examples">
                <h4>常用表达式示例</h4>
                <el-table :data="cronExamples" size="small" stripe>
                  <el-table-column prop="expression" label="表达式" width="120" />
                  <el-table-column prop="description" label="说明" />
                  <el-table-column label="操作" width="60">
                    <template #default="{ row }">
                      <el-button type="primary" link size="small" @click="crontabForm.cron_expression = row.expression">使用</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-popover>
          </div>
        </el-form-item>
        <el-form-item v-if="crontabForm.period !== 'custom'" label="执行时间">
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item prop="hour">
                <el-input v-model="crontabForm.hour" placeholder="小时" type="number" min="0" max="23">
                  <template #append>时</template>
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item prop="minute">
                <el-input v-model="crontabForm.minute" placeholder="分钟" type="number" min="0" max="59">
                  <template #append>分</template>
                </el-input>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item label="任务内容" prop="cmd">
          <el-input
            v-model="crontabForm.cmd"
            type="textarea"
            :rows="4"
            placeholder="请输入任务命令或URL"
          />
        </el-form-item>
        <el-form-item label="备份到">
          <el-select v-model="crontabForm.backup_to" placeholder="选择备份位置">
            <el-option label="本地磁盘" value="local" />
            <el-option label="FTP" value="ftp" />
            <el-option label="阿里云OSS" value="aliyun" />
            <el-option label="腾讯云COS" value="tencent" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="crontabForm.ps" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCrontab" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 执行日志对话框 -->
    <el-dialog v-model="logDialogVisible" title="执行日志" width="700px">
      <el-timeline>
        <el-timeline-item
          v-for="log in taskLogs"
          :key="log.id"
          :timestamp="log.add_time"
          :type="log.status === 1 ? 'success' : 'danger'"
        >
          <p>{{ log.log }}</p>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-if="taskLogs.length === 0" description="暂无执行日志" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  getCrontabList,
  deleteCrontab as apiDeleteCrontab,
  setCrontabStatus,
  getCrontabLogs,
  addCrontab,
  modifyCrontab,
  startCrontabTask
} from '@/api/index';

const crontabList = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const dialogVisible = ref(false);
const logDialogVisible = ref(false);
const isEdit = ref(false);
const submitting = ref(false);
const crontabFormRef = ref(null);
const taskLogs = ref([]);

const cronExamples = [
  { expression: '* * * * *', description: '每分钟执行' },
  { expression: '0 * * * *', description: '每小时整点执行' },
  { expression: '0 0 * * *', description: '每天凌晨0点执行' },
  { expression: '0 2 * * *', description: '每天凌晨2点执行' },
  { expression: '0 0 * * 1', description: '每周一凌晨0点执行' },
  { expression: '0 0 1 * *', description: '每月1日凌晨0点执行' },
  { expression: '*/5 * * * *', description: '每5分钟执行' },
  { expression: '0 */2 * * *', description: '每2小时执行' },
  { expression: '30 3 * * 6', description: '每周六凌晨3:30执行' },
  { expression: '0 0 1 1 *', description: '每年1月1日执行' },
];

const crontabForm = ref({
  id: null,
  name: '',
  type: 'execshell',
  period: 'day',
  hour: '0',
  minute: '0',
  cron_expression: '',
  cmd: '',
  backup_to: 'local',
  ps: ''
});

const crontabRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择任务类型', trigger: 'change' }
  ],
  cmd: [
    { required: true, message: '请输入任务内容', trigger: 'blur' }
  ]
};

const stats = computed(() => {
  const total = crontabList.value.length;
  const running = crontabList.value.filter(c => c.status === 1).length;
  const paused = total - running;
  const today = new Date().toISOString().split('T')[0];
  const todayExecuted = crontabList.value.filter(c => c.last_run && c.last_run.startsWith(today)).length;
  return { total, running, paused, todayExecuted };
});

const filteredCrontabList = computed(() => {
  if (!searchQuery.value) return crontabList.value;
  const query = searchQuery.value.toLowerCase();
  return crontabList.value.filter(c =>
    c.name.toLowerCase().includes(query) ||
    (c.ps && c.ps.toLowerCase().includes(query))
  );
});

const fetchCrontabs = async () => {
  loading.value = true;
  try {
    const res = await getCrontabList({ page: currentPage.value, limit: pageSize.value });
    if (res && res.data) {
      crontabList.value = res.data || [];
      total.value = res.data.length || 0;
    }
  } catch (error) {
    console.error('获取计划任务列表失败:', error);
  } finally {
    loading.value = false;
  }
};

const handleSizeChange = (size) => {
  pageSize.value = size;
  fetchCrontabs();
};

const handleCurrentChange = (page) => {
  currentPage.value = page;
  fetchCrontabs();
};

const getTypeName = (type) => {
  const types = {
    'execshell': 'Shell脚本',
    'backup': '备份任务',
    'visit': '访问URL',
    'logsplit': '日志切割'
  };
  return types[type] || type || '未知';
};

const getTypeTag = (type) => {
  const tags = {
    'execshell': '',
    'backup': 'success',
    'visit': 'warning',
    'logsplit': 'info'
  };
  return tags[type] || '';
};

const formatCronExpression = (row) => {
  if (row.cron_expression) return row.cron_expression;

  const period = row.period || 'day';
  const hour = row.hour || '0';
  const minute = row.minute || '0';

  switch (period) {
    case 'minute': return '每分钟';
    case 'hour': return `每小时的第 ${minute} 分钟`;
    case 'day': return `每天 ${hour}:${minute.toString().padStart(2, '0')}`;
    case 'week': return `每周 ${hour}:${minute.toString().padStart(2, '0')}`;
    case 'month': return `每月1日 ${hour}:${minute.toString().padStart(2, '0')}`;
    default: return row.cron_expression || '-';
  }
};

const showAddCrontab = () => {
  isEdit.value = false;
  crontabForm.value = {
    id: null,
    name: '',
    type: 'execshell',
    period: 'day',
    hour: '0',
    minute: '0',
    cron_expression: '',
    cmd: '',
    backup_to: 'local',
    ps: ''
  };
  dialogVisible.value = true;
};

const editCrontab = (row) => {
  isEdit.value = true;
  crontabForm.value = {
    id: row.id,
    name: row.name,
    type: row.type,
    period: row.period || 'day',
    hour: row.where_hour || '0',
    minute: row.where_minute || '0',
    cron_expression: row.cron_expression || '',
    cmd: row.cmd || row.sbody || '',
    backup_to: row.backup_to || 'local',
    ps: row.ps || ''
  };
  dialogVisible.value = true;
};

const submitCrontab = async () => {
  submitting.value = true;
  try {
    const form = crontabForm.value;
    const stype = form.type === 'visit' ? 'toUrl' : 'toShell';
    const params = {
      name: form.name,
      type: form.type,
      where1: form.period,
      hour: form.hour || '0',
      minute: form.minute || '0',
      stype: stype,
      sbody: form.cmd,
      url_address: form.type === 'visit' ? form.cmd : '',
      backup_to: form.backup_to || 'local',
      save: ''
    };

    // 处理自定义 cron 表达式
    if (form.period === 'custom' && form.cron_expression) {
      const parts = form.cron_expression.trim().split(/\s+/);
      if (parts.length >= 5) {
        params.minute = parts[0];
        params.hour = parts[1];
        params.where1 = 'day';
      }
    }

    let res;
    if (isEdit.value && form.id) {
      res = await modifyCrontab(form.id, params);
    } else {
      res = await addCrontab(params);
    }

    if (res && res.status === false) {
      ElMessage.error(res.msg || '操作失败');
      return;
    }

    ElMessage.success(isEdit.value ? '任务更新成功' : '任务添加成功');
    dialogVisible.value = false;
    fetchCrontabs();
  } catch (error) {
    ElMessage.error('操作失败');
  } finally {
    submitting.value = false;
  }
};

const toggleStatus = async (row) => {
  try {
    await setCrontabStatus(row.id);
    const action = row.status === 1 ? '启用' : '暂停';
    ElMessage.success(`任务已${action}`);
    fetchCrontabs();
  } catch (error) {
    console.error('切换任务状态失败:', error);
  }
};

const runTask = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要立即执行任务 "${row.name}" 吗？`, '执行确认');
    const res = await startCrontabTask(row.id);
    if (res && res.status === false) {
      ElMessage.error(res.msg || '执行失败');
      return;
    }
    ElMessage.success('任务已开始执行');
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('执行失败');
  }
};

const viewLogs = async (row) => {
  try {
    const res = await getCrontabLogs(row.id);
    if (res && res.data) {
      taskLogs.value = Array.isArray(res.data) ? res.data : [];
    } else {
      taskLogs.value = [];
    }
  } catch (error) {
    taskLogs.value = [];
  }
  logDialogVisible.value = true;
};

const deleteCrontab = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除任务 "${row.name}" 吗？`, '删除确认', { type: 'warning' });
    await apiDeleteCrontab(row.id);
    ElMessage.success('删除成功');
    fetchCrontabs();
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败');
  }
};

onMounted(() => fetchCrontabs());
</script>

<style lang="scss" scoped>
.crontab-page {
  .stats-row {
    margin-bottom: 16px;

    .stat-card {
      text-align: center;
      margin-bottom: 8px;
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

  .cron-expression {
    display: flex;
    align-items: center;
    gap: 4px;
    color: #606266;

    .el-icon {
      color: #409eff;
    }
  }

  .cron-help {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .cron-examples {
    h4 {
      margin: 0 0 8px;
      font-size: 14px;
    }
  }

  .el-pagination {
    margin-top: 16px;
    justify-content: flex-end;
  }
}
</style>
