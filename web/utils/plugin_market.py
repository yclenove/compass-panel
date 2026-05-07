# coding:utf-8

"""
插件市场模块
提供插件市场功能，包括插件搜索、评分、下载等
"""

import json
import os
import time
import logging
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)


class PluginMarketItem:
    """插件市场项目"""

    def __init__(self, name, title, description, author, version, category='other'):
        """初始化插件市场项目

        Args:
            name: 插件名称
            title: 插件标题
            description: 插件描述
            author: 作者
            version: 版本
            category: 分类
        """
        self.name = name
        self.title = title
        self.description = description
        self.author = author
        self.version = version
        self.category = category
        self.downloads = 0
        self.rating = 0.0
        self.rating_count = 0
        self.created_at = time.time()
        self.updated_at = time.time()
        self.tags = []
        self.homepage = ''
        self.repository = ''
        self.min_version = ''
        self.max_version = ''
        self.dependencies = []
        self.screenshots = []

    def to_dict(self):
        """转换为字典"""
        return {
            'name': self.name,
            'title': self.title,
            'description': self.description,
            'author': self.author,
            'version': self.version,
            'category': self.category,
            'downloads': self.downloads,
            'rating': self.rating,
            'rating_count': self.rating_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'tags': self.tags,
            'homepage': self.homepage,
            'repository': self.repository,
            'min_version': self.min_version,
            'max_version': self.max_version,
            'dependencies': self.dependencies,
            'screenshots': self.screenshots
        }

    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        item = cls(
            name=data['name'],
            title=data['title'],
            description=data['description'],
            author=data['author'],
            version=data['version'],
            category=data.get('category', 'other')
        )
        item.downloads = data.get('downloads', 0)
        item.rating = data.get('rating', 0.0)
        item.rating_count = data.get('rating_count', 0)
        item.created_at = data.get('created_at', time.time())
        item.updated_at = data.get('updated_at', time.time())
        item.tags = data.get('tags', [])
        item.homepage = data.get('homepage', '')
        item.repository = data.get('repository', '')
        item.min_version = data.get('min_version', '')
        item.max_version = data.get('max_version', '')
        item.dependencies = data.get('dependencies', [])
        item.screenshots = data.get('screenshots', [])
        return item


