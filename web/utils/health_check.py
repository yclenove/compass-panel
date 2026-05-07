# coding:utf-8

"""
健康检查模块
提供系统健康状态检查和监控功能
"""

import time
import psutil
from datetime import datetime
from collections import deque


class HealthChecker:
    """系统健康检查器

    检查系统各项指标，包括：
    - CPU 使用率
    - 内存使用率
    - 磁盘使用率
    - 网络连接
    - 服务状态
    """

    def __init__(self):
        """初始化健康检查器"""
        self._checks = {}
        self._history = deque(maxlen=1000)
        self._alerts = []
        self._thresholds = {
            'cpu_warning': 70,
            'cpu_critical': 90,
            'memory_warning': 70,
            'memory_critical': 90,
            'disk_warning': 80,
            'disk_critical': 95,
        }
        self._alert_callbacks = []

    def register_check(self, name, check_func, description=''):
        """注册健康检查项

        Args:
            name: 检查项名称
            check_func: 检查函数，返回 (status, message, details)
            description: 检查项描述
        """
        self._checks[name] = {
            'func': check_func,
            'description': description,
            'last_check': None,
            'last_status': None,
            'last_message': None
        }

    def set_threshold(self, key, value):
        """设置告警阈值

        Args:
            key: 阈值键名
            value: 阈值
        """
        self._thresholds[key] = value

    def add_alert_callback(self, callback):
        """添加告警回调

        Args:
            callback: 回调函数，接收 (check_name, status, message)
        """
        self._alert_callbacks.append(callback)

    def check_all(self):
        """执行所有健康检查

        Returns:
            健康检查结果字典
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'checks': {}
        }

        for name, check_info in self._checks.items():
            try:
                status, message, details = check_info['func']()
                results['checks'][name] = {
                    'status': status,
                    'message': message,
                    'details': details,
                    'description': check_info['description']
                }

                check_info['last_check'] = time.time()
                check_info['last_status'] = status
                check_info['last_message'] = message

                if status == 'critical':
                    results['status'] = 'critical'
                    self._trigger_alert(name, status, message)
                elif status == 'warning' and results['status'] != 'critical':
                    results['status'] = 'warning'
                    self._trigger_alert(name, status, message)

            except Exception as e:
                results['checks'][name] = {
                    'status': 'error',
                    'message': str(e),
                    'details': None,
                    'description': check_info['description']
                }
                results['status'] = 'error'

        self._history.append(results)
        return results

    def check_cpu(self):
        """检查 CPU 使用率

        Returns:
            (status, message, details)
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            details = {
                'percent': cpu_percent,
                'count': cpu_count,
                'freq_current': cpu_freq.current if cpu_freq else None,
                'freq_max': cpu_freq.max if cpu_freq else None
            }

            if cpu_percent >= self._thresholds['cpu_critical']:
                return 'critical', f'CPU 使用率过高: {cpu_percent}%', details
            elif cpu_percent >= self._thresholds['cpu_warning']:
                return 'warning', f'CPU 使用率较高: {cpu_percent}%', details
            else:
                return 'healthy', f'CPU 使用率正常: {cpu_percent}%', details

        except Exception as e:
            return 'error', f'CPU 检查失败: {str(e)}', None

    def check_memory(self):
        """检查内存使用率

        Returns:
            (status, message, details)
        """
        try:
            memory = psutil.virtual_memory()

            details = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            }

            if memory.percent >= self._thresholds['memory_critical']:
                return 'critical', f'内存使用率过高: {memory.percent}%', details
            elif memory.percent >= self._thresholds['memory_warning']:
                return 'warning', f'内存使用率较高: {memory.percent}%', details
            else:
                return 'healthy', f'内存使用率正常: {memory.percent}%', details

        except Exception as e:
            return 'error', f'内存检查失败: {str(e)}', None

    def check_disk(self, path='/'):
        """检查磁盘使用率

        Args:
            path: 磁盘路径

        Returns:
            (status, message, details)
        """
        try:
            disk = psutil.disk_usage(path)

            details = {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }

            if disk.percent >= self._thresholds['disk_critical']:
                return 'critical', f'磁盘使用率过高: {disk.percent}%', details
            elif disk.percent >= self._thresholds['disk_warning']:
                return 'warning', f'磁盘使用率较高: {disk.percent}%', details
            else:
                return 'healthy', f'磁盘使用率正常: {disk.percent}%', details

        except Exception as e:
            return 'error', f'磁盘检查失败: {str(e)}', None

    def check_network(self):
        """检查网络连接

        Returns:
            (status, message, details)
        """
        try:
            net_io = psutil.net_io_counters()
            connections = psutil.net_connections()

            details = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'connections': len(connections)
            }

            return 'healthy', '网络连接正常', details

        except Exception as e:
            return 'error', f'网络检查失败: {str(e)}', None

    def check_service(self, service_name, port=None):
        """检查服务状态

        Args:
            service_name: 服务名称
            port: 服务端口（可选）

        Returns:
            (status, message, details)
        """
        try:
            # 检查进程是否存在
            for proc in psutil.process_iter(['pid', 'name']):
                if service_name.lower() in proc.info['name'].lower():
                    details = {
                        'pid': proc.info['pid'],
                        'name': proc.info['name']
                    }

                    if port:
                        # 检查端口是否监听
                        import socket
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        result = sock.connect_ex(('localhost', port))
                        sock.close()

                        if result == 0:
                            details['port'] = port
                            details['port_status'] = 'listening'
                            return 'healthy', f'{service_name} 服务运行正常', details
                        else:
                            details['port'] = port
                            details['port_status'] = 'not_listening'
                            return 'warning', f'{service_name} 端口 {port} 未监听', details

                    return 'healthy', f'{service_name} 服务运行正常', details

            return 'critical', f'{service_name} 服务未运行', None

        except Exception as e:
            return 'error', f'{service_name} 检查失败: {str(e)}', None

    def get_history(self, limit=100):
        """获取检查历史

        Args:
            limit: 返回数量限制

        Returns:
            历史记录列表
        """
        return list(self._history)[-limit:]

    def get_alerts(self, limit=100):
        """获取告警记录

        Args:
            limit: 返回数量限制

        Returns:
            告警记录列表
        """
        return self._alerts[-limit:]

    def _trigger_alert(self, check_name, status, message):
        """触发告警

        Args:
            check_name: 检查项名称
            status: 状态
            message: 消息
        """
        alert = {
            'timestamp': datetime.now().isoformat(),
            'check': check_name,
            'status': status,
            'message': message
        }
        self._alerts.append(alert)

        # 调用回调
        for callback in self._alert_callbacks:
            try:
                callback(check_name, status, message)
            except Exception:
                pass

    def get_summary(self):
        """获取健康状态摘要

        Returns:
            摘要字典
        """
        if not self._history:
            return {'status': 'unknown', 'message': '尚未执行健康检查'}

        latest = self._history[-1]
        return {
            'status': latest['status'],
            'timestamp': latest['timestamp'],
            'checks': {
                name: {
                    'status': check['status'],
                    'message': check['message']
                }
                for name, check in latest['checks'].items()
            }
        }


# 全局健康检查器实例
_health_checker = HealthChecker()


def get_health_checker():
    """获取全局健康检查器"""
    return _health_checker


def setup_default_checks():
    """设置默认健康检查项"""
    checker = get_health_checker()
    checker.register_check('cpu', checker.check_cpu, 'CPU 使用率检查')
    checker.register_check('memory', checker.check_memory, '内存使用率检查')
    checker.register_check('disk', checker.check_disk, '磁盘使用率检查')
    checker.register_check('network', checker.check_network, '网络连接检查')
