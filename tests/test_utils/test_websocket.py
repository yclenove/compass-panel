# coding:utf-8
"""WebSocket 模块测试"""

import pytest
from utils.websocket import WebSocketManager, WebSocketMessage


class TestWebSocketManager:
    """WebSocket 管理器测试"""

    def test_add_connection(self):
        """测试添加连接"""
        manager = WebSocketManager()
        manager.add_connection('client1', 'mock_connection')
        assert manager.get_connection_count() == 1

    def test_remove_connection(self):
        """测试移除连接"""
        manager = WebSocketManager()
        manager.add_connection('client1', 'mock_connection')
        manager.remove_connection('client1')
        assert manager.get_connection_count() == 0

    def test_get_connection(self):
        """测试获取连接"""
        manager = WebSocketManager()
        manager.add_connection('client1', 'mock_connection')
        assert manager.get_connection('client1') == 'mock_connection'
        assert manager.get_connection('nonexistent') is None

    def test_subscribe(self):
        """测试订阅频道"""
        manager = WebSocketManager()
        manager.add_connection('client1', 'mock_connection')
        manager.subscribe('client1', 'channel1')

        subscribers = manager.get_channel_subscribers('channel1')
        assert 'client1' in subscribers

    def test_unsubscribe(self):
        """测试取消订阅"""
        manager = WebSocketManager()
        manager.add_connection('client1', 'mock_connection')
        manager.subscribe('client1', 'channel1')
        manager.unsubscribe('client1', 'channel1')

        subscribers = manager.get_channel_subscribers('channel1')
        assert 'client1' not in subscribers

    def test_get_client_channels(self):
        """测试获取客户端订阅的频道"""
        manager = WebSocketManager()
        manager.add_connection('client1', 'mock_connection')
        manager.subscribe('client1', 'channel1')
        manager.subscribe('client1', 'channel2')

        channels = manager.get_client_channels('client1')
        assert 'channel1' in channels
        assert 'channel2' in channels

    def test_broadcast(self):
        """测试广播消息"""
        manager = WebSocketManager()

        class MockConnection:
            def __init__(self):
                self.messages = []

            def send(self, message):
                self.messages.append(message)

        conn1 = MockConnection()
        conn2 = MockConnection()

        manager.add_connection('client1', conn1)
        manager.add_connection('client2', conn2)

        manager.broadcast('test message')
        assert len(conn1.messages) == 1
        assert len(conn2.messages) == 1

    def test_broadcast_to_channel(self):
        """测试广播到频道"""
        manager = WebSocketManager()

        class MockConnection:
            def __init__(self):
                self.messages = []

            def send(self, message):
                self.messages.append(message)

        conn1 = MockConnection()
        conn2 = MockConnection()

        manager.add_connection('client1', conn1)
        manager.add_connection('client2', conn2)

        manager.subscribe('client1', 'channel1')
        manager.subscribe('client2', 'channel2')

        manager.broadcast_to_channel('channel1', 'channel message')
        assert len(conn1.messages) == 1
        assert len(conn2.messages) == 0

    def test_update_heartbeat(self):
        """测试更新心跳"""
        manager = WebSocketManager()
        manager.add_connection('client1', 'mock_connection')
        manager.update_heartbeat('client1')
        # 不应该抛出异常

    def test_get_stats(self):
        """测试获取统计信息"""
        manager = WebSocketManager()
        manager.add_connection('client1', 'mock_connection')
        manager.subscribe('client1', 'channel1')

        stats = manager.get_stats()
        assert stats['connections'] == 1
        assert stats['channels'] == 1

    def test_remove_connection_cleans_channels(self):
        """测试移除连接时清理频道"""
        manager = WebSocketManager()
        manager.add_connection('client1', 'mock_connection')
        manager.subscribe('client1', 'channel1')
        manager.subscribe('client1', 'channel2')

        manager.remove_connection('client1')

        assert 'client1' not in manager.get_channel_subscribers('channel1')
        assert 'client1' not in manager.get_channel_subscribers('channel2')


class TestWebSocketMessage:
    """WebSocket 消息格式化测试"""

    def test_format_message(self):
        """测试格式化消息"""
        msg = WebSocketMessage.format_message('test', {'key': 'value'})
        assert msg['type'] == 'test'
        assert msg['data'] == {'key': 'value'}
        assert 'timestamp' in msg

    def test_format_message_with_channel(self):
        """测试带频道的消息"""
        msg = WebSocketMessage.format_message('test', 'data', channel='channel1')
        assert msg['channel'] == 'channel1'

    def test_system_info(self):
        """测试系统信息消息"""
        msg = WebSocketMessage.system_info({'cpu': 50})
        assert msg['type'] == 'system_info'
        assert msg['data'] == {'cpu': 50}

    def test_task_update(self):
        """测试任务更新消息"""
        msg = WebSocketMessage.task_update('task1', 'completed', progress=100)
        assert msg['type'] == 'task_update'
        assert msg['data']['task_id'] == 'task1'
        assert msg['data']['status'] == 'completed'
        assert msg['data']['progress'] == 100

    def test_log_entry(self):
        """测试日志条目消息"""
        msg = WebSocketMessage.log_entry('error', 'Something failed')
        assert msg['type'] == 'log_entry'
        assert msg['data']['log_type'] == 'error'
        assert msg['data']['content'] == 'Something failed'

    def test_error(self):
        """测试错误消息"""
        msg = WebSocketMessage.error('Error occurred', code=500)
        assert msg['type'] == 'error'
        assert msg['data']['message'] == 'Error occurred'
        assert msg['data']['code'] == 500

    def test_success(self):
        """测试成功消息"""
        msg = WebSocketMessage.success('Operation completed', data={'id': 1})
        assert msg['type'] == 'success'
        assert msg['data']['message'] == 'Operation completed'
        assert msg['data']['data'] == {'id': 1}
