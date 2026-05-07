import request from '@/utils/request';

// ==================== 系统信息 ====================

// 获取系统信息（CPU、内存基本信息）
export function getSystemInfo() {
  return request({ url: '/system/system_total', method: 'post' });
}

// 获取系统综合信息（CPU、负载、内存、磁盘IO、网络）
export function getSystemNetwork() {
  return request({ url: '/system/network', method: 'get' });
}

// 获取系统负载
export function getSystemLoad() {
  return request({ url: '/system/get_load_average', method: 'get' });
}

// 获取磁盘IO历史数据
export function getDiskIo(params = {}) {
  return request({ url: '/system/get_disk_io', method: 'get', params });
}

// 获取CPU IO历史数据
export function getCpuIo(params = {}) {
  return request({ url: '/system/get_cpu_io', method: 'get', params });
}

// 获取网络IO历史数据
export function getNetworkIo(params = {}) {
  return request({ url: '/system/get_network_io', method: 'get', params });
}

// 获取磁盘信息
export function getDiskInfo() {
  return request({ url: '/system/disk_info', method: 'post' });
}

// 获取面板信息
export function getPanelInfo() {
  return request({ url: '/panel/get_panel_info', method: 'post' });
}

// 获取监控设置
export function getMonitorControl() {
  const data = new URLSearchParams();
  data.append('type', 'get');
  return request({ url: '/system/set_control', method: 'post', data });
}

// 设置监控开关
export function setMonitorControl(stype, day) {
  const data = new URLSearchParams();
  data.append('type', stype);
  data.append('day', day || '30');
  return request({ url: '/system/set_control', method: 'post', data });
}

// ==================== 网站管理 ====================

// 站点列表
export function getSiteList(params = {}) {
  const data = new URLSearchParams();
  data.append('p', params.page || 1);
  data.append('limit', params.limit || 10);
  if (params.type_id !== undefined && params.type_id !== '') data.append('type_id', params.type_id);
  if (params.search) data.append('search', params.search);
  if (params.order) data.append('order', params.order);
  return request({ url: '/site/list', method: 'post', data });
}

// 添加站点
export function addSite(params) {
  const data = new URLSearchParams();
  data.append('webinfo', params.name);
  data.append('ps', params.ps || '');
  data.append('path', params.path || '');
  data.append('version', params.php_version || '');
  data.append('port', params.port || '80');
  return request({ url: '/site/add', method: 'post', data });
}

// 启动站点
export function startSite(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/site/start', method: 'post', data });
}

// 停止站点
export function stopSite(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/site/stop', method: 'post', data });
}

// 删除站点
export function deleteSite(id, path) {
  const data = new URLSearchParams();
  data.append('id', id);
  if (path) data.append('path', path);
  return request({ url: '/site/delete', method: 'post', data });
}

// 获取站点域名列表
export function getSiteDomains(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/site/get_site_domains', method: 'post', data });
}

// 添加站点域名
export function addSiteDomain(id, siteName, domain) {
  const data = new URLSearchParams();
  data.append('id', id);
  data.append('site_name', siteName);
  data.append('domain', domain);
  return request({ url: '/site/add_domain', method: 'post', data });
}

// 删除站点域名
export function delSiteDomain(id, siteName, domain, port) {
  const data = new URLSearchParams();
  data.append('id', id);
  data.append('site_name', siteName);
  data.append('domain', domain);
  data.append('port', port || '');
  return request({ url: '/site/del_domain', method: 'post', data });
}

// 获取站点SSL证书信息
export function getSiteSsl(siteName, sslType) {
  const data = new URLSearchParams();
  data.append('site_name', siteName);
  data.append('ssl_type', sslType || '');
  return request({ url: '/site/get_ssl', method: 'post', data });
}

// 设置站点SSL证书
export function setSiteSsl(siteName, key, csr) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  data.append('key', key);
  data.append('csr', csr);
  return request({ url: '/site/set_ssl', method: 'post', data });
}

// 关闭站点SSL
export function closeSiteSsl(siteName) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  return request({ url: '/site/close_ssl_conf', method: 'post', data });
}

// 强制HTTPS
export function httpToHttps(siteName) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  return request({ url: '/site/http_to_https', method: 'post', data });
}

