# 文件管理 API 文档

## 概述

文件管理模块提供服务器文件的浏览、编辑、上传、下载、压缩等操作。

**基础路径**: `/files`

## 接口列表

### 1. 文件管理页面

获取文件管理页面。

**请求**
- **URL**: `/files/index`
- **Method**: `GET`
- **认证**: 需要登录

---

### 2. 获取目录列表

获取指定目录下的文件和文件夹列表。

**请求**
- **URL**: `/files/get_dir`
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 目录路径 |
| search | string | 否 | 搜索关键词 |
| all | string | 否 | 设为 "yes" 搜索所有子目录 |
| p | string | 否 | 页码，默认 1 |
| row | string | 否 | 每页数量，默认 10 |
| order | string | 否 | 排序方式 |

**响应**
```json
{
  "dir": [...],
  "files": [...],
  "count": 100,
  "page": "<分页HTML>"
}
```

**文件对象结构**
```json
{
  "name": "filename.txt",
  "size": 1024,
  "mtime": "2024-01-01 12:00:00",
  "accept": "-rw-r--r--",
  "user": "www"
}
```

---

### 3. 获取文件内容

读取文件内容。

**请求**
- **URL**: `/files/get_body`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 文件路径 |

**响应**
```json
{
  "code": true,
  "msg": "ok",
  "data": "文件内容..."
}
```

---

### 4. 保存文件内容

保存文件内容。

**请求**
- **URL**: `/files/save_body`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 文件路径 |
| data | string | 是 | 文件内容 |
| encoding | string | 否 | 文件编码 |

**响应**
```json
{
  "code": true,
  "msg": "文件保存成功"
}
```

---

### 5. 获取文件最后几行

获取文件的最后 N 行内容，适用于查看日志文件。

**请求**
- **URL**: `/files/get_last_body`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 文件路径 |
| line | string | 否 | 行数，默认 100 |

**响应**
```json
{
  "code": true,
  "msg": "OK",
  "data": "最后N行内容..."
}
```

---

### 6. 创建文件

创建新文件。

**请求**
- **URL**: `/files/create_file`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 文件完整路径 |

---

### 7. 创建目录

创建新目录。

**请求**
- **URL**: `/files/create_dir`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 目录完整路径 |

---

### 8. 删除文件

删除指定文件。

**请求**
- **URL**: `/files/delete`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 文件路径 |

---

### 9. 删除目录

删除指定目录。

**请求**
- **URL**: `/files/delete_dir`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 目录路径 |

---

### 10. 重命名/移动文件

重命名或移动文件。

**请求**
- **URL**: `/files/mv_file`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sfile | string | 是 | 源文件路径 |
| dfile | string | 是 | 目标文件路径 |

---

### 11. 复制文件

复制文件到指定位置。

**请求**
- **URL**: `/files/copy_file`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sfile | string | 是 | 源文件路径 |
| dfile | string | 是 | 目标文件路径 |

---

### 12. 批量粘贴

批量复制或移动文件。

**请求**
- **URL**: `/files/batch_paste`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 目标目录 |
| type | string | 是 | 操作类型: copy/move |

---

### 13. 检查文件是否存在

检查目标位置是否存在同名文件。

**请求**
- **URL**: `/files/check_exists_files`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| dfile | string | 是 | 目标目录 |
| filename | string | 否 | 文件名，不传则从 Session 读取 |

---

### 14. 压缩文件

压缩文件或目录。

**请求**
- **URL**: `/files/zip`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sfile | string | 是 | 源文件/目录路径 |
| dfile | string | 是 | 压缩文件保存路径 |
| type | string | 是 | 压缩格式: zip/tar.gz/tar.bz2 |
| path | string | 否 | 工作目录 |

---

### 15. 解压文件

解压文件。

**请求**
- **URL**: `/files/unzip`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sfile | string | 是 | 压缩文件路径 |
| dfile | string | 是 | 解压目标目录 |
| type | string | 是 | 压缩格式 |
| path | string | 否 | 工作目录 |

