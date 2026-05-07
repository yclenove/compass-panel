# coding:utf-8

"""
插件依赖管理模块
提供插件依赖关系解析、冲突检测和安装顺序计算
"""

import logging
import threading
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class DependencyNode:
    """依赖节点"""

    def __init__(self, name, version=None, optional=False):
        """初始化依赖节点

        Args:
            name: 插件名称
            version: 版本要求
            optional: 是否可选依赖
        """
        self.name = name
        self.version = version
        self.optional = optional
        self.dependencies = []  # 依赖的其他插件
        self.dependents = []  # 被依赖（反向依赖）

    def to_dict(self):
        """转换为字典"""
        return {
            'name': self.name,
            'version': self.version,
            'optional': self.optional,
            'dependencies': self.dependencies,
            'dependents': self.dependents
        }


class PluginDependencyManager:
    """插件依赖管理器

    管理插件之间的依赖关系，提供：
    - 依赖注册
    - 依赖解析
    - 冲突检测
    - 安装顺序计算
    - 循环依赖检测
    """

    def __init__(self):
        """初始化依赖管理器"""
        self._nodes = {}  # {name: DependencyNode}
        self._conflicts = []  # 冲突列表
        self._lock = threading.RLock()

    def register_plugin(self, name, version=None, dependencies=None):
        """注册插件及其依赖

        Args:
            name: 插件名称
            version: 插件版本
            dependencies: 依赖列表，格式:
                [{'name': 'xxx', 'version': '>=1.0',
                  'optional': False}]
        """
        with self._lock:
            if name not in self._nodes:
                self._nodes[name] = DependencyNode(name, version)
            else:
                self._nodes[name].version = version

            node = self._nodes[name]
            node.dependencies = []

            if dependencies:
                for dep in dependencies:
                    dep_name = dep['name']
                    dep_version = dep.get('version')
                    dep_optional = dep.get('optional', False)

                    node.dependencies.append({
                        'name': dep_name,
                        'version': dep_version,
                        'optional': dep_optional
                    })

                    # 确保依赖节点存在
                    if dep_name not in self._nodes:
                        self._nodes[dep_name] = DependencyNode(dep_name)

                    # 添加反向依赖
                    dep_names = [
                        d['name'] for d in
                        self._nodes[dep_name].dependents
                    ]
                    if name not in dep_names:
                        self._nodes[dep_name].dependents.append({
                            'name': name,
                            'version': version,
                            'optional': dep_optional
                        })

            logger.debug(f"注册插件依赖: {name} (依赖: {len(node.dependencies)} 个)")

    def unregister_plugin(self, name):
        """注销插件

        Args:
            name: 插件名称
        """
        with self._lock:
            if name not in self._nodes:
                return

            node = self._nodes[name]

            # 清理反向依赖
            for dep_info in node.dependencies:
                dep_name = dep_info['name']
                if dep_name in self._nodes:
                    self._nodes[dep_name].dependents = [
                        d for d in self._nodes[dep_name].dependents
                        if d['name'] != name
                    ]

            # 清理依赖
            for dep_info in node.dependents:
                dep_name = dep_info['name']
                if dep_name in self._nodes:
                    self._nodes[dep_name].dependencies = [
                        d for d in self._nodes[dep_name].dependencies
                        if d['name'] != name
                    ]

            del self._nodes[name]
            logger.debug(f"注销插件依赖: {name}")

    def get_dependencies(self, name, recursive=False):
        """获取插件依赖

        Args:
            name: 插件名称
            recursive: 是否递归获取所有依赖

        Returns:
            依赖列表
        """
        with self._lock:
            if name not in self._nodes:
                return []

            node = self._nodes[name]
            if not recursive:
                return node.dependencies.copy()

            # 递归获取所有依赖
            all_deps = []
            visited = set()
            queue = deque([name])

            while queue:
                current = queue.popleft()
                if current in visited:
                    continue
                visited.add(current)

                if current in self._nodes:
                    for dep in self._nodes[current].dependencies:
                        all_deps.append(dep)
                        queue.append(dep['name'])

            return all_deps

    def get_dependents(self, name, recursive=False):
        """获取依赖此插件的其他插件

        Args:
            name: 插件名称
            recursive: 是否递归获取

        Returns:
            依赖此插件的列表
        """
        with self._lock:
            if name not in self._nodes:
                return []

            node = self._nodes[name]
            if not recursive:
                return node.dependents.copy()

            # 递归获取所有依赖此插件的
            all_dependents = []
            visited = set()
            queue = deque([name])

            while queue:
                current = queue.popleft()
                if current in visited:
                    continue
                visited.add(current)

                if current in self._nodes:
                    for dep in self._nodes[current].dependents:
                        all_dependents.append(dep)
                        queue.append(dep['name'])

            return all_dependents

    def check_circular_dependency(self, name=None):
        """检查循环依赖

        Args:
            name: 指定插件名称，None 检查所有

        Returns:
            循环依赖列表，每个元素是一个循环路径
        """
        with self._lock:
            cycles = []
            visited = set()
            rec_stack = set()

            def dfs(node_name, path):
                visited.add(node_name)
                rec_stack.add(node_name)
                path.append(node_name)

                if node_name in self._nodes:
                    for dep in self._nodes[node_name].dependencies:
                        dep_name = dep['name']
                        if dep_name not in visited:
                            dfs(dep_name, path)
                        elif dep_name in rec_stack:
                            # 找到循环
                            cycle_start = path.index(dep_name)
                            cycle = path[cycle_start:] + [dep_name]
                            cycles.append(cycle)

                path.pop()
                rec_stack.remove(node_name)

            if name:
                if name in self._nodes:
                    dfs(name, [])
            else:
                for node_name in self._nodes:
                    if node_name not in visited:
                        dfs(node_name, [])

            return cycles

    def check_conflicts(self):
        """检查依赖冲突

        Returns:
            冲突列表
        """
        with self._lock:
            conflicts = []

            for name, node in self._nodes.items():
                for dep in node.dependencies:
                    dep_name = dep['name']

                    # 检查依赖是否存在
                    if dep_name not in self._nodes:
                        conflicts.append({
                            'type': 'missing_dependency',
                            'plugin': name,
                            'dependency': dep_name,
                            'message': f'插件 {name} 依赖 {dep_name}，但 {dep_name} 未注册'
                        })
                        continue

                    # 检查版本兼容性
                    if dep.get('version') and self._nodes[dep_name].version:
                        if not self._check_version_compatibility(
                            self._nodes[dep_name].version,
                            dep['version']
                        ):
                            conflicts.append({
                                'type': 'version_incompatible',
                                'plugin': name,
                                'dependency': dep_name,
                                'required': dep['version'],
                                'available': self._nodes[dep_name].version,
                                'message': (
                                    f'插件 {name} 需要 {dep_name} '
                                    f'{dep["version"]}，但当前版本是 '
                                    f'{self._nodes[dep_name].version}'
                                )
                            })

            self._conflicts = conflicts
            return conflicts

    def _check_version_compatibility(self, available, required):
        """检查版本兼容性

        Args:
            available: 可用版本
            required: 要求版本

        Returns:
            是否兼容
        """
        # 简单版本比较，支持 >= 和 ^ 前缀
        if required.startswith('>='):
            min_version = required[2:]
            return self._compare_versions(available, min_version) >= 0
        elif required.startswith('^'):
            base_version = required[1:]
            return self._compare_versions(available, base_version) >= 0
        elif required.startswith('<='):
            max_version = required[2:]
            return self._compare_versions(available, max_version) <= 0
        elif required.startswith('='):
            exact_version = required[1:]
            return available == exact_version
        else:
            # 默认要求精确匹配
            return available == required

    def _compare_versions(self, v1, v2):
        """比较版本号

        Args:
            v1: 版本 1
            v2: 版本 2

        Returns:
            -1 (v1 < v2), 0 (v1 == v2), 1 (v1 > v2)
        """
        try:
            parts1 = [int(x) for x in v1.split('.')]
            parts2 = [int(x) for x in v2.split('.')]

            # 补齐长度
            max_len = max(len(parts1), len(parts2))
            parts1.extend([0] * (max_len - len(parts1)))
            parts2.extend([0] * (max_len - len(parts2)))

            for p1, p2 in zip(parts1, parts2):
                if p1 < p2:
                    return -1
                elif p1 > p2:
                    return 1

            return 0
        except (ValueError, AttributeError):
            return 0

    def get_install_order(self, plugins):
        """计算插件安装顺序（拓扑排序）

        Args:
            plugins: 要安装的插件列表

        Returns:
            安装顺序列表

        Raises:
            ValueError: 存在循环依赖时
        """
        with self._lock:
            # 构建子图
            subgraph = defaultdict(list)
            in_degree = defaultdict(int)

            for plugin_name in plugins:
                if plugin_name not in in_degree:
                    in_degree[plugin_name] = 0

                if plugin_name in self._nodes:
                    for dep in self._nodes[plugin_name].dependencies:
                        dep_name = dep['name']
                        if dep_name in plugins:  # 只考虑列表中的插件
                            subgraph[dep_name].append(plugin_name)
                            in_degree[plugin_name] += 1

            # 拓扑排序
            queue = deque([
                name for name in plugins
                if in_degree[name] == 0
            ])
            order = []

            while queue:
                current = queue.popleft()
                order.append(current)

                for dependent in subgraph[current]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

            # 检查是否有循环
            if len(order) != len(plugins):
                missing = [p for p in plugins if p not in order]
                raise ValueError(f"存在循环依赖: {missing}")

            return order

    def resolve_dependencies(self, name, installed=None):
        """解析插件的所有依赖

        Args:
            name: 插件名称
            installed: 已安装的插件集合

        Returns:
            需要安装的插件列表（按安装顺序）
        """
        with self._lock:
            if installed is None:
                installed = set()

            # 收集所有需要的插件
            needed = set()
            queue = deque([name])

            while queue:
                current = queue.popleft()
                if current in needed:
                    continue

                needed.add(current)

                if current in self._nodes:
                    for dep in self._nodes[current].dependencies:
                        if dep['name'] not in installed:
                            queue.append(dep['name'])

            # 排除已安装的
            to_install = needed - installed

            # 计算安装顺序
            try:
                return self.get_install_order(list(to_install))
            except ValueError as e:
                logger.error(f"依赖解析失败: {e}")
                return list(to_install)

    def get_dependency_tree(self, name, depth=0, max_depth=5):
        """获取依赖树

        Args:
            name: 插件名称
            depth: 当前深度
            max_depth: 最大深度

        Returns:
            依赖树字典
        """
        with self._lock:
            if depth > max_depth:
                return {'name': name, 'children': [], 'truncated': True}

            if name not in self._nodes:
                return {'name': name, 'children': []}

            node = self._nodes[name]
            children = []

            for dep in node.dependencies:
                child = self.get_dependency_tree(
                    dep['name'], depth + 1, max_depth
                )
                child['optional'] = dep.get('optional', False)
                child['version_requirement'] = dep.get('version')
                children.append(child)

            return {
                'name': name,
                'version': node.version,
                'children': children
            }

    def get_stats(self):
        """获取依赖管理统计信息

        Returns:
            统计信息字典
        """
        with self._lock:
            total_plugins = len(self._nodes)
            total_dependencies = sum(
                len(node.dependencies) for node in self._nodes.values()
            )
            plugins_with_deps = sum(
                1 for node in self._nodes.values()
                if node.dependencies
            )

            return {
                'total_plugins': total_plugins,
                'total_dependencies': total_dependencies,
                'plugins_with_dependencies': plugins_with_deps,
                'conflicts': len(self._conflicts)
            }


# 全局依赖管理器实例
_dependency_manager = PluginDependencyManager()


def get_dependency_manager():
    """获取全局依赖管理器"""
    return _dependency_manager
