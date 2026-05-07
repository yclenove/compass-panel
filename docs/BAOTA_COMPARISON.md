# Compass面板 深度功能差距分析与迭代计划

> **Compass 指南面板** - 新一代Linux服务器管理面板
> 项目名: compass-panel | CLI: compass | GitHub: midoks/compass-panel
>
> 基于宝塔面板源码深度分析，覆盖 class/ 目录下 130+ 个模块的完整功能清单
> 目标: 不是对标宝塔，是要比宝塔更好。迭代的尽头是完美产品。

---

## 一、功能全景对比

| 功能域 | MW现状 | 宝塔完整能力 | 差距 |
|-------|--------|------------|------|
| **项目类型** | PHP/Node.js/Java 基础 | PHP/Node.js/Java/Python/Go/HTML/反代 7种，各有独立环境管理 | ★★★ |
| **语言运行时** | 依赖插件 | PHP多版本(5.6~8.x)管理、Python虚拟环境(pyenv/pyvm)、Go版本管理(gvm)、Node.js版本管理、JDK多版本(8/11)、Tomcat多版本(7/8/9) | ★★★ |
| **Web服务器** | Nginx/OpenResty | Nginx + Apache + OpenLiteSpeed + Caddy，支持在线切换 | ★★☆ |
| **网站功能** | 基础增删 | 伪静态/防盗链/重定向/目录密码/子目录绑定/负载均衡/错误页/PHP版本切换/分类管理/批量操作 | ★★★ |
| **数据库** | MySQL基础 | MySQL/PostgreSQL/MongoDB/Redis/Redis Cluster/SQLite/SQL Server + phpMyAdmin集成 | ★★★ |
| **文件管理** | 列表/编辑/基础操作 | 压缩(zip/gz/rar/7z)/解压/上传/下载/搜索(文件名+内容+正则)/回收站/软链接/MD5校验/所有者修改/编码转换 | ★★☆ |
| **安全** | 基础端口 | WAF(SQL注入/XSS检测 via libinjection)/SSH加固(12项检查规则)/入侵检测/安全扫描(漏洞评分)/爬虫防御/扫描器拦截/面板日报 | ★★★ |
| **SSL** | Let's Encrypt基础 | 15+ DNS API(阿里/腾讯/Cloudflare/AWS/华为/火山引擎/GoDaddy/DNSPod等)/自动续期/到期提醒/通配符/安全评分/证书管理器 | ★★☆ |
| **监控** | 基础4卡片 | 实时折线图/进程管理/服务管理/站点流量统计/状态码分布(401/500/502/503)/多网卡/磁盘IO | ★★☆ |
| **备份** | 基础本地 | 本地+云存储(七牛/阿里OSS/AWS S3/腾讯COS/Google Drive/OneDrive)/增量备份/拆分备份(5GB)/定时计划/备份通知/整机备份 | ★★★ |
| **计划任务** | 基础cron | Shell/网站备份/数据库备份/日志切割/URL请求/清理/FTP同步，含执行日志+错误通知+文件锁 | ★★☆ |
| **Docker** | 插件形式 | 容器/镜像/网络/卷/Compose/仓库/容器组/安全/监控/代理，25个子模块 | ★★★ |
| **FTP** | 无 | PureFTPd完整集成(用户管理/配额/日志/分类/推送配置) | ★★★ |
| **邮件** | 无 | 邮件服务器(接收/转发/批量/PowerMTA)/Roundcube WebMail | ★★☆ |
| **日志** | 基础查看 | 站点日志/FTP日志/面板日志/系统日志/日志分析(XSS/SQL/敏感信息检测)/日志切割/日志推送 | ★★☆ |
| **通知推送** | 基础邮件 | 模块化推送系统(push/): 邮件/Telegram/微信/企业微信/钉钉/短信/Bark/PushPlus/Server酱 | ★★☆ |
| **用户** | 单用户 | 多用户CRUD/权限隔离/API密钥管理/IP白名单/扫码登录(App)/WebAuthn | ★★☆ |
| **面板安全** | 基础 | 两步验证(TOTP)/Basic Auth/面板SSL/安全入口/Google Authenticator/微信扫码/防御模块(爬虫/扫描器/脚本工具) | ★★☆ |
| **系统优化** | 无 | Swap管理/进程管理/服务管理/系统清理/端口扫描/系统日报/面板工作台(远程协助) | ★★☆ |
| **一键部署** | 无 | WordPress扫描检测/插件部署系统/软件商店(付费+免费) | ★★☆ |
| **主题** | 默认 | 主题配置系统(配置读写/验证/格式转换/模板/上传/下载) | ★☆☆ |
| **API** | 无 | 完整API接口(token认证/IP限制/绑定管理/扫码登录) | ★★☆ |
| **流媒体** | 无 | 视频流媒体支持(Range请求/分片传输) | ★☆☆ |
| **phpMyAdmin** | 无 | 内置HTTP代理转发到PHP-FPM，面板内嵌phpMyAdmin | ★★☆ |

---

## 二、宝塔网站管理深度分析 - 7种项目类型详解

### 2.1 PHP项目 (class/projectModel/phpModel.py)
**环境管理:**
- PHP版本矩阵(config/php_versions.json): 5.2/5.3/5.4/5.5/5.6/7.0/7.1/7.2/7.3/7.4/8.0/8.1/8.2/8.3/8.4/8.5 (16个版本)
- 每个站点可独立选择PHP版本
- PHP-FPM配置管理(进程数/超时/内存限制)
- PHP扩展管理(安装/卸载/配置)
- PHP配置编辑(php.ini完整支持)
- PHP会话管理
- 慢日志分析
- mod/project/php/: serviceconfMod(PHP服务配置) + php_asyncMod(异步PHP) + aepgMod

### 2.2 Node.js项目 (class/projectModel/nodejsModel.py + mod/project/nodejs/)
**环境管理:**
- Node.js多版本安装/切换
- 包管理器: npm/pnpm/yarn 全支持 (mod/project/nodejs/packageManage.py)
- PM2进程守护完整集成 (mod/project/nodejs/pm2Mod.py)
- mod/project/nodejs/: base/comMod/generalMod/nodeMod/packageManage/pm2Mod/utils

**项目功能:**
- 项目启动脚本配置(start script)
- 项目端口配置
- npm执行日志
- 项目日志管理
- 运行用户配置
- Node.js项目分类管理

### 2.3 Java项目 (class/projectModel/javaModel.py + mod/project/java/)
**环境管理:**
- JDK多版本(JDK8/JDK11) - 安装路径 /usr/local/btjdk/
- Tomcat多版本(Tomcat7/8/9) - 安装路径 /usr/local/bttomcat/
- mod/project/java/: groupMod(项目组)/group_script/java_web_conf/JMX监控/projectMod/project_update/server_proxy(代理)/springboot_parser/utils

**Spring Boot项目:**
- JAR包直接部署
- JVM参数配置(-Xms/-Xmx/-XX等)
- 项目端口配置
- 进程守护(systemd/supervisor)
- 启动脚本管理(/var/tmp/springboot/vhost/scripts/)
- PID管理(/var/tmp/springboot/vhost/pids/)
- 日志管理(/www/wwwlogs/java/springboot/)

**Tomcat项目:**
- WAR包部署到Tomcat
- Tomcat虚拟主机管理(server.xml XML解析)
- Tomcat版本切换
- 自动部署/热部署

### 2.4 Python项目 (class/projectModel/pythonModel.py + mod/project/python/)
**环境管理:**
- Python多版本管理(pyvm工具 - class/projectModel/btpyvm.py)
- Python虚拟环境完整支持 (mod/project/python/pyenv_tool.py - EnvironmentManager/PythonEnvironment)
- 虚拟环境创建/激活/删除
- pip源配置(7个国内镜像):
  - 阿里云: mirrors.aliyun.com/pypi/simple/
  - 清华大学: pypi.tuna.tsinghua.edu.cn/simple
  - 中国科技大学: pypi.mirrors.ustc.edu.cn/simple/
  - 豆瓣: pypi.douban.com/simple/
  - 腾讯云: mirrors.cloud.tencent.com/pypi/simple
  - 华为云: mirrors.huaweicloud.com/repository/pypi/simple
  - 网易: mirrors.163.com/pypi/simple/
- mod/project/python/: environmentMod(环境管理)/pyenv_tool(虚拟环境工具)/serviceMod(服务管理)

**项目功能:**
- 项目启动方式: Gunicorn / uWSGI / 自定义脚本
- WSGI/ASGI配置
- 项目端口配置
- 进程守护
- 项目日志管理(/www/wwwlogs/python/)
- 运行用户配置
- 项目路径: /www/server/python_project/
- 虚拟环境路径: /www/server/pyporject_evn/

### 2.5 Go项目 (class/projectModel/goModel.py)
**环境管理:**
- Go版本管理(gvm工具 - class/projectModel/btpygvm.py)
- Go安装路径: /www/server/go_project/

**项目功能:**
- Go项目部署(编译后的二进制文件部署)
- 源码编译部署
- 项目端口配置
- 进程守护
- PID管理(/var/tmp/gopids/)
- 日志管理(/www/wwwlogs/go/)
- 运行用户配置

### 2.6 HTML/静态网站 (class/projectModel/htmlModel.py)
- 静态文件托管
- 默认文档配置(index.html/index.htm等)
- 分类管理(type_id)
- 批量操作(启动/停止/删除)
- 搜索(名称/备注)
- 分页

### 2.7 反向代理项目 (class/projectModel/proxyModel.py + mod/base/web_conf/proxy.py)
**代理功能:**
- 反向代理配置生成(Nginx/Apache/OLS)
- 代理地址配置
- 负载均衡(多后端+权重)
- WebSocket支持
- 代理缓存配置(Nginx Cache - mod/base/web_conf/nginx_cache.py)
- 代理头配置(Proxy Headers)
- SSL代理
- 代理日志

**附加功能(mod/base/web_conf/):**
- 访问控制(access_control/ - Nginx/Apache CORS管理)
- 访问限制(access_restriction.py)
- IP限制(ip_restrict.py)
- 网络限速(limit_net.py)
- 真实IP获取(nginx_realip.py)
- Nginx Gzip压缩(nginx_gzip.py)
- 防盗链(referer.py)
- 重定向(redirect.py)
- 目录保护(dir_tool.py)
- 日志管理(logmanager.py)
- 默认站点(default_site.py)
- SSL管理(ssl.py)
- DNS API(dns_api.py)
- 域名工具(domain_tool.py)

### 2.8 通用项目基类 (class/projectModel/base.py)
所有项目类型共享:
- 域名管理(批量添加/删除 - mod/project/domain/domainMod.py)
- 子目录绑定
- 分类管理(groupModel.py)
- 项目状态管理(启动/停止/重启)
- 项目配置导出/导入
- 项目监控(monitorModel.py - 站点流量/状态码分布/IP统计/UV/PV)
- 项目安全扫描(scanningModel.py - XSS/SQL/敏感信息检测)
- 项目漏洞扫描(java_scanningModel.py/webscanningModel.py/webbasicscanningModel.py)
- 项目清理(clearModel.py)
- 项目内容管理(contentModel.py)
- Binlog分析(binlogModel.py/analysis_binlogModel.py)
- Sphinx搜索(sphinx_searchModel.py)
- 磁盘配额(quotaModel.py)
- 项目观察(watchModel.py - 文件变更监控)
- Docker项目(dockerModel.py)
- 网络管理(netModel.py)

---

## 三、宝塔安全体系深度分析

### 3.1 WAF防火墙 (class/panelWaf.py)
- SQL注入检测(基于libinjection库)
- XSS攻击检测
- 自定义规则引擎
- Nginx WAF配置
- Apache ModSecurity

### 3.2 SSH安全加固 (class/ssh_security.py) - 12项检查规则
1. MaxAuthTries 设置为3-6
2. 强制使用V2安全协议
3. 空闲超时退出(ClientAliveInterval)
4. SSH LogLevel设置为INFO
5. 禁止空密码登录
6. 修改默认端口22
7. SSH密钥类型管理(ed25519/ecdsa/rsa/dsa)
8. SSH密钥生成/下载
9. SSH登录记录(数据库记录)
10. 异常登录告警(邮件通知)
11. Root登录方式控制(密码/密钥/禁止)
12. IP白名单访问控制

### 3.3 安全扫描 (class/panelWarning.py)
- 系统漏洞扫描(CentOS7漏洞库)
- 安全评分系统(100分制)
- 扫描进度条
- 一键修复
- 修复历史记录
- 漏洞忽略管理
- 安全报告生成

### 3.4 防御模块 (class/panelDefense.py)
- 爬虫防御(搜索引擎爬虫识别)
- 扫描器拦截(wpscan/sqlmap/nmap等30+工具)
- 脚本工具拦截(curl/wget/python/requests等)
- UA长度过滤
- 局域网IP放行

### 3.5 后门扫描 (class/panelSafe.py)
- PHP后门检测(20+规则)
- 一句话木马检测
- WebShell行为检测
- 危险文件操作检测
- 危险上传漏洞检测
- 文件编码自动检测(chardet)

### 3.6 站点目录密码保护 (class/site_dir_auth.py)
- Apache htpasswd格式
- Nginx auth_basic
- APR1-MD5加密

---

## 四、宝塔备份体系深度分析