// 关闭强制HTTPS
export function closeToHttps(siteName) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  return request({ url: '/site/close_to_https', method: 'post', data });
}

// 获取站点备份列表
export function getSiteBackup(id, page, limit) {
  const data = new URLSearchParams();
  data.append('search', id);
  data.append('p', page || 1);
  data.append('limit', limit || 10);
  return request({ url: '/site/get_backup', method: 'post', data });
}

// 创建站点备份
export function createSiteBackup(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/site/to_backup', method: 'post', data });
}

// 删除站点备份
export function delSiteBackup(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/site/del_backup', method: 'post', data });
}

// 获取站点访问日志
export function getSiteLogs(siteName) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  return request({ url: '/site/get_logs', method: 'post', data });
}

// 获取站点错误日志
export function getSiteErrorLogs(siteName) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  return request({ url: '/site/get_error_logs', method: 'post', data });
}

// 获取站点配置
export function getSiteHostConf(siteName) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  return request({ url: '/site/get_host_conf', method: 'post', data });
}

// 保存站点配置
export function saveSiteHostConf(path, dataContent, encoding) {
  const data = new URLSearchParams();
  data.append('path', path);
  data.append('data', dataContent);
  data.append('encoding', encoding || '');
  return request({ url: '/site/save_host_conf', method: 'post', data });
}

// 设置站点路径
export function setSitePath(id, path) {
  const data = new URLSearchParams();
  data.append('id', id);
  data.append('path', path);
  return request({ url: '/site/set_path', method: 'post', data });
}

// 设置站点备注
export function setSiteRemark(id, ps) {
  const data = new URLSearchParams();
  data.append('id', id);
  data.append('ps', ps);
  return request({ url: '/site/set_ps', method: 'post', data });
}

// 设置站点到期时间
export function setSiteEndDate(id, edate) {
  const data = new URLSearchParams();
  data.append('id', id);
  data.append('edate', edate);
  return request({ url: '/site/set_end_date', method: 'post', data });
}

// 获取站点PHP版本
export function getSitePhpVersion(siteName) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  return request({ url: '/site/get_site_php_version', method: 'post', data });
}

// 设置站点PHP版本
export function setSitePhpVersion(siteName, version) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  data.append('version', version);
  return request({ url: '/site/set_php_version', method: 'post', data });
}

// 获取站点默认文档
export function getSiteIndex(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/site/get_index', method: 'post', data });
}

// 设置站点默认文档
export function setSiteIndex(id, index) {
  const data = new URLSearchParams();
  data.append('id', id);
  data.append('index', index);
  return request({ url: '/site/set_index', method: 'post', data });
}

// 获取站点流量限制
export function getSiteLimitNet(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/site/get_limit_net', method: 'post', data });
}

// 设置站点流量限制
export function setSiteLimitNet(id, perserver, perip, limitRate) {
  const data = new URLSearchParams();
  data.append('id', id);
  data.append('perserver', perserver);
  data.append('perip', perip);
  data.append('limit_rate', limitRate);
  return request({ url: '/site/set_limit_net', method: 'post', data });
}

// 关闭站点流量限制
export function closeSiteLimitNet(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/site/close_limit_net', method: 'post', data });
}

// 设置站点密码访问
export function setSiteHasPwd(id, username, password) {
  const data = new URLSearchParams();
  data.append('id', id);
  data.append('username', username);
  data.append('password', password);
  return request({ url: '/site/set_has_pwd', method: 'post', data });
}

// 关闭站点密码访问
export function closeSiteHasPwd(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/site/close_has_pwd', method: 'post', data });
}

// 获取站点重定向列表
export function getSiteRedirect(siteName) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  return request({ url: '/site/get_redirect', method: 'post', data });
}

// 设置站点重定向
export function setSiteRedirect(siteName, from, to, type, rType, keepPath) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  data.append('from', from);
  data.append('to', to);
  data.append('type', type || '');
  data.append('r_type', rType || '');
  data.append('keep_path', keepPath || '');
  return request({ url: '/site/set_redirect', method: 'post', data });
}

// 删除站点重定向
export function delSiteRedirect(siteName, id) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  data.append('id', id);
  return request({ url: '/site/del_redirect', method: 'post', data });
}

