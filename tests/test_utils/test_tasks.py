# coding:utf-8
"""任务模块测试"""

import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'web'))


class TestTasksModule:
    """任务模块测试"""

    def test_add_task_by_download_no_cmd(self):
        """测试添加下载任务 - 无命令"""
        from thisdb.tasks import addTaskByDownload
        result = addTaskByDownload(cmd=None)
        assert result is False

    def test_add_task_no_cmd(self):
        """测试添加任务 - 无命令"""
        from thisdb.tasks import addTask
        result = addTask(cmd=None)
        assert result is False

    def test_module_imports(self):
        """测试模块导入"""
        from thisdb import tasks
        assert hasattr(tasks, 'addTask')
        assert hasattr(tasks, 'addTaskByDownload')
        assert hasattr(tasks, 'getTaskList')
        assert hasattr(tasks, 'getTaskPage')
        assert hasattr(tasks, 'getTaskFirstByRun')
        assert hasattr(tasks, 'getTaskRunList')
        assert hasattr(tasks, 'getTaskRunAll')
        assert hasattr(tasks, 'getTaskRunPage')
        assert hasattr(tasks, 'setTaskStatus')
        assert hasattr(tasks, 'setTaskData')
        assert hasattr(tasks, 'getTaskCount')
        assert hasattr(tasks, 'getTaskUnexecutedCount')
