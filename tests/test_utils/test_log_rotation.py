# coding:utf-8
"""日志轮转模块测试"""

import pytest
import os
import sys
import tempfile
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'web'))


class TestEnhancedRotatingFileHandler:
    """增强日志轮转处理器测试"""

    def test_handler_creation(self, tmp_path):
        """测试处理器创建"""
        from utils.enhanced_log_rotation import EnhancedRotatingFileHandler
        log_file = str(tmp_path / "test.log")
        handler = EnhancedRotatingFileHandler(
            filename=log_file,
            max_bytes=1,
            interval=60,
            backup_count=5,
            encoding="utf-8",
            when="M",
        )
        assert handler is not None
        assert isinstance(handler, logging.Handler)
        handler.close()

    def test_handler_should_rollover_size(self, tmp_path):
        """测试大小触发轮转"""
        from utils.enhanced_log_rotation import EnhancedRotatingFileHandler
        log_file = str(tmp_path / "test.log")
        handler = EnhancedRotatingFileHandler(
            filename=log_file,
            max_bytes=1,
            interval=60,
            backup_count=5,
            encoding="utf-8",
        )
        # 写入超过 1MB 的数据
        with open(log_file, "w") as f:
            f.write("x" * (1024 * 1024 + 1))

        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="",
            lineno=0, msg="test", args=(), exc_info=None,
        )
        # 应该触发轮转
        assert handler.shouldRollover(record) == 1
        handler.close()

    def test_handler_should_not_rollover(self, tmp_path):
        """测试不应触发轮转"""
        from utils.enhanced_log_rotation import EnhancedRotatingFileHandler
        log_file = str(tmp_path / "test.log")
        handler = EnhancedRotatingFileHandler(
            filename=log_file,
            max_bytes=10,
            interval=60,
            backup_count=5,
            encoding="utf-8",
        )
        # 写入少量数据
        with open(log_file, "w") as f:
            f.write("small")

        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="",
            lineno=0, msg="test", args=(), exc_info=None,
        )
        # 不应该触发轮转
        assert handler.shouldRollover(record) == 0
        handler.close()

    def test_handler_in_logger(self, tmp_path):
        """测试处理器在 logger 中使用"""
        from utils.enhanced_log_rotation import EnhancedRotatingFileHandler
        log_file = str(tmp_path / "test.log")
        handler = EnhancedRotatingFileHandler(
            filename=log_file,
            max_bytes=10,
            interval=60,
            backup_count=5,
            encoding="utf-8",
        )
        logger = logging.getLogger("test_logger")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        logger.info("test message")
        assert os.path.exists(log_file)

        logger.removeHandler(handler)
        handler.close()