// 获取站点代理列表
export function getSiteProxyList(siteName) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  return request({ url: '/site/get_proxy_list', method: 'post', data });
}

// 设置站点代理
export function setSiteProxy(params) {
  const data = new URLSearchParams();
  data.append('siteName', params.siteName || '');
  data.append('from', params.from || '');
  data.append('to', params.to || '');
  data.append('host', params.host || '');
  data.append('name', params.name || '');
  data.append('open_proxy', params.open_proxy || '');
  data.append('open_cors', params.open_cors || '');
  data.append('open_http3', params.open_http3 || '');
  data.append('open_cache', params.open_cache || '');
  data.append('cache_time', params.cache_time || '');
  if (params.id) data.append('id', params.id);
  return request({ url: '/site/set_proxy', method: 'post', data });
}

// 删除站点代理
export function delSiteProxy(siteName, id) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  data.append('id', id);
  return request({ url: '/site/del_proxy', method: 'post', data });
}

// 获取防盗链信息
export function getSiteSecurity(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/site/get_security', method: 'post', data });
}

// 设置防盗链
export function setSiteSecurity(id, fix, domains, status, none) {
  const data = new URLSearchParams();
  data.append('id', id);
  data.append('fix', fix || '');
  data.append('domains', domains || '');
  data.append('status', status || '');
  data.append('none', none || '');
  return request({ url: '/site/set_security', method: 'post', data });
}

// 获取Rewrite配置
export function getSiteRewriteConf(siteName) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  return request({ url: '/site/get_rewrite_conf', method: 'post', data });
}

// 保存Rewrite配置
export function saveSiteRewrite(path, dataContent, encoding) {
  const data = new URLSearchParams();
  data.append('path', path);
  data.append('data', dataContent);
  data.append('encoding', encoding || '');
  return request({ url: '/site/set_rewrite', method: 'post', data });
}

// 获取Rewrite模板列表
export function getRewriteList() {
  return request({ url: '/site/get_rewrite_list', method: 'post' });
}

// 获取Rewrite模板内容
export function getRewriteTpl(name) {
  const data = new URLSearchParams();
  data.append('name', name);
  return request({ url: '/site/get_rewrite_tpl', method: 'post', data });
}

// 设置Rewrite模板
export function setRewriteTpl(name, dataContent) {
  const data = new URLSearchParams();
  data.append('name', name);
  data.append('data', dataContent);
  return request({ url: '/site/set_rewrite_tpl', method: 'post', data });
}

// 日志开关
export function toggleSiteLogs(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/site/logs_open', method: 'post', data });
}

// ==================== 防火墙 ====================

// 防火墙规则列表
export function getFirewallList(params = {}) {
  const data = new URLSearchParams();
  data.append('p', params.page || 1);
  data.append('limit', params.limit || 10);
  return request({ url: '/firewall/get_list', method: 'post', data });
}

// 添加放行端口
export function addAcceptPort(params) {
  const data = new URLSearchParams();
  data.append('port', params.port);
  data.append('ps', params.ps || '');
  data.append('protocol', params.protocol || 'tcp');
  data.append('type', params.type || 'accept');
  return request({ url: '/firewall/add_accept_port', method: 'post', data });
}

// 删除放行端口
export function delAcceptPort(id, port, protocol) {
  const data = new URLSearchParams();
  data.append('id', id);
  data.append('port', port || '');
  data.append('protocol', protocol || '');
  return request({ url: '/firewall/del_accept_port', method: 'post', data });
}

// 获取SSH信息
export function getSshInfo() {
  return request({ url: '/firewall/get_ssh_info', method: 'post' });
}

// 设置SSH端口
export function setSshPort(port) {
  const data = new URLSearchParams();
  data.append('port', port);
  return request({ url: '/firewall/set_ssh_port', method: 'post', data });
}

// 设置ping状态
export function setPingStatus(status) {
  const data = new URLSearchParams();
  data.append('status', status);
  return request({ url: '/firewall/set_ping', method: 'post', data });
}

// 设置SSH Root登录状态
export function setSshRootStatus(status) {
  const data = new URLSearchParams();
  data.append('status', status);
  return request({ url: '/firewall/set_ssh_root_status', method: 'post', data });
}

