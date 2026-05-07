<template>
  <div class="firewall-page">
    <!-- 安全概览 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="防火墙规则" :value="stats.rules">
            <template #prefix><el-icon style="color: #409eff"><Shield /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="放行端口" :value="stats.openPorts">
            <template #prefix><el-icon style="color: #67c23a"><CircleCheck /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="拦截IP" :value="stats.blockedIPs">
            <template #prefix><el-icon style="color: #f56c6c"><CircleClose /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="今日拦截" :value="stats.todayBlocked">
            <template #prefix><el-icon style="color: #e6a23c"><Warning /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 标签页 -->
    <el-card>
      <el-tabs v-model="activeTab">
        <!-- 端口规则 -->
        <el-tab-pane label="端口规则" name="ports">
          <template #label>
            <span><el-icon><Connection /></el-icon> 端口规则</span>
          </template>
          <div class="tab-header">
            <div class="tab-header-left">
              <el-button type="primary" icon="Plus" @click="showAddPort">添加端口规则</el-button>
              <el-dropdown @command="quickAddPort" trigger="click">
                <el-button icon="Promotion">快速放行 <el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :command="{ port: '80', protocol: 'tcp' }">80 (HTTP)</el-dropdown-item>
                    <el-dropdown-item :command="{ port: '443', protocol: 'tcp' }">443 (HTTPS)</el-dropdown-item>
                    <el-dropdown-item :command="{ port: '22', protocol: 'tcp' }">22 (SSH)</el-dropdown-item>
                    <el-dropdown-item :command="{ port: '3306', protocol: 'tcp' }">3306 (MySQL)</el-dropdown-item>
                    <el-dropdown-item :command="{ port: '6379', protocol: 'tcp' }">6379 (Redis)</el-dropdown-item>
                    <el-dropdown-item :command="{ port: '888', protocol: 'tcp' }">888 (面板)</el-dropdown-item>
                    <el-dropdown-item :command="{ port: '8080', protocol: 'tcp' }">8080 (备用HTTP)</el-dropdown-item>
                    <el-dropdown-item :command="{ port: '20-21', protocol: 'tcp' }">20-21 (FTP)</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
            <el-input v-model="portSearch" placeholder="搜索端口..." clearable size="small" style="width: 180px" :prefix-icon="Search" />
          </div>
          <el-table :data="filteredPortRules" stripe v-loading="loading">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="port" label="端口" width="100" />
            <el-table-column prop="protocol" label="协议" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.protocol }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="strategy" label="策略" width="100">
              <template #default="{ row }">
                <el-tag :type="row.strategy === 'accept' ? 'success' : 'danger'" size="small">
                  {{ row.strategy === 'accept' ? '放行' : '拦截' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="ps" label="备注" min-width="150" />
            <el-table-column prop="add_time" label="添加时间" width="160" />
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button type="danger" link @click="deletePortRule(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- IP规则 -->
        <el-tab-pane label="IP规则" name="ips">
          <template #label>
            <span><el-icon><Location /></el-icon> IP规则</span>
          </template>
          <div class="tab-header">
            <div class="tab-header-left">
              <el-button type="primary" icon="Plus" @click="showAddIP">添加IP规则</el-button>
            </div>
            <el-input v-model="ipSearch" placeholder="搜索IP..." clearable size="small" style="width: 180px" :prefix-icon="Search" />
          </div>
          <el-table :data="filteredIpRules" stripe v-loading="loading">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="ip" label="IP地址" min-width="150" />
            <el-table-column prop="strategy" label="策略" width="100">
              <template #default="{ row }">
                <el-tag :type="row.strategy === 'allow' ? 'success' : 'danger'" size="small">
                  {{ row.strategy === 'allow' ? '放行' : '拦截' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="ps" label="备注" min-width="150" />
            <el-table-column prop="add_time" label="添加时间" width="160" />
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button type="danger" link @click="deleteIPRule(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 攻击日志 -->
        <el-tab-pane label="攻击日志" name="attacks">
          <template #label>
            <span><el-icon><Warning /></el-icon> 攻击日志</span>
          </template>
          <el-table :data="attackLogs" stripe v-loading="loading">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="ip" label="攻击IP" min-width="150" />
            <el-table-column prop="type" label="攻击类型" width="120">
              <template #default="{ row }">
                <el-tag type="danger" size="small">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="port" label="目标端口" width="100" />
            <el-table-column prop="count" label="攻击次数" width="100" />
            <el-table-column prop="add_time" label="时间" width="160" />
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="blockIP(row)">封禁IP</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- SSH安全 -->
        <el-tab-pane label="SSH安全" name="ssh">
          <template #label>
            <span><el-icon><Lock /></el-icon> SSH安全</span>
          </template>
          <el-form :model="sshConfig" label-width="120px" class="ssh-form">
            <el-form-item label="SSH端口">
              <el-input v-model="sshConfig.port" placeholder="22" style="width: 200px" />
            </el-form-item>
            <el-form-item label="允许Root登录">
              <el-switch v-model="sshConfig.rootLogin" @change="handleSshRootChange" />
            </el-form-item>
            <el-form-item label="密码登录">
              <el-switch v-model="sshConfig.passwordAuth" @change="handleSshPassChange" />
            </el-form-item>
            <el-form-item label="公钥登录">
              <el-switch v-model="sshConfig.pubkeyAuth" @change="handleSshPubkeyChange" />
            </el-form-item>
            <el-form-item label="允许Ping">
              <el-switch v-model="sshConfig.pingEnabled" @change="handlePingChange" />
              <span class="form-tip">关闭Ping可增强安全性，但可能影响监控</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSSHConfig">保存SSH端口</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 添加端口规则对话框 -->
    <el-dialog v-model="portDialogVisible" title="添加端口规则" width="500px">
      <el-form :model="portForm" :rules="portRules2" ref="portFormRef" label-width="100px">
        <el-form-item label="端口" prop="port">
          <el-input v-model="portForm.port" placeholder="如: 80 或 8000-9000" />
        </el-form-item>
        <el-form-item label="协议" prop="protocol">
          <el-select v-model="portForm.protocol" placeholder="选择协议">
            <el-option label="TCP" value="tcp" />
            <el-option label="UDP" value="udp" />
            <el-option label="TCP/UDP" value="tcp/udp" />
          </el-select>
        </el-form-item>
        <el-form-item label="策略" prop="strategy">
          <el-radio-group v-model="portForm.strategy">
            <el-radio value="accept">放行</el-radio>
            <el-radio value="drop">拦截</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="portForm.ps" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="portDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPortRule">确定</el-button>
      </template>
    </el-dialog>

    <!-- 添加IP规则对话框 -->
    <el-dialog v-model="ipDialogVisible" title="添加IP规则" width="500px">
      <el-form :model="ipForm" :rules="ipRules2" ref="ipFormRef" label-width="100px">
        <el-form-item label="IP地址" prop="ip">
          <el-input v-model="ipForm.ip" placeholder="如: 1.2.3.4 或 1.2.3.0/24" />
        </el-form-item>
        <el-form-item label="策略" prop="strategy">
          <el-radio-group v-model="ipForm.strategy">
            <el-radio value="allow">放行</el-radio>
            <el-radio value="block">拦截</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="ipForm.ps" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ipDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitIPRule">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, ArrowDown } from '@element-plus/icons-vue';
import {
  getFirewallList,
  addAcceptPort,
  delAcceptPort,
  getSshInfo,
  setSshPort,
  setPingStatus,
  setSshRootStatus,
  setSshPassStatus,
  setSshPubkeyStatus
} from '@/api/index';

const activeTab = ref('ports');
const loading = ref(false);
const portRules = ref([]);
const ipRules = ref([]);
const attackLogs = ref([]);
const portSearch = ref('');
const ipSearch = ref('');

// 过滤后的规则列表
const filteredPortRules = computed(() => {
  if (!portSearch.value) return portRules.value;
  const q = portSearch.value.toLowerCase();
  return portRules.value.filter(r =>
    String(r.port).includes(q) || (r.protocol || '').toLowerCase().includes(q) || (r.ps || '').toLowerCase().includes(q)
  );
});

const filteredIpRules = computed(() => {
  if (!ipSearch.value) return ipRules.value;
  const q = ipSearch.value.toLowerCase();
  return ipRules.value.filter(r =>
    (r.ip || '').toLowerCase().includes(q) || (r.ps || '').toLowerCase().includes(q)
  );
});
const portDialogVisible = ref(false);
const ipDialogVisible = ref(false);
const portFormRef = ref(null);
const ipFormRef = ref(null);

const sshConfig = ref({
  port: '22',
  rootLogin: true,
  passwordAuth: true,
  pubkeyAuth: true,
  pingEnabled: true
});

const portForm = ref({
  port: '',
  protocol: 'tcp',
  strategy: 'accept',
  ps: ''
});

const ipForm = ref({
  ip: '',
  strategy: 'block',
  ps: ''
});

const portRules2 = {
  port: [
    { required: true, message: '请输入端口号', trigger: 'blur' },
    { pattern: /^\d+(-\d+)?$/, message: '端口格式: 单个端口或范围(如80, 8000-9000)', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback();
          return;
        }
        const parts = value.split('-');
        for (const part of parts) {
          const num = parseInt(part);
          if (isNaN(num) || num < 1 || num > 65535) {
            callback(new Error('端口范围必须在 1-65535 之间'));
            return;
          }
        }
        if (parts.length === 2 && parseInt(parts[0]) >= parseInt(parts[1])) {
          callback(new Error('端口范围不正确'));
          return;
        }
        callback();
      },
      trigger: 'blur'
    }
  ],
  protocol: [
    { required: true, message: '请选择协议', trigger: 'change' }
  ]
};

const ipRules2 = {
  ip: [
    { required: true, message: '请输入IP地址', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback();
          return;
        }
        // 支持单个IP、CIDR、IP范围
        const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/;
        const cidrPattern = /^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$/;

        if (cidrPattern.test(value)) {
          const [ip, mask] = value.split('/');
          const octets = ip.split('.');
          for (const octet of octets) {
            if (parseInt(octet) > 255) {
              callback(new Error('IP地址格式不正确'));
              return;
            }
          }
          if (parseInt(mask) > 32) {
            callback(new Error('CIDR掩码不正确'));
            return;
          }
          callback();
        } else if (ipPattern.test(value)) {
          const octets = value.split('.');
          for (const octet of octets) {
            if (parseInt(octet) > 255) {
              callback(new Error('IP地址格式不正确'));
              return;
            }
          }
          callback();
        } else {
          callback(new Error('IP地址格式不正确，支持: 1.2.3.4 或 1.2.3.0/24'));
        }
      },
      trigger: 'blur'
    }
  ]
};

