# coding:utf-8
"""
缓存模块扩展测试
覆盖更多边界条件和高级功能
"""

import pytest
import time
import threading
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'web'))

from utils.cache import MemoryCache, FileCache, get_memory_cache, get_file_cache


class TestMemoryCacheExtended:
    """内存缓存扩展测试"""

    def test_set_overwrite(self):
        """测试覆盖写入"""
        cache = MemoryCache()
        cache.set('key1', 'value1')
        cache.set('key1', 'value2')
        assert cache.get('key1') == 'value2'

    def test_get_expired_returns_default(self):
        """测试过期后返回默认值"""
        cache = MemoryCache(default_ttl=1)
        cache.set('key1', 'value1', ttl=1)
        time.sleep(1.1)
        assert cache.get('key1', 'expired_default') == 'expired_default'

    def test_has_expired(self):
        """测试过期后has返回False"""
        cache = MemoryCache(default_ttl=1)
        cache.set('key1', 'value1', ttl=1)
        time.sleep(1.1)
        assert cache.has('key1') is False

    def test_delete_returns_true_for_existing(self):
        """测试删除存在的键返回True"""
        cache = MemoryCache()
        cache.set('key1', 'value1')
        assert cache.delete('key1') is True

    def test_delete_returns_false_for_nonexistent(self):
        """测试删除不存在的键返回False"""
        cache = MemoryCache()
        assert cache.delete('nonexistent') is False

    def test_clear_empty_cache(self):
        """测试清空空缓存"""
        cache = MemoryCache()
        cache.clear()  # 不应抛出异常

    def test_get_stats_empty(self):
        """测试空缓存的统计信息"""
        cache = MemoryCache()
        stats = cache.get_stats()
        assert stats['size'] == 0
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['evictions'] == 0
        assert stats['hit_rate'] == 0

    def test_get_stats_hit_rate(self):
        """测试命中率计算"""
        cache = MemoryCache()
        cache.set('key1', 'value1')
        cache.get('key1')  # hit
        cache.get('key1')  # hit
        cache.get('nonexistent')  # miss

        stats = cache.get_stats()
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['hit_rate'] == pytest.approx(66.67, abs=0.01)

    def test_max_size_eviction(self):
        """测试容量限制和驱逐"""
        cache = MemoryCache(max_size=3)
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        cache.set('key4', 'value4')  # 应触发驱逐

        stats = cache.get_stats()
        assert stats['size'] <= 3

    def test_get_or_set_with_ttl(self):
        """测试get_or_set带TTL"""
        cache = MemoryCache(default_ttl=1)
        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return 'computed'

        cache.get_or_set('key1', factory, ttl=1)
        assert call_count == 1

        time.sleep(1.1)
        cache.get_or_set('key1', factory, ttl=1)
        assert call_count == 2  # 过期后重新计算

    def test_get_many_partial(self):
        """测试批量获取部分命中"""
        cache = MemoryCache()
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')

        result = cache.get_many(['key1', 'key2', 'key3'])
        assert len(result) == 2
        assert 'key3' not in result

    def test_set_many_with_ttl(self):
        """测试批量设置带TTL"""
        cache = MemoryCache(default_ttl=1)
        cache.set_many({'key1': 'value1', 'key2': 'value2'}, ttl=1)
        assert cache.get('key1') == 'value1'
        time.sleep(1.1)
        assert cache.get('key1') is None

    def test_delete_many_partial(self):
        """测试批量删除部分"""
        cache = MemoryCache()
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')

        cache.delete_many(['key1', 'key2'])
        assert cache.get('key1') is None
        assert cache.get('key2') is None
        assert cache.get('key3') == 'value3'

    def test_thread_safety(self):
        """测试线程安全性"""
        cache = MemoryCache()
        errors = []

        def writer():
            try:
                for i in range(100):
                    cache.set(f'key_{i}', f'value_{i}')
            except Exception as e:
                errors.append(e)

        def reader():
            try:
                for i in range(100):
                    cache.get(f'key_{i}')
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer) for _ in range(5)]
        threads += [threading.Thread(target=reader) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0

    def test_complex_nested_values(self):
        """测试复杂嵌套值"""
        cache = MemoryCache()
        value = {
            'list': [1, 2, {'nested': True}],
            'dict': {'a': [3, 4], 'b': {'c': 5}},
            'tuple_like': (1, 2, 3),
        }
        cache.set('complex', value)
        assert cache.get('complex') == value

    def test_none_value(self):
        """测试None值存储"""
        cache = MemoryCache()
        cache.set('key1', None)
        # None值应该能存储但has会返回False
        assert cache.has('key1') is False

    def test_empty_string_value(self):
        """测试空字符串值"""
        cache = MemoryCache()
        cache.set('key1', '')
        assert cache.get('key1') == ''
        assert cache.has('key1') is True


class TestFileCacheExtended:
    """文件缓存扩展测试"""

    def test_delete_nonexistent(self, tmp_path):
        """测试删除不存在的缓存"""
        cache = FileCache(cache_dir=str(tmp_path))
        assert cache.delete('nonexistent') is False

    def test_has_expired(self, tmp_path):
        """测试过期后has返回False"""
        cache = FileCache(cache_dir=str(tmp_path), default_ttl=1)
        cache.set('key1', 'value1', ttl=1)
        time.sleep(1.1)
        assert cache.has('key1') is False

    def test_clear_empty(self, tmp_path):
        """测试清空空缓存目录"""
        cache = FileCache(cache_dir=str(tmp_path))
        cache.clear()  # 不应抛出异常

    def test_special_characters_in_key(self, tmp_path):
        """测试特殊字符键名"""
        cache = FileCache(cache_dir=str(tmp_path))
        cache.set('key/with/slashes', 'value1')
        assert cache.get('key/with/slashes') == 'value1'

    def test_unicode_key(self, tmp_path):
        """测试Unicode键名"""
        cache = FileCache(cache_dir=str(tmp_path))
        cache.set('键名_测试', '值')
        assert cache.get('键名_测试') == '值'

    def test_large_value(self, tmp_path):
        """测试大值存储"""
        cache = FileCache(cache_dir=str(tmp_path))
        large_value = 'x' * 100000
        cache.set('large', large_value)
        assert cache.get('large') == large_value

    def test_json_value(self, tmp_path):
        """测试JSON值存储"""
        cache = FileCache(cache_dir=str(tmp_path))
        value = {'key': 'value', 'number': 42, 'list': [1, 2, 3]}
        cache.set('json', value)
        assert cache.get('json') == value


class TestGlobalCacheInstances:
    """全局缓存实例测试"""

    def test_get_memory_cache_returns_instance(self):
        """测试获取全局内存缓存实例"""
        cache = get_memory_cache()
        assert isinstance(cache, MemoryCache)

    def test_get_file_cache_returns_instance(self):
        """测试获取全局文件缓存实例"""
        cache = get_file_cache()
        assert isinstance(cache, FileCache)

    def test_memory_cache_singleton(self):
        """测试内存缓存单例"""
        cache1 = get_memory_cache()
        cache2 = get_memory_cache()
        assert cache1 is cache2
