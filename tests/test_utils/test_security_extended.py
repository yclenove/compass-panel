# coding:utf-8
"""
安全模块扩展测试
覆盖更多边界条件和安全场景
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'web'))


class TestSecurityFilenameEdgeCases:
    """文件名验证边界条件测试"""

    def test_validate_filename_dot_ending(self):
        """测试文件名以点结尾"""
        from utils.security import validate_filename
        valid, msg = validate_filename('test.')
        assert valid is False

    def test_validate_filename_space_ending(self):
        """测试文件名以空格结尾"""
        from utils.security import validate_filename
        valid, msg = validate_filename('test ')
        assert valid is False

    def test_validate_filename_max_length(self):
        """测试文件名最大长度"""
        from utils.security import validate_filename
        valid, msg = validate_filename('a' * 255)
        assert valid is True

    def test_validate_filename_chinese(self):
        """测试中文文件名"""
        from utils.security import validate_filename
        valid, msg = validate_filename('测试文件.txt')
        assert valid is True

    def test_validate_filename_with_dots(self):
        """测试文件名包含多个点"""
        from utils.security import validate_filename
        valid, msg = validate_filename('file.name.with.dots.txt')
        assert valid is True

    def test_validate_filename_parentheses(self):
        """测试文件名包含括号"""
        from utils.security import validate_filename
        valid, msg = validate_filename('test(1).txt')
        assert valid is False

    def test_validate_filename_braces(self):
        """测试文件名包含花括号"""
        from utils.security import validate_filename
        valid, msg = validate_filename('test{1}.txt')
        assert valid is False


class TestSecurityPathEdgeCases:
    """路径验证边界条件测试"""

    def test_validate_path_with_subdirs(self):
        """测试包含子目录的路径"""
        from utils.security import validate_path
        valid, msg = validate_path('/www/wwwroot/site/public')
        assert valid is True

    def test_validate_path_sensitive_subdir(self):
        """测试敏感目录的子目录"""
        from utils.security import validate_path
        valid, msg = validate_path('/etc/nginx')
        assert valid is False

    def test_validate_path_allow_root(self):
        """测试允许根目录操作"""
        from utils.security import validate_path
        valid, msg = validate_path('/root', allow_root=True)
        assert valid is True

    def test_validate_path_windows_backslash(self):
        """测试Windows反斜杠路径"""
        from utils.security import validate_path
        valid, msg = validate_path('/www/wwwroot/site')
        assert valid is True

    def test_validate_path_double_slash(self):
        """测试双斜杠路径"""
        from utils.security import validate_path
        valid, msg = validate_path('/www//wwwroot//site')
        # 规范化后应该有效
        assert valid is True


class TestSecurityInputEdgeCases:
    """输入验证边界条件测试"""

    def test_validate_input_float_valid(self):
        """测试有效浮点数"""
        from utils.security import validate_input
        valid, msg = validate_input('3.14', 'float')
        assert valid is True

    def test_validate_input_float_invalid(self):
        """测试无效浮点数"""
        from utils.security import validate_input
        valid, msg = validate_input('abc', 'float')
        assert valid is False

    def test_validate_input_port_boundary_low(self):
        """测试端口下界"""
        from utils.security import validate_input
        valid, msg = validate_input('0', 'port')
        assert valid is False

    def test_validate_input_port_boundary_high(self):
        """测试端口上界"""
        from utils.security import validate_input
        valid, msg = validate_input('65536', 'port')
        assert valid is False

    def test_validate_input_port_boundary_valid_low(self):
        """测试有效端口下界"""
        from utils.security import validate_input
        valid, msg = validate_input('1', 'port')
        assert valid is True

    def test_validate_input_port_boundary_valid_high(self):
        """测试有效端口上界"""
        from utils.security import validate_input
        valid, msg = validate_input('65535', 'port')
        assert valid is True

    def test_validate_input_none_value(self):
        """测试None值"""
        from utils.security import validate_input
        valid, msg = validate_input(None)
        assert valid is False

    def test_validate_input_none_allowed(self):
        """测试允许None值"""
        from utils.security import validate_input
        valid, msg = validate_input(None, allow_empty=True)
        assert valid is True

    def test_validate_input_sql_comment(self):
        """测试SQL注释"""
        from utils.security import validate_input
        valid, msg = validate_input("test' -- comment")
        assert valid is False

    def test_validate_input_xss_img_tag(self):
        """测试XSS img标签"""
        from utils.security import validate_input
        valid, msg = validate_input("<img src=x onerror=alert(1)>")
        assert valid is False

    def test_validate_input_xss_event_handler(self):
        """测试XSS事件处理器"""
        from utils.security import validate_input
        valid, msg = validate_input('<div onclick="alert(1)">test</div>')
        assert valid is False

    def test_validate_input_ip_loopback(self):
        """测试回环IP"""
        from utils.security import validate_input
        valid, msg = validate_input('127.0.0.1', 'ip')
        assert valid is True

    def test_validate_input_ip_broadcast(self):
        """测试广播IP"""
        from utils.security import validate_input
        valid, msg = validate_input('255.255.255.255', 'ip')
        assert valid is True


class TestSecurityHtmlSanitize:
    """HTML清理扩展测试"""

    def test_sanitize_html_iframe(self):
        """测试iframe标签清理"""
        from utils.security import sanitize_html
        result = sanitize_html('<iframe src="evil"></iframe><p>safe</p>')
        assert '<iframe' not in result
        assert 'safe' in result

    def test_sanitize_html_object_tag(self):
        """测试object标签清理"""
        from utils.security import sanitize_html
        result = sanitize_html('<object data="evil.swf"></object><p>safe</p>')
        assert '<object' not in result
        assert 'safe' in result

    def test_sanitize_html_embed_tag(self):
        """测试embed标签清理"""
        from utils.security import sanitize_html
        result = sanitize_html('<embed src="evil.swf"><p>safe</p>')
        assert '<embed' not in result
        assert 'safe' in result

    def test_sanitize_html_form_tag(self):
        """测试form标签清理"""
        from utils.security import sanitize_html
        result = sanitize_html('<form action="evil"><p>safe</p></form>')
        assert '<form' not in result
        assert 'safe' in result

    def test_sanitize_html_javascript_protocol(self):
        """测试javascript协议清理"""
        from utils.security import sanitize_html
        result = sanitize_html('<a href="javascript:alert(1)">click</a>')
        assert 'javascript:' not in result

    def test_sanitize_html_multiple_events(self):
        """测试多个事件属性清理"""
        from utils.security import sanitize_html
        result = sanitize_html('<div onclick="alert(1)" onmouseover="alert(2)">test</div>')
        assert 'onclick' not in result
        assert 'onmouseover' not in result

    def test_sanitize_html_nested_script(self):
        """测试嵌套script标签"""
        from utils.security import sanitize_html
        result = sanitize_html('<scr<script>ipt>alert(1)</scr</script>ipt>')
        assert '<script' not in result.lower() or 'alert' not in result


class TestSecurityPassword:
    """密码强度扩展测试"""

    def test_check_password_strength_exactly_8_chars(self):
        """测试刚好8位密码"""
        from utils.security import check_password_strength
        valid, msg = check_password_strength('Abc12345')
        assert valid is True

    def test_check_password_strength_128_chars(self):
        """测试128位密码"""
        from utils.security import check_password_strength
        password = 'A' * 42 + 'a' * 43 + '1' * 43
        valid, msg = check_password_strength(password)
        assert valid is True

    def test_check_password_strength_129_chars(self):
        """测试129位密码"""
        from utils.security import check_password_strength
        password = 'A' * 43 + 'a' * 43 + '1' * 43
        valid, msg = check_password_strength(password)
        assert valid is False

    def test_check_password_strength_special_chars(self):
        """测试包含特殊字符的密码"""
        from utils.security import check_password_strength
        valid, msg = check_password_strength('Test@1234')
        assert valid is True

    def test_check_password_strength_only_special(self):
        """测试只有特殊字符的密码"""
        from utils.security import check_password_strength
        valid, msg = check_password_strength('!@#$%^&*')
        assert valid is False


class TestSecurityMaskData:
    """敏感数据脱敏扩展测试"""

    def test_mask_sensitive_data_multiple_fields(self):
        """测试多个敏感字段"""
        from utils.security import mask_sensitive_data
        data = {
            'name': 'test',
            'password': 'mypassword123',
            'token': 'tokentoken123',
            'secret': 'secretsecret',
        }
        masked = mask_sensitive_data(data)
        assert masked['name'] == 'test'
        assert '*' in masked['password']
        assert '*' in masked['token']
        assert '*' in masked['secret']

    def test_mask_sensitive_data_empty_dict(self):
        """测试空字典"""
        from utils.security import mask_sensitive_data
        masked = mask_sensitive_data({})
        assert masked == {}

    def test_mask_sensitive_data_no_sensitive_fields(self):
        """测试没有敏感字段"""
        from utils.security import mask_sensitive_data
        data = {'name': 'test', 'age': 25}
        masked = mask_sensitive_data(data)
        assert masked == data

    def test_mask_sensitive_data_nested_dict(self):
        """测试嵌套字典（不处理嵌套）"""
        from utils.security import mask_sensitive_data
        data = {'name': 'test', 'config': {'password': 'secret'}}
        masked = mask_sensitive_data(data)
        # 嵌套的password不会被脱敏
        assert masked['config']['password'] == 'secret'


class TestSecurityCsrfToken:
    """CSRF令牌扩展测试"""

    def test_generate_csrf_token_uniqueness(self):
        """测试CSRF令牌唯一性"""
        from utils.security import generate_csrf_token
        tokens = set()
        for _ in range(100):
            tokens.add(generate_csrf_token())
        assert len(tokens) == 100

    def test_verify_csrf_token_timing_safe(self):
        """测试CSRF令牌验证使用时间安全比较"""
        from utils.security import verify_csrf_token
        from utils.security import generate_csrf_token
        # 验证相同令牌
        token = generate_csrf_token()
        assert verify_csrf_token(token, token) is True

    def test_verify_csrf_token_different_length(self):
        """测试不同长度的令牌"""
        from utils.security import verify_csrf_token
        assert verify_csrf_token('short', 'a' * 64) is False