const stats = computed(() => ({
  rules: portRules.value.length + ipRules.value.length,
  openPorts: portRules.value.filter(r => r.strategy === 'accept').length,
  blockedIPs: ipRules.value.filter(r => r.strategy === 'block').length,
  todayBlocked: attackLogs.value.length
}));

const showAddPort = () => {
  portForm.value = { port: '', protocol: 'tcp', strategy: 'accept', ps: '' };
  portDialogVisible.value = true;
};

const showAddIP = () => {
  ipForm.value = { ip: '', strategy: 'block', ps: '' };
  ipDialogVisible.value = true;
};

const quickAddPort = async ({ port, protocol }) => {
  try {
    await addAcceptPort({ port, protocol, ps: `快速放行 ${port}`, type: 'accept' });
    ElMessage.success(`端口 ${port} 已放行`);
    fetchFirewallData();
  } catch (error) {
    ElMessage.error('放行失败');
  }
};

const submitPortRule = async () => {
  try {
    await addAcceptPort({
      port: portForm.value.port,
      protocol: portForm.value.protocol,
      ps: portForm.value.ps,
      type: portForm.value.strategy === 'accept' ? 'accept' : 'drop'
    });
    ElMessage.success('端口规则添加成功');
    portDialogVisible.value = false;
    fetchFirewallData();
  } catch (error) {
    console.error('添加端口规则失败:', error);
  }
};

