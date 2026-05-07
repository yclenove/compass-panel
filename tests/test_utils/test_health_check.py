# coding:utf-8
"""健康检查模块测试"""

import pytest
from utils.health_check import HealthChecker


class TestHealthChecker:
    """健康检查器测试"""

    def test_register_check(self):
        """测试注册检查项"""
        checker = HealthChecker()
        checker.register_check('test', lambda: ('healthy', 'OK', {}), '测试检查')
        assert 'test' in checker._checks

    def test_set_threshold(self):
        """测试设置阈值"""
        checker = HealthChecker()
        checker.set_threshold('cpu_warning', 80)
        assert checker._thresholds['cpu_warning'] == 80

    def test_check_cpu(self):
        """测试 CPU 检查"""
        checker = HealthChecker()
        status, message, details = checker.check_cpu()
        assert status in ['healthy', 'warning', 'critical', 'error']
        assert isinstance(message, str)

    def test_check_memory(self):
        """测试内存检查"""
        checker = HealthChecker()
        status, message, details = checker.check_memory()
        assert status in ['healthy', 'warning', 'critical', 'error']
        assert isinstance(message, str)

    def test_check_disk(self):
        """测试磁盘检查"""
        checker = HealthChecker()
        status, message, details = checker.check_disk()
        assert status in ['healthy', 'warning', 'critical', 'error']
        assert isinstance(message, str)

    def test_check_network(self):
        """测试网络检查"""
        checker = HealthChecker()
        status, message, details = checker.check_network()
        assert status in ['healthy', 'warning', 'critical', 'error']
        assert isinstance(message, str)

    def test_check_all(self):
        """测试执行所有检查"""
        checker = HealthChecker()
        checker.register_check('cpu', checker.check_cpu, 'CPU检查')
        checker.register_check('memory', checker.check_memory, '内存检查')

        result = checker.check_all()
        assert 'timestamp' in result
        assert 'status' in result
        assert 'checks' in result
        assert 'cpu' in result['checks']
        assert 'memory' in result['checks']

    def test_get_history(self):
        """测试获取历史记录"""
        checker = HealthChecker()
        checker.register_check('test', lambda: ('healthy', 'OK', {}), '测试')
        checker.check_all()

        history = checker.get_history()
        assert len(history) == 1

    def test_get_summary(self):
        """测试获取摘要"""
        checker = HealthChecker()
        checker.register_check('test', lambda: ('healthy', 'OK', {}), '测试')
        checker.check_all()

        summary = checker.get_summary()
        assert 'status' in summary
        assert 'timestamp' in summary

    def test_alert_callback(self):
        """测试告警回调"""
        checker = HealthChecker()
        alerts_received = []

        def callback(name, status, message):
            alerts_received.append((name, status, message))

        checker.add_alert_callback(callback)
        checker.register_check('test', lambda: ('critical', 'ERROR', {}), '测试')
        checker.check_all()

        assert len(alerts_received) == 1
        assert alerts_received[0][0] == 'test'

    def test_custom_check(self):
        """测试自定义检查项"""
        checker = HealthChecker()

        def custom_check():
            return 'healthy', '自定义检查通过', {'custom': True}

        checker.register_check('custom', custom_check, '自定义检查')
        result = checker.check_all()

        assert result['checks']['custom']['status'] == 'healthy'
        assert result['checks']['custom']['details'] == {'custom': True}
