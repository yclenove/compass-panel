import { defineStore } from 'pinia';
import { ref } from 'vue';
import { getSystemInfo, getSystemNetwork, getDiskInfo } from '@/api/index';

// 解析 "1007G" "18G" 这种格式为字节数
function parseSize(str) {
  if (!str || str === '-') return 0;
  str = str.toString().trim();
  const match = str.match(/^([\d.]+)\s*([KMGTP]?B?)$/i);
  if (!match) return 0;
  const num = parseFloat(match[1]);
  const unit = match[2].toUpperCase();
  const multipliers = { '': 1, 'B': 1, 'K': 1024, 'KB': 1024, 'M': 1024**2, 'MB': 1024**2, 'G': 1024**3, 'GB': 1024**3, 'T': 1024**4, 'TB': 1024**4 };
  return Math.round(num * (multipliers[unit] || 1));
}

export const useAppStore = defineStore('app', () => {
  const systemInfo = ref({
    cpu: { cores: 0, usage: 0, model: '' },
    memory: { total: 0, used: 0, free: 0, usage: 0 },
    disk: { total: 0, used: 0, free: 0, usage: 0 },
    network: { up: 0, down: 0, tcp: 0, established: 0 },
    load: { one: 0, five: 0, fifteen: 0 },
    process: { total: 0, running: 0, sleeping: 0 },
    swap: { total: 0, used: 0, usage: 0 },
    uptime: '',
    hostname: '',
    os: '',
    kernel: '',
    arch: '',
    version: '',
    time: '',
  });

  const sidebarCollapsed = ref(false);
  const theme = ref(localStorage.getItem('mw_theme') || 'light');

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value;
  }

  function setTheme(newTheme) {
    theme.value = newTheme;
    localStorage.setItem('mw_theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  }

  async function fetchSystemInfo() {
    try {
      const [basicRes, networkRes, diskRes] = await Promise.all([
        getSystemInfo(),
        getSystemNetwork(),
        getDiskInfo().catch(() => null),
      ]);

      const basic = basicRes || {};
      const net = networkRes || {};

      // CPU: cpu array = [usage, cores, perCore[], model, ...]
      const cpuArr = net.cpu || [];
      const cpuUsage = basic.cpuRealUsed ?? cpuArr[0] ?? 0;
      const cpuCores = basic.cpuNum ?? cpuArr[1] ?? 0;
      const cpuModel = cpuArr[3] || basic.cpuModel || '';

      // Load
      const load = net.load || {};

      // Memory
      const mem = net.mem || basic;

      // Network: network.ALL has up/down in bytes/sec
      const netAll = net.network?.ALL || {};

      // Disk space from disk_info endpoint (root partition "/")
      let diskTotal = 0, diskUsed = 0, diskFree = 0, diskUsage = 0;
      if (diskRes?.data) {
        // 找到根分区
        const rootDisk = diskRes.data.find(d => d.path === '/');
        if (rootDisk?.size) {
          diskTotal = parseSize(rootDisk.size[0]);
          diskUsed = parseSize(rootDisk.size[1]);
          diskFree = parseSize(rootDisk.size[2]);
          diskUsage = parseInt(rootDisk.size[3]) || 0;
        }
      }

      // 解析运行时间字符串
      const timeStr = basic.time || '';

      systemInfo.value = {
        cpu: {
          cores: cpuCores,
          usage: Math.round(cpuUsage),
          model: cpuModel,
        },
        memory: {
          total: (mem.memTotal || basic.memTotal || 0) * 1024 * 1024, // MB -> bytes
          used: (mem.memRealUsed || basic.memRealUsed || 0) * 1024 * 1024,
          free: (mem.memFree || basic.memFree || 0) * 1024 * 1024,
          usage: (mem.memTotal || basic.memTotal)
            ? Math.round(((mem.memRealUsed || basic.memRealUsed || 0) / (mem.memTotal || basic.memTotal)) * 100)
            : 0,
        },
        disk: {
          total: diskTotal,
          used: diskUsed,
          free: diskFree,
          usage: diskUsage,
        },
        network: {
          up: Math.round(netAll.up || 0),
          down: Math.round(netAll.down || 0),
          tcp: 0,
          established: 0,
        },
        load: {
          one: load.one ?? 0,
          five: load.five ?? 0,
          fifteen: load.fifteen ?? 0,
        },
        process: {
          total: 0,
          running: 0,
          sleeping: 0,
        },
        swap: {
          total: (mem.memSwapTotal || 0) * 1024 * 1024, // MB -> bytes
          used: (mem.memSwapUsed || 0) * 1024 * 1024,
          usage: mem.memSwapTotal
            ? Math.round(((mem.memSwapUsed || 0) / mem.memSwapTotal) * 100)
            : 0,
        },
        uptime: timeStr,
        hostname: basic.hostname || '',
        os: basic.system || '',
        kernel: basic.kernel || '',
        arch: basic.arch || '',
        version: basic.version || '',
        time: timeStr,
      };

      return systemInfo.value;
    } catch (error) {
      console.error('获取系统信息失败:', error);
      throw error;
    }
  }

  return {
    systemInfo,
    sidebarCollapsed,
    theme,
    toggleSidebar,
    setTheme,
    fetchSystemInfo,
  };
});
