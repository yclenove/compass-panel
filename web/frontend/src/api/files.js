import request from '@/utils/request';

// 获取目录列表
export function getDir(path, showHidden, page, row, order, search) {
  const data = new URLSearchParams();
  data.append('path', path || '/');
  if (showHidden) data.append('showHidden', '1');
  if (page) data.append('p', page);
  if (row) data.append('row', row);
  if (order) data.append('order', order);
  if (search) data.append('search', search);
  return request({ url: '/files/get_dir', method: 'post', data });
}

// 获取文件内容
export function getFileContent(path) {
  const data = new URLSearchParams();
  data.append('path', path);
  return request({ url: '/files/get_body', method: 'post', data });
}

// 保存文件内容
export function saveFileContent(path, content, encoding) {
  const data = new URLSearchParams();
  data.append('path', path);
  data.append('data', content);
  data.append('encoding', encoding || 'utf-8');
  return request({ url: '/files/save_body', method: 'post', data });
}

// 创建文件
export function createFile(path) {
  const data = new URLSearchParams();
  data.append('path', path);
  return request({ url: '/files/create_file', method: 'post', data });
}

// 创建目录
export function createDir(path) {
  const data = new URLSearchParams();
  data.append('path', path);
  return request({ url: '/files/create_dir', method: 'post', data });
}

// 删除文件/目录
export function deleteFile(path) {
  const data = new URLSearchParams();
  data.append('path', path);
  return request({ url: '/files/delete', method: 'post', data });
}

// 删除目录
export function deleteDir(path) {
  const data = new URLSearchParams();
  data.append('path', path);
  return request({ url: '/files/delete_dir', method: 'post', data });
}

// 重命名/移动文件
export function rename(source, target) {
  const data = new URLSearchParams();
  data.append('sfile', source);
  data.append('dfile', target);
  return request({ url: '/files/mv_file', method: 'post', data });
}

// 复制文件
export function copyFile(source, target) {
  const data = new URLSearchParams();
  data.append('sfile', source);
  data.append('dfile', target);
  return request({ url: '/files/copy_file', method: 'post', data });
}

// 移动文件 (同 rename)
export function moveFile(source, target) {
  return rename(source, target);
}

// 压缩文件
export function zipFile(sfile, dfile, stype, path) {
  const data = new URLSearchParams();
  data.append('sfile', sfile);
  data.append('dfile', dfile);
  data.append('type', stype);
  data.append('path', path || '');
  return request({ url: '/files/zip', method: 'post', data });
}

// 解压文件
export function unzipFile(sfile, dfile, stype, path) {
  const data = new URLSearchParams();
  data.append('sfile', sfile);
  data.append('dfile', dfile);
  data.append('type', stype);
  data.append('path', path || '');
  return request({ url: '/files/unzip', method: 'post', data });
}

// 获取文件权限
export function getFileAccess(filename) {
  const data = new URLSearchParams();
  data.append('filename', filename);
  return request({ url: '/files/file_access', method: 'post', data });
}

// 设置文件权限
export function setFileAccess(filename, user, access) {
  const data = new URLSearchParams();
  data.append('filename', filename);
  data.append('user', user);
  data.append('access', access);
  return request({ url: '/files/set_file_access', method: 'post', data });
}

// 获取目录大小
export function getDirSize(path) {
  const data = new URLSearchParams();
  data.append('path', path);
  return request({ url: '/files/get_dir_size', method: 'post', data });
}

// 远程下载文件
export function downloadFile(url, path, filename) {
  const data = new URLSearchParams();
  data.append('url', url);
  data.append('path', path);
  data.append('filename', filename);
  return request({ url: '/files/download_file', method: 'post', data });
}

// 批量粘贴操作
export function batchPaste(path, type) {
  const data = new URLSearchParams();
  data.append('path', path);
  data.append('type', type);
  return request({ url: '/files/batch_paste', method: 'post', data });
}

// 获取文件最新内容（日志尾部）
export function getLastBody(path, line) {
  const data = new URLSearchParams();
  data.append('path', path);
  data.append('line', line || '100');
  return request({ url: '/files/get_last_body', method: 'post', data });
}
