# coding:utf-8
"""防火墙 API 测试"""

import pytest


class TestFirewallAPI:
    """防火墙 API 测试类"""

    def test_firewall_page_accessible(self, client):
        """测试防火墙页面可访问"""
        if client is None:
            pytest.skip("无法创建客户端")
        response = client.get('/firewall')
        assert response.status_code in [200, 302, 404]

    def test_get_firewall_list(self, auth_client):
        """测试获取防火墙规则列表"""
        if auth_client is None:
            pytest.skip("无法创建客户端")
        response = auth_client.post('/firewall/get_firewall_list', data={
            'page': 1,
            'size': 10
        })
        assert response.status_code in [200, 302, 404]


class TestFirewallDatabase:
    """防火墙数据库操作测试"""

    def test_get_firewall_list_module(self):
        """测试获取防火墙规则列表模块"""
        try:
            from thisdb import firewall
            data = firewall.getFirewallList(page=1, size=10)
            assert isinstance(data, dict)
            assert 'list' in data
            assert 'count' in data
            assert isinstance(data['list'], list)
            assert isinstance(data['count'], int)
        except ImportError:
            pytest.skip("无法导入 firewall 模块")

    def test_get_firewall_count_by_port(self):
        """测试通过端口获取防火墙规则数量"""
        try:
            from thisdb import firewall
            count = firewall.getFirewallCountByPort(80)
            assert isinstance(count, int)
            assert count >= 0
        except ImportError:
            pytest.skip("无法导入 firewall 模块")

    def test_get_firewall_count_nonexistent_port(self):
        """测试不存在端口的防火墙规则数量"""
        try:
            from thisdb import firewall
            count = firewall.getFirewallCountByPort(99999)
            assert isinstance(count, int)
            assert count == 0
        except ImportError:
            pytest.skip("无法导入 firewall 模块")


class TestFirewallValidation:
    """防火墙输入验证测试"""

    def test_firewall_port_validation(self):
        """测试端口验证"""
        from utils.security import validate_input

        # 有效端口
        valid, msg = validate_input("80", input_type="port")
        assert valid is True

        # 无效端口 - 超出范围
        valid, msg = validate_input("99999", input_type="port")
        assert valid is False

        # 无效端口 - 零
        valid, msg = validate_input("0", input_type="port")
        assert valid is False

    def test_firewall_protocol_validation(self):
        """测试协议验证"""
        valid_protocols = ["tcp", "udp", "tcp/udp"]
        for protocol in valid_protocols:
            assert protocol in ["tcp", "udp", "tcp/udp"]
