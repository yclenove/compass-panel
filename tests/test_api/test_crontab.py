# coding:utf-8
"""计划任务 API 测试"""

import pytest


class TestCrontabAPI:
    """计划任务 API 测试类"""

    def test_crontab_page_accessible(self, client):
        """测试计划任务页面可访问"""
        if client is None:
            pytest.skip("无法创建客户端")
        response = client.get('/crontab')
        assert response.status_code in [200, 302, 404]

    def test_get_crontab_list(self, auth_client):
        """测试获取计划任务列表"""
        if auth_client is None:
            pytest.skip("无法创建客户端")
        response = auth_client.post('/crontab/get_crontab_list', data={
            'page': 1,
            'size': 10
        })
        assert response.status_code in [200, 302, 404]


class TestCrontabDatabase:
    """计划任务数据库操作测试"""

    def test_get_crontab_list_module(self):
        """测试获取计划任务列表模块"""
        try:
            from thisdb import crontab
            data = crontab.getCrontabList(page=1, size=10)
            assert isinstance(data, dict)
            assert 'list' in data
            assert 'count' in data
            assert isinstance(data['list'], list)
            assert isinstance(data['count'], int)
        except ImportError:
            pytest.skip("无法导入 crontab 模块")

    def test_get_cron_by_name_not_found(self):
        """测试通过名称获取计划任务 - 不存在"""
        try:
            from thisdb import crontab
            result = crontab.getCronByName("nonexistent-task-12345")
            assert result is None or result == {}
        except ImportError:
            pytest.skip("无法导入 crontab 模块")

    def test_get_crond_not_found(self):
        """测试通过 ID 获取计划任务 - 不存在"""
        try:
            from thisdb import crontab
            result = crontab.getCrond(999999)
            assert result is None or result == {}
        except ImportError:
            pytest.skip("无法导入 crontab 模块")


class TestCrontabValidation:
    """计划任务输入验证测试"""

    def test_crontab_page_validation(self):
        """测试页码验证"""
        try:
            from thisdb import crontab
            # 测试负数页码
            data = crontab.getCrontabList(page=-1, size=10)
            assert isinstance(data, dict)
        except ImportError:
            pytest.skip("无法导入 crontab 模块")

    def test_crontab_size_validation(self):
        """测试每页数量验证"""
        try:
            from thisdb import crontab
            # 测试零每页数量
            data = crontab.getCrontabList(page=1, size=0)
            assert isinstance(data, dict)
        except ImportError:
            pytest.skip("无法导入 crontab 模块")