const submitIPRule = async () => {
  try {
    await addAcceptPort({
      port: ipForm.value.ip,
      protocol: 'tcp',
      ps: ipForm.value.ps || `IP规则: ${ipForm.value.strategy}`,
      type: ipForm.value.strategy === 'allow' ? 'accept' : 'drop'
    });
    ElMessage.success('IP规则添加成功');
    ipDialogVisible.value = false;
    fetchFirewallData();
  } catch (error) {
    ElMessage.error('添加失败');
  }
};

const deletePortRule = async (rule) => {
  try {
    await ElMessageBox.confirm('确定要删除这条规则吗？', '删除确认', { type: 'warning' });
    await delAcceptPort(rule.id, rule.port, rule.protocol);
    ElMessage.success('删除成功');
    fetchFirewallData();
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败');
  }
};

const deleteIPRule = async (rule) => {
  try {
    await ElMessageBox.confirm('确定要删除这条规则吗？', '删除确认', { type: 'warning' });
    await delAcceptPort(rule.id, rule.port || rule.ip, rule.protocol || 'tcp');
    ElMessage.success('删除成功');
    fetchFirewallData();
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败');
  }
};

const blockIP = (log) => {
  ipForm.value = { ip: log.ip, strategy: 'block', ps: `攻击类型: ${log.type}` };
  ipDialogVisible.value = true;
};

