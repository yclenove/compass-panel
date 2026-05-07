# coding:utf-8
"""设置模块测试"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'web'))


class TestSettingSingleton:
    """测试设置类单例模式"""

    def test_instance_returns_same(self):
        """测试单例返回同一实例"""
        from utils.setting import setting
        s1 = setting.instance()
        s2 = setting.instance()
        assert s1 is s2

    def test_instance_has_expected_methods(self):
        """测试实例有预期方法"""
        from utils.setting import setting
        s = setting.instance()
        assert hasattr(s, 'savePanelSsl')
        assert hasattr(s, 'getPanelSsl')
