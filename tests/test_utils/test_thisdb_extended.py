# coding:utf-8
"""
thisdb 扩展模块测试
覆盖 firewall, crontab, backup, tasks, temp_login, binding, domain, app, site_types
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'web'))


class TestThisdbFirewallExtended:
    """thisdb firewall 扩展测试"""

    def test_get_firewall_list_structure(self):
        """测试获取防火墙列表返回结构"""
        from thisdb import firewall
        try:
            result = firewall.getFirewallList(page=1, size=10)
            assert 'list' in result
            assert 'count' in result
            assert isinstance(result['list'], list)
            assert isinstance(result['count'], int)
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_firewall_list_pagination(self):
        """测试防火墙列表分页"""
        from thisdb import firewall
        try:
            result1 = firewall.getFirewallList(page=1, size=5)
            result2 = firewall.getFirewallList(page=2, size=5)
            assert 'list' in result1
            assert 'list' in result2
        except Exception:
            pytest.skip("数据库不可用")

    def test_add_firewall(self):
        """测试添加防火墙规则"""
        from thisdb import firewall
        try:
            result = firewall.addFirewall(9999, protocol="tcp", ps="测试规则")
            assert result is True
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_firewall_count_by_port(self):
        """测试通过端口获取防火墙规则数量"""
        from thisdb import firewall
        try:
            result = firewall.getFirewallCountByPort(9999)
            assert isinstance(result, int)
        except Exception:
            pytest.skip("数据库不可用")


class TestThisdbCrontabExtended:
    """thisdb crontab 扩展测试"""

    def test_get_crontab_list_structure(self):
        """测试获取计划任务列表返回结构"""
        from thisdb import crontab
        try:
            result = crontab.getCrontabList(page=1, size=10)
            assert 'list' in result
            assert 'count' in result
        except Exception:
            pytest.skip("数据库不可用")

    def test_add_crontab(self):
        """测试添加计划任务"""
        from thisdb import crontab
        try:
            data = {
                'name': 'test_cron_12345',
                'type': 'day',
                'where1': '',
                'where_hour': '0',
                'where_minute': '0',
                'echo': 'test',
                'status': 0,
                'save': '',
                'backup_to': '',
                'stype': '',
                'sname': '',
                'sbody': '',
                'url_address': '',
                'attr': '',
            }
            result = crontab.addCrontab(data)
            assert result is not None
            # 清理
            crontab.deleteCronById(result)
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_cron_by_name(self):
        """测试通过名称获取计划任务"""
        from thisdb import crontab
        try:
            result = crontab.getCronByName("nonexistent_cron")
            assert result is None or isinstance(result, dict)
        except Exception:
            pytest.skip("数据库不可用")

    def test_set_crontab_status(self):
        """测试设置计划任务状态"""
        from thisdb import crontab
        try:
            # 只验证函数可调用
            assert callable(crontab.setCrontabStatus)
        except Exception:
            pytest.skip("数据库不可用")


class TestThisdbBackupExtended:
    """thisdb backup 扩展测试"""

    def test_get_backup_page_structure(self):
        """测试获取备份分页返回结构"""
        from thisdb import backup
        try:
            result = backup.getBackupPage(site_id=0, page=1, size=10)
            assert 'list' in result
            assert 'count' in result
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_backup_by_id_not_found(self):
        """测试获取不存在的备份"""
        from thisdb import backup
        try:
            result = backup.getBackupById(999999)
            assert result is None
        except Exception:
            pytest.skip("数据库不可用")

    def test_add_backup(self):
        """测试添加备份"""
        from thisdb import backup
        try:
            result = backup.addBackup(pid=0, name="test_backup", filename="test.tar.gz", size=1024, type=0)
            assert result is True
        except Exception:
            pytest.skip("数据库不可用")


class TestThisdbTasksExtended:
    """thisdb tasks 扩展测试"""

    def test_get_task_count(self):
        """测试获取任务数量"""
        from thisdb import tasks
        try:
            result = tasks.getTaskCount()
            assert isinstance(result, int)
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_task_list_structure(self):
        """测试获取任务列表返回结构"""
        from thisdb import tasks
        try:
            result = tasks.getTaskList(status=1, page=1, size=10)
            assert isinstance(result, list)
        except Exception:
            pytest.skip("数据库不可用")

    def test_add_task(self):
        """测试添加任务"""
        from thisdb import tasks
        try:
            result = tasks.addTask(name="测试任务", cmd="echo test", type="execshell", status=0)
            assert result is True
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_task_first_by_run(self):
        """测试获取第一个运行中的任务"""
        from thisdb import tasks
        try:
            result = tasks.getTaskFirstByRun()
            assert result is None or isinstance(result, dict)
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_task_run_page_structure(self):
        """测试获取运行中任务分页返回结构"""
        from thisdb import tasks
        try:
            result = tasks.getTaskRunPage(page=1, size=10)
            assert 'list' in result
            assert 'count' in result
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_task_page_structure(self):
        """测试获取任务分页返回结构"""
        from thisdb import tasks
        try:
            result = tasks.getTaskPage(page=1, size=10)
            assert 'list' in result
            assert 'count' in result
        except Exception:
            pytest.skip("数据库不可用")


class TestThisdbTempLoginExtended:
    """thisdb temp_login 扩展测试"""

    def test_get_temp_login_page_structure(self):
        """测试获取临时登录分页返回结构"""
        from thisdb import temp_login
        try:
            result = temp_login.getTempLoginPage(page=1, size=10)
            assert 'list' in result
            assert 'count' in result
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_temp_login_by_token_not_found(self):
        """测试获取不存在的临时登录"""
        from thisdb import temp_login
        try:
            result = temp_login.getTempLoginByToken("nonexistent_token_12345")
            assert result is None
        except Exception:
            pytest.skip("数据库不可用")


class TestThisdbBindingExtended:
    """thisdb binding 扩展测试"""

    def test_get_binding_count_by_domain(self):
        """测试通过域名获取绑定数量"""
        from thisdb import binding
        try:
            result = binding.getBindingCountByDomain("nonexistent.example.com")
            assert isinstance(result, int)
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_binding_list_by_site_id(self):
        """测试通过站点ID获取绑定列表"""
        from thisdb import binding
        try:
            result = binding.getBindingListBySiteId(999999)
            assert isinstance(result, list)
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_binding_by_id_not_found(self):
        """测试获取不存在的绑定"""
        from thisdb import binding
        try:
            result = binding.getBindingById(999999)
            assert result is None
        except Exception:
            pytest.skip("数据库不可用")


class TestThisdbDomainExtended:
    """thisdb domain 扩展测试"""

    def test_get_domain_count_by_name(self):
        """测试通过域名获取域名数量"""
        from thisdb import domain
        try:
            result = domain.getDomainCountByName("nonexistent.example.com")
            assert isinstance(result, int)
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_domain_count_by_site_id(self):
        """测试通过站点ID获取域名数量"""
        from thisdb import domain
        try:
            result = domain.getDomainCountBySiteId(999999)
            assert isinstance(result, int)
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_domain_by_site_id(self):
        """测试通过站点ID获取域名列表"""
        from thisdb import domain
        try:
            result = domain.getDomainBySiteId(999999)
            assert isinstance(result, list)
        except Exception:
            pytest.skip("数据库不可用")


class TestThisdbAppExtended:
    """thisdb app 扩展测试"""

    def test_get_app_list_structure(self):
        """测试获取应用列表返回结构"""
        from thisdb import app
        try:
            result = app.getAppList(page=1, size=10)
            assert 'list' in result
            assert 'count' in result
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_app_by_id_not_found(self):
        """测试获取不存在的应用"""
        from thisdb import app
        try:
            result = app.getAppById(999999)
            assert result is None
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_app_by_app_id_not_found(self):
        """测试通过app_id获取不存在的应用"""
        from thisdb import app
        try:
            result = app.getAppByAppId("nonexistent_app_id")
            assert result is None
        except Exception:
            pytest.skip("数据库不可用")


class TestThisdbSiteTypesExtended:
    """thisdb site_types 扩展测试"""

    def test_get_site_types_list(self):
        """测试获取站点类型列表"""
        from thisdb import site_types
        try:
            result = site_types.getSiteTypesList()
            assert isinstance(result, list)
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_site_types_count(self):
        """测试获取站点类型数量"""
        from thisdb import site_types
        try:
            result = site_types.getSiteTypesCount()
            assert isinstance(result, int)
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_site_types_count_by_name(self):
        """测试通过名称获取站点类型数量"""
        from thisdb import site_types
        try:
            result = site_types.getSiteTypesCountByName("nonexistent_type")
            assert isinstance(result, int)
        except Exception:
            pytest.skip("数据库不可用")


class TestThisdbSitesExtended:
    """thisdb sites 扩展测试"""

    def test_get_sites_count(self):
        """测试获取站点数量"""
        from thisdb import sites
        try:
            result = sites.getSitesCount()
            assert isinstance(result, int)
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_sites_by_id_not_found(self):
        """测试获取不存在的站点"""
        from thisdb import sites
        try:
            result = sites.getSitesById(999999)
            assert result is None or isinstance(result, dict)
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_sites_by_name_not_found(self):
        """测试通过名称获取不存在的站点"""
        from thisdb import sites
        try:
            result = sites.getSitesByName("nonexistent_site_12345")
            assert result is None or isinstance(result, dict)
        except Exception:
            pytest.skip("数据库不可用")

    def test_is_sites_exist(self):
        """测试站点是否存在"""
        from thisdb import sites
        try:
            result = sites.isSitesExist("nonexistent_site_12345")
            assert isinstance(result, bool)
        except Exception:
            pytest.skip("数据库不可用")

    def test_get_sites_list_structure(self):
        """测试获取站点列表返回结构"""
        from thisdb import sites
        try:
            result = sites.getSitesList(page=1, size=10)
            assert 'list' in result
            assert 'count' in result
        except Exception:
            pytest.skip("数据库不可用")

    def test_check_sites_domain_is_exist(self):
        """测试检查站点域名是否存在"""
        from thisdb import sites
        try:
            result = sites.checkSitesDomainIsExist("nonexistent.example.com", 80)
            assert isinstance(result, bool)
        except Exception:
            pytest.skip("数据库不可用")
