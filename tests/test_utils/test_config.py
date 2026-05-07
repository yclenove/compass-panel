# coding:utf-8
"""配置模块测试"""

import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'web'))


class TestGetUnauthStatus:
    """测试未认证状态获取"""

    def test_default_status(self):
        """测试默认状态"""
        from utils.config import getUnauthStatus
        result = getUnauthStatus()
        assert result["code"] == "0"
        assert "默认" in result["text"]

    def test_400_status(self):
        """测试 400 状态"""
        from utils.config import getUnauthStatus
        result = getUnauthStatus("400")
        assert result["code"] == "400"
        assert "400" in result["text"]

    def test_401_status(self):
        """测试 401 状态"""
        from utils.config import getUnauthStatus
        result = getUnauthStatus("401")
        assert result["code"] == "401"
        assert "401" in result["text"]

    def test_403_status(self):
        """测试 403 状态"""
        from utils.config import getUnauthStatus
        result = getUnauthStatus("403")
        assert result["code"] == "403"
        assert "403" in result["text"]

    def test_404_status(self):
        """测试 404 状态"""
        from utils.config import getUnauthStatus
        result = getUnauthStatus("404")
        assert result["code"] == "404"
        assert "404" in result["text"]

    def test_408_status(self):
        """测试 408 状态"""
        from utils.config import getUnauthStatus
        result = getUnauthStatus("408")
        assert result["code"] == "408"
        assert "408" in result["text"]

    def test_416_status(self):
        """测试 416 状态"""
        from utils.config import getUnauthStatus
        result = getUnauthStatus("416")
        assert result["code"] == "416"
        assert "416" in result["text"]

    def test_unknown_status(self):
        """测试未知状态"""
        from utils.config import getUnauthStatus
        result = getUnauthStatus("999")
        assert result["code"] == "0"
        assert "默认" in result["text"]

    def test_integer_input(self):
        """测试整数输入"""
        from utils.config import getUnauthStatus
        result = getUnauthStatus(404)
        assert result["code"] == "404"
