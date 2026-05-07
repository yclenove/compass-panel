import os
import sys
import pytest

# 添加 web/ 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))


def test_development_mode_enabled(monkeypatch):
    """测试开发模式启用"""
    monkeypatch.setenv('MW_ENV', 'development')
    import importlib
    import config
    importlib.reload(config)
    assert config.DEV_MODE is True
    assert config.DISABLE_CAPTCHA is True


def test_development_mode_disabled(monkeypatch):
    """测试开发模式禁用"""
    monkeypatch.delenv('MW_ENV', raising=False)
    import importlib
    import config
    importlib.reload(config)
    assert config.DEV_MODE is False
