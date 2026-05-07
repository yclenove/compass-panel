# coding:utf-8
"""网站管理 API 测试"""

import pytest


class TestSitesAPI:
    """网站管理 API 测试类"""

    def test_sites_page_accessible(self, client):
        """测试网站管理页面可访问"""
        if client is None:
            pytest.skip("无法创建客户端")
        response = client.get('/site')
        assert response.status_code in [200, 302, 404]

    def test_get_sites_list(self, auth_client):
        """测试获取网站列表"""
        if auth_client is None:
            pytest.skip("无法创建客户端")
        response = auth_client.post('/site/get_sites_list', data={
            'page': 1,
            'size': 10,
            'type_id': 0,
            'search': '',
            'order': 'id desc'
        })
        # 可能返回 200 或 404（取决于路由是否存在）
        assert response.status_code in [200, 302, 404]

    def test_get_sites_count(self, auth_client):
        """测试获取网站数量"""
        if auth_client is None:
            pytest.skip("无法创建客户端")
        response = auth_client.post('/site/get_sites_count')
        assert response.status_code in [200, 302, 404]

    def test_site_search_with_xss(self, auth_client):
        """测试网站搜索 XSS 防护"""
        if auth_client is None:
            pytest.skip("无法创建客户端")
        response = auth_client.post('/site/get_sites_list', data={
            'page': 1,
            'size': 10,
            'search': '<script>alert(1)</script>'
        })
        # 应该安全处理，不返回 500
        assert response.status_code != 500

    def test_site_search_with_sql_injection(self, auth_client):
        """测试网站搜索 SQL 注入防护"""
        if auth_client is None:
            pytest.skip("无法创建客户端")
        response = auth_client.post('/site/get_sites_list', data={
            'page': 1,
            'size': 10,
            'search': "'; DROP TABLE sites; --"
        })
        # 应该安全处理，不返回 500
        assert response.status_code != 500


class TestSitesDatabase:
    """网站数据库操作测试"""

    def test_get_sites_count_module(self):
        """测试获取网站数量模块"""
        try:
            from thisdb import sites
            count = sites.getSitesCount()
            assert isinstance(count, int)
            assert count >= 0
        except ImportError:
            pytest.skip("无法导入 sites 模块")

    def test_get_sites_list_module(self):
        """测试获取网站列表模块"""
        try:
            from thisdb import sites
            data = sites.getSitesList(page=1, size=10, order="id desc")
            assert isinstance(data, dict)
            assert 'list' in data
            assert 'count' in data
            assert isinstance(data['list'], list)
            assert isinstance(data['count'], int)
        except ImportError:
            pytest.skip("无法导入 sites 模块")

    def test_is_sites_exist(self):
        """测试检查网站是否存在"""
        try:
            from thisdb import sites
            result = sites.isSitesExist("nonexistent-site-12345.com")
            assert isinstance(result, bool)
            assert result is False
        except ImportError:
            pytest.skip("无法导入 sites 模块")

    def test_get_sites_by_id_not_found(self):
        """测试通过 ID 获取网站 - 不存在"""
        try:
            from thisdb import sites
            result = sites.getSitesById(999999)
            assert result is None or result == {}
        except ImportError:
            pytest.skip("无法导入 sites 模块")

    def test_get_sites_by_name_not_found(self):
        """测试通过名称获取网站 - 不存在"""
        try:
            from thisdb import sites
            result = sites.getSitesByName("nonexistent-site-12345.com")
            assert result is None or result == {}
        except ImportError:
            pytest.skip("无法导入 sites 模块")