### 4.1 备份类型 (class/panelBackup.py + mod/base/backup_tool/)
- 网站备份(整站打包)
- 数据库备份(MySQL/PostgreSQL/MongoDB/Redis)
- 增量备份
- 拆分备份(5GB分片)
- 整机备份(whole_machine_backupModel.py)
- Docker Compose备份(docker_compose_backup.py)
- 备份版本管理(mod/base/backup_tool/versions_tool.py)

### 4.2 云存储支持
- 本地存储
- 七牛云(qiniu)
- 阿里云OSS(alioss)
- AWS S3
- 腾讯云COS
- Google Drive(gdrive)
- OneDrive(msonedrive)
- FTP备份(backup_ftp)
- Rsync同步(script/rsyncd)

### 4.3 备份恢复 (mod/project/backup_restore/)
- 备份管理器(backup_manager.py)
- 恢复管理器(restore_manager.py)
- 配置管理器(config_manager.py)
- 数据管理器(data_manager.py)
- SSH管理器(ssh_manager.py - 跨服务器恢复)
- 备份模块(modules/)

### 4.4 备份计划 (class/panelModel/sitebackupModel.py + whole_machine_backupModel.py)
- 定时备份(cron表达式)
- 备份保留策略
- 备份通知(成功/失败 - 推送到消息系统)
- 备份日志
- 备份恢复(一键恢复)
- 整机备份/恢复

---

## 五、宝塔Docker体系深度分析 (class/btdockerModel/ + mod/base/docker/)

### 5.1 完整模块列表(25个)
| 模块 | 功能 |
|------|------|
| containerModel | 容器CRUD/日志/终端/监控 |
| imageModel | 镜像拉取/构建/删除/导入导出 |
| networkModel | 网络创建/删除/连接 |
| volumeModel | 卷创建/删除/清理 |
| composeModel | Docker Compose编排 |
| registryModel | 私有仓库管理 |
| projectModel | 容器化项目管理 |
| backupModel | 容器备份/恢复 |
| securityModel | 容器安全配置 |
| monitorModel | 容器资源监控 |
| proxyModel | 容器代理配置 |
| statusModel | Docker状态监控 |
| setupModel | Docker安装/配置 |
| appModel | 应用商店 |
| hostModel | 主机管理 |
| dkgroupModel | 容器组管理 |
| dockerBase | Docker基础工具 |
| dk_public | Docker公共函数 |
| screen | 容器终端 |

---

## 六、宝塔日志分析体系 (class/log_analysis.py)

### 6.1 日志分析能力
- 站点访问日志分析
- 安全扫描(XSS/SQL注入/敏感信息/PHP代码执行)
- 状态码分布统计(401/500/502/503)
- IP访问统计
- URL访问排行
- 蜘蛛爬取统计
- 日志分析结果保存

### 6.2 日志推送 (class/logsModel/sitelogpushModel.py)
- 实时日志推送到外部系统
- 日志格式化

---

## 七、宝塔消息推送体系 (class/panelPush.py + class/push/)

### 7.1 推送模块化架构
```
class/push/
├── base_push.py          # 推送基类
├── email_push.py         # 邮件推送
├── telegram_push.py      # Telegram推送
├── wechat_push.py        # 微信推送
├── dingding_push.py      # 钉钉推送
├── feishu_push.py        # 飞书推送
├── sms_push.py           # 短信推送
├── bark_push.py          # Bark推送(iOS)
├── pushplus_push.py      # PushPlus推送
├── serverchan_push.py    # Server酱推送
└── ...
```

### 7.2 推送触发场景
- 安全告警
- 备份结果
- SSL到期提醒
- 系统异常
- 面板日报
- 登录通知

---

## 八、宝塔其他重要模块

### 8.1 面板日报 (class/panelDaily.py)
- 每日服务器状态汇总
- 应用使用统计
- 备份状态统计
- 安全事件统计

### 8.2 面板API (class/panelApi.py)
- Token认证
- IP白名单限制
- App扫码登录
- API密钥管理

### 8.3 工单系统 (class/panelWorkorder.py)
- 远程协助
- WebSocket实时通信

### 8.4 流媒体支持 (class/panelVideo.py)
- 视频文件流式传输
- HTTP Range请求支持
- 分片传输

### 8.5 phpMyAdmin集成 (class/panelPmd.py)
- 内嵌phpMyAdmin
- PHP-FPM FastCGI转发
- 自动PHP版本匹配

### 8.6 磁盘配额 (class/projectModel/quotaModel.py)
- 磁盘配额管理
- 用户配额设置

### 8.7 主题配置 (class/theme_config.py)
- 主题安装/卸载
- 配置验证
- 格式转换(新旧版本)
- 主题模板管理

### 8.8 Nginx配置模板 (class/panelModel/nginxtemplateModel.py)
- Nginx配置模板管理
- 模板导入/导出

### 8.9 伪静态规则模板 (rewrite/nginx/ + rewrite/apache/)
- 31套Nginx伪静态规则模板
- 16套Apache伪静态规则模板
- 支持的CMS/框架: WordPress/Discuz/Typecho/Laravel5/ThinkPHP/Drupal/PHPcms/EmpireCMS/ECShop/ShopEx/Dedecms/PHPWind/Sablog/Emlog/MacCMS/PBootCMS/NiuShop/CRMEB/DBShop/EduSoho/SeaCMS等

### 8.9 站点同步 (class/panelModel/syncsiteModel.py)
- 站点数据同步
- 多服务器同步

### 8.10 流量统计 (class/panelModel/siteflowModel.py + sitelinkModel.py + projectModel/monitorModel.py)
- 站点流量统计(全站三日总览 + 近7天趋势)
- 站点排名TOP5
- 状态码分布(401/500/502/503)
- IP数量/UV/PV/流量/请求数
- 站点链接分析

### 8.11 日志切割 (class/scriptModel.py + class/crontabModel/ + mod/base/web_conf/logmanager.py)
- 日志自动切割(cron定时)
- 切割规则配置(按大小/时间)
- 切割后压缩
- 日志管理器(logmanager.py)

### 8.12 安全检查规则库 (class/safe_warning/) - 160+项检查
涵盖:
- SSH安全(12项): 端口/密钥/密码/协议/超时/日志级别等
- MySQL安全: 端口/密码/权限/备份
- Redis安全: 端口/密码
- FTP安全: 端口/密码/umask/Root登录
- Nginx安全: 版本泄露/恶意文件/MD5
- PHP安全: 禁用函数/错误显示/expose/URL include/后门检测
- Tomcat安全: 密码
- 面板安全: 端口/密码/路径/SSL/控制
- 系统安全: 空密码用户/UID重复/GID重复/SUID/内核参数
- 网络安全: IPv4/IPv6配置/TCP SYN Cookie/ICMP
- 文件安全: 风险文件/文件锁/回收站/目录权限
- 审计安全: 20+审计规则(登录/权限/挂载/网络/会话等)
- CVE漏洞: CVE-2019-5736/CVE-2021-4034/CVE-2022-2068/CVE-2022-25845/CVE-2023-0386
- Docker安全: API暴露/CVE检查
- 弱密码检测(config/weak_pass.txt + pass1000.txt)

### 8.13 Web服务器配置管理 (mod/base/web_conf/)
- Nginx配置管理(config_mgr.py)
- SSL管理(ssl.py + sslMod.py)
- DNS API(dns_api.py - 配置文件 config/dns_api.json)
- 域名工具(domain_tool.py)
- 访问控制(Nginx/Apache CORS - access_control/)
- 访问限制(access_restriction.py)
- IP限制(ip_restrict.py)
- 网络限速(limit_net.py)
- Nginx真实IP(nginx_realip.py)
- Nginx Gzip(nginx_gzip.py)
- Nginx缓存(nginx_cache.py)
- 防盗链(referer.py)
- 重定向(redirect.py)
- 目录保护(dir_tool.py)
- 日志管理(logmanager.py)
- 默认站点(default_site.py)
- 服务器扩展(server_extension.py)
- Nginx配置解析(pynginx/)

### 8.14 消息推送详细模块 (mod/base/push_mod/)
| 模块 | 功能 |
|------|------|
| site_push | 站点推送(状态变更/到期提醒) |
| database_push | 数据库推送(备份结果/异常) |
| ssl_push | SSL证书推送(到期提醒) |
| system_push | 系统推送(CPU/内存/磁盘告警) |
| monitor_push | 监控推送(服务状态变更) |
| ftp_push | FTP推送(异常登录) |
| load_push | 负载推送(高负载告警) |
| safe_mod_push | 安全模块推送(安全事件) |
| web_log_push | Web日志推送(实时日志) |
| rsync_push | Rsync推送(同步状态) |
| mod_node_push | 节点模块推送 |
| task_manager_push | 任务管理推送 |

### 8.15 SSH管理详细 (mod/project/ssh/)
- SSH基础管理(base.py)
- 通用管理(comMod.py)
- 安全管理(secureMod.py)
- 日志管理(journalctlMod.py)

### 8.16 Git集成 (mod/project/git/ + script/)
- Git部署(comMod.py)
- Git钩子脚本(scripts/)
- Git工具(mod/base/git_tool/)

### 8.17 配置文件体系 (config/)
| 配置文件 | 用途 |
|---------|------|
| dns_api.json | DNS API提供商配置 |
| php_versions.json | PHP版本列表(16个版本) |
| phplib.json | PHP扩展库 |
| safe_autofix.json | 安全自动修复配置 |
| safe_categories.json | 安全检查分类 |
| weak_pass.txt | 弱密码字典 |
| pass1000.txt | 常用密码字典 |
| domain_root.txt | 顶级域名列表 |
| crontab.json | 计划任务配置 |
| databases.json | 数据库配置 |
| docker_project_info.json | Docker项目信息 |
| menu.json | 菜单配置 |
| theme_validators.json | 主题验证器 |
| status_code.json | 状态码配置 |

---

## 九、完整迭代计划

### S0: 数据层基础设施 [所有S的前置]

> 地基决定上层建筑。S0 必须在所有其他迭代之前完成。

#### 0.1 数据库选型: SQLite (全新架构)

**选型结论: SQLite 是面板数据库的唯一正确答案。**

理由:
- **零依赖**: Python 内置 `import sqlite3`，不需要用户安装任何数据库服务
- **单文件**: 一个 .db 文件就是整个数据库，备份/迁移/恢复极其简单
- **性能足够**: 面板数据量小(千级)，SQLite 绰绰有余
- **WAL模式**: 支持并发读写，不会成为瓶颈
- **宝塔和MW都验证了可行性**: 两个成熟面板都用 SQLite 跑了多年

**但用法必须比宝塔和MW都好。**

#### 0.2 SQLAlchemy 2.0 引擎配置

```python
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "sqlite:///data/panel.db",
    connect_args={"check_same_thread": False},
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    echo=False,
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")          # WAL模式(并发读写)
    cursor.execute("PRAGMA synchronous=NORMAL")         # 平衡性能和安全
    cursor.execute("PRAGMA cache_size=-64000")          # 64MB缓存
    cursor.execute("PRAGMA mmap_size=268435456")        # 256MB内存映射
    cursor.execute("PRAGMA temp_store=MEMORY")          # 临时表存内存
    cursor.execute("PRAGMA busy_timeout=5000")          # 忙等待5秒
    cursor.execute("PRAGMA foreign_keys=ON")            # 外键约束
    cursor.close()
```

- [ ] SQLAlchemy 2.0 声明式模型(DeclarativeBase)
- [ ] WAL模式(PRAGMA journal_mode=WAL)
- [ ] 连接池(QueuePool, pool_size=5, max_overflow=10)
- [ ] PRAGMA优化(cache_size/mmap/synchronous/busy_timeout/foreign_keys)
- [ ] 事件监听(连接时自动设置PRAGMA)

#### 0.3 多库分离

```
为什么分离?
- 监控数据写入频繁(每秒)，和配置数据(偶尔写)混在一起会互相影响
- 安全数据(登录日志/WAF日志)增长快，需要独立清理策略
- 备份时可以只备份核心库(面板配置)，监控日志库可以不备份
- 单库文件不会太大，SQLite 性能更好

data/
├── panel.db        # 核心配置(站点/用户/配置/域名/备份记录)
├── security.db     # 安全相关(防火墙/登录日志/WAF规则/IP黑白名单)
├── monitor.db      # 监控数据(CPU/内存/网络/磁盘/进程/负载)
├── task.db         # 任务相关(计划任务/任务日志/任务状态)
└── log.db          # 操作日志(审计/操作记录/访问日志)
```

- [ ] panel.db: sites, domains, site_types, users, options, bindings, ssl_certificates, backups
- [ ] security.db: firewall, waf_rules, ssh_logs, login_records, ip_blacklist, ip_whitelist
- [ ] monitor.db: cpu_stats, memory_stats, network_stats, disk_stats, process_stats, load_avg
- [ ] task.db: crontab, tasks, task_logs, task_status
- [ ] log.db: operation_logs, access_logs, system_logs
- [ ] 数据库路由(表名→库文件自动映射)
- [ ] 每个库独立引擎实例

#### 0.4 Alembic 数据库迁移

```python
# 宝塔: 手动执行SQL，config/databases.json 里写建表语句
# MW: 手动执行 default.sql
# 新方案: Alembic 自动迁移，版本升级无感

# 迁移脚本示例:
def upgrade():
    op.create_table('ssl_certificates',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('domain', sa.String(255), nullable=False),
        sa.Column('cert_path', sa.String(500)),
        sa.Column('not_after', sa.DateTime),
        sa.Column('auto_renew', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
```

