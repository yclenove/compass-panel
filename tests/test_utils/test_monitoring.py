# coding:utf-8
"""监控告警模块测试"""

import pytest
import time
from utils.monitoring import AlertRule, AlertManager, SystemMonitor


class TestAlertRule:
    """告警规则测试"""

    def test_create_rule(self):
        """测试创建规则"""
        rule = AlertRule('test', 'gt', 80, severity='warning')
        assert rule.name == 'test'
        assert rule.condition == 'gt'
        assert rule.threshold == 80
        assert rule.severity == 'warning'
        assert rule.enabled is True

    def test_rule_defaults(self):
        """测试规则默认值"""
        rule = AlertRule('test', 'gt', 80)
        assert rule.duration == 0
        assert rule.severity == 'warning'
        assert rule.trigger_count == 0
        assert rule.last_triggered is None


class TestAlertManager:
    """告警管理器测试"""

    def test_add_rule(self):
        """测试添加规则"""
        manager = AlertManager()
        rule = AlertRule('test', 'gt', 80)
        manager.add_rule(rule)
        assert 'test' in manager._rules

    def test_remove_rule(self):
        """测试移除规则"""
        manager = AlertManager()
        rule = AlertRule('test', 'gt', 80)
        manager.add_rule(rule)
        manager.remove_rule('test')
        assert 'test' not in manager._rules

    def test_enable_disable_rule(self):
        """测试启用/禁用规则"""
        manager = AlertManager()
        rule = AlertRule('test', 'gt', 80)
        manager.add_rule(rule)

        manager.disable_rule('test')
        assert manager._rules['test'].enabled is False

        manager.enable_rule('test')
        assert manager._rules['test'].enabled is True

    def test_evaluate_gt(self):
        """测试大于条件评估"""
        manager = AlertManager()
        # 禁用告警抑制
        manager._suppress_duration = 0

        rule = AlertRule('cpu_high', 'gt', 80, severity='warning')
        manager.add_rule(rule)

        # 值超过阈值
        alerts = manager.evaluate('cpu', 90)
        assert len(alerts) == 1
        assert alerts[0]['rule'] == 'cpu_high'

        # 值未超过阈值
        alerts = manager.evaluate('cpu', 70)
        assert len(alerts) == 0

    def test_evaluate_lt(self):
        """测试小于条件评估"""
        manager = AlertManager()
        manager._suppress_duration = 0

        rule = AlertRule('disk_low', 'lt', 10, severity='critical')
        manager.add_rule(rule)

        # 值低于阈值
        alerts = manager.evaluate('disk_free', 5)
        assert len(alerts) == 1

        # 值高于阈值
        alerts = manager.evaluate('disk_free', 20)
        assert len(alerts) == 0

    def test_evaluate_eq(self):
        """测试等于条件评估"""
        manager = AlertManager()
        manager._suppress_duration = 0

        rule = AlertRule('status', 'eq', 0, severity='critical')
        manager.add_rule(rule)

        alerts = manager.evaluate('service_status', 0)
        assert len(alerts) == 1

    def test_alert_suppression(self):
        """测试告警抑制"""
        manager = AlertManager()
        manager._suppress_duration = 60

        rule = AlertRule('test', 'gt', 80)
        manager.add_rule(rule)

        # 第一次应该触发
        alerts = manager.evaluate('test', 90)
        assert len(alerts) == 1

        # 立即再次触发应该被抑制
        alerts = manager.evaluate('test', 90)
        assert len(alerts) == 0

    def test_disabled_rule(self):
        """测试禁用规则不触发"""
        manager = AlertManager()
        manager._suppress_duration = 0

        rule = AlertRule('test', 'gt', 80)
        manager.add_rule(rule)
        manager.disable_rule('test')

        alerts = manager.evaluate('test', 90)
        assert len(alerts) == 0

    def test_get_alerts(self):
        """测试获取告警记录"""
        manager = AlertManager()
        manager._suppress_duration = 0

        rule = AlertRule('test', 'gt', 80)
        manager.add_rule(rule)
        manager.evaluate('test', 90)

        alerts = manager.get_alerts()
        assert len(alerts) == 1

    def test_get_rules(self):
        """测试获取规则列表"""
        manager = AlertManager()
        rule = AlertRule('test', 'gt', 80)
        manager.add_rule(rule)

        rules = manager.get_rules()
        assert 'test' in rules

    def test_clear_alerts(self):
        """测试清空告警记录"""
        manager = AlertManager()
        manager._suppress_duration = 0

        rule = AlertRule('test', 'gt', 80)
        manager.add_rule(rule)
        manager.evaluate('test', 90)

        manager.clear_alerts()
        alerts = manager.get_alerts()
        assert len(alerts) == 0

    def test_add_channel(self):
        """测试添加通知渠道"""
        manager = AlertManager()
        manager.add_channel('email', 'email', {'smtp_host': 'smtp.example.com'})
        assert 'email' in manager._channels

    def test_remove_channel(self):
        """测试移除通知渠道"""
        manager = AlertManager()
        manager.add_channel('email', 'email', {})
        manager.remove_channel('email')
        assert 'email' not in manager._channels


class TestSystemMonitor:
    """系统监控器测试"""

    def test_record_metric(self):
        """测试记录指标"""
        monitor = SystemMonitor()
        monitor._record_metric('test', 50)

        metrics = monitor.get_metrics('test')
        assert len(metrics) == 1
        assert metrics[0]['value'] == 50

    def test_get_latest_metrics(self):
        """测试获取最新指标"""
        monitor = SystemMonitor()
        monitor._record_metric('cpu', 50)
        monitor._record_metric('cpu', 60)
        monitor._record_metric('memory', 70)

        latest = monitor.get_latest_metrics()
        assert latest['cpu'] == 60
        assert latest['memory'] == 70

    def test_metrics_history_limit(self):
        """测试指标历史限制"""
        monitor = SystemMonitor()

        for i in range(1500):
            monitor._record_metric('test', i)

        metrics = monitor.get_metrics('test')
        assert len(metrics) <= 1000
