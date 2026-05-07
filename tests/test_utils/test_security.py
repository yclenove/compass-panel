# coding:utf-8
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'web'))


class TestSecurityUtils:
    """安全工具函数测试"""

    def test_validate_filename_valid(self):
        """测试文件名验证 - 合法文件名"""
        from utils.security import validate_filename
        valid, msg = validate_filename('test.txt')
        assert valid is True
        assert msg == ""

    def test_validate_filename_empty(self):
        """测试文件名验证 - 空文件名"""
        from utils.security import validate_filename
        valid, msg = validate_filename('')
        assert valid is False
        assert '不能为空' in msg

    def test_validate_filename_too_long(self):
        """测试文件名验证 - 过长文件名"""
        from utils.security import validate_filename
        valid, msg = validate_filename('a' * 256)
        assert valid is False
        assert '长度' in msg

    def test_validate_filename_dangerous_chars(self):
        """测试文件名验证 - 危险字符"""
        from utils.security import validate_filename
        for char in [';', '&', '|', '*', '<', '>', '`', '$']:
            valid, msg = validate_filename(f'test{char}file')
            assert valid is False
            assert '字符' in msg

    def test_validate_filename_path_traversal(self):
        """测试文件名验证 - 路径遍历"""
        from utils.security import validate_filename
        valid, msg = validate_filename('../../../etc/passwd')
        assert valid is False

    def test_validate_filename_starts_with_slash(self):
        """测试文件名验证 - 以斜杠开头"""
        from utils.security import validate_filename
        valid, msg = validate_filename('/etc/passwd')
        assert valid is False

    def test_validate_path_valid(self):
        """测试路径验证 - 合法路径"""
        from utils.security import validate_path
        valid, msg = validate_path('/www/wwwroot/site')
        assert valid is True

    def test_validate_path_empty(self):
        """测试路径验证 - 空路径"""
        from utils.security import validate_path
        valid, msg = validate_path('')
        assert valid is False
        assert '不能为空' in msg

    def test_validate_path_traversal(self):
        """测试路径验证 - 路径遍历"""
        from utils.security import validate_path
        # 使用 .. 直接在路径中
        valid, msg = validate_path('/www/../etc/passwd')
        assert valid is False
        assert '遍历' in msg

    def test_validate_path_sensitive_dir(self):
        """测试路径验证 - 敏感目录"""
        from utils.security import validate_path
        sensitive_paths = ['/root', '/etc', '/bin', '/sbin', '/boot']
        for path in sensitive_paths:
            valid, msg = validate_path(path)
            assert valid is False
            assert '敏感目录' in msg

    def test_validate_input_string(self):
        """测试输入验证 - 字符串"""
        from utils.security import validate_input
        valid, msg = validate_input('hello', 'string')
        assert valid is True

    def test_validate_input_empty(self):
        """测试输入验证 - 空值"""
        from utils.security import validate_input
        valid, msg = validate_input('', 'string')
        assert valid is False

    def test_validate_input_empty_allowed(self):
        """测试输入验证 - 允许空值"""
        from utils.security import validate_input
        valid, msg = validate_input('', 'string', allow_empty=True)
        assert valid is True

    def test_validate_input_too_long(self):
        """测试输入验证 - 过长"""
        from utils.security import validate_input
        valid, msg = validate_input('a' * 1001, 'string')
        assert valid is False
        assert '长度' in msg

    def test_validate_input_sql_injection(self):
        """测试输入验证 - SQL注入"""
        from utils.security import validate_input
        sql_inputs = [
            "1; DROP TABLE users",
            "SELECT * FROM users",
            "UNION SELECT * FROM passwords",
            "INSERT INTO users VALUES(1)",
        ]
        for sql in sql_inputs:
            valid, msg = validate_input(sql)
            assert valid is False
            assert '非法字符' in msg

    def test_validate_input_xss(self):
        """测试输入验证 - XSS"""
        from utils.security import validate_input
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert(1)",
            "<iframe src='evil'>",
            "<img onerror='alert(1)'>",
        ]
        for xss in xss_inputs:
            valid, msg = validate_input(xss)
            assert valid is False
            assert '非法字符' in msg

    def test_validate_input_integer(self):
        """测试输入验证 - 整数"""
        from utils.security import validate_input
        valid, msg = validate_input('123', 'integer')
        assert valid is True

    def test_validate_input_integer_invalid(self):
        """测试输入验证 - 非整数"""
        from utils.security import validate_input
        valid, msg = validate_input('abc', 'integer')
        assert valid is False
        assert '整数' in msg

    def test_validate_input_email_valid(self):
        """测试输入验证 - 合法邮箱"""
        from utils.security import validate_input
        valid, msg = validate_input('test@example.com', 'email')
        assert valid is True

    def test_validate_input_email_invalid(self):
        """测试输入验证 - 非法邮箱"""
        from utils.security import validate_input
        valid, msg = validate_input('not-an-email', 'email')
        assert valid is False
        assert '邮箱' in msg

    def test_validate_input_ip_valid(self):
        """测试输入验证 - 合法IP"""
        from utils.security import validate_input
        valid, msg = validate_input('192.168.1.1', 'ip')
        assert valid is True

    def test_validate_input_ip_invalid(self):
        """测试输入验证 - 非法IP"""
        from utils.security import validate_input
        valid, msg = validate_input('999.999.999.999', 'ip')
        assert valid is False
        assert 'IP' in msg

    def test_validate_input_port_valid(self):
        """测试输入验证 - 合法端口"""
        from utils.security import validate_input
        valid, msg = validate_input('8080', 'port')
        assert valid is True

    def test_validate_input_port_invalid(self):
        """测试输入验证 - 非法端口"""
        from utils.security import validate_input
        valid, msg = validate_input('99999', 'port')
        assert valid is False
        assert '端口' in msg

    def test_sanitize_html_safe(self):
        """测试HTML清理 - 安全内容"""
        from utils.security import sanitize_html
        result = sanitize_html('<p>Hello World</p>')
        assert '<p>' in result
        assert 'Hello World' in result

    def test_sanitize_html_script(self):
        """测试HTML清理 - script标签"""
        from utils.security import sanitize_html
        result = sanitize_html('<script>alert("xss")</script><p>safe</p>')
        assert '<script>' not in result
        assert 'safe' in result

    def test_sanitize_html_event(self):
        """测试HTML清理 - 事件属性"""
        from utils.security import sanitize_html
        result = sanitize_html('<img src="x" onerror="alert(1)">')
        assert 'onerror' not in result

    def test_sanitize_html_empty(self):
        """测试HTML清理 - 空值"""
        from utils.security import sanitize_html
        assert sanitize_html('') == ''
        assert sanitize_html(None) == ''

    def test_generate_csrf_token(self):
        """测试CSRF令牌生成"""
        from utils.security import generate_csrf_token
        token1 = generate_csrf_token()
        token2 = generate_csrf_token()
        assert len(token1) == 64
        assert token1 != token2

    def test_verify_csrf_token_valid(self):
        """测试CSRF令牌验证 - 有效"""
        from utils.security import verify_csrf_token
        token = 'a' * 64
        assert verify_csrf_token(token, token) is True

    def test_verify_csrf_token_invalid(self):
        """测试CSRF令牌验证 - 无效"""
        from utils.security import verify_csrf_token
        assert verify_csrf_token('token1', 'token2') is False

    def test_verify_csrf_token_empty(self):
        """测试CSRF令牌验证 - 空值"""
        from utils.security import verify_csrf_token
        assert verify_csrf_token('', 'token') is False
        assert verify_csrf_token('token', '') is False
        assert verify_csrf_token(None, 'token') is False

    def test_check_password_strength_valid(self):
        """测试密码强度检查 - 有效密码"""
        from utils.security import check_password_strength
        valid, msg = check_password_strength('TestPass123')
        assert valid is True

    def test_check_password_strength_too_short(self):
        """测试密码强度检查 - 太短"""
        from utils.security import check_password_strength
        valid, msg = check_password_strength('Ab1')
        assert valid is False
        assert '8位' in msg

    def test_check_password_strength_no_upper(self):
        """测试密码强度检查 - 无大写字母"""
        from utils.security import check_password_strength
        valid, msg = check_password_strength('testpass123')
        assert valid is False
        assert '大小写' in msg

    def test_check_password_strength_no_lower(self):
        """测试密码强度检查 - 无小写字母"""
        from utils.security import check_password_strength
        valid, msg = check_password_strength('TESTPASS123')
        assert valid is False
        assert '大小写' in msg

    def test_check_password_strength_no_digit(self):
        """测试密码强度检查 - 无数字"""
        from utils.security import check_password_strength
        valid, msg = check_password_strength('TestPassword')
        assert valid is False
        assert '大小写' in msg

    def test_mask_sensitive_data(self):
        """测试敏感数据脱敏"""
        from utils.security import mask_sensitive_data
        data = {
            'username': 'admin',
            'password': 'supersecretpassword',
            'token': 'abc123def456',
        }
        masked = mask_sensitive_data(data)
        assert masked['username'] == 'admin'  # 不脱敏
        assert masked['password'] != 'supersecretpassword'  # 已脱敏
        assert masked['token'] != 'abc123def456'  # 已脱敏
        assert '*' in masked['password']
        assert '*' in masked['token']

    def test_mask_sensitive_data_custom_fields(self):
        """测试敏感数据脱敏 - 自定义字段"""
        from utils.security import mask_sensitive_data
        data = {
            'name': 'test',
            'api_key': 'my_secret_key_12345',
        }
        masked = mask_sensitive_data(data, fields=['api_key'])
        assert masked['name'] == 'test'
        assert '*' in masked['api_key']

    def test_mask_sensitive_data_short_value(self):
        """测试敏感数据脱敏 - 短值"""
        from utils.security import mask_sensitive_data
        data = {'password': 'ab'}
        masked = mask_sensitive_data(data)
        assert masked['password'] == '****'

    def test_mask_sensitive_data_non_dict(self):
        """测试敏感数据脱敏 - 非字典"""
        from utils.security import mask_sensitive_data
        assert mask_sensitive_data('string') == 'string'
        assert mask_sensitive_data(None) is None