- [ ] Alembic 配置(每个库独立迁移目录)
- [ ] 自动生成迁移脚本(alembic revision --autogenerate)
- [ ] 自动执行迁移(面板启动时 alembic upgrade head)
- [ ] 迁移回滚(alembic downgrade)
- [ ] 迁移历史查看
- [ ] 迁移前自动备份数据库文件

#### 0.5 敏感字段加密

```python
# 宝塔: 依赖编译好的 PluginLoader .so 文件做加密
# MW: 无加密
# 新方案: Fernet 对称加密(Python标准库 cryptography)

from cryptography.fernet import Fernet

class EncryptedType(TypeDecorator):
    """SQLAlchemy自定义加密字段类型"""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return fernet.encrypt(value.encode()).decode()
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return fernet.decrypt(value.encode()).decode()
        return value

# 使用:
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    password = Column(EncryptedType(), nullable=False)      # 加密
    salt = Column(EncryptedType(), nullable=False)           # 加密
    email = Column(EncryptedType(), nullable=True)           # 加密
    api_key = Column(EncryptedType(), nullable=True)         # 加密
```

- [ ] Fernet加密实现(cryptography库)
- [ ] SQLAlchemy自定义字段类型(EncryptedType)
- [ ] 加密密钥管理(密钥文件 + 权限控制 600)
- [ ] 敏感字段自动加密(password/salt/email/api_key/token/mysql_root/ssh_key)
- [ ] 加密密钥轮换支持

#### 0.6 Repository Pattern

```python
# 宝塔: 直接在业务代码里写 SQL
# MW: SQLAlchemy 当查询构建器用
# 新方案: Repository Pattern，数据访问和业务逻辑分离

class SiteRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, site_id: int) -> Optional[Site]:
        return self.session.query(Site).filter(Site.id == site_id).first()

    def get_list(self, page=1, size=20, status=None, search=None):
        query = self.session.query(Site)
        if status is not None:
            query = query.filter(Site.status == status)
        if search:
            query = query.filter(Site.name.contains(search))
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return total, items

    def create(self, **kwargs) -> Site:
        site = Site(**kwargs)
        self.session.add(site)
        self.session.commit()
        return site
```

- [ ] Repository基类(通用CRUD)
- [ ] SiteRepository(站点)
- [ ] DomainRepository(域名)
- [ ] UserRepository(用户)
- [ ] FirewallRepository(防火墙)
- [ ] CrontabRepository(计划任务)
- [ ] BackupRepository(备份)
- [ ] OptionRepository(配置)
- [ ] MonitorRepository(监控)
- [ ] LogRepository(日志)

#### 0.7 SQLAlchemy 声明式模型(所有核心表)

```python
class Site(Base):
    __tablename__ = 'sites'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    path = Column(String(500), nullable=False)
    status = Column(Integer, default=1)  # 0=停止 1=运行
    project_type = Column(String(50), default='PHP')
    php_version = Column(String(20))
    port = Column(Integer, default=80)
    ps = Column(Text)
    type_id = Column(Integer, default=0)
    ssl = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    domains = relationship("Domain", back_populates="site", cascade="all, delete-orphan")
    backups = relationship("Backup", back_populates="site", cascade="all, delete-orphan")
```

- [ ] Site模型(站点)
- [ ] Domain模型(域名)
- [ ] SiteType模型(站点分类)
- [ ] User模型(用户)
- [ ] Option模型(面板配置)
- [ ] Binding模型(子目录绑定)
- [ ] SslCertificate模型(SSL证书)
- [ ] Backup模型(备份记录)
- [ ] Firewall模型(防火墙规则)
- [ ] Crontab模型(计划任务)
- [ ] Task模型(任务)
- [ ] TaskLog模型(任务日志)
- [ ] LoginRecord模型(登录记录)
- [ ] OperationLog模型(操作日志)
- [ ] CpuStat/MemoryStat/NetworkStat/DiskStat模型(监控数据)

#### 0.8 监控数据时序优化

```python
# 监控数据特殊性: 高频写入，按时间查询，定期清理

# 优化:
# 1. 按月分区(cpu_stats_202605, cpu_stats_202606)
# 2. 定时清理(保留30天)
# 3. 聚合查询(按小时/天聚合，减少数据量)
# 4. 批量插入(insertmany_values)
# 5. 定期 VACUUM 回收空间
```

- [ ] 监控数据按月分区(动态表名)
- [ ] 自动清理(保留30天，cron定时)
- [ ] 聚合查询(按小时/天聚合)
- [ ] 批量插入优化(insertmany_values)
- [ ] 定期VACUUM(回收空间)
- [ ] 监控数据导出(CSV/JSON)

#### 0.9 磁盘满降级

```python
# 宝塔: 磁盘满时自动切内存盘(/dev/shm) + 只读模式
# MW: 无此功能
# 新方案: 更优雅的降级策略
```

- [ ] 磁盘空间监控(定时检查)
- [ ] 磁盘满时自动切换到内存模式(/dev/shm)
- [ ] 只读模式(磁盘满时标记数据库只读，防止写入失败导致数据损坏)
- [ ] 磁盘满告警(通知管理员)
- [ ] 自动恢复(磁盘空间恢复后自动切回文件模式)

#### 0.10 数据库备份/恢复

- [ ] 文件级备份(直接复制 .db 文件)
- [ ] 在线备份(sqlite3 backup API，不锁库)
- [ ] 备份前自动checkpoint(WAL→主库)
- [ ] 备份压缩(zstd)
- [ ] 备份加密(Fernet)
- [ ] 自动备份(每日/每次变更前)
- [ ] 备份保留策略(保留最近N份)
- [ ] 恢复(替换 .db 文件 + 重启面板)
- [ ] 恢复前验证(检查数据库完整性)

---

### S1: 项目类型与语言运行时 [P0]

**目标:** 支撑6种项目类型，补齐语言运行时管理

#### 1.1 Python项目支持 [P0]
- [ ] Python多版本管理(pyvm工具)
- [ ] Python虚拟环境管理(pyenv)
- [ ] pip源配置(国内镜像源)
- [ ] 项目创建/删除/配置
- [ ] Gunicorn/uWSGI启动方式
- [ ] 项目端口/JVM参数配置
- [ ] 进程守护
- [ ] 项目日志管理
- [ ] 运行用户配置
- [ ] 前端: Python项目管理页面

#### 1.2 Go项目支持 [P0]
- [ ] Go版本管理(gvm工具)
- [ ] Go项目部署(二进制/源码编译)
- [ ] 项目端口配置
- [ ] 进程守护
- [ ] 项目PID管理
- [ ] 前端: Go项目管理页面

#### 1.3 HTML/静态网站 [P0]
- [ ] 静态文件托管
- [ ] 默认文档配置(index.html等)
- [ ] 前端: 静态网站创建选项

#### 1.4 反向代理项目 [P0]
- [ ] 反向代理配置生成(Nginx/Apache)
- [ ] 代理地址配置
- [ ] 负载均衡(多后端+权重)
- [ ] WebSocket支持
- [ ] 代理缓存配置
- [ ] 代理头配置
- [ ] 前端: 反向代理项目创建/管理页面

#### 1.5 PHP多版本管理 [P0]
- [ ] PHP版本安装/卸载(5.6/7.x/8.x)
- [ ] 站点PHP版本切换
- [ ] PHP-FPM配置管理
- [ ] PHP扩展管理
- [ ] PHP配置编辑(php.ini)
- [ ] 前端: PHP版本管理/切换UI

#### 1.6 JDK/Tomcat管理 [P1]
- [ ] JDK多版本管理(JDK8/JDK11)
- [ ] Tomcat多版本(Tomcat7/8/9)
- [ ] Spring Boot JAR部署增强
- [ ] JVM参数配置UI
- [ ] Tomcat虚拟主机管理
- [ ] 前端: Java项目管理增强

#### 1.7 Node.js版本管理 [P1]
- [ ] Node.js多版本安装/切换
- [ ] npm/pnpm/yarn支持
- [ ] 项目启动脚本配置UI
- [ ] PM2进程守护集成
- [ ] 前端: Node.js项目管理增强

---

### Phase 2: 安全体系 (2-3周) [P0]

**目标:** 构建完整的安全防护体系

#### 2.1 WAF防火墙 [P0]
- [ ] SQL注入检测(libinjection集成)
- [ ] XSS攻击检测
- [ ] 自定义WAF规则引擎
- [ ] Nginx WAF配置生成
- [ ] WAF日志查看
- [ ] WAF规则启用/禁用
- [ ] 前端: WAF管理页面

#### 2.2 SSH安全加固 [P0]
- [ ] SSH配置检查(12项规则)
  - MaxAuthTries检查
  - 协议版本检查
  - 空闲超时检查
  - LogLevel检查
  - 空密码检查
  - 默认端口检查
- [ ] SSH密钥管理(ed25519/ecdsa/rsa)
- [ ] SSH密钥生成/下载
- [ ] SSH登录记录(数据库)
- [ ] 异常登录告警(邮件)
- [ ] Root登录方式控制
- [ ] IP白名单访问控制
- [ ] 一键安全加固
- [ ] 前端: SSH安全管理页面

#### 2.3 安全扫描与评分 [P1]
- [ ] 系统漏洞扫描
- [ ] 安全评分系统(100分制)
- [ ] 扫描进度条
- [ ] 一键修复
- [ ] 修复历史记录
- [ ] 漏洞忽略管理
- [ ] 安全报告生成
- [ ] 前端: 安全扫描页面

#### 2.4 防御模块 [P1]
- [ ] 爬虫防御(搜索引擎识别)
- [ ] 扫描器拦截(30+工具UA)
- [ ] 脚本工具拦截
- [ ] UA长度过滤
- [ ] 局域网IP放行
- [ ] 前端: 防御配置页面

#### 2.5 后门扫描 [P1]
- [ ] PHP后门检测(20+规则)
- [ ] 一句话木马检测
- [ ] WebShell行为检测
- [ ] 危险文件操作检测
- [ ] 文件编码自动检测
- [ ] 前端: 后门扫描页面

#### 2.6 面板安全增强 [P1]
- [ ] 两步验证(TOTP)
- [ ] 面板SSL强制
- [ ] 安全入口路径
- [ ] 登录日志
- [ ] 异常登录告警
- [ ] 前端: 面板安全设置页面

---

### Phase 3: 备份与云存储 (2-3周) [P1]

**目标:** 完善备份体系，支持多种云存储

#### 3.1 备份核心功能 [P1]
- [ ] 网站备份(整站打包)
- [ ] 数据库备份(MySQL/PG/MongoDB/Redis)
- [ ] 增量备份
- [ ] 拆分备份(大文件分片)
- [ ] 备份计划(定时备份)
- [ ] 备份保留策略
- [ ] 备份日志
- [ ] 一键恢复
- [ ] 前端: 备份管理页面

#### 3.2 云存储支持 [P1]
- [ ] 阿里云OSS
- [ ] 腾讯云COS
- [ ] AWS S3
- [ ] 七牛云
- [ ] FTP备份
- [ ] Google Drive
- [ ] OneDrive
- [ ] 前端: 云存储配置页面

#### 3.3 SSL证书增强 [P2]
- [ ] 多DNS API提供商(15+)
  - 阿里云DNS
  - 腾讯云DNS
  - Cloudflare
  - AWS Route53
  - 华为云DNS
  - 火山引擎DNS
  - GoDaddy
  - DNSPod
  - 西部数码
- [ ] 自动续期(cron)
- [ ] 证书到期提醒(推送通知)
- [ ] SSL安全评分
- [ ] 证书管理器(SSLManger)
- [ ] 前端: SSL管理增强页面

---

### Phase 4: 数据库管理增强 (2-3周) [P1]

**目标:** 支持多种数据库，完善管理功能

#### 4.1 PostgreSQL支持 [P0]
- [ ] PostgreSQL安装/卸载
- [ ] 数据库CRUD
- [ ] 用户管理(精细权限)
- [ ] 数据导入/导出
- [ ] 备份/恢复
- [ ] 前端: PostgreSQL管理页面

#### 4.2 Redis管理 [P0]
- [ ] Redis安装/卸载
- [ ] 数据查看/编辑
- [ ] 配置管理(redis.conf)
- [ ] 持久化配置(RDB/AOF)
- [ ] 内存管理
- [ ] 慢日志查看
- [ ] Redis Cluster支持
- [ ] 前端: Redis管理页面

#### 4.3 MongoDB支持 [P1]
- [ ] MongoDB安装/卸载
- [ ] 数据库CRUD
- [ ] 用户管理
- [ ] 数据导入/导出(mongodump/mongoexport)
- [ ] 备份/恢复
- [ ] 前端: MongoDB管理页面

#### 4.4 SQLite支持 [P2]
- [ ] SQLite数据库管理
- [ ] 数据查看/编辑
- [ ] 前端: SQLite管理页面

#### 4.5 phpMyAdmin集成 [P1]
- [ ] phpMyAdmin安装/配置
- [ ] 面板内嵌(HTTP代理转发)
- [ ] PHP-FPM FastCGI集成
- [ ] 自动PHP版本匹配
- [ ] 前端: phpMyAdmin入口

#### 4.6 数据库增强功能 [P1]
- [ ] 数据库用户管理(精细权限)
- [ ] 数据库优化(表优化/修复/分析)
- [ ] 慢查询日志分析
- [ ] 数据库导入/导出增强
- [ ] 数据库同步
- [ ] 前端: 数据库管理增强页面

