"""ORM 模块测试"""

import pytest
from unittest.mock import patch, MagicMock


class TestORMBuildConnKwargs:
    """测试 ORM._build_conn_kwargs 方法"""

    def test_basic_kwargs(self):
        """测试基本连接参数构建"""
        from core.orm import ORM

        o = ORM()
        o.setHost("localhost")
        o.setPort(3306)
        o.setUser("root")
        o.setPwd("password")
        o.setDbName("testdb")
        o.setTimeout(5)

        kwargs = o._build_conn_kwargs(use_socket=False)
        assert kwargs["host"] == "localhost"
        assert kwargs["port"] == 3306
        assert kwargs["user"] == "root"
        assert kwargs["passwd"] == "password"
        assert kwargs["database"] == "testdb"
        assert kwargs["connect_timeout"] == 5
        assert "unix_socket" not in kwargs
        assert kwargs["cursorclass"] is not None

    def test_socket_kwargs(self):
        """测试 socket 连接参数构建"""
        from core.orm import ORM

        o = ORM()
        kwargs = o._build_conn_kwargs(use_socket=True)
        assert "unix_socket" in kwargs

    def test_setters(self):
        """测试各种 setter 方法"""
        from core.orm import ORM

        o = ORM()
        o.setHost("192.168.1.1")
        o.setPort(3307)
        o.setUser("admin")
        o.setPwd("secret")
        o.setDbName("mydb")
        o.setTimeout(10)
        o.setCharset("utf8mb4")
        o.setSocket("/tmp/mysql.sock")
        o.setDbConf("/etc/my.cnf")

        assert o.getPwd() == "secret"

    def test_default_values(self):
        """测试默认值"""
        from core.orm import ORM

        o = ORM()
        kwargs = o._build_conn_kwargs(use_socket=False)
        assert kwargs["host"] == "localhost"
        assert kwargs["port"] == 3306
        assert kwargs["user"] == "root"
        assert kwargs["charset"] == "utf8"


class TestORMConnection:
    """测试 ORM 连接逻辑"""

    @patch("core.orm.pymysql")
    def test_conn_remote_host(self, mock_pymysql):
        """测试远程主机连接"""
        from core.orm import ORM

        o = ORM()
        o.setHost("192.168.1.100")

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_pymysql.connect.return_value = mock_conn
        mock_pymysql.cursors.DictCursor = "DictCursor"

        result = o._ORM__Conn()
        assert result is True
        mock_pymysql.connect.assert_called_once()

    @patch("core.orm.pymysql")
    def test_conn_failure(self, mock_pymysql):
        """测试连接失败"""
        from core.orm import ORM

        o = ORM()
        o.setHost("invalid-host")

        mock_pymysql.connect.side_effect = Exception("Connection refused")
        mock_pymysql.cursors.DictCursor = "DictCursor"

        result = o._ORM__Conn()
        assert result is False
