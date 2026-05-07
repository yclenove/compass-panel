# coding:utf-8

"""
WebSocket 实时通信模块
提供 WebSocket 服务器和客户端支持
"""

import json
import time
import threading
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket 连接管理器

    管理所有 WebSocket 连接，支持：
    - 连接管理（添加、删除、查找）
    - 消息广播
    - 频道订阅
    - 心跳检测
    """

    def __init__(self):
        """初始化 WebSocket 管理器"""
        self._connections = {}  # {client_id: connection}
        self._channels = defaultdict(set)  # {channel: {client_id}}
        self._lock = threading.Lock()
        self._heartbeat_interval = 30  # 心跳间隔（秒）
        self._heartbeat_thread = None
        self._running = False

    def start(self):
        """启动心跳检测"""
        self._running = True
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True
        )
        self._heartbeat_thread.start()
        logger.info("WebSocket 管理器已启动")

    def stop(self):
        """停止心跳检测"""
        self._running = False
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=5)
        logger.info("WebSocket 管理器已停止")

    def add_connection(self, client_id, connection):
        """添加连接

        Args:
            client_id: 客户端 ID
            connection: 连接对象
        """
        with self._lock:
            self._connections[client_id] = {
                'connection': connection,
                'connected_at': time.time(),
                'last_heartbeat': time.time(),
                'channels': set()
            }
            logger.info(f"客户端 {client_id} 已连接")

    def remove_connection(self, client_id):
        """移除连接

        Args:
            client_id: 客户端 ID
        """
        with self._lock:
            if client_id in self._connections:
                # 从所有频道中移除
                for channel in self._connections[client_id]['channels']:
                    self._channels[channel].discard(client_id)

                del self._connections[client_id]
                logger.info(f"客户端 {client_id} 已断开")

    def get_connection(self, client_id):
        """获取连接

        Args:
            client_id: 客户端 ID

        Returns:
            连接对象或 None
        """
        with self._lock:
            if client_id in self._connections:
                return self._connections[client_id]['connection']
            return None

    def get_connection_count(self):
        """获取连接数

        Returns:
            连接数
        """
        with self._lock:
            return len(self._connections)

    def subscribe(self, client_id, channel):
        """订阅频道

        Args:
            client_id: 客户端 ID
            channel: 频道名称
        """
        with self._lock:
            if client_id in self._connections:
                self._channels[channel].add(client_id)
                self._connections[client_id]['channels'].add(channel)
                logger.debug(f"客户端 {client_id} 订阅频道 {channel}")

    def unsubscribe(self, client_id, channel):
        """取消订阅

        Args:
            client_id: 客户端 ID
            channel: 频道名称
        """
        with self._lock:
            self._channels[channel].discard(client_id)
            if client_id in self._connections:
                self._connections[client_id]['channels'].discard(channel)
                logger.debug(f"客户端 {client_id} 取消订阅频道 {channel}")

    def send_to(self, client_id, message):
        """发送消息给指定客户端

        Args:
            client_id: 客户端 ID
            message: 消息内容（字典或字符串）

        Returns:
            是否发送成功
        """
        with self._lock:
            if client_id not in self._connections:
                return False

            conn_info = self._connections[client_id]
            connection = conn_info['connection']

            try:
                if isinstance(message, dict):
                    message = json.dumps(message, ensure_ascii=False)

                if hasattr(connection, 'send'):
                    connection.send(message)
                elif hasattr(connection, 'send_text'):
                    connection.send_text(message)

                return True
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                self.remove_connection(client_id)
                return False

    def broadcast(self, message, channel=None):
        """广播消息

        Args:
            message: 消息内容
            channel: 频道名称（可选，None 表示广播给所有）
        """
        with self._lock:
            if channel:
                client_ids = self._channels.get(channel, set()).copy()
            else:
                client_ids = set(self._connections.keys())

        for client_id in client_ids:
            self.send_to(client_id, message)

    def broadcast_to_channel(self, channel, message):
        """广播消息到频道

        Args:
            channel: 频道名称
            message: 消息内容
        """
        self.broadcast(message, channel)

    def update_heartbeat(self, client_id):
        """更新心跳时间

        Args:
            client_id: 客户端 ID
        """
        with self._lock:
            if client_id in self._connections:
                self._connections[client_id]['last_heartbeat'] = time.time()

    def _heartbeat_loop(self):
        """心跳检测循环"""
        while self._running:
            try:
                self._check_heartbeats()
            except Exception as e:
                logger.error(f"心跳检测错误: {e}")

            time.sleep(self._heartbeat_interval)

    def _check_heartbeats(self):
        """检查心跳，移除超时连接"""
        now = time.time()
        timeout = self._heartbeat_interval * 3  # 3 倍心跳间隔超时

        with self._lock:
            expired_clients = [
                client_id for client_id, info in self._connections.items()
                if now - info['last_heartbeat'] > timeout
            ]

        for client_id in expired_clients:
            logger.warning(f"客户端 {client_id} 心跳超时，断开连接")
            self.remove_connection(client_id)

    def get_channel_subscribers(self, channel):
        """获取频道订阅者

        Args:
            channel: 频道名称

        Returns:
            订阅者 ID 集合
        """
        with self._lock:
            return self._channels.get(channel, set()).copy()

    def get_client_channels(self, client_id):
        """获取客户端订阅的频道

        Args:
            client_id: 客户端 ID

        Returns:
            频道集合
        """
        with self._lock:
            if client_id in self._connections:
                return self._connections[client_id]['channels'].copy()
            return set()

    def get_stats(self):
        """获取统计信息

        Returns:
            统计信息字典
        """
        with self._lock:
            return {
                'connections': len(self._connections),
                'channels': len(self._channels),
                'channel_details': {
                    channel: len(subscribers)
                    for channel, subscribers in self._channels.items()
                }
            }


class WebSocketMessage:
    """WebSocket 消息格式化"""

    @staticmethod
    def format_message(msg_type, data, channel=None):
        """格式化消息

        Args:
            msg_type: 消息类型
            data: 消息数据
            channel: 频道（可选）

        Returns:
            格式化的消息字典
        """
        message = {
            'type': msg_type,
            'data': data,
            'timestamp': time.time()
        }
        if channel:
            message['channel'] = channel
        return message

    @staticmethod
    def system_info(data):
        """系统信息消息"""
        return WebSocketMessage.format_message('system_info', data)

    @staticmethod
    def task_update(task_id, status, progress=None):
        """任务更新消息"""
        data = {
            'task_id': task_id,
            'status': status
        }
        if progress is not None:
            data['progress'] = progress
        return WebSocketMessage.format_message('task_update', data)

    @staticmethod
    def log_entry(log_type, content):
        """日志条目消息"""
        return WebSocketMessage.format_message('log_entry', {
            'log_type': log_type,
            'content': content
        })

    @staticmethod
    def error(message, code=None):
        """错误消息"""
        data = {'message': message}
        if code:
            data['code'] = code
        return WebSocketMessage.format_message('error', data)

    @staticmethod
    def success(message, data=None):
        """成功消息"""
        return WebSocketMessage.format_message('success', {
            'message': message,
            'data': data
        })


# 全局 WebSocket 管理器实例
_ws_manager = WebSocketManager()


def get_ws_manager():
    """获取全局 WebSocket 管理器"""
    return _ws_manager