---

### Phase 5: 监控与运维 (2-3周) [P1]

**目标:** 完善监控体系，提升运维体验

#### 5.1 系统监控增强 [P1]
- [ ] 实时折线图(ECharts)
  - CPU使用率趋势
  - 内存使用率趋势
  - 网络流量趋势
  - 磁盘IO趋势
- [ ] 进程管理(查看/搜索/杀掉)
- [ ] 系统服务管理(启动/停止/重启/状态)
- [ ] 多网卡流量监控
- [ ] 前端: 监控增强页面

#### 5.2 日志分析系统 [P1]
- [ ] 站点访问日志分析
- [ ] 安全扫描(XSS/SQL/敏感信息)
- [ ] 状态码分布统计
- [ ] IP访问统计
- [ ] URL访问排行
- [ ] 蜘蛛爬取统计
- [ ] 日志分析结果保存
- [ ] 日志自动切割(cron)
- [ ] 日志推送(外部系统)
- [ ] 前端: 日志分析页面

#### 5.3 面板日报 [P2]
- [ ] 每日服务器状态汇总
- [ ] 应用使用统计
- [ ] 备份状态统计
- [ ] 安全事件统计
- [ ] 日报生成/查看
- [ ] 前端: 面板日报页面

#### 5.4 系统优化 [P2]
- [ ] Swap管理(创建/删除/调整)
- [ ] 进程管理增强
- [ ] 服务管理增强
- [ ] 系统清理(日志/缓存/临时文件)
- [ ] 端口扫描
- [ ] 前端: 系统优化页面

---

### Phase 6: Docker管理 (3-4周) [P2]

**目标:** 构建完整的Docker管理体系

#### 6.1 Docker核心功能 [P2]
- [ ] Docker安装/配置
- [ ] 容器管理(CRUD/日志/终端/监控)
- [ ] 镜像管理(拉取/构建/删除/导入导出)
- [ ] 网络管理(创建/删除/连接)
- [ ] 卷管理(创建/删除/清理)
- [ ] 前端: Docker管理页面

#### 6.2 Docker高级功能 [P2]
- [ ] Docker Compose编排
- [ ] 私有仓库管理
- [ ] 容器化项目管理
- [ ] 容器备份/恢复
- [ ] 容器安全配置
- [ ] 容器代理配置
- [ ] 容器组管理
- [ ] 前端: Docker高级管理页面

---

### Phase 7: FTP与邮件 (1-2周) [P2]

#### 7.1 FTP管理 [P2]
- [ ] PureFTPd安装/配置
- [ ] FTP用户管理(CRUD)
- [ ] FTP配额管理
- [ ] FTP日志查看
- [ ] FTP分类管理
- [ ] FTP推送配置
- [ ] 前端: FTP管理页面

#### 7.2 邮件服务 [P3]
- [ ] 邮件服务器配置
- [ ] 邮件接收/转发
- [ ] 批量邮件发送
- [ ] Roundcube WebMail集成
- [ ] 前端: 邮件管理页面

---

### Phase 8: 推送通知与用户 (2周) [P2]

#### 8.1 消息推送系统 [P2]
- [ ] 模块化推送架构
- [ ] 邮件推送
- [ ] Telegram推送
- [ ] 微信推送
- [ ] 企业微信推送
- [ ] 钉钉推送
- [ ] 飞书推送
- [ ] Bark推送(iOS)
- [ ] PushPlus推送
- [ ] Server酱推送
- [ ] 推送触发场景配置
- [ ] 前端: 推送配置页面

#### 8.2 用户管理增强 [P3]
- [ ] 多用户CRUD
- [ ] 权限隔离
- [ ] API密钥管理
- [ ] IP白名单
- [ ] 扫码登录(App)
- [ ] WebAuthn支持
- [ ] 操作审计日志
- [ ] 前端: 用户管理页面

---

### Phase 9: Web服务器扩展 (2周) [P3]

#### 9.1 Apache支持 [P2]
- [ ] Apache安装/配置
- [ ] 虚拟主机管理
- [ ] Apache状态监控
- [ ] Apache性能调优
- [ ] 前端: Apache管理页面

#### 9.2 OpenLiteSpeed支持 [P3]
- [ ] OpenLiteSpeed安装/配置
- [ ] 虚拟主机管理
- [ ] OLS状态监控
- [ ] 前端: OLS管理页面

#### 9.3 Caddy支持 [P3]
- [ ] Caddy安装/配置
- [ ] 站点管理
- [ ] 前端: Caddy管理页面

#### 9.4 Web服务器切换 [P3]
- [ ] Nginx/Apache/OLS/Caddy切换
- [ ] 配置自动迁移
- [ ] 前端: Web服务器切换UI

---

### Phase 10: 高级功能 (3-4周) [P3]

#### 10.1 插件系统增强 [P2]
- [ ] 插件商店
- [ ] 插件安装/卸载/更新
- [ ] 插件配置管理
- [ ] 插件依赖管理
- [ ] PHP插件兼容层(PanelPHP)
- [ ] 前端: 插件商店页面

#### 10.2 一键部署 [P2]
- [ ] WordPress一键部署
- [ ] Laravel一键部署
- [ ] Node.js应用一键部署
- [ ] Python应用一键部署
- [ ] 前端: 一键部署页面

#### 10.3 面板API [P2]
- [ ] RESTful API接口
- [ ] Token认证
- [ ] IP白名单限制
- [ ] API密钥管理
- [ ] App扫码登录
- [ ] 前端: API管理页面

#### 10.4 主题系统 [P3]
- [ ] 主题安装/卸载
- [ ] 主题配置管理
- [ ] 主题模板
- [ ] 前端: 主题管理页面

#### 10.5 流媒体支持 [P3]
- [ ] 视频流式传输
- [ ] HTTP Range请求
- [ ] 分片传输

#### 10.6 站点同步 [P3]
- [ ] 多服务器站点同步
- [ ] 同步日志
- [ ] 前端: 站点同步页面

#### 10.7 磁盘配额 [P3]
- [ ] 磁盘配额管理
- [ ] 用户配额设置
- [ ] 前端: 配额管理页面

---

## 十、时间估算

| 阶段 | 时间 | 内容 | 优先级 |
|------|------|------|--------|
| Phase 1 | 3-4周 | 项目类型(6种) + 语言运行时管理 | P0 |
| Phase 2 | 2-3周 | 安全体系(WAF/SSH/扫描/防御) | P0 |
| Phase 3 | 2-3周 | 备份云存储 + SSL增强 | P1 |
| Phase 4 | 2-3周 | 数据库增强(PG/Redis/Mongo/phpMyAdmin) | P1 |
| Phase 5 | 2-3周 | 监控增强 + 日志分析 + 面板日报 | P1 |
| Phase 6 | 3-4周 | Docker完整管理 | P2 |
| Phase 7 | 1-2周 | FTP + 邮件服务 | P2 |
| Phase 8 | 2周 | 推送通知 + 用户管理 | P2 |
| Phase 9 | 2周 | Web服务器扩展(Apache/OLS/Caddy) | P3 |
| Phase 10 | 3-4周 | 插件商店/一键部署/API/主题 | P3 |

**总计:** 约 22-30 周完成核心功能追赶

---

## 十一、快速见效路线图 (MVP - 4周)

如果资源有限，建议按以下顺序快速出效果:

### 第1周: Python + Go + 反代项目
- Python项目基础支持(单版本+Gunicorn)
- Go项目基础支持(二进制部署)
- 反向代理项目(基础配置)
- 静态网站支持

### 第2周: 安全基础
- SSH安全检查(6项核心规则)
- WAF基础规则(SQL注入/XSS)
- 两步验证(TOTP)
- 后门扫描

### 第3周: 备份 + 数据库
- 云存储支持(阿里OSS + 腾讯COS)
- 定时备份计划
- PostgreSQL基础支持
- Redis管理增强

### 第4周: 监控 + 日志
- 实时折线图(ECharts)
- 进程管理
- 日志分析基础
- 安全评分系统

这4周可以覆盖约40%的宝塔核心功能，显著提升竞争力。

---

## 十二、完美产品迭代计划 (终极版)

> 目标: 迭代的尽头是完美产品，不设时间上限，分步推进，每一步都做到极致。

### 迭代总纲

```
S1  → 项目类型与运行时        (7种项目 + 语言环境管理)
S2  → 网站管理核心功能        (伪静态/重定向/防盗链/目录保护/子目录/分类)
S3  → 安全体系               (WAF/SSH加固/安全扫描/防御/后门检测/安全评分)
S4  → 数据库全支持            (MySQL增强/PostgreSQL/Redis/MongoDB/phpMyAdmin)
S5  → 文件管理增强            (压缩解压/上传下载/回收站/搜索/编码转换)
S6  → 备份与云存储            (多云存储/增量备份/定时计划/备份恢复/整机备份)
S7  → 监控与日志              (实时图表/进程管理/日志分析/面板日报/流量统计)
S8  → Docker完整管理          (容器/镜像/网络/卷/Compose/仓库/GPU/应用商店)
S9  → SSL证书全能力           (15+DNS API/自动续期/到期提醒/证书管理器)
S10 → 计划任务增强            (多类型任务/备份集成/日志切割/任务诊断)
S11 → FTP与邮件服务           (PureFTPd/邮件服务器/Roundcube)
S12 → 通知推送体系            (12种推送渠道/模块化架构/触发场景配置)
S13 → 用户与权限              (多用户/角色权限/API密钥/审计日志)
S14 → Web服务器全支持         (Nginx/Apache/OLS/Caddy/切换/配置管理)
S15 → 系统优化与运维          (Swap/服务管理/系统清理/端口扫描/配额管理)
S16 → 伪静态规则库            (31套Nginx + 16套Apache模板)
S17 → AI智能助手              (14个诊断Agent/智能建站/AI终端)
S18 → 插件生态与一键部署      (插件商店/模板部署/应用市场)
S19 → 面板安全加固            (两步验证/TOTP/面板SSL/安全入口/防御模块)
S20 → 高级功能                (Git部署/站点同步/虚拟空间/Binlog备份/流媒体)
S21 → 主题与个性化            (主题系统/自定义配置/多语言)
S22 → API与开放平台           (RESTful API/App扫码/WebAuthn/第三方集成)
S23 → 运维自动化              (自动修复/智能告警/容量规划/性能基线)
S24 → 企业级功能              (多服务器管理/集群/CDN集成/灾备)
```

---

### S1: 项目类型与语言运行时

**目标:** 7种项目类型全覆盖，每种都有完整的语言运行时管理

#### 1.1 Python项目 (完整度: 100%)
- [ ] Python多版本管理(pyvm工具，参考 class/projectModel/btpyvm.py)
- [ ] Python虚拟环境管理(pyenv，参考 mod/project/python/pyenv_tool.py)
  - EnvironmentManager 环境管理器
  - PythonEnvironment 虚拟环境类
  - 虚拟环境创建/激活/删除/克隆
- [ ] pip源配置(7个国内镜像源，参考 pythonModel.py pip_source_dict)
  - 阿里云/清华/中科大/豆瓣/腾讯/华为/网易
  - 自定义pip源
- [ ] 项目启动方式
  - Gunicorn (workers/bind/timeout/config)
  - uWSGI (processes/threads/socket)
  - 自定义启动脚本
- [ ] WSGI/ASGI配置
- [ ] 项目端口/绑定地址配置
- [ ] 进程守护(systemd/supervisor/pm2)
- [ ] 项目日志管理(access.log/error.log/custom)
- [ ] 运行用户配置(www/root/自定义)
- [ ] 依赖管理(requirements.txt/pip install/pip freeze)
- [ ] 环境变量管理(.env文件)
- [ ] 前端: Python项目创建/管理/配置页面

#### 1.2 Go项目 (完整度: 100%)
- [ ] Go版本管理(gvm工具，参考 class/projectModel/btpygvm.py)
- [ ] Go项目部署
  - 二进制文件直接部署
  - 源码编译部署(go build)
  - 交叉编译支持
- [ ] 项目端口/绑定地址配置
- [ ] 进程守护(systemd/supervisor)
- [ ] PID管理(/var/tmp/gopids/)
- [ ] 项目日志管理(/www/wwwlogs/go/)
- [ ] 运行用户配置
- [ ] 环境变量管理(GOPATH/GOROOT/自定义)
- [ ] 前端: Go项目创建/管理/配置页面

#### 1.3 HTML/静态网站 (完整度: 100%)
- [ ] 静态文件托管
- [ ] 默认文档配置(index.html/index.htm/default.html等)
- [ ] 分类管理(type_id)
- [ ] 批量操作(启动/停止/删除)
- [ ] 搜索(名称/备注)
- [ ] 缓存配置(浏览器缓存/CDN)
- [ ] Gzip压缩配置
- [ ] 前端: 静态网站创建选项

#### 1.4 反向代理项目 (完整度: 100%)
- [ ] 反向代理配置生成(Nginx/Apache/OLS)
- [ ] 代理地址配置(单后端/多后端)
- [ ] 负载均衡算法(轮询/权重/ip_hash/least_conn)
- [ ] WebSocket代理支持
- [ ] 代理缓存配置(Nginx Cache)
- [ ] 代理头配置(X-Real-IP/X-Forwarded-For/X-Forwarded-Proto)
- [ ] SSL代理(HTTPS后端)
- [ ] 代理超时配置(proxy_connect_timeout/proxy_read_timeout)
- [ ] 代理缓冲配置(proxy_buffering/proxy_buffer_size)
- [ ] 代理日志
- [ ] 健康检查(后端存活检测)
- [ ] 前端: 反向代理项目创建/管理/配置页面

