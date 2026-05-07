# coding:utf-8

"""
插件版本控制模块
提供插件版本管理、历史记录和回滚功能
"""

import json
import os
import time
import logging
import threading
logger = logging.getLogger(__name__)


class VersionInfo:
    """版本信息"""

    def __init__(self, version, release_notes='', changelog=None):
        """初始化版本信息

        Args:
            version: 版本号
            release_notes: 发布说明
            changelog: 变更日志
        """
        self.version = version
        self.release_notes = release_notes
        self.changelog = changelog or []
        self.created_at = time.time()
        self.checksum = ''
        self.file_size = 0
        self.download_url = ''
        self.min_panel_version = ''
        self.max_panel_version = ''
        self.is_stable = True
        self.is_beta = False
        self.download_count = 0

    def to_dict(self):
        """转换为字典"""
        return {
            'version': self.version,
            'release_notes': self.release_notes,
            'changelog': self.changelog,
            'created_at': self.created_at,
            'checksum': self.checksum,
            'file_size': self.file_size,
            'download_url': self.download_url,
            'min_panel_version': self.min_panel_version,
            'max_panel_version': self.max_panel_version,
            'is_stable': self.is_stable,
            'is_beta': self.is_beta,
            'download_count': self.download_count
        }

    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        info = cls(
            version=data['version'],
            release_notes=data.get('release_notes', ''),
            changelog=data.get('changelog', [])
        )
        info.created_at = data.get('created_at', time.time())
        info.checksum = data.get('checksum', '')
        info.file_size = data.get('file_size', 0)
        info.download_url = data.get('download_url', '')
        info.min_panel_version = data.get('min_panel_version', '')
        info.max_panel_version = data.get('max_panel_version', '')
        info.is_stable = data.get('is_stable', True)
        info.is_beta = data.get('is_beta', False)
        info.download_count = data.get('download_count', 0)
        return info