// 设置SSH密码登录状态
export function setSshPassStatus(status) {
  const data = new URLSearchParams();
  data.append('status', status);
  return request({ url: '/firewall/set_ssh_pass_status', method: 'post', data });
}

// 设置SSH公钥登录状态
export function setSshPubkeyStatus(status) {
  const data = new URLSearchParams();
  data.append('status', status);
  return request({ url: '/firewall/set_ssh_pubkey_status', method: 'post', data });
}

// 设置防火墙状态
export function setFirewallStatus(status) {
  const data = new URLSearchParams();
  data.append('status', status);
  return request({ url: '/firewall/set_fw', method: 'post', data });
}

// ==================== 计划任务 ====================

// 计划任务列表
export function getCrontabList(params = {}) {
  const data = new URLSearchParams();
  data.append('p', params.page || 1);
  data.append('limit', params.limit || 10);
  return request({ url: '/crontab/list', method: 'post', data });
}

// 删除计划任务
export function deleteCrontab(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/crontab/del', method: 'post', data });
}

// 设置计划任务状态
export function setCrontabStatus(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/crontab/set_cron_status', method: 'post', data });
}

// 添加计划任务
export function addCrontab(params) {
  const data = new URLSearchParams();
  data.append('name', params.name || '');
  data.append('type', params.type || '');
  data.append('week', params.week || '');
  data.append('where1', params.where1 || '');
  data.append('hour', params.hour || '');
  data.append('minute', params.minute || '');
  data.append('save', params.save || '');
  data.append('backup_to', params.backup_to || '');
  data.append('stype', params.stype || '');
  data.append('sname', params.sname || '');
  data.append('sbody', params.sbody || '');
  data.append('url_address', params.url_address || '');
  data.append('attr', params.attr || '');
  return request({ url: '/crontab/add', method: 'post', data });
}

// 修改计划任务
export function modifyCrontab(id, params) {
  const data = new URLSearchParams();
  data.append('id', id);
  data.append('name', params.name || '');
  data.append('type', params.type || '');
  data.append('week', params.week || '');
  data.append('where1', params.where1 || '');
  data.append('hour', params.hour || '');
  data.append('minute', params.minute || '');
  data.append('save', params.save || '');
  data.append('backup_to', params.backup_to || '');
  data.append('stype', params.stype || '');
  data.append('sname', params.sname || '');
  data.append('sbody', params.sbody || '');
  data.append('url_address', params.url_address || '');
  data.append('attr', params.attr || '');
  return request({ url: '/crontab/modify_crond', method: 'post', data });
}

// 执行计划任务
export function startCrontabTask(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/crontab/start_task', method: 'post', data });
}

// 获取计划任务日志
export function getCrontabLogs(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/crontab/logs', method: 'post', data });
}

// 删除计划任务日志
export function deleteCrontabLogs(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/crontab/del_logs', method: 'post', data });
}

// ==================== 日志管理 ====================

// 获取日志列表
export function getLogList(params = {}) {
  const data = new URLSearchParams();
  data.append('p', params.page || 1);
  data.append('limit', params.limit || 10);
  if (params.search) data.append('search', params.search);
  return request({ url: '/logs/get_log_list', method: 'post', data });
}

// 清空日志
export function clearLogs() {
  return request({ url: '/logs/del_panel_logs', method: 'post' });
}

// ==================== 面板设置 ====================

// 获取面板设置信息
export function getPanelSettings() {
  return request({ url: '/setting/get_panel_settings', method: 'post' });
}

// 设置面板名称
export function setWebname(webname) {
  const data = new URLSearchParams();
  data.append('webname', webname);
  return request({ url: '/setting/set_webname', method: 'post', data });
}

// 设置服务器IP
export function setServerIp(host_ip) {
  const data = new URLSearchParams();
  data.append('host_ip', host_ip);
  return request({ url: '/setting/set_ip', method: 'post', data });
}

// 设置备份目录
export function setBackupDir(backup_path) {
  const data = new URLSearchParams();
  data.append('backup_path', backup_path);
  return request({ url: '/setting/set_backup_dir', method: 'post', data });
}

// 设置站点目录
export function setSitesDir(sites_path) {
  const data = new URLSearchParams();
  data.append('sites_path', sites_path);
  return request({ url: '/setting/set_www_dir', method: 'post', data });
}