class PluginMarket:
    """插件市场管理器

    管理插件市场的所有功能，包括：
    - 插件发布
    - 插件搜索
    - 插件评分
    - 插件下载
    - 分类管理
    """

    def __init__(self, market_dir=None):
        """初始化插件市场

        Args:
            market_dir: 市场数据目录
        """
        if market_dir is None:
            market_dir = os.path.join(
                os.path.dirname(__file__), '..', 'data', 'market'
            )

        self._market_dir = market_dir
        self._plugins = {}  # {name: PluginMarketItem}
        self._categories = {
            'web': 'Web 服务器',
            'database': '数据库',
            'cache': '缓存',
            'language': '编程语言',
            'tool': '工具',
            'security': '安全',
            'monitor': '监控',
            'other': '其他'
        }
        self._lock = threading.RLock()

        # 加载市场数据
        self._load_market_data()

    def _load_market_data(self):
        """加载市场数据"""
        market_file = os.path.join(self._market_dir, 'plugins.json')
        if os.path.exists(market_file):
            try:
                with open(market_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for name, info in data.items():
                    self._plugins[name] = PluginMarketItem.from_dict(info)
                logger.info(f"加载了 {len(self._plugins)} 个插件市场数据")
            except Exception as e:
                logger.error(f"加载市场数据失败: {e}")

    def _save_market_data(self):
        """保存市场数据"""
        market_file = os.path.join(self._market_dir, 'plugins.json')
        os.makedirs(self._market_dir, exist_ok=True)

        data = {
            name: item.to_dict()
            for name, item in self._plugins.items()
        }

        try:
            with open(market_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存市场数据失败: {e}")

    def publish_plugin(self, plugin_info):
        """发布插件到市场

        Args:
            plugin_info: 插件信息字典

        Returns:
            (bool, str) - (是否成功, 消息)
        """
        with self._lock:
            name = plugin_info.get('name')
            if not name:
                return False, "缺少插件名称"

            # 创建市场项目
            item = PluginMarketItem(
                name=name,
                title=plugin_info.get('title', name),
                description=plugin_info.get('description', ''),
                author=plugin_info.get('author', '未知'),
                version=plugin_info.get('version', '1.0.0'),
                category=plugin_info.get('category', 'other')
            )

            # 设置可选字段
            if 'tags' in plugin_info:
                item.tags = plugin_info['tags']
            if 'homepage' in plugin_info:
                item.homepage = plugin_info['homepage']
            if 'repository' in plugin_info:
                item.repository = plugin_info['repository']
            if 'min_version' in plugin_info:
                item.min_version = plugin_info['min_version']
            if 'max_version' in plugin_info:
                item.max_version = plugin_info['max_version']
            if 'dependencies' in plugin_info:
                item.dependencies = plugin_info['dependencies']

            self._plugins[name] = item
            self._save_market_data()

            logger.info(f"插件已发布到市场: {name}")
            return True, "发布成功"

    def update_plugin(self, name, plugin_info):
        """更新插件信息

        Args:
            name: 插件名称
            plugin_info: 更新的插件信息

        Returns:
            (bool, str) - (是否成功, 消息)
        """
        with self._lock:
            if name not in self._plugins:
                return False, "插件不存在"

            item = self._plugins[name]

            # 更新字段
            if 'title' in plugin_info:
                item.title = plugin_info['title']
            if 'description' in plugin_info:
                item.description = plugin_info['description']
            if 'version' in plugin_info:
                item.version = plugin_info['version']
            if 'category' in plugin_info:
                item.category = plugin_info['category']
            if 'tags' in plugin_info:
                item.tags = plugin_info['tags']
            if 'homepage' in plugin_info:
                item.homepage = plugin_info['homepage']
            if 'repository' in plugin_info:
                item.repository = plugin_info['repository']
            if 'dependencies' in plugin_info:
                item.dependencies = plugin_info['dependencies']

            item.updated_at = time.time()
            self._save_market_data()

            logger.info(f"插件已更新: {name}")
            return True, "更新成功"

    def remove_plugin(self, name):
        """从市场移除插件

        Args:
            name: 插件名称

        Returns:
            (bool, str) - (是否成功, 消息)
        """
        with self._lock:
            if name not in self._plugins:
                return False, "插件不存在"

            del self._plugins[name]
            self._save_market_data()

            logger.info(f"插件已从市场移除: {name}")
            return True, "移除成功"

    def get_plugin(self, name):
        """获取插件信息

        Args:
            name: 插件名称

        Returns:
            插件信息字典或 None
        """
        with self._lock:
            if name in self._plugins:
                return self._plugins[name].to_dict()
            return None

    def search_plugins(self, keyword=None, category=None, tags=None,
                       sort_by='downloads', page=1, page_size=20):
        """搜索插件

        Args:
            keyword: 搜索关键词
            category: 分类过滤
            tags: 标签过滤
            sort_by: 排序字段 (downloads, rating, created_at, updated_at)
            page: 页码
            page_size: 每页数量

        Returns:
            搜索结果字典
        """
        with self._lock:
            results = list(self._plugins.values())

            # 关键词过滤
            if keyword:
                keyword_lower = keyword.lower()
                results = [
                    item for item in results
                    if (keyword_lower in item.name.lower() or
                        keyword_lower in item.title.lower() or
                        keyword_lower in item.description.lower() or
                        keyword_lower in item.author.lower())
                ]

            # 分类过滤
            if category:
                results = [
                    item for item in results
                    if item.category == category
                ]

            # 标签过滤
            if tags:
                tag_set = set(tags)
                results = [
                    item for item in results
                    if tag_set.intersection(item.tags)
                ]

            # 排序
            if sort_by == 'downloads':
                results.sort(key=lambda x: x.downloads, reverse=True)
            elif sort_by == 'rating':
                results.sort(key=lambda x: x.rating, reverse=True)
            elif sort_by == 'created_at':
                results.sort(key=lambda x: x.created_at, reverse=True)
            elif sort_by == 'updated_at':
                results.sort(key=lambda x: x.updated_at, reverse=True)

            # 分页
            total = len(results)
            start = (page - 1) * page_size
            end = start + page_size
            page_results = results[start:end]

            return {
                'total': total,
                'page': page,
                'page_size': page_size,
                'plugins': [item.to_dict() for item in page_results]
            }

    def rate_plugin(self, name, rating, user_id=None):
        """对插件评分

        Args:
            name: 插件名称
            rating: 评分 (1-5)
            user_id: 用户 ID

        Returns:
            (bool, str) - (是否成功, 消息)
        """
        with self._lock:
            if name not in self._plugins:
                return False, "插件不存在"

            if rating < 1 or rating > 5:
                return False, "评分必须在 1-5 之间"

            item = self._plugins[name]

            # 更新评分
            total_rating = item.rating * item.rating_count + rating
            item.rating_count += 1
            item.rating = round(total_rating / item.rating_count, 2)

            self._save_market_data()

            logger.info(f"插件 {name} 收到评分: {rating}")
            return True, "评分成功"

    def download_plugin(self, name):
        """下载插件（记录下载次数）

        Args:
            name: 插件名称

        Returns:
            插件信息字典或 None
        """
        with self._lock:
            if name not in self._plugins:
                return None

            item = self._plugins[name]
            item.downloads += 1
            self._save_market_data()

            logger.info(f"插件 {name} 被下载，总下载次数: {item.downloads}")
            return item.to_dict()

    def get_categories(self):
        """获取所有分类

        Returns:
            分类字典
        """
        return self._categories.copy()

    def get_plugins_by_category(self, category, page=1, page_size=20):
        """按分类获取插件

        Args:
            category: 分类名称
            page: 页码
            page_size: 每页数量

        Returns:
            插件列表
        """
        return self.search_plugins(
            category=category,
            sort_by='downloads',
            page=page,
            page_size=page_size
        )

    def get_popular_plugins(self, limit=10):
        """获取热门插件

        Args:
            limit: 返回数量

        Returns:
            热门插件列表
        """
        with self._lock:
            sorted_plugins = sorted(
                self._plugins.values(),
                key=lambda x: x.downloads,
                reverse=True
            )[:limit]
            return [item.to_dict() for item in sorted_plugins]

    def get_top_rated_plugins(self, limit=10):
        """获取评分最高的插件

        Args:
            limit: 返回数量

        Returns:
            评分最高插件列表
        """
        with self._lock:
            sorted_plugins = sorted(
                self._plugins.values(),
                key=lambda x: x.rating,
                reverse=True
            )[:limit]
            return [item.to_dict() for item in sorted_plugins]

    def get_recent_plugins(self, limit=10):
        """获取最新插件

        Args:
            limit: 返回数量

        Returns:
            最新插件列表
        """
        with self._lock:
            sorted_plugins = sorted(
                self._plugins.values(),
                key=lambda x: x.created_at,
                reverse=True
            )[:limit]
            return [item.to_dict() for item in sorted_plugins]

    def get_stats(self):
        """获取市场统计信息

        Returns:
            统计信息字典
        """
        with self._lock:
            total_plugins = len(self._plugins)
            total_downloads = sum(
                item.downloads for item in self._plugins.values()
            )
            avg_rating = 0.0
            if total_plugins > 0:
                total_rating = sum(
                    item.rating for item in self._plugins.values()
                )
                avg_rating = round(total_rating / total_plugins, 2)

            category_stats = defaultdict(int)
            for item in self._plugins.values():
                category_stats[item.category] += 1

            return {
                'total_plugins': total_plugins,
                'total_downloads': total_downloads,
                'average_rating': avg_rating,
                'categories': dict(category_stats)
            }


# 全局插件市场实例
_plugin_market = PluginMarket()


def get_plugin_market():
    """获取全局插件市场实例"""
    return _plugin_market