#### 1.5 PHP项目增强 (完整度: 100%)
- [ ] PHP版本矩阵(16个版本: 5.2~8.5，参考 config/php_versions.json)
- [ ] PHP版本安装/卸载/切换
- [ ] 每站点独立PHP版本
- [ ] PHP-FPM配置管理
  - 进程管理(dynamic/static/ondemand)
  - 最大子进程数/最小空闲/最大空闲
  - 请求超时/内存限制
  - 慢日志配置
- [ ] PHP扩展管理(安装/卸载/配置)
- [ ] PHP配置编辑(php.ini完整支持)
  - upload_max_filesize/post_max_size
  - max_execution_time/memory_limit
  - date.timezone/error_reporting
  - disable_functions/open_basedir
- [ ] PHP会话管理(session.save_handler/session.save_path)
- [ ] PHP OPcache配置
- [ ] 前端: PHP版本管理/配置编辑UI

#### 1.6 Java项目增强 (完整度: 100%)
- [ ] JDK多版本管理(JDK8/JDK11，参考 mod/project/java/)
- [ ] Tomcat多版本(Tomcat7/8/9)
- [ ] Spring Boot项目
  - JAR包部署
  - JVM参数配置(-Xms/-Xmx/-XX:MetaspaceSize等)
  - 项目端口配置
  - 进程守护(systemd/supervisor)
  - 启动脚本管理
  - PID管理
  - JMX监控(mod/project/java/jmxquery/)
- [ ] WAR包部署到Tomcat
- [ ] Tomcat虚拟主机管理(server.xml)
- [ ] 项目组管理(mod/project/java/groupMod.py)
- [ ] 项目更新(mod/project/java/project_update.py)
- [ ] 服务器代理(mod/project/java/server_proxy.py)
- [ ] Spring Boot配置解析(springboot_parser.py)
- [ ] 前端: Java项目管理增强

#### 1.7 Node.js项目增强 (完整度: 100%)
- [ ] Node.js多版本安装/切换
- [ ] 包管理器支持
  - npm (mod/project/nodejs/packageManage.py)
  - pnpm
  - yarn
- [ ] PM2进程守护完整集成 (mod/project/nodejs/pm2Mod.py)
  - 启动/停止/重启
  - 集群模式
  - 日志管理
  - 自动重启
- [ ] 项目启动脚本配置(start script)
- [ ] 项目端口配置
- [ ] npm执行日志
- [ ] 项目日志管理
- [ ] 运行用户配置
- [ ] 环境变量管理(NODE_ENV/PORT/自定义)
- [ ] 通用管理(mod/project/nodejs/generalMod.py)
- [ ] 前端: Node.js项目管理增强

---

### S2: 网站管理核心功能

**目标:** 补齐宝塔网站管理的所有细节功能

- [ ] 伪静态规则管理
  - 规则选择器(31套Nginx + 16套Apache预设模板)
  - 支持CMS: WordPress/Discuz/Typecho/Laravel5/ThinkPHP/Drupal/PHPcms/EmpireCMS/ECShop/ShopEx/Dedecms/PHPWind/Sablog/Emlog/MacCMS/PBootCMS/NiuShop/CRMEB/DBShop/EduSoho/SeaCMS等
  - 自定义规则编辑
  - 规则导入/导出
  - 规则测试(语法检查)
- [ ] URL重定向 (参考 class/panelRedirect.py + mod/base/web_conf/redirect.py)
  - 301永久重定向
  - 302临时重定向
  - 域名重定向
  - 路径重定向
  - 正则匹配重定向
  - 重定向规则管理(CRUD)
  - 重定向日志
- [ ] 防盗链 (参考 mod/base/web_conf/referer.py)
  - 允许的来源域名
  - 防盗链文件类型
  - 防盗链返回404/重定向
  - URL加密防盗链
- [ ] 目录密码保护 (参考 class/site_dir_auth.py)
  - Apache htpasswd格式
  - Nginx auth_basic
  - APR1-MD5加密
  - 多用户支持
  - 目录选择器
- [ ] 子目录绑定
  - 子目录独立域名绑定
  - 子目录独立SSL
  - 子目录独立配置
- [ ] 多域名管理
  - 批量添加域名
  - 域名通配符(*.example.com)
  - 域名端口管理
  - IPv6支持
- [ ] PHP版本切换(多版本共存)
- [ ] 网站日志查看
  - 访问日志(access.log)
  - 错误日志(error.log)
  - 日志实时刷新
  - 日志下载
  - 日志分析(IP统计/URL排行/状态码分布)
- [ ] 自定义错误页面
  - 404/500/502/503错误页
  - 自定义HTML模板
  - 错误页模板管理
- [ ] 网站备份/恢复(单站点级别)
- [ ] 网站分类管理
  - 分类CRUD
  - 按分类筛选
  - 分类统计
- [ ] 批量操作
  - 批量启动/停止/删除
  - 批量备份
  - 批量SSL部署
- [ ] 网站配置导入/导出
- [ ] 网站流量统计 (参考 projectModel/monitorModel.py)
  - 全站三日总览
  - 近7天趋势
  - 站点排名TOP5
  - 状态码分布(401/500/502/503)
  - IP/UV/PV/流量/请求数
- [ ] CORS跨域管理 (参考 mod/base/web_conf/access_control/)
  - Nginx CORS配置
  - Apache CORS配置
  - 允许的来源/方法/头
- [ ] 网络限速 (参考 mod/base/web_conf/limit_net.py)
  - 连接数限制
  - 带宽限制
  - 请求速率限制
- [ ] 访问限制 (参考 mod/base/web_conf/access_restriction.py)
  - IP白名单/黑名单
  - URI访问控制
  - User-Agent过滤
- [ ] 真实IP获取 (参考 mod/base/web_conf/nginx_realip.py)
  - CDN真实IP配置
  - 代理真实IP配置
- [ ] Nginx缓存配置 (参考 mod/base/web_conf/nginx_cache.py)
  - 缓存路径/大小
  - 缓存有效期
  - 缓存清理
- [ ] Nginx Gzip配置 (参考 mod/base/web_conf/nginx_gzip.py)
  - 压缩级别
  - 压缩文件类型
  - 最小压缩大小
- [ ] 默认站点配置 (参考 mod/base/web_conf/default_site.py)
  - 默认站点设置
  - 未绑定域名处理
- [ ] SSL管理 (参考 mod/base/web_conf/ssl.py + sslMod.py)
  - SSL部署/卸载
  - SSL强制HTTPS
  - HSTS配置
  - OCSP Stapling
  - SSL协议版本控制
  - SSL加密套件配置

---

### S3: 安全体系 (完整度: 100%)

**目标:** 构建宝塔同级别的完整安全防护体系

#### 3.1 WAF防火墙 (参考 class/panelWaf.py)
- [ ] SQL注入检测(libinjection库集成)
- [ ] XSS攻击检测(libinjection库集成)
- [ ] 自定义WAF规则引擎
  - 规则CRUD
  - 规则启用/禁用
  - 规则优先级
  - 规则测试
- [ ] Nginx WAF配置生成
- [ ] Apache ModSecurity配置
- [ ] WAF日志查看
- [ ] WAF统计(拦截次数/类型分布)
- [ ] WAF白名单(URL/IP白名单)
- [ ] 前端: WAF管理页面

#### 3.2 SSH安全加固 (参考 class/ssh_security.py + mod/project/ssh/)
- [ ] SSH配置检查(12项规则)
  1. MaxAuthTries 设置为3-6
  2. 强制使用V2安全协议
  3. 空闲超时退出(ClientAliveInterval 300-900)
  4. SSH LogLevel设置为INFO
  5. 禁止空密码登录(PermitEmptyPasswords no)
  6. 修改默认端口22(建议6000-65535)
  7. SSH密钥类型管理(ed25519/ecdsa/rsa/dsa)
  8. SSH密钥生成/下载
  9. SSH登录记录(数据库存储)
  10. 异常登录告警(邮件通知)
  11. Root登录方式控制(yes/no/without-password/forced-commands-only)
  12. IP白名单访问控制
- [ ] SSH配置编辑(/etc/ssh/sshd_config)
- [ ] SSH登录记录查看
- [ ] SSH会话录制回放
- [ ] 一键安全加固(批量修复)
- [ ] 前端: SSH安全管理页面

#### 3.3 安全扫描与评分 (参考 class/panelWarning.py + class/safe_warning/)
- [ ] 系统漏洞扫描(160+检查规则)
  - SSH安全(12项)
  - MySQL安全(端口/密码/权限/备份)
  - Redis安全(端口/密码)
  - FTP安全(端口/密码/umask/Root登录)
  - Nginx安全(版本泄露/恶意文件/MD5)
  - PHP安全(禁用函数/错误显示/expose/URL include/后门)
  - Tomcat安全(密码)
  - 面板安全(端口/密码/路径/SSL/控制)
  - 系统安全(空密码用户/UID重复/GID重复/SUID/内核参数)
  - 网络安全(IPv4/IPv6/TCP SYN Cookie/ICMP)
  - 文件安全(风险文件/文件锁/回收站/目录权限)
  - 审计安全(20+审计规则)
  - CVE漏洞(CVE-2019-5736/CVE-2021-4034/CVE-2022-2068/CVE-2022-25845/CVE-2023-0386)
  - Docker安全(API暴露/CVE检查)
- [ ] 安全评分系统(100分制，动态计算)
- [ ] 扫描进度条
- [ ] 一键修复(safe_autofix.json)
- [ ] 修复历史记录
- [ ] 漏洞忽略管理
- [ ] 安全报告生成/导出
- [ ] 弱密码检测(config/weak_pass.txt + pass1000.txt)
- [ ] 前端: 安全扫描页面

#### 3.4 防御模块 (参考 class/panelDefense.py)
- [ ] 爬虫防御(搜索引擎爬虫识别)
  - 检查UA是否包含bot/spider
  - 放行搜索引擎爬虫
  - 拒绝伪装爬虫
- [ ] 扫描器拦截(30+工具UA)
  - wpscan/sqlmap/nmap/hydra/nikto等
  - 自定义UA黑名单
- [ ] 脚本工具拦截
  - curl/wget/python/php/requests/urllib等
  - 自定义UA黑名单
- [ ] UA长度过滤(24-350字符)
- [ ] 局域网IP放行
- [ ] 前端: 防御配置页面

#### 3.5 后门扫描 (参考 class/panelSafe.py)
- [ ] PHP后门检测(20+规则)
  - 一句话木马(eval/assert + $_POST/$_GET)
  - WebShell行为(shell_exec/system/popen/exec)
  - 危险文件操作(fopen/fwrite/file_put_contents + $_POST)
  - 危险上传漏洞($_FILES)
  - 危险引用(include/require + $_POST)
  - base64解码执行
  - preg_replace /e修饰符
- [ ] 文件编码自动检测(chardet)
- [ ] 扫描结果保存
- [ ] 批量删除/隔离
- [ ] 定时扫描计划
- [ ] 前端: 后门扫描页面

