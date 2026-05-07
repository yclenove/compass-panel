import pytest
import hashlib
import os
import sys
import json
import tempfile
import time

# 确保 web 目录在 path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'web'))


class TestMwUtils:
    """mw 工具函数测试"""

    def test_md5_basic(self):
        """测试 MD5 基本功能"""
        from core.mw import md5
        result = md5('hello')
        assert result == hashlib.md5('hello'.encode('utf-8')).hexdigest()

    def test_md5_empty_string(self):
        """测试 MD5 空字符串"""
        from core.mw import md5
        result = md5('')
        assert result == hashlib.md5(b'').hexdigest()

    def test_md5_chinese(self):
        """测试 MD5 中文字符串"""
        from core.mw import md5
        result = md5('你好世界')
        expected = hashlib.md5('你好世界'.encode('utf-8')).hexdigest()
        assert result == expected

    def test_return_data_without_data(self):
        """测试返回数据格式（无数据）"""
        from core.mw import returnData
        result = returnData(True, 'success')
        assert result['status'] is True
        assert result['msg'] == 'success'
        assert 'data' not in result

    def test_return_data_with_data(self):
        """测试返回数据格式（有数据）"""
        from core.mw import returnData
        result = returnData(False, 'error', {'key': 'value'})
        assert result['status'] is False
        assert result['msg'] == 'error'
        assert result['data'] == {'key': 'value'}

    def test_return_data_with_none_data(self):
        """测试返回数据格式（None 数据）"""
        from core.mw import returnData
        result = returnData(True, 'ok', None)
        assert result['status'] is True
        assert 'data' not in result

    def test_get_random_string_length(self):
        """测试随机字符串长度"""
        from core.mw import getRandomString
        for length in [0, 1, 10, 50, 100]:
            result = getRandomString(length)
            assert len(result) == length

    def test_get_random_string_uniqueness(self):
        """测试随机字符串唯一性"""
        from core.mw import getRandomString
        results = set()
        for _ in range(100):
            results.add(getRandomString(16))
        assert len(results) == 100

    def test_get_random_string_charset(self):
        """测试随机字符串字符集"""
        from core.mw import getRandomString
        valid_chars = set('AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789')
        result = getRandomString(1000)
        for char in result:
            assert char in valid_chars

    def test_to_size_bytes(self):
        """测试字节单位转换 - 字节"""
        from core.mw import toSize
        assert toSize(100) == '100b'
        assert toSize(0) == '0b'

    def test_to_size_kb(self):
        """测试字节单位转换 - KB"""
        from core.mw import toSize
        assert toSize(1024) == '1.0KB'
        assert toSize(2048) == '2.0KB'

    def test_to_size_mb(self):
        """测试字节单位转换 - MB"""
        from core.mw import toSize
        result = toSize(1048576)
        assert 'MB' in result
        assert '1.0' in result

    def test_to_size_gb(self):
        """测试字节单位转换 - GB"""
        from core.mw import toSize
        result = toSize(1073741824)
        assert 'GB' in result

    def test_to_size_with_middle(self):
        """测试字节单位转换（带分隔符）"""
        from core.mw import toSize
        result = toSize(1024, ' ')
        assert result == '1.0 KB'

    def test_check_port_valid(self):
        """测试合法端口检查"""
        from core.mw import checkPort
        assert checkPort('8080') is True
        assert checkPort('80') is True
        assert checkPort('3306') is True
        assert checkPort('65535') is True
        assert checkPort('1') is True

    def test_check_port_invalid(self):
        """测试非法端口检查"""
        from core.mw import checkPort
        assert checkPort('21') is False
        assert checkPort('443') is False
        assert checkPort('888') is False
        assert checkPort('0') is False
        assert checkPort('65536') is False
        assert checkPort('-1') is False

    def test_check_ip_valid(self):
        """测试合法 IP 地址检查"""
        from core.mw import checkIp
        assert checkIp('192.168.1.1') is True
        assert checkIp('10.0.0.1') is True
        assert checkIp('255.255.255.255') is True
        assert checkIp('0.0.0.0') is True
        assert checkIp('127.0.0.1') is True

    def test_check_ip_invalid(self):
        """测试非法 IP 地址检查"""
        from core.mw import checkIp
        assert checkIp('256.1.1.1') is False
        assert checkIp('1.1.1') is False
        assert checkIp('abc.def.ghi.jkl') is False
        assert checkIp('') is False

    def test_is_number_valid(self):
        """测试数字检查 - 有效数字"""
        from core.mw import isNumber
        assert isNumber('123') is True
        assert isNumber('3.14') is True
        assert isNumber('-1') is True
        assert isNumber('0') is True
        assert isNumber('1e10') is True

    def test_is_number_invalid(self):
        """测试数字检查 - 非数字"""
        from core.mw import isNumber
        assert isNumber('abc') is False
        assert isNumber('') is False
        assert isNumber('12abc') is False

    def test_file_name_check_valid(self):
        """测试文件名检查 - 合法文件名"""
        from core.mw import fileNameCheck
        assert fileNameCheck('test.txt') is True
        assert fileNameCheck('my_file-name.html') is True
        assert fileNameCheck('file123') is True

    def test_file_name_check_invalid(self):
        """测试文件名检查 - 非法文件名"""
        from core.mw import fileNameCheck
        assert fileNameCheck('file;name') is False
        assert fileNameCheck('file&name') is False
        assert fileNameCheck('file<name') is False
        assert fileNameCheck('file>name') is False

    def test_in_array_found(self):
        """测试数组搜索 - 找到"""
        from core.mw import inArray
        assert inArray(['a', 'b', 'c'], 'b') is True

    def test_in_array_not_found(self):
        """测试数组搜索 - 未找到"""
        from core.mw import inArray
        assert inArray(['a', 'b', 'c'], 'd') is False
        assert inArray([], 'a') is False

    def test_get_date_format(self):
        """测试日期格式"""
        from core.mw import getDate
        result = getDate()
        # 验证格式为 YYYY-MM-DD HH:MM:SS
        assert len(result) == 19
        assert result[4] == '-'
        assert result[7] == '-'
        assert result[13] == ':'
        assert result[16] == ':'

    def test_get_unique_id(self):
        """测试唯一ID生成"""
        import time
        from core.mw import getUniqueId
        id1 = getUniqueId()
        time.sleep(0.002)  # 确保时间戳不同
        id2 = getUniqueId()
        assert id1 != id2
        assert len(id1) > 0

    def test_get_info_format(self):
        """测试消息格式化"""
        from core.mw import getInfo
        result = getInfo("测试{1}消息{2}", ("参数1", "参数2"))
        assert result == "测试参数1消息参数2"

    def test_get_info_no_args(self):
        """测试消息格式化（无参数）"""
        from core.mw import getInfo
        result = getInfo("简单消息")
        assert result == "简单消息"

    def test_get_file_suffix(self):
        """测试获取文件后缀"""
        from core.mw import getFileSuffix
        assert getFileSuffix('test.txt') == 'txt'
        assert getFileSuffix('archive.tar.gz') == 'gz'
        assert getFileSuffix('noext') == 'noext'

    def test_get_path_suffix(self):
        """测试获取路径后缀"""
        from core.mw import getPathSuffix
        assert getPathSuffix('/path/to/file.txt') == '.txt'
        assert getPathSuffix('/path/to/file') == ''

    def test_format_date_default(self):
        """测试日期格式化 - 默认"""
        from core.mw import formatDate
        result = formatDate()
        assert len(result) == 19
        assert '-' in result
        assert ':' in result

    def test_format_date_custom_format(self):
        """测试日期格式化 - 自定义格式"""
        from core.mw import formatDate
        result = formatDate("%Y/%m/%d")
        assert '/' in result

    def test_format_date_with_timestamp(self):
        """测试日期格式化 - 指定时间戳"""
        from core.mw import formatDate
        ts = 1609459200  # 2021-01-01 00:00:00 UTC
        result = formatDate(times=ts)
        assert '2021' in result or '2020' in result  # 取决于时区

    def test_get_data_from_int(self):
        """测试时间戳转日期"""
        from core.mw import getDataFromInt
        ts = 1609459200
        result = getDataFromInt(ts)
        assert len(result) == 19
        assert '-' in result

    def test_read_write_file(self, tmp_path):
        """测试文件读写"""
        from core.mw import readFile, writeFile
        test_file = str(tmp_path / "test.txt")
        content = "Hello, World!\n你好世界"

        # 写入
        result = writeFile(test_file, content)
        assert result is True

        # 读取
        read_content = readFile(test_file)
        assert read_content == content

    def test_read_file_not_exists(self):
        """测试读取不存在的文件"""
        from core.mw import readFile
        result = readFile('/nonexistent/file/path.txt')
        assert result is False

    def test_write_file_invalid_path(self, tmp_path):
        """测试写入无效路径"""
        from core.mw import writeFile
        import core.mw as mw
        # 需要确保日志目录存在
        original = mw.getPanelDir
        mw.getPanelDir = lambda: str(tmp_path)
        try:
            logs_dir = tmp_path / "logs"
            logs_dir.mkdir(exist_ok=True)
            result = writeFile('/nonexistent/dir/file.txt', 'content')
            assert result is False
        finally:
            mw.getPanelDir = original

    def test_get_path_size_file(self, tmp_path):
        """测试获取文件大小"""
        from core.mw import getPathSize
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"Hello" * 100)
        size = getPathSize(str(test_file))
        assert size == 500

    def test_get_path_size_dir(self, tmp_path):
        """测试获取目录大小"""
        from core.mw import getPathSize
        (tmp_path / "file1.txt").write_bytes(b"A" * 100)
        (tmp_path / "file2.txt").write_bytes(b"B" * 200)
        size = getPathSize(str(tmp_path))
        assert size == 300

    def test_get_path_size_not_exists(self):
        """测试获取不存在路径的大小"""
        from core.mw import getPathSize
        assert getPathSize('/nonexistent/path') == 0

    def test_get_json(self):
        """测试 JSON 序列化"""
        from core.mw import getJson
        data = {'key': 'value', 'num': 123}
        result = getJson(data)
        parsed = json.loads(result)
        assert parsed == data

    def test_get_object_by_json(self):
        """测试 JSON 反序列化"""
        from core.mw import getObjectByJson
        json_str = '{"key": "value", "num": 123}'
        result = getObjectByJson(json_str)
        assert result == {'key': 'value', 'num': 123}

    def test_get_default_exists(self):
        """测试获取默认值 - 键存在"""
        from core.mw import getDefault
        data = {'key': 'value'}
        assert getDefault(data, 'key', 'default') == 'value'

    def test_get_default_not_exists(self):
        """测试获取默认值 - 键不存在"""
        from core.mw import getDefault
        data = {'key': 'value'}
        assert getDefault(data, 'missing', 'default') == 'default'

    def test_is_valid_ipv4(self):
        """测试 IPv4 验证"""
        from core.mw import isVaildIpV4
        assert isVaildIpV4('192.168.1.1') is True
        assert isVaildIpV4('10.0.0.1') is True
        assert isVaildIpV4('::1') is False
        assert isVaildIpV4('invalid') is False

    def test_is_valid_ipv6(self):
        """测试 IPv6 验证"""
        from core.mw import isVaildIpV6
        assert isVaildIpV6('::1') is True
        assert isVaildIpV6('fe80::1') is True
        assert isVaildIpV6('192.168.1.1') is False

    def test_is_valid_ip(self):
        """测试 IP 验证（通用）"""
        from core.mw import isVaildIp
        assert isVaildIp('192.168.1.1') is True
        assert isVaildIp('::1') is True
        assert isVaildIp('invalid') is False

    def test_get_str_between(self):
        """测试字符串截取"""
        from core.mw import getStrBetween
        result = getStrBetween('start', 'end', 'start_hello_end')
        assert result is not None
        assert 'hello' in result

    def test_get_str_between_not_found(self):
        """测试字符串截取 - 未找到"""
        from core.mw import getStrBetween
        result = getStrBetween('xxx', 'yyy', 'start_hello_end')
        assert result is None

    def test_is_number_integer(self):
        """测试整数判断"""
        from core.mw import isNumber
        assert isNumber('42') is True
        assert isNumber('-42') is True

    def test_is_number_float(self):
        """测试浮点数判断"""
        from core.mw import isNumber
        assert isNumber('3.14') is True
        assert isNumber('-3.14') is True

    def test_write_speed(self, tmp_path):
        """测试进度写入"""
        from core.mw import writeSpeed, getSpeed
        import core.mw as mw
        original = mw.getPanelDir
        mw.getPanelDir = lambda: str(tmp_path)
        try:
            # 确保 data 和 logs 目录存在
            (tmp_path / "data").mkdir(exist_ok=True)
            (tmp_path / "logs").mkdir(exist_ok=True)
            writeSpeed('test_task', 50, 100, 1024)
            speed = getSpeed()
            assert speed['title'] == 'test_task'
            assert speed['used'] == 50
            assert speed['total'] == 100
            assert speed['speed'] == 1024
            assert speed['progress'] == 50

            # 测试清除进度
            writeSpeed(None, 0, 0)
            speed = getSpeed()
            assert speed['title'] is None
        finally:
            mw.getPanelDir = original

    def test_return_json(self):
        """测试 JSON 返回格式"""
        from core.mw import returnJson
        result = returnJson(True, 'ok', {'data': 123})
        parsed = json.loads(result)
        assert parsed['status'] is True
        assert parsed['msg'] == 'ok'
        assert parsed['data'] == {'data': 123}

    def test_get_common_file(self):
        """测试通用配置文件路径"""
        from core.mw import getCommonFile
        data = getCommonFile()
        assert 'debug' in data
        assert 'close' in data
        assert 'basic_auth' in data
        assert 'ipv6' in data
        assert 'bind_domain' in data
        assert 'auth_secret' in data
        assert 'ssl' in data

    def test_get_os(self):
        """测试获取操作系统"""
        from core.mw import getOs
        result = getOs()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_is_apple_system(self):
        """测试是否为苹果系统"""
        from core.mw import isAppleSystem
        result = isAppleSystem()
        assert isinstance(result, bool)

    def test_sort_file_list_mtime(self, tmp_path):
        """测试文件列表排序 - 修改时间"""
        from core.mw import sortFileList
        # 创建测试文件
        for i in range(3):
            f = tmp_path / f"file{i}.txt"
            f.write_text(f"content{i}")
            time.sleep(0.01)

        result = sortFileList(str(tmp_path), 'mtime', 'desc')
        assert len(result) == 3

        result_asc = sortFileList(str(tmp_path), 'mtime', 'asc')
        assert len(result_asc) == 3

    def test_sort_file_list_size(self, tmp_path):
        """测试文件列表排序 - 文件大小"""
        from core.mw import sortFileList
        (tmp_path / "small.txt").write_text("a")
        (tmp_path / "medium.txt").write_text("a" * 100)
        (tmp_path / "large.txt").write_text("a" * 1000)

        result = sortFileList(str(tmp_path), 'size', 'desc')
        assert len(result) == 3
        assert result[0] == 'large.txt'

    def test_sort_file_list_fname(self, tmp_path):
        """测试文件列表排序 - 文件名"""
        from core.mw import sortFileList
        (tmp_path / "c.txt").write_text("c")
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")

        result = sortFileList(str(tmp_path), 'fname', 'asc')
        assert len(result) == 3

    @pytest.mark.skipif(sys.platform == 'win32', reason="pwd 模块在 Windows 不可用")
    def test_get_file_stats_desc(self, tmp_path):
        """测试获取文件状态描述"""
        from core.mw import getFileStatsDesc
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")

        result = getFileStatsDesc(str(test_file))
        assert isinstance(result, str)
        assert 'test.txt' in result
        assert ';' in result

    def test_encode_decode_aes(self):
        """测试 AES 加密解密"""
        from core.mw import aesEncrypt, aesDecrypt
        data = "Hello, World! 你好世界"
        key = "ABCDEFGHIJKLMNOP"
        vi = "0102030405060708"

        encrypted = aesEncrypt(data, key, vi)
        assert encrypted != data

        decrypted = aesDecrypt(encrypted, key, vi)
        assert decrypted.decode('utf-8') == data

    def test_double_crypt(self):
        """测试双重加密解密"""
        from core.mw import enDoubleCrypt, deDoubleCrypt
        key = "test_key"
        data = "Hello, World!"

        encrypted = enDoubleCrypt(key, data)
        assert encrypted != data

        decrypted = deDoubleCrypt(key, encrypted)
        assert decrypted == data

    def test_is_docker(self):
        """测试 Docker 环境检测"""
        from core.mw import isDocker
        result = isDocker()
        assert isinstance(result, bool)

    def test_systemd_cfg_dir(self):
        """测试 systemd 配置目录"""
        from core.mw import systemdCfgDir
        result = systemdCfgDir()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_panel_port(self, tmp_path):
        """测试获取面板端口"""
        from core.mw import getPanelPort
        import core.mw as mw
        original = mw.getPanelDir
        mw.getPanelDir = lambda: str(tmp_path)
        try:
            port_file = tmp_path / "data" / "port.pl"
            port_file.parent.mkdir(parents=True, exist_ok=True)
            port_file.write_text("8888")
            port = getPanelPort()
            assert port == 8888
        finally:
            mw.getPanelDir = original

    def test_get_host_port(self, tmp_path):
        """测试获取主机端口"""
        from core.mw import getHostPort
        import core.mw as mw
        original = mw.getPanelDir
        mw.getPanelDir = lambda: str(tmp_path)
        try:
            port_file = tmp_path / "data" / "port.pl"
            port_file.parent.mkdir(parents=True, exist_ok=True)
            port_file.write_text("9999")
            port = getHostPort()
            assert port == "9999"
        finally:
            mw.getPanelDir = original

    def test_set_host_port(self, tmp_path):
        """测试设置主机端口"""
        from core.mw import setHostPort, getHostPort
        import core.mw as mw
        original = mw.getPanelDir
        mw.getPanelDir = lambda: str(tmp_path)
        try:
            port_file = tmp_path / "data" / "port.pl"
            port_file.parent.mkdir(parents=True, exist_ok=True)
            setHostPort("7777")
            port = getHostPort()
            assert port == "7777"
        finally:
            mw.getPanelDir = original

    def test_delete_file(self, tmp_path):
        """测试删除文件"""
        from core.mw import deleteFile
        test_file = tmp_path / "to_delete.txt"
        test_file.write_text("delete me")
        assert test_file.exists()
        deleteFile(str(test_file))
        assert not test_file.exists()

    def test_delete_file_not_exists(self):
        """测试删除不存在的文件"""
        from core.mw import deleteFile
        # 不应抛出异常
        deleteFile('/nonexistent/file.txt')

    def test_build_soft_link(self, tmp_path):
        """测试创建软链接"""
        from core.mw import buildSoftLink
        src = tmp_path / "source.txt"
        src.write_text("source content")
        dst = tmp_path / "link.txt"

        result = buildSoftLink(str(src), str(dst))
        if sys.platform != 'win32':
            assert result is True
            assert dst.exists()

    def test_build_soft_link_force(self, tmp_path):
        """测试强制创建软链接"""
        from core.mw import buildSoftLink
        src = tmp_path / "source.txt"
        src.write_text("source content")
        dst = tmp_path / "link.txt"
        dst.write_text("old content")

        result = buildSoftLink(str(src), str(dst), force=True)
        if sys.platform != 'win32':
            assert result is True

    def test_get_language(self, tmp_path):
        """测试获取语言设置"""
        from core.mw import getLanguage
        import core.mw as mw
        original = mw.getPanelDir
        mw.getPanelDir = lambda: str(tmp_path)
        try:
            # 没有语言文件时应返回默认值
            lang = getLanguage()
            assert lang == "Simplified_Chinese"
        finally:
            mw.getPanelDir = original

    def test_get_language_custom(self, tmp_path):
        """测试获取自定义语言设置"""
        from core.mw import getLanguage
        import core.mw as mw
        original = mw.getPanelDir
        mw.getPanelDir = lambda: str(tmp_path)
        try:
            lang_file = tmp_path / "data" / "language.pl"
            lang_file.parent.mkdir(parents=True, exist_ok=True)
            lang_file.write_text("English")
            lang = getLanguage()
            assert lang == "English"
        finally:
            mw.getPanelDir = original

    def test_echo_functions(self, capsys):
        """测试打印函数"""
        from core.mw import echoStart, echoEnd, echoInfo

        echoStart("测试")
        captured = capsys.readouterr()
        assert "开始测试" in captured.out

        echoEnd("测试")
        captured = capsys.readouterr()
        assert "测试完成" in captured.out

        echoInfo("信息消息")
        captured = capsys.readouterr()
        assert "信息消息" in captured.out

    def test_file_name_check_edge_cases(self):
        """测试文件名检查边界情况"""
        from core.mw import fileNameCheck
        # 只包含特殊字符
        assert fileNameCheck(';') is False
        assert fileNameCheck('&') is False
        assert fileNameCheck('<') is False
        assert fileNameCheck('>') is False
        # 正常文件名
        assert fileNameCheck('a') is True
        assert fileNameCheck('1') is True
        assert fileNameCheck('.hidden') is True

    def test_md5_consistency(self):
        """测试 MD5 一致性"""
        from core.mw import md5
        for _ in range(10):
            assert md5('test') == md5('test')

    def test_write_speed_progress_calculation(self, tmp_path):
        """测试进度计算"""
        from core.mw import writeSpeed, getSpeed
        import core.mw as mw
        original = mw.getPanelDir
        mw.getPanelDir = lambda: str(tmp_path)
        try:
            (tmp_path / "data").mkdir(exist_ok=True)
            (tmp_path / "logs").mkdir(exist_ok=True)
            writeSpeed('task', 75, 100)
            speed = getSpeed()
            assert speed['progress'] == 75
        finally:
            mw.getPanelDir = original

    def test_decode_output_bytes(self):
        """测试 bytes 输出解码"""
        from core.mw import _decode_output
        result = _decode_output(b"hello world")
        assert result == "hello world"
        assert isinstance(result, str)

    def test_decode_output_string(self):
        """测试字符串输出直接返回"""
        from core.mw import _decode_output
        result = _decode_output("hello world")
        assert result == "hello world"

    def test_decode_output_empty_bytes(self):
        """测试空 bytes 解码"""
        from core.mw import _decode_output
        result = _decode_output(b"")
        assert result == ""

    def test_decode_output_none(self):
        """测试 None 输出"""
        from core.mw import _decode_output
        result = _decode_output(None)
        assert result is None

    def test_decode_output_utf8_chinese(self):
        """测试中文 bytes 解码"""
        from core.mw import _decode_output
        result = _decode_output("你好世界".encode("utf-8"))
        assert result == "你好世界"
