# 插件开发入门指南

## 概述

mdserver-web 采用插件化架构，支持通过插件扩展面板功能。本文档介绍如何开发一个标准的面板插件。

## 插件目录结构

每个插件是一个独立的目录，位于 `plugins/` 目录下:

```
plugins/
└── my_plugin/
    ├── info.json          # 插件元信息 (必需)
    ├── index.py           # 插件主逻辑 (必需)
    ├── index.html         # 插件设置页面 (必需)
    ├── install.sh         # 安装脚本 (必需)
    ├── uninstall.sh       # 卸载脚本 (可选)
    ├── ico.png            # 插件图标 (推荐)
    ├── init.d/            # 服务管理脚本目录
    │   └── my_plugin      # 服务控制脚本
    ├── conf/              # 配置文件模板目录
    │   └── config.conf    # 配置文件模板
    ├── js/                # 前端 JavaScript 目录
    │   └── my_plugin.js   # 前端逻辑
    └── tpl/               # 模板目录
```

## info.json 配置

`info.json` 是插件的元信息文件，定义了插件的基本属性:

```json
{
  "sort": 1,
  "title": "My Plugin",
  "tip": "soft",
  "name": "my_plugin",
  "type": "其他插件",
  "ps": "插件功能描述",
  "coexist": false,
  "install_pre_inspection": true,
  "uninstall_pre_inspection": true,
  "checks": "server/my_plugin",
  "path": "server/my_plugin",
  "shell": "install.sh",
  "versions": ["1.0.0", "1.1.0"],
  "updates": ["1.0.0", "1.1.0"],
  "author": "作者名",
  "home": "https://example.com",
  "date": "2024-01-01",
  "pid": "1",
  "display": 1
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sort | int | 否 | 排序权重，数字越大越靠前 |
| title | string | 是 | 插件显示名称 |
| tip | string | 是 | 插件类型标识: soft/service |
| name | string | 是 | 插件唯一标识，与目录名一致 |
| type | string/int | 是 | 分类: 0-全部, 1-运行环境, 2-数据软件, 3-代码管理, 4-系统工具, 5-其他插件, 6-辅助插件, 7-AI插件 |
| ps | string | 是 | 插件功能描述 |
| coexist | bool | 否 | 是否允许多版本共存 |
| install_pre_inspection | bool | 否 | 安装前是否检查 |
| uninstall_pre_inspection | bool | 否 | 卸载前是否检查 |
| checks | string | 是 | 安装检查路径 |
| path | string | 是 | 安装路径 (相对于 /www/server/) |
| shell | string | 是 | 安装脚本名 |
| versions | array | 是 | 可安装版本列表 |
| updates | array | 否 | 可更新版本列表 |
| author | string | 否 | 作者名称 |
| home | string | 否 | 官方网站 |
| date | string | 否 | 发布日期 |
| pid | string | 否 | 进程 ID |
| display | int | 否 | 是否在首页显示 |

## index.py 开发

`index.py` 是插件的主逻辑文件，需要实现以下标准函数:

### 基础函数

```python
import sys
import os

# 添加 web 目录到路径
web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw

def getPluginName():
    """返回插件名称"""
    return 'my_plugin'

def getPluginDir():
    """返回插件源码目录"""
    return mw.getPluginDir() + '/' + getPluginName()

def getServerDir():
    """返回插件安装目录"""
    return mw.getServerDir() + '/' + getPluginName()

def getInitDFile():
    """返回服务管理脚本路径"""
    current_os = mw.getOs()
    if current_os == 'darwin':
        return '/tmp/' + getPluginName()
    if current_os.startswith('freebsd'):
        return '/etc/rc.d/' + getPluginName()
    return '/etc/init.d/' + getPluginName()

def getArgs():
    """解析命令行参数"""
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)
    if args_len == 1:
        t = args[0].strip('{').strip('}')
        t = t.split(':', 2)
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':', 2)
            tmp[t[0]] = t[1]
    return tmp

def checkArgs(data, ck=[]):
    """检查必需参数"""
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))
```

### 服务管理函数

```python
def start():
    """启动服务"""
    cmd = getInitDFile() + ' start'
    data = mw.execShell(cmd)
    if data[1] == '':
        return 'ok'
    return data[1]

