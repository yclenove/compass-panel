import pytest


@pytest.fixture
def sample_user():
    """创建示例用户数据"""
    return {'username': 'admin', 'password': 'admin123'}