#### 3.6 面板安全增强
- [ ] 两步验证(TOTP - Google Authenticator)
- [ ] 面板SSL强制(自签名/Let's Encrypt)
- [ ] 安全入口路径(自定义面板访问路径)
- [ ] Basic Auth认证
- [ ] 登录日志(数据库记录)
- [ ] 异常登录告警(邮件/推送)
- [ ] IP白名单访问控制
- [ ] 登录验证码(图片/算术)
- [ ] 登录失败锁定(次数/时间)
- [ ] 面板端口修改
- [ ] 面板域名绑定
- [ ] 前端: 面板安全设置页面

---

### S4: 数据库全支持

#### 4.1 MySQL增强
- [ ] MySQL用户管理(精细权限 - 14种权限类型)
- [ ] 数据库优化(表优化/修复/分析/检查)
- [ ] 慢查询日志分析
- [ ] 数据库导入(SQL文件/CSV)
- [ ] 数据库导出(SQL/CSV/JSON)
- [ ] 批量操作(批量删除/批量优化)
- [ ] MySQL配置编辑(my.cnf)
- [ ] MySQL状态监控(连接数/QPS/缓存命中率)
- [ ] MySQL Binlog管理(查看/解析/清理)
- [ ] MySQL Binlog增量备份 (mod/project/mysql_binlog_backup/)
  - 增量备份管理器(backup_manager.py)
  - 清理管理器(cleanup_manager.py)
  - 配置管理器(config_manager.py)
  - 恢复管理器(restore_manager.py)
  - 任务调度器(task_scheduler.py)
- [ ] phpMyAdmin集成 (class/panelPmd.py + class/panelHttpProxy.py)
  - 面板内嵌(HTTP代理转发)
  - PHP-FPM FastCGI集成
  - 自动PHP版本匹配
- [ ] 前端: MySQL管理增强页面

#### 4.2 PostgreSQL支持 (参考 mod/base/database_tool/pgsql.py)
- [ ] PostgreSQL安装/卸载
- [ ] 数据库CRUD
- [ ] 用户管理(精细权限)
- [ ] 数据导入(pg_dump/psql)
- [ ] 数据导出(pg_dump)
- [ ] 备份/恢复
- [ ] PostgreSQL配置编辑(postgresql.conf)
- [ ] PostgreSQL状态监控
- [ ] 前端: PostgreSQL管理页面

#### 4.3 Redis管理增强 (参考 mod/base/database_tool/ - Redis相关)
- [ ] Redis安装/卸载
- [ ] 数据查看/编辑(字符串/哈希/列表/集合/有序集合)
- [ ] 配置管理(redis.conf)
- [ ] 持久化配置(RDB/AOF)
- [ ] 内存管理(maxmemory/maxmemory-policy)
- [ ] 慢日志查看
- [ ] Redis Cluster支持
- [ ] Redis Sentinel支持
- [ ] Redis状态监控(内存/连接/命中率/OPS)
- [ ] 前端: Redis管理页面

#### 4.4 MongoDB支持 (参考 mod/base/database_tool/mongodb.py)
- [ ] MongoDB安装/卸载
- [ ] 数据库CRUD
- [ ] 集合管理
- [ ] 文档CRUD
- [ ] 用户管理(角色权限)
- [ ] 数据导入(mongoimport)
- [ ] 数据导出(mongoexport/mongodump)
- [ ] 备份/恢复
- [ ] MongoDB配置编辑(mongod.conf)
- [ ] MongoDB状态监控
- [ ] 前端: MongoDB管理页面

#### 4.5 SQLite支持
- [ ] SQLite数据库管理
- [ ] 数据查看/编辑
- [ ] SQL执行
- [ ] 表结构管理
- [ ] 前端: SQLite管理页面

#### 4.6 SQL Server支持 (参考 mod/base/database_tool/sql_server.py)
- [ ] SQL Server连接管理
- [ ] 数据库CRUD
- [ ] 用户管理
- [ ] 前端: SQL Server管理页面

---

### S5: 文件管理增强

- [ ] 文件压缩/解压 (参考 class/filesModel/)
  - zip压缩/解压 (zipModel.py)
  - tar.gz压缩/解压 (gzModel.py)
  - rar解压 (rarModel.py)
  - 7z压缩/解压
  - 压缩级别选择
  - 密码保护压缩
- [ ] 文件上传 (uploadModel.py)
  - 单文件/多文件上传
  - 大文件分片上传
  - 拖拽上传
  - URL上传(远程下载)
- [ ] 文件下载 (downModel.py)
  - 单文件下载
  - 批量下载(打包)
  - 分享链接下载
  - 限速下载
- [ ] 文件搜索 (searchModel.py)
  - 文件名搜索
  - 内容搜索(正则支持)
  - 文件类型过滤
  - 文件大小过滤
  - 修改时间过滤
  - 搜索结果高亮
- [ ] 回收站
  - 删除文件进入回收站
  - 回收站文件恢复
  - 回收站清空
  - 自动清理策略
- [ ] 文件编码转换 (conversionModel.py)
  - 编码检测(chardet)
  - 编码转换(UTF-8/GBK/GB2312/BIG5等)
- [ ] 文件大小分析 (sizeModel.py)
  - 目录大小统计
  - 大文件排行
  - 磁盘占用分析
- [ ] 文件操作日志 (logsModel.py)
  - 操作记录(创建/修改/删除/移动/复制)
  - 操作用户
  - 操作时间
- [ ] 批量权限/所有者修改
- [ ] 软链接管理(创建/查看/删除)
- [ ] 文件校验(MD5/SHA1/SHA256)
- [ ] 终端打开当前目录
- [ ] 文件预览(图片/视频/音频/PDF/Markdown)
- [ ] 前端: 文件管理增强页面

---

### S6: 备份与云存储

#### 6.1 备份核心
- [ ] 网站备份(整站打包 - 文件+配置+数据库)
- [ ] 数据库备份(MySQL/PG/MongoDB/Redis)
- [ ] 增量备份(仅备份变更文件)
- [ ] 拆分备份(大文件5GB分片)
- [ ] 整机备份 (class/panelModel/whole_machine_backupModel.py)
- [ ] Docker Compose备份
- [ ] 备份版本管理(mod/base/backup_tool/versions_tool.py)
- [ ] 备份加密(AES加密)
- [ ] 备份压缩(gzip/zstd)

#### 6.2 云存储支持
- [ ] 阿里云OSS
- [ ] 腾讯云COS
- [ ] AWS S3
- [ ] 七牛云
- [ ] FTP备份
- [ ] Google Drive
- [ ] OneDrive
- [ ] Rsync同步
- [ ] 自定义S3兼容存储(MinIO等)
- [ ] 云存储连接测试
- [ ] 云存储空间监控

#### 6.3 备份恢复 (mod/project/backup_restore/)
- [ ] 备份管理器(backup_manager.py)
- [ ] 恢复管理器(restore_manager.py)
- [ ] 配置管理器(config_manager.py)
- [ ] 数据管理器(data_manager.py)
- [ ] SSH管理器(ssh_manager.py - 跨服务器恢复)
- [ ] 一键恢复(网站/数据库/全站)
- [ ] 恢复前预览(查看备份内容)
- [ ] 恢复日志

#### 6.4 备份计划
- [ ] 定时备份(cron表达式)
- [ ] 备份保留策略(保留最近N份/保留N天)
- [ ] 备份通知(成功/失败 - 推送到消息系统)
- [ ] 备份日志
- [ ] 备份统计(备份次数/大小/成功率)

---

### S7: 监控与日志

#### 7.1 系统监控增强
- [ ] 实时折线图(ECharts)
  - CPU使用率趋势(24h/7d/30d)
  - 内存使用率趋势
  - 网络流量趋势(上行/下行)
  - 磁盘IO趋势(读/写)
  - 磁盘使用率趋势
  - 负载趋势(1/5/15分钟)
- [ ] 进程管理 (mod/base/process/)
  - 进程列表(psutil)
  - 进程搜索(名称/PID/用户)
  - 进程详情(CPU/内存/打开文件/网络连接)
  - 进程终止/重启
  - 进程树查看
  - 进程资源限制(cgroups)
- [ ] 系统服务管理
  - 服务列表(systemctl)
  - 服务启动/停止/重启
  - 服务状态查看
  - 服务开机自启管理
  - 服务日志查看(journalctl)
- [ ] 多网卡流量监控
- [ ] 磁盘IO监控(iostat)
- [ ] 系统信息(OS/内核/架构/运行时间)

#### 7.2 日志分析系统 (参考 class/log_analysis.py + mod/base/web_conf/logmanager.py)
- [ ] 站点访问日志分析
  - IP访问统计(TOP N)
  - URL访问排行
  - 状态码分布(200/301/302/404/500/502/503)
  - 蜘蛛爬取统计(百度/Google/Bing/搜狗/360)
  - 访问时段分布
  - 流量统计
- [ ] 安全扫描(在日志中检测)
  - XSS攻击检测
  - SQL注入检测
  - 敏感信息检测
  - PHP代码执行检测
- [ ] 日志自动切割(cron定时)
  - 按大小切割
  - 按时间切割(日/周/月)
  - 切割后压缩(gzip)
  - 保留份数
- [ ] 日志推送(外部系统)
- [ ] 日志分析结果保存/查看

#### 7.3 面板日报 (参考 class/panelDaily.py)
- [ ] 每日服务器状态汇总
  - CPU/内存/磁盘/网络使用率
  - 系统负载
  - 运行时间
- [ ] 应用使用统计
  - 网站访问量
  - 数据库连接数
  - FTP传输量
- [ ] 备份状态统计
  - 备份成功/失败数
  - 备份大小
- [ ] 安全事件统计
  - WAF拦截数
  - SSH异常登录
  - 端口扫描
- [ ] 日报生成/查看/导出
- [ ] 日报邮件推送

#### 7.4 站点流量统计 (参考 projectModel/monitorModel.py)
- [ ] 全站三日总览
- [ ] 近7天趋势
- [ ] 站点排名TOP5
- [ ] 状态码分布(401/500/502/503)
- [ ] IP数量/UV/PV/流量/请求数
- [ ] 同比/环比分析

---

### S8: Docker完整管理

#### 8.1 Docker核心 (class/btdockerModel/ + mod/project/docker/ + class/projectModel/bt_docker/)
- [ ] Docker安装/配置/卸载
- [ ] 容器管理
  - 容器CRUD(创建/启动/停止/重启/删除/暂停)
  - 容器日志(实时/历史)
  - 容器终端(exec交互)
  - 容器监控(CPU/内存/网络/IO)
  - 容器资源限制(CPU/内存限制)
  - 容器环境变量
  - 容器端口映射
  - 容器卷挂载
- [ ] 镜像管理
  - 镜像拉取/构建/删除
  - 镜像导入/导出(save/load)
  - 镜像标签管理
  - Dockerfile编辑
  - 镜像构建历史
- [ ] 网络管理
  - 网络创建/删除/连接
  - 网络类型(bridge/host/overlay/macvlan)
  - 网络配置(IP范围/网关/子网)
- [ ] 卷管理
  - 卷创建/删除/清理
  - 卷类型(local/nfs/自定义驱动)
  - 卷使用情况

#### 8.2 Docker高级
- [ ] Docker Compose (mod/project/docker/composeMod.py + compose_utils.py)
  - Compose文件编辑
  - Compose启动/停止/重启
  - Compose日志
  - Compose配置验证
- [ ] 私有仓库管理 (dk_registry.py)
  - 仓库添加/删除
  - 仓库认证
  - 镜像推送/拉取
- [ ] 容器化项目管理 (dk_project.py)
  - 项目创建/管理
  - 项目配置
  - 项目部署
- [ ] 容器备份/恢复 (btdockerModel/backupModel.py)
- [ ] 容器安全配置 (btdockerModel/securityModel.py)
- [ ] 容器代理配置 (mod/project/docker/proxy/)
- [ ] 容器组管理 (btdockerModel/dkgroupModel.py)
- [ ] 容器监控 (dk_monitor.py + btdockerModel/monitorModel.py)

#### 8.3 Docker应用商店 (mod/project/docker/app/)
- [ ] 应用管理(appManageMod.py)
- [ ] 应用商店(apphub - apphubManage.py)
- [ ] 应用镜像检测(mirrorDetector.py)
- [ ] GPU支持 (mod/project/docker/app/gpu/)
  - NVIDIA GPU支持(nvidia.py)
  - AMD GPU支持(amd.py)
  - GPU类型检测(type.py)
- [ ] AI应用部署 (mod/project/docker/app/sub_app/)
  - Ollama本地大模型部署(ollamaMod.py)
  - AI模型管理

#### 8.4 Docker运行时 (mod/project/docker/runtime/)
- [ ] 运行时管理(runtimeManage.py)
- [ ] 运行时切换(containerd/docker)

#### 8.5 Docker站点 (mod/project/docker/sites/)
- [ ] Docker站点管理(sitesManage.py)
- [ ] Docker站点SSL(sslManage.py)

---

### S9: SSL证书全能力

- [ ] 证书申请(Let's Encrypt/ZeroSSL/自签名)
- [ ] DNS API提供商(15+，参考 config/dns_api.json + class/sslModel/)
  - CloudFlare
  - 宝塔DNS云解析
  - DnsPod
  - 阿里云DNS
  - CloudXns
  - 手动解析
  - 腾讯云DNS(tencentcloudModel.py)
  - AWS Route53(awsModel.py)
  - 华为云DNS(huaweicloudModel.py)
  - 火山引擎DNS(volcenginecloudModel.py)
  - GoDaddy(godaddyModel.py)
  - 西部数码(westModel.py)
  - 自动部署(autodeployModel.py)
- [ ] 自动续期(cron定时检查)
- [ ] 证书到期提醒(邮件/推送)
- [ ] 通配符证书(*.example.com)
- [ ] 多域名证书(SAN证书)
- [ ] SSL安全评分
- [ ] 证书管理器(SSLManger - class/ssl_manage.py)
  - 证书列表/详情
  - 证书部署/卸载
  - 证书下载
  - 证书链验证
- [ ] 商业证书部署(上传证书文件)
- [ ] 面板SSL管理
- [ ] 前端: SSL管理页面

---

### S10: 计划任务增强

- [ ] 多任务类型
  - Shell脚本执行
  - 网站备份(单站点/全站)
  - 数据库备份(单库/全库)
  - 日志切割(站点日志/系统日志)
  - URL请求(curl)
  - 文件清理(过期文件删除)
  - FTP同步备份
  - Rsync同步
  - Nginx/Apache日志切割
  - MySQL Binlog清理
- [ ] 任务调度 (class/crontabModel/)
  - 脚本任务(scriptModel.py)
  - 触发器任务(triggerModel.py)
- [ ] 任务执行日志
  - 执行时间
  - 执行结果(成功/失败)
  - 执行输出
  - 错误信息
- [ ] 任务状态监控
  - 运行中/已完成/失败
  - 任务耗时
  - 下次执行时间
- [ ] 错误通知(失败时推送)
- [ ] 文件锁(防并发执行)
- [ ] 任务超时设置
- [ ] 任务依赖(前置任务)
- [ ] 前端: 计划任务增强页面

---

### S11: FTP与邮件服务

#### 11.1 FTP管理
- [ ] PureFTPd安装/配置/卸载
- [ ] FTP用户管理(CRUD)
  - 用户名/密码
  - 主目录
  - 权限(读/写/删除)
  - 速度限制
  - IP限制
- [ ] FTP配额管理(磁盘配额)
- [ ] FTP日志查看
- [ ] FTP分类管理
- [ ] FTP推送配置
- [ ] FTP状态监控(在线用户/传输速度)
- [ ] 前端: FTP管理页面

#### 11.2 邮件服务 (参考 class/mailModel/)
- [ ] 邮件服务器配置
- [ ] 邮件接收(mainModel.py)
- [ ] 邮件转发(fowardModel.py)
- [ ] 批量邮件发送(bulkModel.py)
- [ ] 邮件管理(manageModel.py)
- [ ] 多IP邮件管理(multipleipModel.py)
- [ ] Roundcube WebMail集成
- [ ] 邮件日志
- [ ] 前端: 邮件管理页面

---

### S12: 通知推送体系

#### 12.1 推送渠道 (参考 mod/base/push_mod/ + class/panel_msg/)
- [ ] 邮件推送(mail_msg.py)
- [ ] Telegram推送
- [ ] 微信推送(weixin_msg.py)
- [ ] 企业微信推送(wx_account_msg.py)
- [ ] 钉钉推送(dingding_msg.py)
- [ ] 飞书推送(feishu_msg.py)
- [ ] 短信推送(sms_msg.py)
- [ ] Bark推送(iOS)
- [ ] PushPlus推送
- [ ] Server酱推送
- [ ] WebHook推送(web_hook_msg.py)
- [ ] 自定义HTTP推送

#### 12.2 推送触发场景 (mod/base/push_mod/)
- [ ] 站点推送(site_push.py) - 状态变更/到期提醒
- [ ] 数据库推送(database_push.py) - 备份结果/异常
- [ ] SSL推送(ssl_push.py) - 证书到期提醒
- [ ] 系统推送(system_push.py) - CPU/内存/磁盘告警
- [ ] 监控推送(monitor_push.py) - 服务状态变更
- [ ] FTP推送(ftp_push.py) - 异常登录
- [ ] 负载推送(load_push.py) - 高负载告警
- [ ] 安全推送(safe_mod_push.py) - 安全事件
- [ ] 日志推送(web_log_push.py) - 实时日志
- [ ] Rsync推送(rsync_push.py) - 同步状态
- [ ] 任务推送(task_manager_push.py) - 任务状态
- [ ] 节点推送(mod_node_push.py) - 节点状态

#### 12.3 推送管理
- [ ] 推送渠道配置(CRUD)
- [ ] 推送测试(发送测试消息)
- [ ] 推送日志(发送记录)
- [ ] 推送频率限制
- [ ] 推送模板管理
- [ ] 前端: 推送配置页面

---

### S13: 用户与权限

- [ ] 多用户CRUD (参考 class/users.py)
- [ ] 角色权限管理
  - 管理员/普通用户/只读用户
  - 细粒度权限(网站/数据库/文件/FTP/计划任务等)
- [ ] API密钥管理 (参考 class/panelApi.py)
  - Token生成/吊销
  - IP白名单限制
  - API使用统计
- [ ] 扫码登录(App扫码 - login_for_app)
- [ ] WebAuthn支持 (class/webauthn/)
- [ ] 操作审计日志 (mod/project/activity/activityMod.py)
  - 操作类型/操作对象
  - 操作用户/操作时间
  - 操作IP/操作结果
  - 审计日志查询/导出
- [ ] 登录日志
  - 登录时间/登录IP
  - 登录设备/登录结果
  - 异常登录检测
- [ ] 前端: 用户管理页面

---

### S14: Web服务器全支持

#### 14.1 Nginx管理
- [ ] Nginx安装/配置/卸载
- [ ] Nginx状态监控(class/panelSite.py GetNginxStatus)
  - 活跃连接数/请求数
  - 读/写/等待连接
  - Worker进程数
  - Worker内存使用
  - CPU使用率
- [ ] Nginx配置编辑(nginx.conf)
- [ ] Nginx性能调优
  - worker_processes/worker_connections
  - keepalive_timeout
  - gzip配置
  - client_max_body_size
  - server_names_hash_bucket_size
- [ ] Nginx配置语法检查(nginx -t)
- [ ] Nginx配置备份/恢复
- [ ] Nginx配置模板 (class/panelModel/nginxtemplateModel.py)

#### 14.2 Apache管理
- [ ] Apache安装/配置/卸载
- [ ] Apache状态监控(class/apache.py GetApacheStatus)
  - 活跃连接数
  - 空闲Worker
  - CPU使用率
  - 请求速率
  - 启动时间
- [ ] Apache配置编辑(httpd.conf)
- [ ] Apache性能调优(MPM配置)
- [ ] Apache模块管理

#### 14.3 OpenLiteSpeed管理
- [ ] OLS安装/配置/卸载
- [ ] OLS状态监控
- [ ] OLS配置编辑(class/ols.py)
  - Gzip压缩级别
  - 最大连接数
  - 最大SSL连接数
  - 连接超时
  - 最大KeepAlive请求数
- [ ] OLS静态缓存配置
- [ ] OLS虚拟主机管理

#### 14.4 Caddy管理
- [ ] Caddy安装/配置/卸载
- [ ] Caddy配置编辑(Caddyfile)
- [ ] Caddy状态监控

#### 14.5 Web服务器切换
- [ ] Nginx ↔ Apache ↔ OLS ↔ Caddy 切换
- [ ] 配置自动迁移
- [ ] 切换前备份
- [ ] 切换后验证
- [ ] 前端: Web服务器切换UI

---

### S15: 系统优化与运维

- [ ] Swap管理
  - Swap创建/删除/调整大小
  - Swap使用监控
  - swappiness配置
- [ ] 进程管理增强 (mod/base/process/)
  - 进程资源限制(cgroups)
  - 进程优先级调整(nice/renice)
  - 进程IO优先级调整(ionice)
- [ ] 服务管理增强
  - 服务依赖管理
  - 服务重启策略
  - 服务资源限制
- [ ] 系统清理
  - 日志清理(过期日志删除)
  - 缓存清理(系统缓存/应用缓存)
  - 临时文件清理
  - 包管理器缓存清理(yum clean/apt clean)
  - Docker清理(未使用镜像/容器/卷/网络)
- [ ] 端口扫描 (class/panelPort.py)
  - 全端口扫描(1-65535)
  - 进程关联(lsof)
  - 端口状态(监听/已连接)
- [ ] 磁盘配额管理 (projectModel/quotaModel.py)
  - 用户配额设置
  - 配额监控
  - 配额告警
- [ ] 系统信息面板
  - OS版本/内核版本
  - CPU型号/核心数
  - 内存大小/交换分区
  - 磁盘信息(分区/挂载点)
  - 网卡信息(IP/MAC/速率)
  - 系统运行时间
- [ ] 前端: 系统优化页面

---

### S16: 伪静态规则库

- [ ] Nginx伪静态规则(31套，参考 rewrite/nginx/)
  - WordPress/Discuz/Typecho/Laravel5/ThinkPHP
  - Drupal/PHPcms/EmpireCMS/ECShop/ShopEx
  - Dedecms/PHPWind/Sablog/Emlog/MacCMS
  - PBootCMS/NiuShop/CRMEB/DBShop/EduSoho/SeaCMS
  - DiscuzX/DiscuzX2/DiscuzX3/PHPWind
  - Dabr/ShopWind/mtvcms/maccms
  - 更多CMS规则持续添加
- [ ] Apache伪静态规则(16套，参考 rewrite/apache/)
- [ ] Python项目配置模板 (vhost/template/python_project/)
- [ ] 自定义规则编辑器
- [ ] 规则语法检查
- [ ] 规则导入/导出
- [ ] 规则版本管理
- [ ] 前端: 伪静态规则管理页面

---

### S17: AI智能助手 (参考 mod/project/agent/)

**这是宝塔最新的创新功能，Compass面板应该前瞻性地规划**

#### 17.1 AI对话系统 (mod/project/agent/chat_client/)
- [ ] 对话引擎(agent.py)
  - 多轮对话管理
  - 上下文记忆(memory.py)
  - 知识检索(retrieval.py)
  - 技能系统(skills.py)
- [ ] AI工具集 (chat_client/tools/)
  - 文件编辑(edit.py)
  - 终端执行(terminal.py)
  - 任务管理(task.py/todo.py)
  - 代码搜索(search)
  - Web获取(webfetch.py)
  - 摘要生成(summary.py)

#### 17.2 智能诊断Agent (14个专业Agent，参考 skill_agents/)
- [ ] 网站诊断助手 - 分析网站配置/运行状态/响应慢原因
- [ ] 数据库诊断助手 - MySQL性能/慢查询/优化建议
- [ ] 性能分析助手 - CPU/内存/磁盘IO/瓶颈定位
- [ ] 安全诊断助手 - 安全风险/异常进程/入侵迹象
- [ ] 防火墙诊断助手 - 端口规则/IP策略/访问限制
- [ ] SSL诊断助手 - 证书状态/有效期/配置问题
- [ ] DNS分析助手 - DNS解析记录/生效状态/延迟分析
- [ ] 日志分析助手 - 系统日志/应用日志/错误检测
- [ ] 文件分析助手 - 文件结构/权限/磁盘占用
- [ ] FTP诊断助手 - FTP账户/连接配置/被动模式
- [ ] 计划任务诊断助手 - 任务配置/执行状态/失败原因
- [ ] 服务器分析助手 - 资源使用/健康状况/清理建议
- [ ] 服务诊断助手 - 服务状态/启动失败/自启配置
- [ ] 流量分析助手 - 流量趋势/带宽使用/热门页面

#### 17.3 AI建站助手 (prompts/agent_buildsite.md)
- [ ] 自然语言建站(描述需求→自动生成网站)
- [ ] 网站模板生成
- [ ] 代码编辑/优化
- [ ] 响应式设计

#### 17.4 AI终端助手 (prompts/agent_shell.md)
- [ ] 自然语言→Linux命令
- [ ] 命令风险评估(low/medium/high)
- [ ] 命令执行前确认
- [ ] 命令执行结果解释
- [ ] 宝塔命令知识库

#### 17.5 AI首页助手 (prompts/agent_aics.md)
- [ ] 服务器状态智能问答
- [ ] 运维问题诊断
- [ ] 苏格拉底式追问(收集问题细节)
- [ ] 操作授权前置(修改前确认)
- [ ] Todo任务管理(多步骤任务展示)

---

### S18: 插件生态与一键部署

#### 18.1 插件系统增强
- [ ] 插件商店
  - 插件列表/搜索/分类
  - 插件详情/截图/评价
  - 插件安装/卸载/更新
  - 付费插件/免费插件
- [ ] 插件配置管理
  - 插件配置编辑
  - 插件配置导入/导出
- [ ] 插件依赖管理
  - 依赖检查
  - 自动安装依赖
- [ ] PHP插件兼容层 (class/panelPHP.py)
  - PHP插件执行
  - 参数传递
  - 结果解析

#### 18.2 一键部署
- [ ] WordPress一键部署
  - 自动创建数据库
  - 自动下载WordPress
  - 自动配置wp-config.php
  - 自动配置Nginx/Apache
  - 自动申请SSL
- [ ] Laravel一键部署
- [ ] Node.js应用一键部署
- [ ] Python应用一键部署
- [ ] Java应用一键部署(Spring Boot)
- [ ] 静态网站一键部署
- [ ] Docker应用一键部署
- [ ] 自定义模板部署

#### 18.3 应用市场
- [ ] 常用软件一键安装
  - phpMyAdmin/Adminer
  - Redis/RedisInsight
  - MongoDB/Mongo Express
  - Grafana/Prometheus
  - GitLab/Gitea
  - Jenkins/Drone CI
  - MinIO/Nextcloud
  - WordPress/Ghost/Typecho
  - 更多...

---

### S19: 面板安全加固

- [ ] 两步验证(TOTP - Google Authenticator)
  - 二维码生成
  - 密钥备份
  - 恢复码
- [ ] 面板SSL
  - 自签名证书生成
  - Let's Encrypt申请
  - 自定义证书上传
  - HTTP→HTTPS强制跳转
- [ ] 安全入口
  - 自定义访问路径(/随机字符串)
  - 安全入口修改
  - 安全入口禁用
- [ ] Basic Auth认证
  - 用户名/密码配置
  - Basic Auth启用/禁用
- [ ] 登录安全
  - 登录验证码(图片/算术)
  - 登录失败锁定(5次失败锁定30分钟)
  - 登录IP白名单
  - 登录时间限制
- [ ] 面板端口修改
- [ ] 面板域名绑定
- [ ] 面板授权管理
- [ ] 前端: 面板安全设置页面

---

### S20: 高级功能

#### 20.1 Git集成 (mod/project/git/)
- [ ] Git部署(comMod.py)
  - Git仓库克隆
  - Git拉取更新
  - Git分支管理
  - Git钩子(webhook)
- [ ] Git钩子脚本(scripts/)
- [ ] Git工具(mod/base/git_tool/)

#### 20.2 站点同步 (class/panelModel/syncsiteModel.py)
- [ ] 多服务器站点同步
- [ ] 同步规则配置
- [ ] 同步日志
- [ ] 同步状态监控
- [ ] 冲突处理策略

#### 20.3 虚拟空间 (mod/project/virtual/)
- [ ] 虚拟空间平台(virtualMod.py)
- [ ] 虚拟空间配置(YAML模板)
- [ ] 虚拟空间SSL管理
- [ ] 虚拟空间防火墙

#### 20.4 MySQL Binlog增量备份 (mod/project/mysql_binlog_backup/)
- [ ] Binlog配置管理(config_manager.py)
- [ ] 增量备份管理(backup_manager.py)
- [ ] 增量恢复管理(restore_manager.py)
- [ ] 清理管理(cleanup_manager.py)
- [ ] 任务调度(task_scheduler.py)

#### 20.5 流媒体支持 (class/panelVideo.py)
- [ ] 视频文件流式传输
- [ ] HTTP Range请求支持
- [ ] 分片传输
- [ ] 视频预览

#### 20.6 phpMyAdmin集成 (class/panelPmd.py + class/panelHttpProxy.py)
- [ ] phpMyAdmin自动安装
- [ ] 面板内嵌(HTTP代理转发)
- [ ] PHP-FPM FastCGI集成
- [ ] 自动PHP版本匹配
- [ ] phpMyAdmin配置管理

---

### S21: 主题与个性化

- [ ] 主题系统 (class/theme_config.py)
  - 主题安装/卸载/切换
  - 主题配置管理
  - 主题验证(FieldValidator)
  - 格式转换(新旧版本)
  - 主题模板管理
  - 主题上传/下载
- [ ] 自定义配置
  - 面板标题/Logo
  - 面板语言(中文/英文)
  - 面板时区
  - 面板端口
  - 面板域名
- [ ] 多语言支持
  - 中文简体
  - 中文繁体
  - English
  - 更多语言...
- [ ] 深色/浅色模式
- [ ] 前端: 主题管理页面

---

### S22: API与开放平台

- [ ] RESTful API (参考 class/panelApi.py)
  - API接口文档
  - Token认证
  - IP白名单限制
  - API使用统计
  - API限流
- [ ] Webhook系统
  - Webhook创建/管理
  - Webhook触发事件
  - Webhook日志
- [ ] App扫码登录
- [ ] WebAuthn支持 (class/webauthn/)
- [ ] 第三方集成
  - 微信小程序
  - 钉钉机器人
  - 飞书机器人
- [ ] SDK开发
  - Python SDK
  - JavaScript SDK
  - Go SDK
- [ ] 前端: API管理页面

---

### S23: 运维自动化

- [ ] 自动修复 (config/safe_autofix.json)
  - 安全问题自动修复
  - 服务异常自动重启
  - 磁盘满自动清理
  - SSL到期自动续期
- [ ] 智能告警
  - 告警规则引擎
  - 告警阈值配置
  - 告警升级策略
  - 告警抑制(避免重复告警)
  - 告警恢复通知
- [ ] 容量规划
  - 磁盘使用趋势预测
  - 内存使用趋势预测
  - 带宽使用趋势预测
  - 扩容建议
- [ ] 性能基线
  - 性能指标采集
  - 性能基线建立
  - 性能异常检测
  - 性能报告生成
- [ ] 自动化任务编排
  - 任务链(前置任务→后续任务)
  - 条件分支(如果...则...)
  - 循环执行
  - 任务模板

---

### S25: 面板迁移与灾备 [P2]

> 宝塔和MW都没有完整的面板迁移能力。这是差异化竞争点。

#### 为什么面板迁移有意义?

| 场景 | 说明 | 频率 |
|------|------|------|
| **服务器更换** | 老服务器到期/配置不够，换新服务器 | 每1-3年 |
| **云厂商切换** | 从阿里云迁到腾讯云/AWS | 偶尔 |
| **系统重装** | 系统出问题需要重装，但想保留所有配置 | 偶尔 |
| **灾备恢复** | 服务器硬盘坏了/被黑了，需要从备份恢复到新机器 | 紧急 |
| **环境复制** | 把生产环境复制到测试环境 | 频繁 |
| **批量部署** | 10台服务器用相同配置 | 运维常见 |
| **版本回退** | 面板升级出问题，回退到旧版本 | 偶尔 |

**宝塔的现状:**
- 只有网站级别的备份/恢复(单个站点打包)
- 没有面板级别的整体迁移
- 没有跨服务器迁移
- 没有配置导出/导入
- 没有灾备方案

**Compass面板现状:**
- 同样只有基础备份
- 没有迁移能力

#### 25.1 面板快照 (一键打包整个面板状态)

```
面板快照 = 面板数据库 + 配置文件 + SSL证书 + 面板设置

快照内容:
├── data/
│   ├── panel.db           # 核心数据库
│   ├── security.db        # 安全数据库
│   ├── task.db            # 任务数据库
│   ├── log.db             # 日志数据库
│   └── *.json             # 各种配置文件
├── config/
│   ├── encryption.key     # 加密密钥
│   └── *.json             # 配置文件
├── ssl/
│   ├── privateKey.pem     # 面板SSL私钥
│   └── certificate.pem    # 面板SSL证书
└── vhost/
    ├── nginx/             # Nginx配置
    ├── apache/            # Apache配置
    ├── rewrite/           # 伪静态规则
    └── cert/              # 站点SSL证书

快照格式: .mw-snapshot (tar.zstd + 加密)
快照大小: 通常 1-50MB (不含网站文件和数据库数据)
```

- [ ] 一键创建面板快照
- [ ] 快照加密(Fernet + 用户密码)
- [ ] 快照压缩(zstd)
- [ ] 快照完整性校验(SHA256)
- [ ] 快照版本标记(面板版本)
- [ ] 快照列表/删除/下载
- [ ] 快照保留策略(保留最近N份)
- [ ] 定时快照(每日/每周)
- [ ] 前端: 快照管理页面

#### 25.2 面板恢复 (从快照恢复面板)

```
恢复流程:
1. 上传快照文件
2. 验证快照完整性(SHA256)
3. 验证快照版本兼容性
4. 解密快照(用户输入密码)
5. 停止面板服务
6. 备份当前面板数据(以防恢复失败)
7. 解压快照到面板目录
8. 执行数据库迁移(如果版本不同)
9. 重启面板服务
10. 验证恢复结果
11. 如果失败，自动回滚到备份
```

- [ ] 快照上传
- [ ] 快照验证(完整性/版本/兼容性)
- [ ] 恢复前自动备份(防恢复失败)
- [ ] 数据库迁移(跨版本恢复时自动执行Alembic迁移)
- [ ] 恢复后自动重启
- [ ] 恢复失败自动回滚
- [ ] 恢复日志
- [ ] 前端: 恢复向导页面

#### 25.3 跨服务器迁移 (面板从A服务器迁移到B服务器)

```
迁移方式A: 快照迁移 (推荐)
┌──────────────┐    上传快照    ┌──────────────┐
│  源服务器 A   │ ──────────→  │  目标服务器 B │
│  创建快照     │              │  恢复快照     │
└──────────────┘              └──────────────┘

迁移方式B: 直接迁移 (SSH通道)
┌──────────────┐    SSH隧道    ┌──────────────┐
│  源服务器 A   │ ←─────────→ │  目标服务器 B │
│  导出数据     │              │  导入数据     │
└──────────────┘              └──────────────┘

迁移方式C: 增量迁移 (逐步同步)
┌──────────────┐    增量同步    ┌──────────────┐
│  源服务器 A   │ ──────────→  │  目标服务器 B │
│  持续同步     │   (rsync)    │  持续接收     │
└──────────────┘              └──────────────┘
```

**迁移内容清单:**

| 内容 | 迁移方式 | 说明 |
|------|---------|------|
| 面板配置 | 快照 | 面板设置/端口/安全入口/用户 |
| 面板数据库 | 快照 | 所有.db文件 |
| SSL证书 | 快照 | 面板SSL + 站点SSL |
| Nginx/Apache配置 | 快照 | vhost/目录 |
| 伪静态规则 | 快照 | rewrite/目录 |
| 网站文件 | rsync | /www/wwwroot/ |
| 网站数据库 | mysqldump | MySQL数据导出/导入 |
| 计划任务 | 快照 | crontab配置 |
| 防火墙规则 | 快照 | firewall配置 |
| 插件 | rsync | plugins/目录 |
| 软件配置 | rsync | /www/server/ |

- [ ] 迁移向导(步骤式引导)
- [ ] SSH连接目标服务器
- [ ] 目标服务器环境检测(OS/磁盘/内存/端口)
- [ ] 目标服务器面板安装(自动)
- [ ] 面板快照传输(SSH/SFTP)
- [ ] 网站文件同步(rsync over SSH)
- [ ] 数据库导出/导入(mysqldump/mysql)
- [ ] 配置适配(路径/IP/域名自动替换)
- [ ] 迁移前预检(磁盘空间/端口冲突/版本兼容)
- [ ] 迁移进度(实时进度条)
- [ ] 迁移日志
- [ ] 迁移回滚(失败时恢复源服务器状态)
- [ ] 增量迁移(支持断点续传)
- [ ] 前端: 迁移向导页面

#### 25.4 环境复制 (把当前环境复制到多台服务器)

```
场景: 10台Web服务器用相同的Nginx+PHP+站点配置

┌──────────────┐
│  模板服务器   │  ← 配置好环境
└──────┬───────┘
       │ 复制
  ┌────┼────┬────┬────┐
  ▼    ▼    ▼    ▼    ▼
 S1   S2   S3   S4   S5  ← 目标服务器
```

- [ ] 创建环境模板(从当前服务器生成)
- [ ] 环境模板管理(列表/删除/导出)
- [ ] 批量部署(选择目标服务器列表)
- [ ] 部署进度(每台服务器独立进度)
- [ ] 部署结果(成功/失败/跳过)
- [ ] 部署后验证(自动检查服务状态)
- [ ] 前端: 环境复制页面

#### 25.5 面板版本回退

```
场景: 面板升级到v2.1后出问题，想回退到v2.0

回退流程:
1. 面板升级前自动创建快照(标记为"升级前快照")
2. 升级后如果出问题，一键回退到升级前快照
3. 回退 = 恢复快照 + 回退代码版本
```

- [ ] 升级前自动快照
- [ ] 一键回退到升级前
- [ ] 版本历史(所有升级记录)
- [ ] 回退日志
- [ ] 前端: 版本回退页面

#### 25.6 灾备方案

```
灾备架构:
┌──────────────┐     定时快照      ┌──────────────┐
│  生产服务器   │ ──────────────→  │  备份存储     │
│              │                  │  (本地/云端)  │
└──────────────┘                  └──────────────┘
       │                                 │
       │ 灾难发生                        │ 快照文件
       ▼                                 ▼
┌──────────────┐     恢复快照      ┌──────────────┐
│  灾备服务器   │ ←────────────── │  备份存储     │
│  (自动接管)   │                  │              │
└──────────────┘                  └──────────────┘
```

- [ ] 定时快照(每日/每周)
- [ ] 快照云端存储(七牛/OSS/S3)
- [ ] 灾备服务器预配置
- [ ] 自动故障检测(心跳监控)
- [ ] 自动故障转移(DNS切换/IP漂移)
- [ ] 灾备恢复演练(定期测试)
- [ ] RTO/RPO指标(恢复时间目标/恢复点目标)
- [ ] 前端: 灾备管理页面

---

### S24: 企业级功能

- [ ] 多服务器管理
  - 服务器添加/删除
  - 服务器分组
  - 服务器状态监控
  - 远程执行命令
  - 远程文件管理
- [ ] 集群管理
  - 负载均衡集群
  - 数据库集群
  - 缓存集群
  - 集群状态监控
- [ ] CDN集成
  - CDN配置管理
  - CDN缓存刷新
  - CDN流量监控
  - CDN日志分析
- [ ] 灾备
  - 异地备份
  - 灾难恢复计划
  - 恢复演练
  - RTO/RPO管理
- [ ] 合规审计
  - 操作审计报告
  - 安全合规检查
  - 等保2.0支持
  - 审计日志导出
- [ ] 成本管理
  - 资源使用统计
  - 成本分析
  - 成本优化建议
- [ ] 团队协作
  - 项目分配
  - 任务指派
  - 工单系统 (参考 class/panelWorkorder.py)
  - 远程协助(WebSocket实时通信)

---

### 迭代优先级矩阵

| 优先级 | 阶段 | 内容 |
|-------|------|------|
| **地基** | **S0** | **数据层基础设施(SQLAlchemy/WAL/多库分离/迁移/加密/Repository)** |
| **P0** | S1-S4 | 项目类型+运行时 / 网站管理 / 安全体系 / 数据库 |
| **P1** | S5-S9 | 文件管理 / 备份 / 监控 / Docker / SSL |
| **P2** | S10-S14 | 计划任务 / FTP邮件 / 推送通知 / 用户权限 / Web服务器 |
| **P3** | S15-S19 | 系统优化 / 伪静态规则 / AI助手 / 插件生态 / 面板安全 |
| **P4** | S20-S25 | 高级功能 / 主题 / API / 运维自动化 / 企业级 / 面板迁移 |

### 迭代节奏建议

```
每轮迭代 = 2-4周
├── 第1周: 需求分析 + 技术方案 + 架构设计
├── 第2周: 后端实现 + API开发
├── 第3周: 前端实现 + 联调测试
└── 第4周: 测试修复 + 文档 + 发布

每完成一个S，进行一次版本发布
S0        → v1.5 (数据层基础设施 - 地基)
S1-S4     → v2.0 (核心功能)
S5-S9     → v3.0 (运维功能)
S10-S14   → v4.0 (扩展功能)
S15-S19   → v5.0 (高级功能)
S20-S25   → v6.0 (企业级 + 面板迁移)
```

**迭代的尽头是完美产品。每一步都做到极致，不妥协。**