---

### 16. 智能解压

自动识别压缩格式并解压。

**请求**
- **URL**: `/files/uncompress`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sfile | string | 是 | 压缩文件路径 |
| dfile | string | 是 | 解压目标目录 |
| path | string | 否 | 工作目录 |

---

### 17. 获取文件权限

获取文件的权限信息。

**请求**
- **URL**: `/files/file_access`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| filename | string | 是 | 文件路径 |

**响应**
```json
{
  "accept": "0644",
  "user": "www",
  "group": "www",
  "sys_users": ["root", "www", "nginx"]
}
```

---

### 18. 设置文件权限

设置文件权限。

**请求**
- **URL**: `/files/set_file_access`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| filename | string | 是 | 文件路径 |
| user | string | 是 | 所有者 |
| access | string | 是 | 权限，如 755、644 |

---

### 19. 上传文件

上传文件到指定目录。

**请求**
- **URL**: `/files/upload_file?path=<path>`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

**参数**
| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| path | query | string | 是 | 目标目录 |
| zunfile | body | file | 是 | 文件内容 |

---

### 20. 分片上传

分片上传大文件。

**请求**
- **URL**: `/files/upload_segment`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 目标目录 |
| name | string | 是 | 文件名 |
| size | string | 是 | 文件总大小 |
| start | string | 是 | 当前分片起始位置 |
| dir_mode | string | 否 | 目录权限 |
| file_mode | string | 否 | 文件权限 |
| b64_data | string | 否 | 是否 Base64 编码 |
| blob | file | 是 | 分片数据 |

---

### 21. 下载文件

下载服务器上的文件。

**请求**
- **URL**: `/files/download?filename=<path>`
- **Method**: `GET`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| filename | string | 是 | 文件完整路径 |

**响应**
- 返回文件流，Content-Disposition: attachment

---

### 22. 远程下载

从 URL 下载文件到服务器。

**请求**
- **URL**: `/files/download_file`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 下载 URL |
| path | string | 是 | 保存目录 |
| filename | string | 是 | 保存文件名 |

**响应**
```json
{
  "code": true,
  "msg": "已将下载任务添加到队列!"
}
```

---

### 23. 获取目录大小

获取目录的大小。

**请求**
- **URL**: `/files/get_dir_size`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 目录路径 |

**响应**
```json
{
  "code": true,
  "msg": "ok",
  "data": "1.5GB"
}
```

---

### 24. 批量操作

批量设置文件权限等操作。

**请求**
- **URL**: `/files/set_batch_data`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 目标目录 |
| type | string | 是 | 操作类型 |
| access | string | 否 | 权限 |
| user | string | 否 | 所有者 |
| data | string | 是 | 文件列表 JSON |

---

### 25. 清空日志

清空指定日志文件。

**请求**
- **URL**: `/files/close_logs`
- **Method**: `POST`

---

## 回收站接口

### 获取回收站文件列表

**请求**
- **URL**: `/files/get_recycle_bin`
- **Method**: `POST`
- **认证**: 需要登录

---

### 恢复回收站文件

**请求**
- **URL**: `/files/re_recycle_bin`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 回收站中的文件路径 |

---

### 删除回收站文件

**请求**
- **URL**: `/files/del_recycle_bin`
- **Method**: `POST`

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 回收站中的文件路径 |

---

### 开启/关闭回收站

**请求**
- **URL**: `/files/recycle_bin`
- **Method**: `POST`

---

### 关闭回收站功能

**请求**
- **URL**: `/files/close_recycle_bin`
- **Method**: `POST`

---

## 注意事项

1. 所有接口都需要登录认证
2. 文件路径建议使用绝对路径
3. 开发机 (macOS) 部分功能受限，如权限设置
4. 上传文件大小受服务器配置限制
5. 远程下载任务会加入后台任务队列
