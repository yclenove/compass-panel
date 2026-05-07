# coding:utf-8

"""
插件 API 模块
提供插件管理的 RESTful API 接口
"""

import logging
import time

logger = logging.getLogger(__name__)


class PluginAPI:
    """插件 API 管理器

    提供插件的 RESTful API 接口管理功能，包括：
    - API 端点注册
    - 请求验证
    - 响应格式化
    - 错误处理
    """

    def __init__(self):
        """初始化插件 API 管理器"""
        self._endpoints = {}
        self._middleware = []
        self._error_handlers = {}
        self._request_log = []

    def register_endpoint(self, path, methods, handler, description=''):
        """注册 API 端点

        Args:
            path: API 路径
            methods: HTTP 方法列表
            handler: 处理函数
            description: 端点描述
        """
        key = f"{path}"
        self._endpoints[key] = {
            'path': path,
            'methods': methods,
            'handler': handler,
            'description': description,
            'created_at': time.time(),
            'call_count': 0,
            'last_called': None
        }
        logger.info(f"注册 API 端点: {path} [{', '.join(methods)}]")

    def unregister_endpoint(self, path):
        """注销 API 端点

        Args:
            path: API 路径
        """
        if path in self._endpoints:
            del self._endpoints[path]
            logger.info(f"注销 API 端点: {path}")

    def get_endpoints(self):
        """获取所有端点

        Returns:
            端点字典
        """
        return {
            path: {
                'methods': info['methods'],
                'description': info['description'],
                'call_count': info['call_count'],
                'last_called': info['last_called']
            }
            for path, info in self._endpoints.items()
        }

    def add_middleware(self, middleware_func):
        """添加中间件

        Args:
            middleware_func: 中间件函数
        """
        self._middleware.append(middleware_func)

    def register_error_handler(self, error_code, handler):
        """注册错误处理器

        Args:
            error_code: 错误码
            handler: 处理函数
        """
        self._error_handlers[error_code] = handler

    def handle_request(self, path, method, data=None, headers=None):
        """处理 API 请求

        Args:
            path: API 路径
            method: HTTP 方法
            data: 请求数据
            headers: 请求头

        Returns:
            响应字典
        """
        start_time = time.time()

        # 查找端点
        endpoint = self._endpoints.get(path)
        if not endpoint:
            return self._error_response(404, 'API 端点不存在')

        # 检查方法
        if method not in endpoint['methods']:
            return self._error_response(405, f'不支持的 HTTP 方法: {method}')

        # 执行中间件
        request = {
            'path': path,
            'method': method,
            'data': data or {},
            'headers': headers or {},
            'timestamp': time.time()
        }

        for middleware in self._middleware:
            try:
                result = middleware(request)
                if result is not None:
                    return result
            except Exception as e:
                logger.error(f"中间件执行错误: {e}")
                return self._error_response(500, '内部服务器错误')

        # 执行处理函数
        try:
            response = endpoint['handler'](request)

            # 更新统计
            endpoint['call_count'] += 1
            endpoint['last_called'] = time.time()

            # 记录请求日志
            duration = time.time() - start_time
            self._log_request(path, method, duration, response.get('status', 200))

            return response
        except Exception as e:
            logger.error(f"处理请求错误: {e}")
            error_handler = self._error_handlers.get(500)
            if error_handler:
                return error_handler(e)
            return self._error_response(500, str(e))

    def _error_response(self, code, message):
        """生成错误响应

        Args:
            code: 错误码
            message: 错误消息

        Returns:
            错误响应字典
        """
        return {
            'status': code,
            'error': message,
            'timestamp': time.time()
        }

    def _log_request(self, path, method, duration, status_code):
        """记录请求日志

        Args:
            path: API 路径
            method: HTTP 方法
            duration: 请求耗时
            status_code: 状态码
        """
        log_entry = {
            'path': path,
            'method': method,
            'duration': round(duration, 3),
            'status': status_code,
            'timestamp': time.time()
        }

        self._request_log.append(log_entry)

        # 保持日志数量在合理范围
        if len(self._request_log) > 10000:
            self._request_log = self._request_log[-5000:]

        logger.debug(f"API 请求: {method} {path} -> {status_code} ({duration:.3f}s)")

    def get_request_log(self, limit=100):
        """获取请求日志

        Args:
            limit: 返回数量限制

        Returns:
            请求日志列表
        """
        return self._request_log[-limit:]

    def get_stats(self):
        """获取 API 统计信息

        Returns:
            统计信息字典
        """
        total_requests = sum(
            info['call_count']
            for info in self._endpoints.values()
        )

        return {
            'total_endpoints': len(self._endpoints),
            'total_requests': total_requests,
            'endpoints': {
                path: {
                    'call_count': info['call_count'],
                    'last_called': info['last_called']
                }
                for path, info in self._endpoints.items()
            }
        }


class PluginAPIError(Exception):
    """插件 API 异常"""

    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(message)


def api_response(success=True, data=None, message='', code=200):
    """生成标准 API 响应

    Args:
        success: 是否成功
        data: 响应数据
        message: 响应消息
        code: 状态码

    Returns:
        标准响应字典
    """
    return {
        'status': code,
        'success': success,
        'data': data,
        'message': message,
        'timestamp': time.time()
    }


def validate_api_key(api_key, valid_keys):
    """验证 API 密钥

    Args:
        api_key: 提交的 API 密钥
        valid_keys: 有效密钥列表

    Returns:
        是否验证通过
    """
    if not api_key or not valid_keys:
        return False
    return api_key in valid_keys


# 全局插件 API 实例
_plugin_api = PluginAPI()


def get_plugin_api():
    """获取全局插件 API 实例"""
    return _plugin_api
