# coding:utf-8

"""
监控告警模块
提供系统监控和告警功能
"""

import time
import json
import smtplib
import logging
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class AlertRule:
    """告警规则"""

    def __init__(self, name, condition, threshold, duration=0, severity='warning'):
        """初始化告警规则

        Args:
            name: 规则名称
            condition: 条件表达式
            threshold: 阈值
            duration: 持续时间（秒）
            severity: 严重程度 (info, warning, critical)
        """
        self.name = name
        self.condition = condition
        self.threshold = threshold
        self.duration = duration
        self.severity = severity
        self.enabled = True
        self.last_triggered = None
        self.trigger_count = 0


class AlertManager:
    """告警管理器

    管理告警规则和通知渠道
    """

    def __init__(self):
        """初始化告警管理器"""
        self._rules = {}
        self._channels = {}
        self._alerts = []
        self._lock = threading.RLock()  # 使用可重入锁避免死锁
        self._suppress_duration = 300  # 告警抑制时间（秒）
        self._last_alerts = {}  # {rule_name: last_alert_time}

    def add_rule(self, rule):
        """添加告警规则

        Args:
            rule: AlertRule 实例
        """
        with self._lock:
            self._rules[rule.name] = rule
            logger.info(f"添加告警规则: {rule.name}")

    def remove_rule(self, name):
        """移除告警规则

        Args:
            name: 规则名称
        """
        with self._lock:
            if name in self._rules:
                del self._rules[name]
                logger.info(f"移除告警规则: {name}")

    def enable_rule(self, name):
        """启用告警规则

        Args:
            name: 规则名称
        """
        with self._lock:
            if name in self._rules:
                self._rules[name].enabled = True

    def disable_rule(self, name):
        """禁用告警规则

        Args:
            name: 规则名称
        """
        with self._lock:
            if name in self._rules:
                self._rules[name].enabled = False

    def add_channel(self, name, channel_type, config):
        """添加通知渠道

        Args:
            name: 渠道名称
            channel_type: 渠道类型 (email, webhook, log)
            config: 渠道配置
        """
        with self._lock:
            self._channels[name] = {
                'type': channel_type,
                'config': config,
                'enabled': True
            }
            logger.info(f"添加通知渠道: {name} ({channel_type})")

    def remove_channel(self, name):
        """移除通知渠道

        Args:
            name: 渠道名称
        """
        with self._lock:
            if name in self._channels:
                del self._channels[name]

    def evaluate(self, metric_name, value):
        """评估指标值

        Args:
            metric_name: 指标名称
            value: 指标值

        Returns:
            触发的告警列表
        """
        triggered = []

        with self._lock:
            for rule_name, rule in self._rules.items():
                if not rule.enabled:
                    continue

                if rule.condition == 'gt' and value > rule.threshold:
                    if self._should_alert(rule_name):
                        alert = self._create_alert(rule, metric_name, value)
                        triggered.append(alert)

                elif rule.condition == 'lt' and value < rule.threshold:
                    if self._should_alert(rule_name):
                        alert = self._create_alert(rule, metric_name, value)
                        triggered.append(alert)

                elif rule.condition == 'eq' and value == rule.threshold:
                    if self._should_alert(rule_name):
                        alert = self._create_alert(rule, metric_name, value)
                        triggered.append(alert)

        # 发送通知
        for alert in triggered:
            self._send_notifications(alert)

        return triggered

    def _should_alert(self, rule_name):
        """检查是否应该发送告警（避免重复告警）

        Args:
            rule_name: 规则名称

        Returns:
            是否应该告警
        """
        now = time.time()
        last_alert = self._last_alerts.get(rule_name, 0)

        if now - last_alert >= self._suppress_duration:
            self._last_alerts[rule_name] = now
            return True

        return False

    def _create_alert(self, rule, metric_name, value):
        """创建告警

        Args:
            rule: 告警规则
            metric_name: 指标名称
            value: 指标值

        Returns:
            告警字典
        """
        alert = {
            'timestamp': datetime.now().isoformat(),
            'rule': rule.name,
            'severity': rule.severity,
            'metric': metric_name,
            'value': value,
            'threshold': rule.threshold,
            'condition': rule.condition,
            'message': f'{metric_name} 当前值 {value} {rule.condition} 阈值 {rule.threshold}'
        }

        with self._lock:
            self._alerts.append(alert)
            rule.trigger_count += 1
            rule.last_triggered = time.time()

        logger.warning(f"告警触发: {alert['message']}")
        return alert

    def _send_notifications(self, alert):
        """发送告警通知

        Args:
            alert: 告警信息
        """
        with self._lock:
            channels = self._channels.copy()

        for channel_name, channel in channels.items():
            if not channel['enabled']:
                continue

            try:
                if channel['type'] == 'email':
                    self._send_email_alert(channel['config'], alert)
                elif channel['type'] == 'webhook':
                    self._send_webhook_alert(channel['config'], alert)
                elif channel['type'] == 'log':
                    self._send_log_alert(alert)
            except Exception as e:
                logger.error(f"发送通知失败 ({channel_name}): {e}")

    def _send_email_alert(self, config, alert):
        """发送邮件告警

        Args:
            config: 邮件配置
            alert: 告警信息
        """
        smtp_host = config.get('smtp_host')
        smtp_port = config.get('smtp_port', 587)
        username = config.get('username')
        password = config.get('password')
        to_addrs = config.get('to', [])
        use_tls = config.get('use_tls', True)

        if not all([smtp_host, username, password, to_addrs]):
            logger.error("邮件配置不完整")
            return

        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = ', '.join(to_addrs)
        msg['Subject'] = f"[{alert['severity'].upper()}] 系统告警: {alert['rule']}"

        body = f"""
告警详情:
- 规则: {alert['rule']}
- 严重程度: {alert['severity']}
- 指标: {alert['metric']}
- 当前值: {alert['value']}
- 阈值: {alert['threshold']}
- 时间: {alert['timestamp']}
- 消息: {alert['message']}
        """

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        try:
            server = smtplib.SMTP(smtp_host, smtp_port)
            if use_tls:
                server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            logger.info(f"邮件告警已发送: {alert['rule']}")
        except Exception as e:
            logger.error(f"发送邮件失败: {e}")

    def _send_webhook_alert(self, config, alert):
        """发送 Webhook 告警

        Args:
            config: Webhook 配置
            alert: 告警信息
        """
        import subprocess

        url = config.get('url')
        if not url:
            return

        data = json.dumps(alert, ensure_ascii=False)
        cmd = [
            'curl', '-s', '-X', 'POST',
            '-H', 'Content-Type: application/json',
            '-d', data,
            url
        ]

        try:
            subprocess.run(cmd, capture_output=True, timeout=10)
            logger.info(f"Webhook 告警已发送: {alert['rule']}")
        except Exception as e:
            logger.error(f"发送 Webhook 失败: {e}")

    def _send_log_alert(self, alert):
        """记录日志告警

        Args:
            alert: 告警信息
        """
        logger.warning(f"ALERT: {json.dumps(alert, ensure_ascii=False)}")

    def get_alerts(self, limit=100, severity=None):
        """获取告警记录

        Args:
            limit: 返回数量限制
            severity: 严重程度过滤

        Returns:
            告警记录列表
        """
        with self._lock:
            alerts = self._alerts.copy()

        if severity:
            alerts = [a for a in alerts if a['severity'] == severity]

        return alerts[-limit:]

    def get_rules(self):
        """获取所有规则

        Returns:
            规则字典
        """
        with self._lock:
            return {
                name: {
                    'name': rule.name,
                    'condition': rule.condition,
                    'threshold': rule.threshold,
                    'duration': rule.duration,
                    'severity': rule.severity,
                    'enabled': rule.enabled,
                    'trigger_count': rule.trigger_count,
                    'last_triggered': rule.last_triggered
                }
                for name, rule in self._rules.items()
            }

    def get_channels(self):
        """获取所有通知渠道

        Returns:
            渠道字典
        """
        with self._lock:
            return self._channels.copy()

    def clear_alerts(self):
        """清空告警记录"""
        with self._lock:
            self._alerts.clear()


