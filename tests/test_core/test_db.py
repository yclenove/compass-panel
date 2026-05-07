"""数据库模块测试"""

import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'web'))


class TestSqlHelperMethods:
    """测试 Sql 类的辅助方法"""

    def test_rows_to_dicts(self):
        """测试行转字典"""
        from core.db import Sql

        sql = Sql()
        data = [(1, "alice", 25), (2, "bob", 30)]
        fields = ["id", "name", "age"]

        result = sql._rows_to_dicts(data, fields)
        assert len(result) == 2
        assert result[0] == {"id": 1, "name": "alice", "age": 25}
        assert result[1] == {"id": 2, "name": "bob", "age": 30}

    def test_rows_to_dicts_empty(self):
        """测试空数据行转字典"""
        from core.db import Sql

        sql = Sql()
        result = sql._rows_to_dicts([], ["id", "name"])
        assert result == []

    def test_build_sql(self):
        """测试 SQL 构建"""
        from core.db import Sql

        sql = Sql()
        sql.table("users")
        sql.where("id=?", (1,))
        sql.order("id DESC")
        sql.limit("10")

        built = sql._build_sql()
        assert "SELECT" in built
        assert "FROM users" in built
        assert "WHERE id=?" in built
        assert "ORDER BY id DESC" in built
        assert "LIMIT 10" in built

    def test_build_sql_defaults(self):
        """测试默认 SQL 构建"""
        from core.db import Sql

        sql = Sql()
        sql.table("test")

        built = sql._build_sql()
        assert built == "SELECT * FROM test"

    def test_field_cache(self):
        """测试字段缓存机制"""
        from core.db import Sql

        sql = Sql()
        # 字段缓存应该是类级别的字典
        assert isinstance(sql._Sql__field_cache, dict)


class TestSqlCheckInput:
    """测试 SQL 输入检查"""

    def test_check_input_normal(self):
        """测试正常输入"""
        from core.db import Sql

        sql = Sql()
        assert sql.checkInput("hello") == "hello"
        assert sql.checkInput("test123") == "test123"

    def test_check_input_empty(self):
        """测试空输入"""
        from core.db import Sql

        sql = Sql()
        assert sql.checkInput("") == ""
        assert sql.checkInput(None) is None

    def test_check_input_non_string(self):
        """测试非字符串输入"""
        from core.db import Sql

        sql = Sql()
        assert sql.checkInput(123) == 123
        assert sql.checkInput(True) is True

    def test_check_input_special_chars(self):
        """测试特殊字符转义"""
        from core.db import Sql

        sql = Sql()
        result = sql.checkInput("<script>alert('xss')</script>")
        assert "<" not in result
        assert ">" not in result


class TestSqlFormatPdata:
    """测试数据格式化"""

    def test_format_pdata(self):
        """测试数据格式化"""
        from core.db import Sql

        sql = Sql()
        pdata = {"name": "alice", "age": 25}
        keys, param = sql._Sql__format_pdata(pdata)

        assert "name" in keys
        assert "age" in keys
        assert "alice" in param
        assert 25 in param

    def test_format_pdata_empty(self):
        """测试空数据格式化"""
        from core.db import Sql

        sql = Sql()
        keys, param = sql._Sql__format_pdata({})
        assert keys == ""
        assert param == ()


class TestSqlBuilderPattern:
    """测试 Sql 链式调用"""

    def test_chaining(self):
        """测试链式调用"""
        from core.db import Sql

        sql = Sql()
        result = (
            sql.table("users")
            .where("id=?", (1,))
            .order("id DESC")
            .limit("10")
            .field("id,name")
        )
        assert result is sql

    def test_where_and_where(self):
        """测试 andWhere"""
        from core.db import Sql

        sql = Sql()
        sql.where("id=?", (1,))
        sql.andWhere("name=?", ("alice",))

        assert "and" in sql._Sql__OPT_WHERE
        assert len(sql._Sql__OPT_PARAM) == 2

    def test_group(self):
        """测试 group by"""
        from core.db import Sql

        sql = Sql()
        sql.group("category")
        assert "GROUP BY" in sql._Sql__OPT_GROUP

    def test_group_empty(self):
        """测试空 group by"""
        from core.db import Sql

        sql = Sql()
        sql.group("")
        assert sql._Sql__OPT_GROUP == ""

    def test_debug_mode(self):
        """测试调试模式"""
        from core.db import Sql

        sql = Sql()
        result = sql.debug(True)
        assert result is sql
        assert sql._Sql__debug is True