class PluginVersionManager:
    """插件版本管理器

    管理插件的版本历史，提供：
    - 版本发布
    - 版本查询
    - 版本比较
    - 版本回滚
    - 变更日志管理
    """

    def __init__(self, version_dir=None):
        """初始化版本管理器

        Args:
            version_dir: 版本数据目录
        """
        if version_dir is None:
            version_dir = os.path.join(
                os.path.dirname(__file__), '..', 'data', 'versions'
            )

        self._version_dir = version_dir
        self._versions = {}  # {plugin_name: [VersionInfo]}
        self._current_versions = {}  # {plugin_name: current_version}
        self._lock = threading.RLock()

        # 加载版本数据
        self._load_version_data()

    def _load_version_data(self):
        """加载版本数据"""
        version_file = os.path.join(self._version_dir, 'versions.json')
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for plugin_name, versions_data in data.get('versions', {}).items():
                    self._versions[plugin_name] = [
                        VersionInfo.from_dict(v) for v in versions_data
                    ]

                self._current_versions = data.get('current_versions', {})
                logger.info(
                    f"加载了 {len(self._versions)} 个插件的版本数据"
                )
            except Exception as e:
                logger.error(f"加载版本数据失败: {e}")

    def _save_version_data(self):
        """保存版本数据"""
        version_file = os.path.join(self._version_dir, 'versions.json')
        os.makedirs(self._version_dir, exist_ok=True)

        data = {
            'versions': {
                name: [v.to_dict() for v in versions]
                for name, versions in self._versions.items()
            },
            'current_versions': self._current_versions
        }

        try:
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存版本数据失败: {e}")

    def publish_version(self, plugin_name, version_info):
        """发布新版本

        Args:
            plugin_name: 插件名称
            version_info: 版本信息（VersionInfo 实例或字典）

        Returns:
            (bool, str) - (是否成功, 消息)
        """
        with self._lock:
            if isinstance(version_info, dict):
                version_info = VersionInfo.from_dict(version_info)

            if plugin_name not in self._versions:
                self._versions[plugin_name] = []

            # 检查版本是否已存在
            for v in self._versions[plugin_name]:
                if v.version == version_info.version:
                    return False, f"版本 {version_info.version} 已存在"

            # 添加版本
            self._versions[plugin_name].append(version_info)

            # 按版本号排序
            self._versions[plugin_name].sort(
                key=lambda x: self._parse_version(x.version),
                reverse=True
            )

            # 更新当前版本
            self._current_versions[plugin_name] = version_info.version

            self._save_version_data()

            logger.info(f"插件 {plugin_name} 发布新版本: {version_info.version}")
            return True, "发布成功"

    def get_current_version(self, plugin_name):
        """获取插件当前版本

        Args:
            plugin_name: 插件名称

        Returns:
            当前版本号或 None
        """
        with self._lock:
            return self._current_versions.get(plugin_name)

    def get_version_info(self, plugin_name, version=None):
        """获取版本信息

        Args:
            plugin_name: 插件名称
            version: 版本号，None 返回当前版本

        Returns:
            版本信息字典或 None
        """
        with self._lock:
            if plugin_name not in self._versions:
                return None

            if version is None:
                version = self._current_versions.get(plugin_name)

            if version is None:
                return None

            for v in self._versions[plugin_name]:
                if v.version == version:
                    return v.to_dict()

            return None

    def get_all_versions(self, plugin_name):
        """获取插件所有版本

        Args:
            plugin_name: 插件名称

        Returns:
            版本信息列表
        """
        with self._lock:
            if plugin_name not in self._versions:
                return []

            return [v.to_dict() for v in self._versions[plugin_name]]

    def get_latest_version(self, plugin_name, stable_only=True):
        """获取最新版本

        Args:
            plugin_name: 插件名称
            stable_only: 是否只返回稳定版本

        Returns:
            版本信息字典或 None
        """
        with self._lock:
            if plugin_name not in self._versions:
                return None

            versions = self._versions[plugin_name]
            if stable_only:
                versions = [v for v in versions if v.is_stable]

            if versions:
                return versions[0].to_dict()

            return None

    def check_update(self, plugin_name, current_version):
        """检查是否有更新

        Args:
            plugin_name: 插件名称
            current_version: 当前版本

        Returns:
            更新信息字典或 None
        """
        with self._lock:
            if plugin_name not in self._versions:
                return None

            latest = self.get_latest_version(plugin_name)
            if latest is None:
                return None

            if self._compare_versions(
                latest['version'], current_version
            ) > 0:
                return {
                    'has_update': True,
                    'current_version': current_version,
                    'latest_version': latest['version'],
                    'release_notes': latest['release_notes'],
                    'is_stable': latest['is_stable']
                }

            return {'has_update': False, 'current_version': current_version}

    def rollback_version(self, plugin_name, target_version):
        """回滚到指定版本

        Args:
            plugin_name: 插件名称
            target_version: 目标版本

        Returns:
            (bool, str) - (是否成功, 消息)
        """
        with self._lock:
            if plugin_name not in self._versions:
                return False, "插件不存在"

            # 检查目标版本是否存在
            target_info = None
            for v in self._versions[plugin_name]:
                if v.version == target_version:
                    target_info = v
                    break

            if target_info is None:
                return False, f"版本 {target_version} 不存在"

            # 更新当前版本
            self._current_versions[plugin_name] = target_version
            self._save_version_data()

            logger.info(
                f"插件 {plugin_name} 回滚到版本: {target_version}"
            )
            return True, "回滚成功"

    def add_changelog(self, plugin_name, version, changelog_entry):
        """添加变更日志

        Args:
            plugin_name: 插件名称
            version: 版本号
            changelog_entry: 变更日志条目

        Returns:
            (bool, str) - (是否成功, 消息)
        """
        with self._lock:
            if plugin_name not in self._versions:
                return False, "插件不存在"

            for v in self._versions[plugin_name]:
                if v.version == version:
                    v.changelog.append(changelog_entry)
                    self._save_version_data()
                    return True, "添加成功"

            return False, f"版本 {version} 不存在"

    def get_changelog(self, plugin_name, version=None):
        """获取变更日志

        Args:
            plugin_name: 插件名称
            version: 版本号，None 返回所有版本

        Returns:
            变更日志列表
        """
        with self._lock:
            if plugin_name not in self._versions:
                return []

            if version:
                for v in self._versions[plugin_name]:
                    if v.version == version:
                        return v.changelog
                return []

            # 返回所有版本的变更日志
            changelog = []
            for v in self._versions[plugin_name]:
                changelog.extend(v.changelog)
            return changelog

    def compare_versions(self, v1, v2):
        """比较两个版本号

        Args:
            v1: 版本 1
            v2: 版本 2

        Returns:
            -1 (v1 < v2), 0 (v1 == v2), 1 (v1 > v2)
        """
        return self._compare_versions(v1, v2)

    def _compare_versions(self, v1, v2):
        """比较版本号（内部方法）

        Args:
            v1: 版本 1
            v2: 版本 2

        Returns:
            -1 (v1 < v2), 0 (v1 == v2), 1 (v1 > v2)
        """
        try:
            parts1 = self._parse_version(v1)
            parts2 = self._parse_version(v2)

            for p1, p2 in zip(parts1, parts2):
                if p1 < p2:
                    return -1
                elif p1 > p2:
                    return 1

            return 0
        except (ValueError, AttributeError):
            return 0

    def _parse_version(self, version):
        """解析版本号

        Args:
            version: 版本号字符串

        Returns:
            版本号元组
        """
        try:
            return tuple(int(x) for x in version.split('.'))
        except (ValueError, AttributeError):
            return (0, 0, 0)

    def get_stats(self):
        """获取版本管理统计信息

        Returns:
            统计信息字典
        """
        with self._lock:
            total_plugins = len(self._versions)
            total_versions = sum(
                len(versions) for versions in self._versions.values()
            )

            return {
                'total_plugins': total_plugins,
                'total_versions': total_versions,
                'current_versions': self._current_versions.copy()
            }


# 全局版本管理器实例
_version_manager = PluginVersionManager()


def get_version_manager():
    """获取全局版本管理器"""
    return _version_manager