def stop():
    """停止服务"""
    cmd = getInitDFile() + ' stop'
    data = mw.execShell(cmd)
    if data[1] == '':
        return 'ok'
    return data[1]

def restart():
    """重启服务"""
    cmd = getInitDFile() + ' restart'
    data = mw.execShell(cmd)
    if data[1] == '':
        return 'ok'
    return data[1]

def reload():
    """重载配置"""
    cmd = getInitDFile() + ' reload'
    data = mw.execShell(cmd)
    if data[1] == '':
        return 'ok'
    return data[1]
```

### 状态查询函数

```python
def status():
    """检查服务状态"""
    cmd = getInitDFile() + ' status'
    data = mw.execShell(cmd)
    if data[0] == '' and data[1] == '':
        return 'stop'
    return 'start'

def runInfo():
    """获取运行信息"""
    # 返回服务运行状态信息
    return mw.getJson({...})

def conf():
    """获取配置文件路径"""
    return getServerDir() + '/conf/config.conf'
```

### 主入口函数

```python
if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == 'start':
        print(start())
    elif func == 'stop':
        print(stop())
    elif func == 'restart':
        print(restart())
    elif func == 'reload':
        print(reload())
    elif func == 'run_info':
        print(runInfo())
    elif func == 'conf':
        print(conf())
    else:
        print('error')
```

## install.sh 安装脚本

安装脚本负责插件的安装和卸载:

```bash
#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

# 插件名称
pluginName=my_plugin
# 安装路径
installPath=/www/server/${pluginName}

# 安装函数
Install_App(){
    echo '正在安装...'

    # 创建目录
    mkdir -p ${installPath}

    # 下载源码
    cd /tmp
    wget https://example.com/${pluginName}-1.0.0.tar.gz
    tar -xzf ${pluginName}-1.0.0.tar.gz

    # 编译安装
    cd ${pluginName}-1.0.0
    ./configure --prefix=${installPath}
    make && make install

    # 创建服务脚本
    cp ${pluginName} /etc/init.d/${pluginName}
    chmod +x /etc/init.d/${pluginName}

    # 启动服务
    /etc/init.d/${pluginName} start

    echo '安装完成'
}

# 卸载函数
Uninstall_App(){
    # 停止服务
    /etc/init.d/${pluginName} stop

    # 删除文件
    rm -rf ${installPath}
    rm -f /etc/init.d/${pluginName}

    echo '卸载完成'
}

# 根据参数执行
action=$1
if [ "${action}" == 'install' ]; then
    Install_App
elif [ "${action}" == 'uninstall' ]; then
    Uninstall_App
fi
```

## init.d 服务脚本

服务管理脚本位于 `init.d/` 目录:

```bash
#!/bin/bash
# chkconfig: 2345 55 25
# description: My Plugin Service

pluginName=my_plugin
installPath=/www/server/${pluginName}

start(){
    echo "Starting ${pluginName}..."
    ${installPath}/bin/${pluginName} -c ${installPath}/conf/config.conf
    echo "Started"
}

stop(){
    echo "Stopping ${pluginName}..."
    kill $(cat ${installPath}/${pluginName}.pid)
    echo "Stopped"
}

restart(){
    stop
    sleep 1
    start
}

