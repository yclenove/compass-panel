# 仪表盘 API 文档

## 概述

仪表盘模块提供面板的主入口、登录认证、安全路径等功能。

**基础路径**: `/`

## 接口列表

### 1. 首页

获取面板首页。

**请求**
- **URL**: `/`
- **Method**: `GET`
- **认证**: 需要登录

**响应**
- 返回渲染的 HTML 页面

---

### 2. 安全路径访问

通过安全路径访问面板，支持安全路径验证和快速登录。

**请求**
- **URL**: `/<path>`
- **Method**: `GET`
- **认证**: 通过安全路径或快速登录 Token

**参数**
| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| path | URL | string | 是 | 安全路径 |
| login | query | string | 否 | Base64 编码的快速登录数据 |

**快速登录数据格式**
```json
{
  "username": "admin",
  "password": "password",
  "time": 1234567890123
}
```

**响应**
- 安全路径正确: 返回登录页面
- 快速登录成功: 重定向到首页
- 安全路径错误: 返回错误页面或 HTTP 状态码

---

### 3. 用户登录

执行用户登录操作。

**请求**
- **URL**: `/do_login`
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |
| code | string | 否 | 验证码 (非开发模式必填) |

**响应**
```json
{
  "code": 1,
  "msg": "登录成功,正在跳转...",
  "data": []
}
```

**错误码**
| code | 说明 |
|------|------|
| -1 | 用户名或密码错误 |
| 1 | 登录成功 |
| 2 | 需要两步验证 |
| false | 面板已关闭 |

**安全限制**
- 连续 5 次验证码错误将自动关闭面板
- 开发模式下跳过验证码检查

---

### 4. 两步验证登录

完成两步验证登录。

**请求**
- **URL**: `/verify_login`
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |
| auth | string | 是 | TOTP 验证码 |

**响应**
```json
{
  "code": 1,
  "msg": "二次验证成功!",
  "data": []
}
```

---

### 5. 检查登录状态

检查当前会话是否已登录。

**请求**
- **URL**: `/check_login`
- **Method**: `GET` / `POST`

**响应**
```json
// 已登录
{
  "code": true,
  "msg": "已登录",
  "data": []
}

// 未登录
{
  "code": false,
  "msg": "未登录",
  "data": []
}
```

---

### 6. 获取验证码

获取登录验证码图片。

**请求**
- **URL**: `/code`
- **Method**: `GET`

**响应**
- Content-Type: `image/png`
- 返回 PNG 格式的验证码图片
- 验证码存储在 Session 中

---

### 7. 登录页面

显示登录页面。

**请求**
- **URL**: `/login`
- **Method**: `GET`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tmp_token | string | 否 | 临时登录 Token |
| signout | string | 否 | 设为 "True" 注销登录 |

**响应**
- 设置了安全路径且未通过: 返回错误页面
- 未设置安全路径: 返回登录页面
- 提供 tmp_token: 自动登录并重定向

---

### 8. 关闭面板页面

显示面板关闭页面。

**请求**
- **URL**: `/close`
- **Method**: `GET`

**响应**
- 面板已关闭: 返回关闭页面
- 面板未关闭: 重定向到首页

---

### 9. Webhook 接口

Webhook 插件专用接口。

**请求**
- **URL**: `/hook`
- **Method**: `POST` / `GET`
- **认证**: 通过 access_key 认证

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| access_key | string | 是 | 访问密钥 |
| params | string | 否 | 附加参数 |

**响应**
- 返回 Webhook 插件的执行结果

**前置条件**
- 需要先安装 Webhook 插件

---

## 系统信息接口

### 获取系统统计信息

**请求**
- **URL**: `/system/system_total`
- **Method**: `GET` / `POST`
- **认证**: 需要登录

**响应**
```json
{
  "mem": {...},
  "cpuNum": 4,
  "cpuRealUsed": 25.5,
  "time": "...",
  "system": "CentOS 7.9",
  "version": "0.0.1"
}
```

---

### 获取网络信息

**请求**
- **URL**: `/system/network`
- **Method**: `GET`
- **认证**: 需要登录

**响应**
```json
{
  "cpu": [...],
  "load": {...},
  "mem": {...},
  "iostat": {...},
  "network": {...}
}
```

---

### 获取磁盘信息

**请求**
- **URL**: `/system/disk_info`
- **Method**: `GET` / `POST`
- **认证**: 需要登录

**响应**
```json
{
  "code": true,
  "msg": "ok",
  "data": [...]
}
```

---

## 任务队列接口

### 获取任务数量

**请求**
- **URL**: `/task/count`
- **Method**: `GET` / `POST`
- **认证**: 需要登录

**响应**
```json
{
  "code": true,
  "msg": "ok",
  "data": 5
}
```

---

### 获取任务列表

**请求**
- **URL**: `/task/list`
- **Method**: `POST`
- **认证**: 需要登录

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| p | string | 否 | 页码，默认 1 |
| limit | string | 否 | 每页数量，默认 10 |
| search | string | 否 | 搜索关键词 |

---

### 获取任务执行日志

**请求**
- **URL**: `/task/get_exec_log`
- **Method**: `POST`
- **认证**: 需要登录

**响应**
- 返回最近 100 行任务执行日志

---

### 获取任务进度

**请求**
- **URL**: `/task/get_task_speed`
- **Method**: `POST`
- **认证**: 需要登录

**响应**
```json
{
  "name": "安装 MySQL",
  "cmd": "...",
  "msg": "...",
  "isDownload": false,
  "count": 3,
  "task": [...]
}
```

---

### 删除任务

**请求**
- **URL**: `/task/remove_task`
- **Method**: `POST`
- **认证**: 需要登录

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 任务 ID |

---

## 日志接口

### 获取操作日志列表

**请求**
- **URL**: `/logs/get_log_list`
- **Method**: `POST`
- **认证**: 需要登录

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| p | string | 否 | 页码，默认 1 |
| limit | string | 否 | 每页数量，默认 10 |
| search | string | 否 | 搜索关键词 |

---

### 清空操作日志

**请求**
- **URL**: `/logs/del_panel_logs`
- **Method**: `POST`
- **认证**: 需要登录

---

## 通用响应格式

所有 API 接口返回 JSON 格式:

```json
{
  "code": true/false/1/-1,
  "msg": "提示信息",
  "data": {}
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| code | boolean/number | 状态码，true/1 表示成功，false/-1 表示失败 |
| msg | string | 提示信息 |
| data | any | 返回数据 |