const saveSSHConfig = async () => {
  try {
    await setSshPort(sshConfig.value.port);
    ElMessage.success('SSH端口已保存，重启SSH后生效');
  } catch (error) {
    console.error('保存SSH配置失败:', error);
    ElMessage.error('保存SSH配置失败');
  }
};

const handleSshRootChange = async (val) => {
  try {
    await setSshRootStatus(val ? '1' : '0');
    ElMessage.success(`Root登录已${val ? '允许' : '禁止'}`);
  } catch {
    sshConfig.value.rootLogin = !val;
    ElMessage.error('设置失败');
  }
};

const handleSshPassChange = async (val) => {
  try {
    await setSshPassStatus(val ? '1' : '0');
    ElMessage.success(`密码登录已${val ? '开启' : '关闭'}`);
  } catch {
    sshConfig.value.passwordAuth = !val;
    ElMessage.error('设置失败');
  }
};

const handleSshPubkeyChange = async (val) => {
  try {
    await setSshPubkeyStatus(val ? '1' : '0');
    ElMessage.success(`公钥登录已${val ? '开启' : '关闭'}`);
  } catch {
    sshConfig.value.pubkeyAuth = !val;
    ElMessage.error('设置失败');
  }
};

const handlePingChange = async (val) => {
  try {
    await setPingStatus(val ? '1' : '0');
    ElMessage.success(`Ping已${val ? '允许' : '禁止'}`);
  } catch {
    sshConfig.value.pingEnabled = !val;
    ElMessage.error('设置失败');
  }
};

const fetchFirewallData = async () => {
  loading.value = true;
  try {
    const res = await getFirewallList({ page: 1, limit: 100 });
    if (res && res.data) {
      portRules.value = res.data || [];
    }
  } catch (error) {
    console.error('获取防火墙列表失败:', error);
  } finally {
    loading.value = false;
  }
};

const fetchSshInfo = async () => {
  try {
    const res = await getSshInfo();
    if (res && res.data) {
      const info = res.data;
      sshConfig.value.port = info.port || '22';
      sshConfig.value.rootLogin = info.is_root === 'yes' || info.is_root === true;
      sshConfig.value.passwordAuth = info.pass_work === 'yes' || info.pass_work === true;
      sshConfig.value.pubkeyAuth = info.pubkey_work === 'yes' || info.pubkey_work === true;
      sshConfig.value.pingEnabled = info.ping !== '0' && info.ping !== false;
    }
  } catch (error) {
    console.error('获取SSH信息失败:', error);
  }
};

onMounted(() => {
  fetchFirewallData();
  fetchSshInfo();
});
</script>

<style lang="scss" scoped>
.firewall-page {
  .stats-row {
    margin-bottom: 16px;

    .stat-card {
      text-align: center;
      margin-bottom: 8px;
    }
  }

  .tab-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    gap: 12px;

    .tab-header-left {
      display: flex;
      gap: 8px;
      align-items: center;
    }
  }

  .ssh-form {
    max-width: 500px;
    margin-top: 16px;
  }

  .form-tip {
    display: inline-block;
    margin-left: 8px;
    font-size: 12px;
    color: #909399;
  }
}
</style>