class SystemMonitor:
    """系统监控器

    定期收集系统指标并触发告警
    """

    def __init__(self, alert_manager=None, interval=60):
        """初始化系统监控器

        Args:
            alert_manager: 告警管理器
            interval: 监控间隔（秒）
        """
        self._alert_manager = alert_manager or AlertManager()
        self._interval = interval
        self._running = False
        self._thread = None
        self._metrics_history = defaultdict(lambda: deque(maxlen=1000))

    def start(self):
        """启动监控"""
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("系统监控已启动")

    def stop(self):
        """停止监控"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("系统监控已停止")

    def _monitor_loop(self):
        """监控循环"""
        while self._running:
            try:
                self._collect_metrics()
            except Exception as e:
                logger.error(f"监控收集错误: {e}")

            time.sleep(self._interval)

    def _collect_metrics(self):
        """收集系统指标"""
        try:
            import psutil

            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self._record_metric('cpu_percent', cpu_percent)
            self._alert_manager.evaluate('cpu_percent', cpu_percent)

            # 内存
            memory = psutil.virtual_memory()
            self._record_metric('memory_percent', memory.percent)
            self._alert_manager.evaluate('memory_percent', memory.percent)

            # 磁盘
            disk = psutil.disk_usage('/')
            self._record_metric('disk_percent', disk.percent)
            self._alert_manager.evaluate('disk_percent', disk.percent)

            # 网络
            net_io = psutil.net_io_counters()
            self._record_metric('bytes_sent', net_io.bytes_sent)
            self._record_metric('bytes_recv', net_io.bytes_recv)

        except ImportError:
            logger.warning("psutil 未安装，无法收集系统指标")
        except Exception as e:
            logger.error(f"收集指标失败: {e}")

    def _record_metric(self, name, value):
        """记录指标

        Args:
            name: 指标名称
            value: 指标值
        """
        self._metrics_history[name].append({
            'timestamp': time.time(),
            'value': value
        })

    def get_metrics(self, name, limit=100):
        """获取指标历史

        Args:
            name: 指标名称
            limit: 返回数量

        Returns:
            指标历史列表
        """
        return list(self._metrics_history.get(name, []))[-limit:]

    def get_latest_metrics(self):
        """获取最新指标

        Returns:
            最新指标字典
        """
        result = {}
        for name, history in self._metrics_history.items():
            if history:
                result[name] = history[-1]['value']
        return result


# 全局实例
_alert_manager = AlertManager()
_system_monitor = SystemMonitor(_alert_manager)


def get_alert_manager():
    """获取全局告警管理器"""
    return _alert_manager


def get_system_monitor():
    """获取全局系统监控器"""
    return _system_monitor


def setup_default_alerts():
    """设置默认告警规则"""
    manager = get_alert_manager()

    # CPU 告警
    manager.add_rule(AlertRule(
        'cpu_warning',
        'gt', 70,
        severity='warning'
    ))
    manager.add_rule(AlertRule(
        'cpu_critical',
        'gt', 90,
        severity='critical'
    ))

    # 内存告警
    manager.add_rule(AlertRule(
        'memory_warning',
        'gt', 70,
        severity='warning'
    ))
    manager.add_rule(AlertRule(
        'memory_critical',
        'gt', 90,
        severity='critical'
    ))

    # 磁盘告警
    manager.add_rule(AlertRule(
        'disk_warning',
        'gt', 80,
        severity='warning'
    ))
    manager.add_rule(AlertRule(
        'disk_critical',
        'gt', 95,
        severity='critical'
    ))

    # 添加日志通知渠道
    manager.add_channel('log', 'log', {})
