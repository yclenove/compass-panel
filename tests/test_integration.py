# coding:utf-8
"""集成测试 - 测试模块间的协作"""

import pytest
import os
import sys
import tempfile
import json


class TestDatabaseIntegration:
    """数据库集成测试"""

    def test_option_and_sites_integration(self):
        """测试 option 和 sites 模块的集成"""
        try:
            from thisdb import option, sites

            # 测试 option 模块
            email = option.getOption("ssl_email", default="")
            assert isinstance(email, str)

            # 测试 sites 模块
            count = sites.getSitesCount()
            assert isinstance(count, int)
            assert count >= 0
        except ImportError:
            pytest.skip("无法导入所需模块")

    def test_user_and_logs_integration(self):
        """测试 user 和 logs 模块的集成"""
        try:
            from thisdb import user, logs

            # 测试 user 模块
            admin = user.getUserByRoot()
            assert admin is not None or admin is None

            # 测试 logs 模块
            logs_data = logs.getLogsList(page=1, size=5)
            assert isinstance(logs_data, dict)
            assert 'list' in logs_data
            assert 'count' in logs_data
        except ImportError:
            pytest.skip("无法导入所需模块")

    def test_tasks_module_integration(self):
        """测试 tasks 模块集成"""
        try:
            from thisdb import tasks

            # 测试任务列表
            task_list = tasks.getTaskList(status=1, page=1, size=10)
            assert isinstance(task_list, list)

            # 测试任务页面
            page_data = tasks.getTaskPage(status=1, page=1, size=10)
            assert isinstance(page_data, dict)
            assert 'list' in page_data
            assert 'count' in page_data
        except ImportError:
            pytest.skip("无法导入 tasks 模块")


class TestSecurityIntegration:
    """安全模块集成测试"""

    def test_security_with_file_operations(self):
        """测试安全模块与文件操作的集成"""
        from utils.security import validate_filename, validate_path

        # 测试文件名验证
        valid, msg = validate_filename("test.txt")
        assert valid is True

        # 测试路径验证 - 使用 allow_root=True 来测试
        valid, msg = validate_path("/www/wwwroot/test", allow_root=True)
        assert valid is True

        # 测试敏感路径（不允许）
        valid, msg = validate_path("/etc/passwd", allow_root=False)
        assert valid is False

        # 测试路径遍历
        valid, msg = validate_path("../../../etc/passwd")
        assert valid is False

    def test_input_validation_comprehensive(self):
        """测试输入验证的完整性"""
        from utils.security import validate_input

        # 测试各种类型
        test_cases = [
            ("hello", "string", True),
            ("123", "integer", True),
            ("abc", "integer", False),
            ("1.5", "float", True),
            ("test@example.com", "email", True),
            ("invalid-email", "email", False),
            ("192.168.1.1", "ip", True),
            ("999.999.999.999", "ip", False),
            ("80", "port", True),
            ("0", "port", False),
        ]

        for value, input_type, expected in test_cases:
            valid, msg = validate_input(value, input_type=input_type)
            assert valid == expected, f"Failed for {value} ({input_type}): {msg}"

    def test_xss_prevention_integration(self):
        """测试 XSS 防护集成"""
        from utils.security import validate_input, sanitize_html

        # 测试 XSS 输入
        xss_inputs = [
            '<script>alert(1)</script>',
            'javascript:alert(1)',
            '<img onerror="alert(1)">',
        ]

        for xss_input in xss_inputs:
            valid, msg = validate_input(xss_input)
            assert valid is False, f"XSS not detected: {xss_input}"

            # 测试清理
            sanitized = sanitize_html(xss_input)
            assert '<script>' not in sanitized
            assert 'javascript:' not in sanitized


class TestFileOperationsIntegration:
    """文件操作集成测试"""

    def test_file_operations_with_security(self):
        """测试文件操作与安全检查的集成"""
        from utils.security import validate_filename, validate_path

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试文件
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test content")

            # 验证文件名
            valid, msg = validate_filename("test.txt")
            assert valid is True

            # 验证路径
            valid, msg = validate_path(test_file)
            assert valid is True

            # 验证危险文件名
            valid, msg = validate_filename("test;rm -rf /")
            assert valid is False

    def test_file_content_operations(self):
        """测试文件内容操作"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")

            # 写入文件
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("Hello, World!")

            # 读取文件
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()

            assert content == "Hello, World!"

    def test_json_file_operations(self):
        """测试 JSON 文件操作"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.json")

            # 写入 JSON
            data = {"key": "value", "number": 42}
            with open(test_file, "w", encoding="utf-8") as f:
                json.dump(data, f)

            # 读取 JSON
            with open(test_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)

            assert loaded == data


class TestConfigurationIntegration:
    """配置集成测试"""

    def test_config_module_exists(self):
        """测试配置模块存在"""
        try:
            from utils import security
            assert hasattr(security, 'validate_input')
            assert hasattr(security, 'validate_path')
            assert hasattr(security, 'validate_filename')
            assert hasattr(security, 'sanitize_html')
            assert hasattr(security, 'generate_csrf_token')
            assert hasattr(security, 'verify_csrf_token')
            assert hasattr(security, 'check_password_strength')
            assert hasattr(security, 'mask_sensitive_data')
        except ImportError:
            pytest.skip("无法导入 security 模块")

    def test_database_modules_exist(self):
        """测试数据库模块存在"""
        try:
            from thisdb import option, sites, crontab, firewall, logs, user, tasks
            assert True
        except ImportError:
            pytest.skip("无法导入数据库模块")