// 设置安全入口
export function setAdminPath(admin_path) {
  const data = new URLSearchParams();
  data.append('admin_path', admin_path);
  return request({ url: '/setting/set_admin_path', method: 'post', data });
}

// 设置BasicAuth
export function setBasicAuth(params) {
  const data = new URLSearchParams();
  data.append('basic_user', params.basic_user || '');
  data.append('basic_pwd', params.basic_pwd || '');
  data.append('is_open', params.is_open ? 'true' : 'false');
  return request({ url: '/setting/set_basic_auth', method: 'post', data });
}

// 设置未授权状态码
export function setStatusCode(status_code) {
  const data = new URLSearchParams();
  data.append('status_code', status_code);
  return request({ url: '/setting/set_status_code', method: 'post', data });
}

// 切换调试模式
export function toggleDebug() {
  return request({ url: '/setting/open_debug', method: 'post' });
}

// 切换面板开关
export function togglePanel() {
  return request({ url: '/setting/close_panel', method: 'post' });
}

// 设置IPv6状态
export function setIpv6Status() {
  return request({ url: '/setting/set_ipv6_status', method: 'post' });
}

// 设置面板用户名
export function setName(name1, name2) {
  const data = new URLSearchParams();
  data.append('name1', name1);
  data.append('name2', name2);
  return request({ url: '/setting/set_name', method: 'post', data });
}

// 设置面板密码
export function setPassword(password1, password2) {
  const data = new URLSearchParams();
  data.append('password1', password1);
  data.append('password2', password2);
  return request({ url: '/setting/set_password', method: 'post', data });
}

// 设置面板端口
export function setPort(port) {
  const data = new URLSearchParams();
  data.append('port', port);
  return request({ url: '/setting/set_port', method: 'post', data });
}

// ==================== 软件/插件管理 ====================

// 获取插件列表
export function getPluginList(params = {}) {
  return request({ url: '/plugins/list', method: 'get', params });
}

// 获取首页插件列表
export function getIndexPluginList() {
  return request({ url: '/plugins/index_list', method: 'post' });
}

// 安装插件
export function installPlugin(name, version) {
  const data = new URLSearchParams();
  data.append('name', name);
  data.append('version', version);
  return request({ url: '/plugins/install', method: 'post', data });
}

// 卸载插件
export function uninstallPlugin(name, version) {
  const data = new URLSearchParams();
  data.append('name', name);
  data.append('version', version);
  return request({ url: '/plugins/uninstall', method: 'post', data });
}

// 设置插件首页展示
export function setPluginIndex(name, status, version) {
  const data = new URLSearchParams();
  data.append('name', name);
  data.append('status', status);
  data.append('version', version);
  return request({ url: '/plugins/set_index', method: 'post', data });
}

// 运行插件回调
export function runPlugin(name, func, version, args, script) {
  const data = new URLSearchParams();
  data.append('name', name);
  data.append('func', func);
  data.append('version', version || '');
  data.append('args', args || '');
  data.append('script', script || 'index');
  return request({ url: '/plugins/run', method: 'post', data });
}

// ==================== 文件管理 ====================

// 获取目录列表
export function getDirList(path, showHidden) {
  const data = new URLSearchParams();
  data.append('path', path || '/');
  data.append('showHidden', showHidden ? '1' : '0');
  return request({ url: '/files/get_dir', method: 'post', data });
}

// 获取文件内容
export function getFileBody(path) {
  const data = new URLSearchParams();
  data.append('path', path);
  return request({ url: '/files/get_body', method: 'post', data });
}

// 保存文件内容
export function saveFileBody(path, data_content) {
  const data = new URLSearchParams();
  data.append('path', path);
  data.append('data', data_content);
  return request({ url: '/files/save_body', method: 'post', data });
}

// 删除文件
export function deleteFile(path) {
  const data = new URLSearchParams();
  data.append('path', path);
  return request({ url: '/files/delete', method: 'post', data });
}

// 创建目录
export function createDir(path) {
  const data = new URLSearchParams();
  data.append('path', path);
  return request({ url: '/files/create_dir', method: 'post', data });
}

// 创建文件
export function createFile(path) {
  const data = new URLSearchParams();
  data.append('path', path);
  return request({ url: '/files/create_file', method: 'post', data });
}