status(){
    if [ -f ${installPath}/${pluginName}.pid ]; then
        pid=$(cat ${installPath}/${pluginName}.pid)
        if ps -p $pid > /dev/null; then
            echo "${pluginName} is running (PID: $pid)"
            return 0
        fi
    fi
    echo "${pluginName} is stopped"
    return 1
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
```

## index.html 设置页面

插件设置页面用于在面板中展示插件的管理界面:

```html
<div class="plugin-box">
    <div class="plugin-header">
        <h3>我的插件</h3>
        <div class="plugin-status">
            运行状态: <span id="status">检测中...</span>
        </div>
    </div>

    <div class="plugin-body">
        <div class="btn-group">
            <button class="btn btn-success" onclick="startPlugin()">启动</button>
            <button class="btn btn-danger" onclick="stopPlugin()">停止</button>
            <button class="btn btn-warning" onclick="restartPlugin()">重启</button>
        </div>

        <div class="config-section">
            <h4>配置文件</h4>
            <textarea id="configContent" rows="20"></textarea>
            <button class="btn btn-primary" onclick="saveConfig()">保存</button>
        </div>
    </div>
</div>

<script src="/plugins/file?name=my_plugin&js/my_plugin.js"></script>
```

## 前端 JavaScript

前端 JavaScript 文件位于 `js/` 目录，用于处理插件的前端交互:

```javascript
// 插件 API 调用封装
function pluginApi(func, args, callback) {
    $.post('/plugins/run', {
        name: 'my_plugin',
        func: func,
        version: '',
        args: JSON.stringify(args)
    }, function(data) {
        if (callback) callback(data);
    });
}

// 启动插件
function startPlugin() {
    pluginApi('start', {}, function(data) {
        if (data.status) {
            layer.msg('启动成功');
            getStatus();
        } else {
            layer.msg('启动失败: ' + data.msg);
        }
    });
}

// 停止插件
function stopPlugin() {
    pluginApi('stop', {}, function(data) {
        if (data.status) {
            layer.msg('停止成功');
            getStatus();
        } else {
            layer.msg('停止失败: ' + data.msg);
        }
    });
}

// 重启插件
function restartPlugin() {
    pluginApi('restart', {}, function(data) {
        if (data.status) {
            layer.msg('重启成功');
            getStatus();
        } else {
            layer.msg('重启失败: ' + data.msg);
        }
    });
}

// 获取状态
function getStatus() {
    pluginApi('status', {}, function(data) {
        if (data.status) {
            $('#status').text(data.data).css('color', 'green');
        } else {
            $('#status').text('已停止').css('color', 'red');
        }
    });
}

// 页面加载时获取状态
$(document).ready(function() {
    getStatus();
});
```

## 开发流程

### 1. 创建插件目录

```bash
mkdir -p plugins/my_plugin/{init.d,conf,js,tpl}
```

### 2. 编写 info.json

定义插件的基本信息和可安装版本。

### 3. 编写 index.py

实现插件的核心逻辑，包括服务管理、配置管理等函数。

### 4. 编写 install.sh

实现插件的安装和卸载逻辑。

### 5. 编写 init.d 脚本

实现服务的启动、停止、重启、状态查询。

### 6. 编写 index.html 和 JS

实现插件的前端管理界面。

### 7. 测试插件

在面板中安装并测试插件功能。

## 调用面板 API

插件可以通过 `core.mw` 模块调用面板的内置功能:

```python
import core.mw as mw

# 执行系统命令
result = mw.execShell('ls -la')

# 读取文件
content = mw.readFile('/path/to/file')

# 写入文件
mw.writeFile('/path/to/file', 'content')

# 获取 JSON 响应
data = mw.getJson({'key': 'value'})

# 获取服务器目录
server_dir = mw.getServerDir()  # /www/server

# 获取面板目录
panel_dir = mw.getPanelDir()  # /path/to/mdserver-web

# 检查操作系统
os_type = mw.getOs()  # linux/darwin/freebsd

# 记录日志
mw.writeLog('插件名称', '操作描述')
```

## 最佳实践

1. **错误处理**: 所有外部调用都要进行异常处理
2. **日志记录**: 重要操作要记录日志
3. **权限检查**: 涉及系统操作时检查权限
4. **配置验证**: 保存配置前验证格式正确性
5. **版本兼容**: 考虑不同版本的数据迁移
6. **安全防护**: 防止命令注入、路径遍历等安全问题

## 示例插件

参考以下现有插件:

- `plugins/openresty/` - Web 服务器插件
- `plugins/mysql/` - 数据库插件
- `plugins/redis/` - 缓存插件
- `plugins/php/` - 运行环境插件

## 常见问题

### Q: 插件安装后不显示?

A: 检查 `info.json` 格式是否正确，`checks` 路径是否存在。

### Q: 如何让插件支持多版本?

A: 在 `info.json` 中设置 `"coexist": true`，并在 `versions` 数组中列出所有版本。

### Q: 如何在首页显示插件?

A: 在 `info.json` 中设置 `"display": 1`。

### Q: 插件如何调用其他插件?

A: 通过 `sys.path` 导入其他插件的模块，或通过面板 API 间接调用。
