# coding:utf-8
"""缓存模块测试"""

import pytest
import time
from utils.cache import MemoryCache, FileCache


class TestMemoryCache:
    """内存缓存测试"""

    def test_basic_get_set(self):
        """测试基本的获取和设置"""
        cache = MemoryCache()
        cache.set('key1', 'value1')
        assert cache.get('key1') == 'value1'

    def test_get_default(self):
        """测试获取不存在的键返回默认值"""
        cache = MemoryCache()
        assert cache.get('nonexistent') is None
        assert cache.get('nonexistent', 'default') == 'default'

    def test_delete(self):
        """测试删除缓存"""
        cache = MemoryCache()
        cache.set('key1', 'value1')
        assert cache.delete('key1') is True
        assert cache.get('key1') is None

    def test_delete_nonexistent(self):
        """测试删除不存在的键"""
        cache = MemoryCache()
        assert cache.delete('nonexistent') is False

    def test_has(self):
        """测试检查缓存是否存在"""
        cache = MemoryCache()
        cache.set('key1', 'value1')
        assert cache.has('key1') is True
        assert cache.has('nonexistent') is False

    def test_ttl(self):
        """测试缓存过期"""
        cache = MemoryCache(default_ttl=1)
        cache.set('key1', 'value1', ttl=1)
        assert cache.get('key1') == 'value1'
        time.sleep(1.1)
        assert cache.get('key1') is None

    def test_clear(self):
        """测试清空缓存"""
        cache = MemoryCache()
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.clear()
        assert cache.get('key1') is None
        assert cache.get('key2') is None

    def test_max_size(self):
        """测试最大容量限制"""
        cache = MemoryCache(max_size=5)
        for i in range(10):
            cache.set(f'key{i}', f'value{i}')
        assert cache.get_stats()['size'] <= 5

    def test_get_or_set(self):
        """测试 get_or_set 方法"""
        cache = MemoryCache()
        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return 'computed_value'

        # 第一次调用应该执行工厂函数
        result = cache.get_or_set('key1', factory)
        assert result == 'computed_value'
        assert call_count == 1

        # 第二次调用应该从缓存获取
        result = cache.get_or_set('key1', factory)
        assert result == 'computed_value'
        assert call_count == 1

    def test_get_many(self):
        """测试批量获取"""
        cache = MemoryCache()
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')

        result = cache.get_many(['key1', 'key2', 'nonexistent'])
        assert result == {'key1': 'value1', 'key2': 'value2'}

    def test_set_many(self):
        """测试批量设置"""
        cache = MemoryCache()
        cache.set_many({'key1': 'value1', 'key2': 'value2'})
        assert cache.get('key1') == 'value1'
        assert cache.get('key2') == 'value2'

    def test_delete_many(self):
        """测试批量删除"""
        cache = MemoryCache()
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.delete_many(['key1', 'key2'])
        assert cache.get('key1') is None
        assert cache.get('key2') is None

    def test_stats(self):
        """测试统计信息"""
        cache = MemoryCache()
        cache.set('key1', 'value1')
        cache.get('key1')  # hit
        cache.get('nonexistent')  # miss

        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['size'] == 1

    def test_complex_values(self):
        """测试复杂值类型"""
        cache = MemoryCache()
        complex_value = {
            'list': [1, 2, 3],
            'dict': {'a': 1, 'b': 2},
            'nested': {'x': [4, 5, 6]}
        }
        cache.set('complex', complex_value)
        assert cache.get('complex') == complex_value


class TestFileCache:
    """文件缓存测试"""

    def test_basic_get_set(self, tmp_path):
        """测试基本的获取和设置"""
        cache = FileCache(cache_dir=str(tmp_path))
        cache.set('key1', 'value1')
        assert cache.get('key1') == 'value1'

    def test_get_default(self, tmp_path):
        """测试获取不存在的键返回默认值"""
        cache = FileCache(cache_dir=str(tmp_path))
        assert cache.get('nonexistent') is None

    def test_delete(self, tmp_path):
        """测试删除缓存"""
        cache = FileCache(cache_dir=str(tmp_path))
        cache.set('key1', 'value1')
        assert cache.delete('key1') is True
        assert cache.get('key1') is None

    def test_ttl(self, tmp_path):
        """测试缓存过期"""
        cache = FileCache(cache_dir=str(tmp_path), default_ttl=1)
        cache.set('key1', 'value1', ttl=1)
        assert cache.get('key1') == 'value1'
        time.sleep(1.1)
        assert cache.get('key1') is None

    def test_clear(self, tmp_path):
        """测试清空缓存"""
        cache = FileCache(cache_dir=str(tmp_path))
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.clear()
        assert cache.get('key1') is None
        assert cache.get('key2') is None

    def test_complex_values(self, tmp_path):
        """测试复杂值类型"""
        cache = FileCache(cache_dir=str(tmp_path))
        complex_value = {
            'list': [1, 2, 3],
            'dict': {'a': 1, 'b': 2}
        }
        cache.set('complex', complex_value)
        assert cache.get('complex') == complex_value