// ==================== 站点代理管理 ====================

// 获取代理列表
export function getProxyList(siteName) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  return request({ url: '/site/get_proxy_list', method: 'post', data });
}

// 设置代理
export function setProxy({ siteName, from, to, host, name, open_proxy, open_cors, open_http3, open_cache, cache_time, id }) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  if (from) data.append('from', from);
  if (to) data.append('to', to);
  if (host) data.append('host', host);
  if (name) data.append('name', name);
  if (open_proxy) data.append('open_proxy', open_proxy);
  if (open_cors) data.append('open_cors', open_cors);
  if (open_http3) data.append('open_http3', open_http3);
  if (open_cache) data.append('open_cache', open_cache);
  if (cache_time) data.append('cache_time', cache_time);
  if (id) data.append('id', id);
  return request({ url: '/site/set_proxy', method: 'post', data });
}

// 设置代理状态
export function setProxyStatus(siteName, id, status) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  data.append('id', id);
  data.append('status', status);
  return request({ url: '/site/set_proxy_status', method: 'post', data });
}

// 获取代理配置
export function getProxyConf(siteName, id) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  data.append('id', id);
  return request({ url: '/site/get_proxy_conf', method: 'post', data });
}

// 保存代理配置
export function saveProxyConf(siteName, id, config) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  data.append('id', id);
  data.append('config', config);
  return request({ url: '/site/save_proxy_conf', method: 'post', data });
}

// 删除代理
export function delProxy(siteName, id) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  data.append('id', id);
  return request({ url: '/site/del_proxy', method: 'post', data });
}

// ==================== 站点重定向管理 ====================

// 获取重定向列表
export function getRedirect(siteName) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  return request({ url: '/site/get_redirect', method: 'post', data });
}

// 设置重定向
export function setRedirect({ siteName, from, to, type, r_type, keep_path }) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  if (from) data.append('from', from);
  if (to) data.append('to', to);
  if (type) data.append('type', type);
  if (r_type) data.append('r_type', r_type);
  if (keep_path) data.append('keep_path', keep_path);
  return request({ url: '/site/set_redirect', method: 'post', data });
}

// 设置重定向状态
export function setRedirectStatus(siteName, id, status) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  data.append('id', id);
  data.append('status', status);
  return request({ url: '/site/set_redirect_status', method: 'post', data });
}

// 获取重定向配置
export function getRedirectConf(siteName, id) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  data.append('id', id);
  return request({ url: '/site/get_redirect_conf', method: 'post', data });
}

// 保存重定向配置
export function saveRedirectConf(siteName, id, config) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  data.append('id', id);
  data.append('config', config);
  return request({ url: '/site/save_redirect_conf', method: 'post', data });
}

// 删除重定向
export function delRedirect(siteName, id) {
  const data = new URLSearchParams();
  data.append('siteName', siteName);
  data.append('id', id);
  return request({ url: '/site/del_redirect', method: 'post', data });
}

// ==================== 站点分类管理 ====================

// 获取站点分类列表
export function getSiteTypes() {
  return request({ url: '/site/get_site_types', method: 'post' });
}

// 添加站点分类
export function addSiteType(name) {
  const data = new URLSearchParams();
  data.append('name', name);
  return request({ url: '/site/add_site_type', method: 'post', data });
}

// 删除站点分类
export function removeSiteType(id) {
  const data = new URLSearchParams();
  data.append('id', id);
  return request({ url: '/site/remove_site_type', method: 'post', data });
}

// 修改站点分类名称
export function modifySiteTypeName(id, name) {
  const data = new URLSearchParams();
  data.append('id', id);
  data.append('name', name);
  return request({ url: '/site/modify_site_type_name', method: 'post', data });
}

// 设置站点分类
export function setSiteType(siteIds, typeId) {
  const data = new URLSearchParams();
  data.append('site_ids', JSON.stringify(siteIds));
  data.append('id', typeId);
  return request({ url: '/site/set_site_type', method: 'post', data });
}

// ==================== 系统控制 ====================

// 重启面板
export function restartPanelApi() {
  return request({ url: '/system/restart', method: 'post' });
}

// 重启服务器
export function restartServerApi() {
  return request({ url: '/system/restart_server', method: 'post' });
}
