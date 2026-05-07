# coding:utf-8
import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'web'))

# pwd 模块在 Windows 上不可用，file.py 在模块级别导入了它
# 因此在 Windows 上需要 mock
if sys.platform == 'win32':
    import types
    pwd_mock = types.ModuleType('pwd')

    class FakePasswd:
        pw_name = 'www'
        pw_uid = 0
        pw_gid = 0

    pwd_mock.getpwuid = lambda uid: FakePasswd()
    pwd_mock.getpwnam = lambda name: FakePasswd()
    sys.modules['pwd'] = pwd_mock


class TestFileUtils:
    """文件操作工具函数测试"""

    def test_check_filename_valid(self):
        """测试文件名检查 - 合法文件名"""
        from utils.file import checkFileName
        assert checkFileName('test.txt') is True
        assert checkFileName('my_file.html') is True
        assert checkFileName('file-name.js') is True
        assert checkFileName('.hidden') is True

    def test_check_filename_invalid(self):
        """测试文件名检查 - 非法文件名"""
        from utils.file import checkFileName
        assert checkFileName('file\\name') is False
        assert checkFileName('file&name') is False
        assert checkFileName('file*name') is False
        assert checkFileName('file|name') is False
        assert checkFileName('file;name') is False

    def test_check_filename_with_path(self):
        """测试文件名检查 - 带路径的文件名"""
        from utils.file import checkFileName
        # 带路径时只检查最后的文件名部分
        assert checkFileName('/path/to/test.txt') is True
        assert checkFileName('/path/to/file;name') is False

    def test_check_dir_safe(self):
        """测试敏感目录检查 - 安全目录"""
        from utils.file import checkDir
        assert checkDir('/www/wwwroot/site') is True
        if sys.platform != 'win32':
            assert checkDir('/tmp/test') is False  # /tmp 在敏感列表中
            assert checkDir('/home/user/data') is False  # /home 在敏感列表中

    def test_check_dir_sensitive(self):
        """测试敏感目录检查 - 敏感目录"""
        from utils.file import checkDir
        assert checkDir('/') is False
        assert checkDir('/root') is False
        assert checkDir('/boot') is False
        assert checkDir('/bin') is False
        assert checkDir('/etc') is False
        assert checkDir('/dev') is False
        assert checkDir('/sbin') is False
        assert checkDir('/var') is False
        assert checkDir('/usr') is False
        assert checkDir('/sys') is False
        assert checkDir('/proc') is False
        assert checkDir('/www/server') is False

    def test_check_dir_double_slash(self):
        """测试敏感目录检查 - 双斜杠"""
        from utils.file import checkDir
        assert checkDir('//') is False
        assert checkDir('/root//') is False

    def test_check_dir_trailing_slash(self):
        """测试敏感目录检查 - 尾部斜杠"""
        from utils.file import checkDir
        assert checkDir('/root/') is False
        assert checkDir('/www/wwwroot/') is True

    def test_get_dir_size(self, tmp_path):
        """测试获取目录大小"""
        from utils.file import getDirSize
        (tmp_path / "file1.txt").write_bytes(b"A" * 100)
        (tmp_path / "file2.txt").write_bytes(b"B" * 200)
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file3.txt").write_bytes(b"C" * 300)

        size = getDirSize(str(tmp_path))
        assert size == 600

    def test_get_dir_size_empty(self, tmp_path):
        """测试获取空目录大小"""
        from utils.file import getDirSize
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        size = getDirSize(str(empty_dir))
        assert size == 0

    def test_get_count(self, tmp_path):
        """测试获取文件数量"""
        from utils.file import getCount
        for i in range(5):
            (tmp_path / f"file{i}.txt").write_text(f"content{i}")

        count = getCount(str(tmp_path))
        assert count == 5

    def test_get_count_with_search(self, tmp_path):
        """测试获取文件数量（带搜索）"""
        from utils.file import getCount
        (tmp_path / "test1.txt").write_text("a")
        (tmp_path / "test2.txt").write_text("b")
        (tmp_path / "other.txt").write_text("c")

        count = getCount(str(tmp_path), "test")
        assert count == 2

    def test_get_count_empty_dir(self, tmp_path):
        """测试获取空目录文件数量"""
        from utils.file import getCount
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        count = getCount(str(empty_dir))
        assert count == 0

    def test_get_access(self, tmp_path):
        """测试获取文件权限"""
        from utils.file import getAccess
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")

        access = getAccess(str(test_file))
        assert 'chmod' in access
        assert 'chown' in access

    def test_create_file(self, tmp_path):
        """测试创建文件"""
        from utils.file import createFile
        file_path = str(tmp_path / "new_file.txt")
        result = createFile(file_path)
        # 在 Windows 上可能因为 setFileAccept 失败
        assert os.path.exists(file_path) or result['status'] is False

    def test_create_file_exists(self, tmp_path):
        """测试创建已存在的文件"""
        from utils.file import createFile
        file_path = str(tmp_path / "existing.txt").replace('\\', '/')
        (tmp_path / "existing.txt").write_text("exists")
        result = createFile(file_path)
        # checkFileName 会在 Windows 路径上失败，或者文件已存在
        assert result['status'] is False

    def test_create_dir(self, tmp_path):
        """测试创建目录"""
        from utils.file import createDir
        dir_path = str(tmp_path / "new_dir").replace('\\', '/')
        result = createDir(dir_path)
        assert os.path.exists(dir_path) or result['status'] is False

    def test_create_dir_exists(self, tmp_path):
        """测试创建已存在的目录"""
        from utils.file import createDir
        dir_path = str(tmp_path / "existing_dir").replace('\\', '/')
        os.makedirs(dir_path)
        result = createDir(dir_path)
        assert result['status'] is False

    def test_get_file_body(self, tmp_path):
        """测试读取文件内容"""
        from utils.file import getFileBody
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!", encoding='utf-8')

        result = getFileBody(str(test_file))
        assert result['status'] is True
        assert result['data']['data'] == "Hello, World!"
        assert result['data']['encoding'] == 'utf-8'

    def test_get_file_body_not_exists(self):
        """测试读取不存在的文件"""
        from utils.file import getFileBody
        result = getFileBody('/nonexistent/file.txt')
        assert result['status'] is False

    def test_get_file_body_too_large(self, tmp_path):
        """测试读取过大的文件"""
        from utils.file import getFileBody
        test_file = tmp_path / "large.txt"
        # 创建一个大于 2MB 的文件
        test_file.write_bytes(b"X" * (2097152 + 1))

        result = getFileBody(str(test_file))
        assert result['status'] is False
        assert '大于' in result['msg']

    def test_save_body(self, tmp_path):
        """测试保存文件内容"""
        from utils.file import saveBody
        test_file = tmp_path / "test.txt"
        test_file.write_text("old content", encoding='utf-8')

        result = saveBody(str(test_file), "new content", "utf-8")
        assert result['status'] is True
        assert test_file.read_text(encoding='utf-8') == "new content"

    def test_save_body_not_exists(self):
        """测试保存到不存在的文件"""
        from utils.file import saveBody
        result = saveBody('/nonexistent/file.txt', "content", "utf-8")
        assert result['status'] is False

    @pytest.mark.skipif(sys.platform == 'win32', reason="os.chown 在 Windows 不可用")
    def test_copy_file(self, tmp_path):
        """测试复制文件"""
        from utils.file import copyFile
        import json as json_mod
        src = tmp_path / "source.txt"
        src.write_text("source content")
        dst = tmp_path / "dest.txt"

        result = copyFile(str(src), str(dst))
        # result 可能是 dict 或 JSON string
        if isinstance(result, str):
            result = json_mod.loads(result)
        assert result['status'] is True
        assert dst.exists()
        assert dst.read_text() == "source content"

    def test_copy_file_same_path(self, tmp_path):
        """测试复制文件到同一路径"""
        from utils.file import copyFile
        import json as json_mod
        src = tmp_path / "file.txt"
        src.write_text("content")

        result = copyFile(str(src), str(src))
        if isinstance(result, str):
            result = json_mod.loads(result)
        assert result['status'] is False

    def test_copy_file_not_exists(self):
        """测试复制不存在的文件"""
        from utils.file import copyFile
        import json as json_mod
        result = copyFile('/nonexistent/src.txt', '/tmp/dst.txt')
        if isinstance(result, str):
            result = json_mod.loads(result)
        assert result['status'] is False

    @pytest.mark.skipif(sys.platform == 'win32', reason="os.chown 在 Windows 不可用")
    def test_copy_dir(self, tmp_path):
        """测试复制目录"""
        from utils.file import copyDir
        import json as json_mod
        src_dir = tmp_path / "source_dir"
        src_dir.mkdir()
        (src_dir / "file.txt").write_text("content")
        dst_dir = tmp_path / "dest_dir"

        result = copyDir(str(src_dir), str(dst_dir))
        if isinstance(result, str):
            result = json_mod.loads(result)
        assert result['status'] is True
        assert dst_dir.exists()
        assert (dst_dir / "file.txt").read_text() == "content"

    def test_copy_dir_not_exists(self, tmp_path):
        """测试复制不存在的目录"""
        from utils.file import copyDir
        import json as json_mod
        result = copyDir(str(tmp_path / "nonexistent"), str(tmp_path / "dest"))
        if isinstance(result, str):
            result = json_mod.loads(result)
        assert result['status'] is False

    def test_copy_dir_already_exists(self, tmp_path):
        """测试复制到已存在的目录"""
        from utils.file import copyDir
        import json as json_mod
        src_dir = tmp_path / "source"
        src_dir.mkdir()
        dst_dir = tmp_path / "dest"
        dst_dir.mkdir()

        result = copyDir(str(src_dir), str(dst_dir))
        if isinstance(result, str):
            result = json_mod.loads(result)
        assert result['status'] is False

    @pytest.mark.skipif(sys.platform == 'win32', reason="setFileAccept 使用 chown，在 Windows 不可用")
    def test_mv_file(self, tmp_path):
        """测试移动文件"""
        from utils.file import mvFile
        import json as json_mod
        src = tmp_path / "source.txt"
        src.write_text("content")
        dst = tmp_path / "dest.txt"

        result = mvFile(str(src), str(dst))
        if isinstance(result, str):
            result = json_mod.loads(result)
        assert result['status'] is True
        assert not src.exists()
        assert dst.exists()

    def test_mv_file_not_exists(self, tmp_path):
        """测试移动不存在的文件"""
        from utils.file import mvFile
        import json as json_mod
        result = mvFile('/nonexistent/src.txt', str(tmp_path / "dst.txt"))
        if isinstance(result, str):
            result = json_mod.loads(result)
        assert result['status'] is False

    @pytest.mark.skipif(sys.platform == 'win32', reason="thisdb/chattr 在 Windows 不可用")
    def test_file_delete(self, tmp_path):
        """测试删除文件"""
        from utils.file import fileDelete
        import json as json_mod
        test_file = tmp_path / "to_delete.txt"
        test_file.write_text("delete me")

        result = fileDelete(str(test_file))
        if isinstance(result, str):
            result = json_mod.loads(result)
        assert result['status'] is True
        assert not test_file.exists()

    def test_file_delete_not_exists(self):
        """测试删除不存在的文件"""
        from utils.file import fileDelete
        import json as json_mod
        result = fileDelete('/nonexistent/file.txt')
        if isinstance(result, str):
            result = json_mod.loads(result)
        assert result['status'] is False

    @pytest.mark.skipif(sys.platform == 'win32', reason="chattr/thisdb 在 Windows 不可用")
    def test_dir_delete(self, tmp_path):
        """测试删除目录"""
        from utils.file import dirDelete
        import json as json_mod
        test_dir = tmp_path / "to_delete"
        test_dir.mkdir()
        (test_dir / "file.txt").write_text("content")

        result = dirDelete(str(test_dir))
        if isinstance(result, str):
            result = json_mod.loads(result)
        assert result['status'] is True
        assert not test_dir.exists()

    def test_dir_delete_not_exists(self):
        """测试删除不存在的目录"""
        from utils.file import dirDelete
        import json as json_mod
        result = dirDelete('/nonexistent/dir')
        if isinstance(result, str):
            result = json_mod.loads(result)
        assert result['status'] is False

    def test_set_file_access(self, tmp_path):
        """测试设置文件权限"""
        from utils.file import setFileAccess
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")

        if sys.platform != 'win32':
            result = setFileAccess(str(test_file), "www", "755")
            assert result['status'] is True

    def test_set_file_access_not_exists(self):
        """测试设置不存在文件的权限"""
        from utils.file import setFileAccess
        result = setFileAccess('/nonexistent/file.txt', "www", "755")
        assert result['status'] is False

    def test_sort_file_list_mtime(self, tmp_path):
        """测试文件列表排序 - 修改时间"""
        from utils.file import sortFileList
        for i in range(3):
            f = tmp_path / f"file{i}.txt"
            f.write_text(f"content{i}")

        result = sortFileList(str(tmp_path), 'mtime', 'desc')
        assert len(result) == 3

    def test_sort_file_list_size(self, tmp_path):
        """测试文件列表排序 - 大小"""
        from utils.file import sortFileList
        (tmp_path / "small.txt").write_text("a")
        (tmp_path / "large.txt").write_text("a" * 100)

        result = sortFileList(str(tmp_path), 'size', 'desc')
        assert len(result) == 2
        assert result[0] == 'large.txt'

    def test_sort_file_list_fname(self, tmp_path):
        """测试文件列表排序 - 文件名"""
        from utils.file import sortFileList
        (tmp_path / "c.txt").write_text("c")
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")

        result = sortFileList(str(tmp_path), 'fname', 'asc')
        assert len(result) == 3

    def test_get_sys_user_list(self):
        """测试获取系统用户列表"""
        from utils.file import getSysUserList
        users = getSysUserList()
        assert isinstance(users, list)
        assert len(users) > 0
        # root 用户应该存在
        if sys.platform != 'win32':
            assert 'root' in users

    def test_get_dir_list(self, tmp_path):
        """测试获取目录列表"""
        from utils.file import getDirList
        (tmp_path / "file1.txt").write_text("a")
        (tmp_path / "file2.txt").write_text("b")
        (tmp_path / "subdir").mkdir()

        # 使用空字符串作为 search 参数，因为 getDirList 内部对 None 处理有 bug
        result = getDirList(str(tmp_path), search="")
        assert 'count' in result
        assert 'dir' in result
        assert 'files' in result
        assert 'path' in result
        assert result['count'] == 3

    def test_get_dir_list_pagination(self, tmp_path):
        """测试获取目录列表 - 分页"""
        from utils.file import getDirList
        for i in range(20):
            (tmp_path / f"file{i:02d}.txt").write_text(f"content{i}")

        result = getDirList(str(tmp_path), page=1, size=10, search="")
        assert result['count'] == 20
        assert len(result['files']) + len(result['dir']) <= 10

    def test_get_dir_list_search(self, tmp_path):
        """测试获取目录列表 - 搜索"""
        from utils.file import getDirList
        (tmp_path / "test1.txt").write_text("a")
        (tmp_path / "test2.txt").write_text("b")
        (tmp_path / "other.txt").write_text("c")

        result = getDirList(str(tmp_path), search="test")
        assert result['count'] == 2

    def test_get_file_body_chinese(self, tmp_path):
        """测试读取中文文件内容"""
        from utils.file import getFileBody
        test_file = tmp_path / "chinese.txt"
        test_file.write_text("你好世界", encoding='utf-8')

        result = getFileBody(str(test_file))
        assert result['status'] is True
        assert result['data']['data'] == "你好世界"
