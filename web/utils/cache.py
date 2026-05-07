# coding:utf-8

"""
缓存工具模块
提供内存缓存、文件缓存和 Redis 缓存支持
"""

import os
import json
import time
import hashlib
import threading
from functools import wraps


class MemoryCache:
    """内存缓存实现

    使用字典存储缓存数据，支持 TTL 过期和最大容量限制。
    线程安全。
    """

    def __init__(self, max_size=1000, default_ttl=300):
        """初始化内存缓存

        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认过期时间（秒）
        """
        self._cache = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = threading.Lock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }

    def get(self, key, default=None):
        """获取缓存值

        Args:
            key: 缓存键
            default: 默认值

        Returns:
            缓存值或默认值
        """
        with self._lock:
            if key in self._cache:
                item = self._cache[key]
                if item['expires_at'] > time.time():
                    self._stats['hits'] += 1
                    return item['value']
                else:
                    # 已过期，删除
                    del self._cache[key]
                    self._stats['evictions'] += 1

            self._stats['misses'] += 1
            return default

    def set(self, key, value, ttl=None):
        """设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None 使用默认值
        """
        if ttl is None:
            ttl = self._default_ttl

        with self._lock:
            # 检查容量，必要时清理
            if len(self._cache) >= self._max_size:
                self._evict()

            self._cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl,
                'created_at': time.time()
            }

    def delete(self, key):
        """删除缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self):
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()

    def has(self, key):
        """检查缓存是否存在

        Args:
            key: 缓存键

        Returns:
            是否存在
        """
        return self.get(key) is not None

    def get_or_set(self, key, factory, ttl=None):
        """获取缓存值，如果不存在则通过工厂函数创建

        Args:
            key: 缓存键
            factory: 工厂函数
            ttl: 过期时间

        Returns:
            缓存值
        """
        value = self.get(key)
        if value is None:
            value = factory()
            self.set(key, value, ttl)
        return value

    def get_many(self, keys):
        """批量获取缓存

        Args:
            keys: 缓存键列表

        Returns:
            字典 {key: value}
        """
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    def set_many(self, mapping, ttl=None):
        """批量设置缓存

        Args:
            mapping: 字典 {key: value}
            ttl: 过期时间
        """
        for key, value in mapping.items():
            self.set(key, value, ttl)

    def delete_many(self, keys):
        """批量删除缓存

        Args:
            keys: 缓存键列表
        """
        for key in keys:
            self.delete(key)

    def get_stats(self):
        """获取缓存统计信息

        Returns:
            统计信息字典
        """
        with self._lock:
            total = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total * 100) if total > 0 else 0
            return {
                'size': len(self._cache),
                'max_size': self._max_size,
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'evictions': self._stats['evictions'],
                'hit_rate': round(hit_rate, 2)
            }

    def _evict(self):
        """清理过期和最少使用的缓存"""
        now = time.time()

        # 首先清理过期的
        expired_keys = [
            k for k, v in self._cache.items()
            if v['expires_at'] <= now
        ]
        for key in expired_keys:
            del self._cache[key]
            self._stats['evictions'] += 1

        # 如果还需要清理，删除最旧的
        if len(self._cache) >= self._max_size:
            sorted_keys = sorted(
                self._cache.keys(),
                key=lambda k: self._cache[k]['created_at']
            )
            evict_count = max(1, len(sorted_keys) // 4)
            for key in sorted_keys[:evict_count]:
                del self._cache[key]
                self._stats['evictions'] += 1


class FileCache:
    """文件缓存实现

    将缓存数据存储到文件系统中。
    """

    def __init__(self, cache_dir=None, default_ttl=300):
        """初始化文件缓存

        Args:
            cache_dir: 缓存目录
            default_ttl: 默认过期时间（秒）
        """
        if cache_dir is None:
            import core.mw as mw
            cache_dir = os.path.join(mw.getPanelDir(), 'data', 'cache')

        self._cache_dir = cache_dir
        self._default_ttl = default_ttl

        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_path(self, key):
        """获取缓存文件路径"""
        # 使用 MD5 作为文件名
        md5 = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self._cache_dir, f"{md5}.json")

    def get(self, key, default=None):
        """获取缓存值"""
        path = self._get_cache_path(key)
        if not os.path.exists(path):
            return default

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if data.get('expires_at', 0) > time.time():
                return data.get('value')
            else:
                os.remove(path)
                return default
        except Exception:
            return default

    def set(self, key, value, ttl=None):
        """设置缓存值"""
        if ttl is None:
            ttl = self._default_ttl

        path = self._get_cache_path(key)
        data = {
            'key': key,
            'value': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }

        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception:
            pass

    def delete(self, key):
        """删除缓存"""
        path = self._get_cache_path(key)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def clear(self):
        """清空所有缓存"""
        for filename in os.listdir(self._cache_dir):
            if filename.endswith('.json'):
                os.remove(os.path.join(self._cache_dir, filename))

    def has(self, key):
        """检查缓存是否存在"""
        return self.get(key) is not None


def cached(ttl=300, key_prefix='', cache_type='memory'):
    """缓存装饰器

    Args:
        ttl: 过期时间（秒）
        key_prefix: 缓存键前缀
        cache_type: 缓存类型 ('memory' 或 'file')

    Returns:
        装饰器函数

    Example:
        @cached(ttl=60)
        def get_user(user_id):
            return db.get_user(user_id)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key_parts = [key_prefix or func.__name__]
            key_parts.extend([str(a) for a in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = ":".join(key_parts)

            # 获取缓存实例
            if cache_type == 'file':
                cache = FileCache()
            else:
                cache = MemoryCache()

            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is not None:
                return result

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator


# 全局缓存实例
_memory_cache = MemoryCache()
_file_cache = FileCache()


def get_memory_cache():
    """获取全局内存缓存实例"""
    return _memory_cache


def get_file_cache():
    """获取全局文件缓存实例"""
    return _file_cache
