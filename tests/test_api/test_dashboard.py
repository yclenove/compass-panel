import pytest


class TestDashboard:
    """仪表盘 API 测试"""

    def test_index_page(self, client):
        """测试首页访问"""
        if client is None:
            pytest.skip("无法创建客户端")
        response = client.get('/')
        assert response.status_code in [200, 302]

    def test_login_page(self, client):
        """测试登录页面"""
        if client is None:
            pytest.skip("无法创建客户端")
        response = client.get('/login')
        assert response.status_code in [200, 302]

    def test_check_login_unauthenticated(self, client):
        """测试未登录状态检查"""
        if client is None:
            pytest.skip("无法创建客户端")
        response = client.get('/check_login')
        data = response.get_json()
        assert data['status'] is False

    def test_system_info(self, auth_client):
        """测试系统信息接口"""
        if auth_client is None:
            pytest.skip("无法创建客户端")
        response = auth_client.post('/system/get_system_info')
        data = response.get_json()
        assert 'data' in data
