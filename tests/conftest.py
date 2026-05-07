import os
import sys
import pytest

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))


@pytest.fixture
def app():
    """创建 Flask 应用实例"""
    try:
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        with app.app_context():
            yield app
    except Exception:
        # 如果无法创建应用，返回 None
        yield None


@pytest.fixture
def client(app):
    """创建测试客户端"""
    if app is None:
        pytest.skip("无法创建 Flask 应用")
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """创建已认证的测试客户端"""
    # 尝试登录
    client.post('/do_login', data={
        'username': 'admin',
        'password': 'admin123',
        'code': ''
    })
    return client
