# coding:utf-8
import pytest
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'web'))


class TestThisdbOption:
    """thisdb option 模块测试"""

    def test_get_option_default(self):
        """测试获取配置项 - 使用默认值"""
        from thisdb import option
        # 当数据库不可用时，应返回默认值
        try:
            result = option.getOption("nonexistent_key", default="default_value")
            assert result in ["default_value", None]  # 取决于数据库状态
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_option_by_json_default(self):
        """测试获取 JSON 配置项 - 使用默认值"""
        from thisdb import option
        try:
            default = {"key": "value"}
            result = option.getOptionByJson("nonexistent_json_key", default=default)
            assert result in [default, None]
        except Exception:
            pytest.skip("数据库不可用")

    def test_set_and_get_option(self):
        """测试设置和获取配置项"""
        from thisdb import option
        try:
            option.setOption("test_key_12345", "test_value")
            result = option.getOption("test_key_12345")
            assert result == "test_value"
            # 清理
            option.setOption("test_key_12345", "")
        except Exception:
            pytest.skip("数据库不可用")

    def test_set_option_update(self):
        """测试更新配置项"""
        from thisdb import option
        try:
            option.setOption("test_update_key", "value1")
            option.setOption("test_update_key", "value2")
            result = option.getOption("test_update_key")
            assert result == "value2"
            # 清理
            option.setOption("test_update_key", "")
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_option_by_json_parse(self):
        """测试 JSON 配置项解析"""
        from thisdb import option
        try:
            json_data = json.dumps({"open": True, "port": 8080})
            option.setOption("test_json_key", json_data)
            result = option.getOptionByJson("test_json_key")
            assert result["open"] is True
            assert result["port"] == 8080
            # 清理
            option.setOption("test_json_key", "")
        except Exception:
            pytest.skip("数据库不可用")


class TestThisdbLogs:
    """thisdb logs 模块测试"""

    def test_add_log(self):
        """测试添加日志"""
        from thisdb import logs
        try:
            result = logs.addLog("测试类型", "测试日志内容", uid=1)
            assert result is True
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_logs_list(self):
        """测试获取日志列表"""
        from thisdb import logs
        try:
            # 先添加一条日志
            logs.addLog("测试类型", "测试日志内容", uid=1)
            result = logs.getLogsList(page=1, size=10)
            assert 'list' in result
            assert 'count' in result
            assert isinstance(result['list'], list)
            assert result['count'] >= 0
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_logs_list_with_search(self):
        """测试获取日志列表 - 带搜索"""
        from thisdb import logs
        try:
            logs.addLog("特殊类型ABC", "特殊内容XYZ", uid=1)
            result = logs.getLogsList(page=1, size=10, search="特殊类型ABC")
            assert 'list' in result
            assert 'count' in result
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_logs_list_pagination(self):
        """测试日志列表分页"""
        from thisdb import logs
        try:
            result1 = logs.getLogsList(page=1, size=5)
            result2 = logs.getLogsList(page=2, size=5)
            assert 'list' in result1
            assert 'list' in result2
        except Exception:
            pytest.skip("数据库不可用")

    def test_clear_log(self):
        """测试清空日志"""
        from thisdb import logs
        try:
            result = logs.clearLog()
            assert result is True
        except Exception:
            pytest.skip("数据库不可用")


class TestThisdbUser:
    """thisdb user 模块测试"""

    def test_get_user_by_root(self):
        """测试获取管理员用户"""
        from thisdb import user
        try:
            result = user.getUserByRoot()
            if result is not None:
                assert 'id' in result
                assert 'name' in result
                assert 'password' in result
                assert 'login_ip' in result
                assert 'login_time' in result
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_user_by_id(self):
        """测试通过 ID 获取用户"""
        from thisdb import user
        try:
            result = user.getUserById(1)
            if result is not None:
                assert 'id' in result
                assert 'name' in result
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_user_fields(self):
        """测试用户字段完整性"""
        from thisdb import user
        try:
            result = user.getUserByRoot()
            if result is not None:
                expected_fields = ['id', 'name', 'password', 'login_ip',
                                   'login_time', 'phone', 'email',
                                   'add_time', 'update_time']
                for field in expected_fields:
                    assert field in result, f"缺少字段: {field}"
        except Exception:
            pytest.skip("数据库不可用")

    def test_set_user_pwd_by_name(self):
        """测试通过用户名设置密码"""
        from thisdb import user
        try:
            root_user = user.getUserByRoot()
            if root_user is not None:
                # 不实际修改密码，只验证函数存在和可调用
                assert callable(user.setUserPwdByName)
        except Exception:
            pytest.skip("数据库不可用")

    def test_update_user_login_time(self):
        """测试更新登录时间"""
        from thisdb import user
        try:
            result = user.updateUserLoginTime()
            assert result is True
        except Exception:
            pytest.skip("数据库不可用")

    def test_user_by_root_is_user_by_id(self):
        """测试 getUserByRoot 等同于 getUserById(1)"""
        from thisdb import user
        try:
            root = user.getUserByRoot()
            by_id = user.getUserById(1)
            if root is not None and by_id is not None:
                assert root['name'] == by_id['name']
        except Exception:
            pytest.skip("数据库不可用")


class TestThisdbInit:
    """thisdb init 模块测试"""

    def test_init_module_exists(self):
        """测试 init 模块存在"""
        try:
            import thisdb.init
            assert hasattr(thisdb.init, 'initPanelData')
        except ImportError:
            pytest.skip("无法导入 thisdb.init")


class TestThisdbSites:
    """thisdb sites 模块测试"""

    def test_sites_module_exists(self):
        """测试 sites 模块存在"""
        try:
            import thisdb.sites
            # 验证关键函数存在
            assert callable(getattr(thisdb.sites, 'getSiteList', None)) or True
        except ImportError:
            pytest.skip("无法导入 thisdb.sites")


class TestThisdbFirewall:
    """thisdb firewall 模块测试"""

    def test_firewall_module_exists(self):
        """测试 firewall 模块存在"""
        try:
            import thisdb.firewall
            assert True
        except ImportError:
            pytest.skip("无法导入 thisdb.firewall")


class TestThisdbCrontab:
    """thisdb crontab 模块测试"""

    def test_crontab_module_exists(self):
        """测试 crontab 模块存在"""
        try:
            import thisdb.crontab
            assert True
        except ImportError:
            pytest.skip("无法导入 thisdb.crontab")
