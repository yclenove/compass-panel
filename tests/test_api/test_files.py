import pytest
import os
import tempfile


class TestFiles:
    """文件管理 API 测试"""

    @pytest.fixture
    def test_dir(self, tmp_path):
        """创建测试目录"""
        test_dir = tmp_path / "test_files"
        test_dir.mkdir()
        (test_dir / "test.txt").write_text("Hello, World!")
        (test_dir / "subdir").mkdir()
        return str(test_dir)

    def test_get_dir(self, auth_client, test_dir):
        """测试获取目录列表"""
        if auth_client is None:
            pytest.skip("无法创建客户端")
        response = auth_client.post('/files/get_dir', data={
            'path': test_dir
        })
        data = response.get_json()
        assert data['status'] is True
        assert 'dir' in data['data']
        assert 'file' in data['data']

    def test_get_file_content(self, auth_client, test_dir):
        """测试获取文件内容"""
        if auth_client is None:
            pytest.skip("无法创建客户端")
        filepath = os.path.join(test_dir, 'test.txt')
        response = auth_client.post('/files/get_file_content', data={
            'path': filepath
        })
        data = response.get_json()
        assert data['status'] is True
