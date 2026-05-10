# coding:utf-8
# Compass Panel - MySQL Database Management (pymysql-based)
# Replaces shell-command-based approach with direct pymysql connections

import os
import time
import re
from flask import Blueprint, request

from admin.user_login_check import panel_login_required
import core.mw as mw
import thisdb

blueprint = Blueprint("database_mysql", __name__, url_prefix="/database/mysql")

MYSQL_ROOT_USER = "root"
MYSQL_SOCKET = "/tmp/mysql.sock"

# Whitelists for security
_VALID_CHARSETS = {"utf8mb4", "utf8", "latin1", "gbk", "gb2312", "utf16", "utf32", "ascii", "binary"}
_VALID_COLLATIONS = {
    "utf8mb4_general_ci", "utf8mb4_unicode_ci", "utf8mb4_bin",
    "utf8_general_ci", "utf8_unicode_ci", "utf8_bin",
    "latin1_general_ci", "latin1_bin", "gbk_chinese_ci", "gbk_bin",
    "utf16_general_ci", "utf16_bin", "utf32_general_ci", "utf32_bin",
    "ascii_general_ci", "ascii_bin", "binary",
}


def _sanitize_db_name(name):
    """Ensure database name is safe for shell commands"""
    if not re.match(r"^[\w\-]+$", name):
        return None
    return name


def _sanitize_error(e):
    """Sanitize error messages to avoid information disclosure"""
    err_str = str(e)
    # Remove file paths
    err_str = re.sub(r'/[\w/\.\-]+', '[path]', err_str)
    # Remove IP addresses
    err_str = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '[host]', err_str)
    # Remove port numbers after host
    err_str = re.sub(r':\d{2,5}', ':[port]', err_str)
    return err_str[:200]


def _get_mysql_connection(database=None):
    """Create a pymysql connection using root credentials from panel config"""
    import pymysql

    # Try to get root password from panel database
    root_pwd = thisdb.getOption("mysql_root_pwd", default="")
    if not root_pwd:
        # Try reading from mysql install config
        root_pwd = _get_mysql_root_password()

    try:
        conn = pymysql.connect(
            unix_socket=MYSQL_SOCKET,
            user=MYSQL_ROOT_USER,
            password=root_pwd,
            database=database,
            charset="utf8mb4",
            connect_timeout=5,
            read_timeout=10,
            write_timeout=10,
        )
        return conn
    except pymysql.Error as e:
        # Try via TCP if socket fails
        try:
            conn = pymysql.connect(
                host="127.0.0.1",
                port=3306,
                user=MYSQL_ROOT_USER,
                password=root_pwd,
                database=database,
                charset="utf8mb4",
                connect_timeout=5,
            )
            return conn
        except pymysql.Error:
            raise


def _get_mysql_root_password():
    """Try to find MySQL root password from various sources"""
    pwd_file = mw.getServerDir() + "/mysql/mysql_root_pwd.pl"
    if os.path.exists(pwd_file):
        return mw.readFile(pwd_file).strip()

    # Try default locations
    for f in ["/www/server/mysql/data/mysql_root_pwd.pl",
              mw.getPanelDir() + "/data/mysql_root_pwd.pl"]:
        if os.path.exists(f):
            return mw.readFile(f).strip()

    return ""


def _exec_sql(conn, sql, params=None):
    """Execute SQL and return results"""
    cursor = conn.cursor()
    cursor.execute(sql, params or ())
    if sql.strip().upper().startswith("SELECT") or sql.strip().upper().startswith("SHOW"):
        columns = [d[0] for d in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    conn.commit()
    return cursor.rowcount


@blueprint.route("/status", methods=["POST"])
@panel_login_required
def mysql_status():
    """Get MySQL service status and info"""
    try:
        import pymysql
        conn = _get_mysql_connection()
        version = _exec_sql(conn, "SELECT VERSION() AS v")[0]["v"]
        conn.close()
        return mw.returnData(True, {
            "running": True,
            "version": version,
            "socket": MYSQL_SOCKET,
        })
    except pymysql.Error as e:
        return mw.returnData(True, {
            "running": False,
            "error": _sanitize_error(e),
        })
    except ImportError:
        return mw.returnData(True, {"running": False, "error": "pymysql未安装"})


@blueprint.route("/databases", methods=["POST"])
@panel_login_required
def list_databases():
    """List all MySQL databases"""
    try:
        conn = _get_mysql_connection()
        dbs = _exec_sql(conn, "SHOW DATABASES")
        conn.close()

        # Filter system databases
        system_dbs = {"information_schema", "mysql", "performance_schema", "sys"}
        user_dbs = [d for d in dbs if d["Database"] not in system_dbs]

        return mw.returnData(True, {"databases": [d["Database"] for d in user_dbs], "count": len(user_dbs)})
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


@blueprint.route("/create_database", methods=["POST"])
@panel_login_required
def create_database():
    """Create a MySQL database"""
    name = request.form.get("name", "").strip()
    charset = request.form.get("charset", "utf8mb4").strip()
    collate = request.form.get("collate", "utf8mb4_general_ci").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not name:
        return mw.returnData(False, "数据库名不能为空")
    if not re.match(r"^[\w\-]+$", name):
        return mw.returnData(False, "数据库名只能包含字母、数字、下划线和连字符")
    if len(name.encode("utf-8")) > 64:
        return mw.returnData(False, "数据库名过长")

    reserved = {"root", "mysql", "test", "sys", "information_schema", "performance_schema"}
    if name.lower() in reserved:
        return mw.returnData(False, "不能使用系统保留的数据库名")

    if charset not in _VALID_CHARSETS:
        return mw.returnData(False, f"不支持的字符集: {charset}")
    if collate not in _VALID_COLLATIONS:
        return mw.returnData(False, f"不支持的排序规则: {collate}")

    try:
        conn = _get_mysql_connection()
        _exec_sql(conn, f"CREATE DATABASE `{name}` DEFAULT CHARACTER SET {charset} COLLATE {collate}")

        # Create user if specified
        if username and password:
            if not re.match(r"^[\w\-]+$", username):
                return mw.returnData(False, "用户名只能包含字母、数字、下划线和连字符")
            # Use pymysql escape for password to prevent SQL injection
            import pymysql as _pymysql
            safe_pwd = _pymysql.escape_string(password)
            _exec_sql(conn, f"CREATE USER IF NOT EXISTS `{username}`@`localhost` IDENTIFIED BY '{safe_pwd}'")
            _exec_sql(conn, f"GRANT ALL PRIVILEGES ON `{name}`.* TO `{username}`@`localhost`")
            _exec_sql(conn, "FLUSH PRIVILEGES")

        conn.close()
        mw.writeLog("MySQL管理", f"创建数据库[{name}]")
        return mw.returnData(True, f"数据库[{name}]创建成功!")
    except Exception as e:
        return mw.returnData(False, f"创建失败: {_sanitize_error(e)}")


@blueprint.route("/delete_database", methods=["POST"])
@panel_login_required
def delete_database():
    """Delete a MySQL database"""
    name = request.form.get("name", "").strip()
    if not name:
        return mw.returnData(False, "数据库名不能为空")

    reserved = {"information_schema", "mysql", "performance_schema", "sys"}
    if name.lower() in reserved:
        return mw.returnData(False, "不能删除系统数据库")

    try:
        conn = _get_mysql_connection()
        _exec_sql(conn, f"DROP DATABASE IF EXISTS `{name}`")
        conn.close()
        mw.writeLog("MySQL管理", f"删除数据库[{name}]")
        return mw.returnData(True, f"数据库[{name}]已删除!")
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


@blueprint.route("/users", methods=["POST"])
@panel_login_required
def list_users():
    """List MySQL users (non-system)"""
    try:
        conn = _get_mysql_connection()
        rows = _exec_sql(conn, "SELECT User, Host FROM mysql.user WHERE User NOT IN ('root', 'mysql.session', 'mysql.sys', 'debian-sys-maint')")
        conn.close()
        return mw.returnData(True, {"users": rows, "count": len(rows)})
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


@blueprint.route("/create_user", methods=["POST"])
@panel_login_required
def create_user():
    """Create MySQL user"""
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    host = request.form.get("host", "localhost").strip()
    db_name = request.form.get("database", "").strip()

    if not username or not password:
        return mw.returnData(False, "用户名和密码不能为空")

    # Validate host
    if not re.match(r"^[\w\.\-%]+$", host):
        return mw.returnData(False, "主机名格式无效")

    try:
        conn = _get_mysql_connection()
        import pymysql as _pymysql
        safe_pwd = _pymysql.escape_string(password)
        _exec_sql(conn, f"CREATE USER IF NOT EXISTS `{username}`@`{host}` IDENTIFIED BY '{safe_pwd}'")

        if db_name:
            if not _sanitize_db_name(db_name):
                return mw.returnData(False, "数据库名格式无效")
            _exec_sql(conn, f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO `{username}`@`{host}`")
            _exec_sql(conn, "FLUSH PRIVILEGES")

        conn.close()
        mw.writeLog("MySQL管理", f"创建用户[{username}]")
        return mw.returnData(True, f"用户[{username}]创建成功!")
    except Exception as e:
        return mw.returnData(False, f"创建失败: {_sanitize_error(e)}")


@blueprint.route("/delete_user", methods=["POST"])
@panel_login_required
def delete_user():
    """Delete MySQL user"""
    username = request.form.get("username", "").strip()
    host = request.form.get("host", "%").strip()

    if not username:
        return mw.returnData(False, "用户名不能为空")
    if username == "root":
        return mw.returnData(False, "不能删除root用户")

    try:
        conn = _get_mysql_connection()
        _exec_sql(conn, f"DROP USER IF EXISTS `{username}`@`{host}`")
        _exec_sql(conn, "FLUSH PRIVILEGES")
        conn.close()
        return mw.returnData(True, f"用户[{username}]已删除!")
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


@blueprint.route("/reset_password", methods=["POST"])
@panel_login_required
def reset_password():
    """Reset MySQL user password"""
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    host = request.form.get("host", "localhost").strip()

    if not username or not password:
        return mw.returnData(False, "用户名和密码不能为空")

    if not re.match(r"^[\w\.\-%]+$", host):
        return mw.returnData(False, "主机名格式无效")

    try:
        conn = _get_mysql_connection()
        import pymysql
        import pymysql as _pymysql
        safe_pwd = _pymysql.escape_string(password)
        try:
            # MySQL 5.7+/8.0+
            _exec_sql(conn, f"ALTER USER `{username}`@`{host}` IDENTIFIED BY '{safe_pwd}'")
        except pymysql.Error:
            # Older MySQL
            _exec_sql(conn, f"SET PASSWORD FOR `{username}`@`{host}` = PASSWORD('{safe_pwd}')")
        _exec_sql(conn, "FLUSH PRIVILEGES")
        conn.close()
        return mw.returnData(True, f"密码已重置!")
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


@blueprint.route("/backup", methods=["POST"])
@panel_login_required
def backup_database():
    """Backup a MySQL database using mysqldump"""
    name = request.form.get("name", "").strip()
    backup_dir = request.form.get("backup_dir", "/www/backup/database").strip()

    if not name:
        return mw.returnData(False, "数据库名不能为空")

    safe_name = _sanitize_db_name(name)
    if not safe_name:
        return mw.returnData(False, "数据库名无效")

    os.makedirs(backup_dir, exist_ok=True)
    backup_file = os.path.join(backup_dir, f"{safe_name}_{time.strftime('%Y%m%d_%H%M%S')}.sql.gz")

    # Use password file to avoid command line exposure
    import tempfile
    root_pwd = _get_mysql_root_password()
    pwd_file = None
    try:
        if root_pwd:
            pwd_file = tempfile.NamedTemporaryFile(mode='w', suffix='.cnf', delete=False)
            pwd_file.write(f"[client]\npassword={root_pwd}\n")
            pwd_file.close()
            defaults = f"--defaults-file='{pwd_file.name}'"
        else:
            defaults = ""

        result = mw.execShell(
            f"mysqldump {defaults} --default-character-set=utf8mb4 --single-transaction --routines --events "
            f"--skip-lock-tables -u root '{safe_name}' | gzip > '{backup_file}' 2>&1",
            timeout=300
        )
    finally:
        if pwd_file:
            try:
                os.unlink(pwd_file.name)
            except OSError:
                pass

    if os.path.exists(backup_file) and os.path.getsize(backup_file) > 0:
        mw.writeLog("MySQL管理", f"备份数据库[{safe_name}]")
        return mw.returnData(True, {"file": backup_file, "size": os.path.getsize(backup_file)})
    return mw.returnData(False, f"备份失败: {_sanitize_error(result[1])}")


@blueprint.route("/restore", methods=["POST"])
@panel_login_required
def restore_database():
    """Restore MySQL database from backup"""
    name = request.form.get("name", "").strip()
    backup_file = request.form.get("file", "").strip()

    safe_name = _sanitize_db_name(name)
    if not safe_name:
        return mw.returnData(False, "数据库名无效")
    if not backup_file:
        return mw.returnData(False, "参数不完整")
    if not os.path.exists(backup_file):
        return mw.returnData(False, "备份文件不存在")

    # Use password file to avoid command line exposure
    import tempfile
    root_pwd = _get_mysql_root_password()
    pwd_file = None
    try:
        if root_pwd:
            pwd_file = tempfile.NamedTemporaryFile(mode='w', suffix='.cnf', delete=False)
            pwd_file.write(f"[client]\npassword={root_pwd}\n")
            pwd_file.close()
            defaults = f"--defaults-file='{pwd_file.name}'"
        else:
            defaults = ""

        result = mw.execShell(
            f"gunzip -c '{backup_file}' | mysql {defaults} -u root '{safe_name}' 2>&1",
            timeout=300
        )
    finally:
        if pwd_file:
            try:
                os.unlink(pwd_file.name)
            except OSError:
                pass

    if result[2] == 0:
        mw.writeLog("MySQL管理", f"恢复数据库[{safe_name}]")
        return mw.returnData(True, "恢复成功!")
    return mw.returnData(False, f"恢复失败: {_sanitize_error(result[1])}")


@blueprint.route("/slow_logs", methods=["POST"])
@panel_login_required
def slow_logs():
    """Get MySQL slow query log (last 100 lines)"""
    try:
        conn = _get_mysql_connection()
        var = _exec_sql(conn, "SHOW VARIABLES LIKE 'slow_query_log_file'")
        conn.close()

        log_file = var[0]["Value"] if var else "/www/server/data/mysql-slow.log"
        if os.path.exists(log_file):
            result = mw.execShell(f"tail -100 '{log_file}' 2>/dev/null", timeout=5)
            return mw.returnData(True, {"log": result[0]})
        return mw.returnData(True, {"log": "慢查询日志文件不存在或慢查询未开启"})
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


@blueprint.route("/error_logs", methods=["POST"])
@panel_login_required
def error_logs():
    """Get MySQL error log (last 100 lines)"""
    try:
        conn = _get_mysql_connection()
        var = _exec_sql(conn, "SHOW VARIABLES LIKE 'log_error'")
        conn.close()

        log_file = var[0]["Value"] if var else "/www/server/data/*.err"
        if os.path.exists(log_file):
            result = mw.execShell(f"tail -100 '{log_file}' 2>/dev/null", timeout=5)
            return mw.returnData(True, {"log": result[0]})
        return mw.returnData(True, {"log": "错误日志文件不存在"})
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


# ==================== User Permission Management (用户权限管理) ====================

@blueprint.route("/user_privileges", methods=["POST"])
@panel_login_required
def user_privileges():
    """Get detailed privileges for a MySQL user"""
    username = request.form.get("username", "").strip()
    host = request.form.get("host", "%").strip()

    if not username:
        return mw.returnData(False, "用户名不能为空")

    try:
        conn = _get_mysql_connection()
        grants = _exec_sql(conn, f"SHOW GRANTS FOR `{username}`@`{host}`")
        conn.close()

        privileges = []
        for g in grants:
            for k, v in g.items():
                privileges.append(v)

        return mw.returnData(True, {"username": username, "host": host, "grants": privileges})
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


@blueprint.route("/grant_privileges", methods=["POST"])
@panel_login_required
def grant_privileges():
    """Grant privileges to a MySQL user"""
    username = request.form.get("username", "").strip()
    host = request.form.get("host", "localhost").strip()
    db_name = request.form.get("database", "*").strip()
    privileges = request.form.get("privileges", "ALL").strip()

    if not username:
        return mw.returnData(False, "用户名不能为空")

    valid_privs = ["ALL", "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP",
                   "INDEX", "ALTER", "EXECUTE", "CREATE VIEW", "SHOW VIEW",
                   "CREATE ROUTINE", "ALTER ROUTINE", "EVENT", "TRIGGER", "REFERENCES"]
    priv_list = [p.strip().upper() for p in privileges.split(",")]
    for p in priv_list:
        if p not in valid_privs and p != "ALL":
            return mw.returnData(False, f"无效的权限: {p}")

    priv_str = ", ".join(priv_list) if "ALL" not in priv_list else "ALL PRIVILEGES"

    try:
        conn = _get_mysql_connection()
        _exec_sql(conn, f"GRANT {priv_str} ON `{db_name}`.* TO `{username}`@`{host}`")
        _exec_sql(conn, "FLUSH PRIVILEGES")
        conn.close()
        mw.writeLog("MySQL管理", f"授权用户[{username}] {priv_str} ON {db_name}")
        return mw.returnData(True, f"权限授予成功!")
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


@blueprint.route("/revoke_privileges", methods=["POST"])
@panel_login_required
def revoke_privileges():
    """Revoke privileges from a MySQL user"""
    username = request.form.get("username", "").strip()
    host = request.form.get("host", "localhost").strip()
    db_name = request.form.get("database", "*").strip()
    privileges = request.form.get("privileges", "ALL").strip()

    if not username:
        return mw.returnData(False, "用户名不能为空")

    priv_str = "ALL PRIVILEGES" if "ALL" in privileges.upper() else privileges

    try:
        conn = _get_mysql_connection()
        _exec_sql(conn, f"REVOKE {priv_str} ON `{db_name}`.* FROM `{username}`@`{host}`")
        _exec_sql(conn, "FLUSH PRIVILEGES")
        conn.close()
        mw.writeLog("MySQL管理", f"撤销用户[{username}]权限")
        return mw.returnData(True, "权限撤销成功!")
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


# ==================== Import/Export (导入导出) ====================

@blueprint.route("/import", methods=["POST"])
@panel_login_required
def import_database():
    """Import SQL file into a database"""
    name = request.form.get("name", "").strip()
    sql_file = request.form.get("file", "").strip()

    safe_name = _sanitize_db_name(name)
    if not safe_name or not sql_file:
        return mw.returnData(False, "参数不完整")
    if not os.path.exists(sql_file):
        return mw.returnData(False, "SQL文件不存在")

    # Use password file to avoid command line exposure
    import tempfile
    root_pwd = _get_mysql_root_password()
    pwd_file = None
    try:
        if root_pwd:
            pwd_file = tempfile.NamedTemporaryFile(mode='w', suffix='.cnf', delete=False)
            pwd_file.write(f"[client]\npassword={root_pwd}\n")
            pwd_file.close()
            defaults = f"--defaults-file='{pwd_file.name}'"
        else:
            defaults = ""

        # Support gzipped SQL files
        if sql_file.endswith(".gz"):
            cmd = f"gunzip -c '{sql_file}' | mysql {defaults} -u root '{safe_name}' 2>&1"
        else:
            cmd = f"mysql {defaults} -u root '{safe_name}' < '{sql_file}' 2>&1"

        result = mw.execShell(cmd, timeout=600)
    finally:
        if pwd_file:
            try:
                os.unlink(pwd_file.name)
            except OSError:
                pass

    if result[2] == 0:
        mw.writeLog("MySQL管理", f"导入数据库[{safe_name}]: {os.path.basename(sql_file)}")
        return mw.returnData(True, "导入成功!")
    return mw.returnData(False, f"导入失败: {_sanitize_error(result[1])}")


@blueprint.route("/export", methods=["POST"])
@panel_login_required
def export_database():
    """Export database to SQL file"""
    name = request.form.get("name", "").strip()
    export_dir = request.form.get("dir", "/www/backup/database").strip()
    compress = request.form.get("compress", "1") == "1"

    safe_name = _sanitize_db_name(name)
    if not safe_name:
        return mw.returnData(False, "数据库名无效")

    os.makedirs(export_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    export_file = os.path.join(export_dir, f"{safe_name}_{timestamp}.sql")
    if compress:
        export_file += ".gz"

    # Use password file to avoid command line exposure
    import tempfile
    root_pwd = _get_mysql_root_password()
    pwd_file = None
    try:
        if root_pwd:
            pwd_file = tempfile.NamedTemporaryFile(mode='w', suffix='.cnf', delete=False)
            pwd_file.write(f"[client]\npassword={root_pwd}\n")
            pwd_file.close()
            defaults = f"--defaults-file='{pwd_file.name}'"
        else:
            defaults = ""

        pipe_cmd = "| gzip" if compress else ""
        redirect = ">" if not compress else ""
        if compress:
            cmd = (
                f"mysqldump {defaults} --default-character-set=utf8mb4 --single-transaction --routines --events "
                f"--skip-lock-tables -u root '{safe_name}' | gzip > '{export_file}' 2>&1"
            )
        else:
            cmd = (
                f"mysqldump {defaults} --default-character-set=utf8mb4 --single-transaction --routines --events "
                f"--skip-lock-tables -u root '{safe_name}' > '{export_file}' 2>&1"
            )

        result = mw.execShell(cmd, timeout=600)
    finally:
        if pwd_file:
            try:
                os.unlink(pwd_file.name)
            except OSError:
                pass

    if os.path.exists(export_file) and os.path.getsize(export_file) > 0:
        mw.writeLog("MySQL管理", f"导出数据库[{safe_name}]")
        return mw.returnData(True, {"file": export_file, "size": os.path.getsize(export_file)})
    return mw.returnData(False, f"导出失败: {_sanitize_error(result[1])}")


# ==================== Table Operations (表操作) ====================

@blueprint.route("/tables", methods=["POST"])
@panel_login_required
def list_tables():
    """List tables in a database"""
    db_name = request.form.get("name", "").strip()
    if not db_name:
        return mw.returnData(False, "数据库名不能为空")

    try:
        conn = _get_mysql_connection(db_name)
        tables = _exec_sql(conn, "SHOW TABLE STATUS")
        conn.close()

        result = []
        for t in tables:
            result.append({
                "name": t.get("Name", ""),
                "engine": t.get("Engine", ""),
                "rows": t.get("Rows", 0),
                "size": _format_table_size(t.get("Data_length", 0) + t.get("Index_length", 0)),
                "collation": t.get("Collation", ""),
                "comment": t.get("Comment", ""),
            })

        return mw.returnData(True, {"tables": result, "count": len(result)})
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


def _format_table_size(size):
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


@blueprint.route("/optimize_table", methods=["POST"])
@panel_login_required
def optimize_table():
    """Optimize a MySQL table"""
    db_name = request.form.get("database", "").strip()
    table_name = request.form.get("table", "").strip()

    if not db_name or not table_name:
        return mw.returnData(False, "参数不完整")

    try:
        conn = _get_mysql_connection(db_name)
        result = _exec_sql(conn, f"OPTIMIZE TABLE `{table_name}`")
        conn.close()
        mw.writeLog("MySQL管理", f"优化表[{db_name}.{table_name}]")
        return mw.returnData(True, f"表[{table_name}]优化完成!")
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


@blueprint.route("/repair_table", methods=["POST"])
@panel_login_required
def repair_table():
    """Repair a MySQL table"""
    db_name = request.form.get("database", "").strip()
    table_name = request.form.get("table", "").strip()

    if not db_name or not table_name:
        return mw.returnData(False, "参数不完整")

    try:
        conn = _get_mysql_connection(db_name)
        result = _exec_sql(conn, f"REPAIR TABLE `{table_name}`")
        conn.close()
        mw.writeLog("MySQL管理", f"修复表[{db_name}.{table_name}]")
        return mw.returnData(True, f"表[{table_name}]修复完成!")
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


@blueprint.route("/truncate_table", methods=["POST"])
@panel_login_required
def truncate_table():
    """Truncate a MySQL table (empty all data)"""
    db_name = request.form.get("database", "").strip()
    table_name = request.form.get("table", "").strip()

    if not db_name or not table_name:
        return mw.returnData(False, "参数不完整")

    try:
        conn = _get_mysql_connection(db_name)
        _exec_sql(conn, f"TRUNCATE TABLE `{table_name}`")
        conn.close()
        mw.writeLog("MySQL管理", f"清空表[{db_name}.{table_name}]")
        return mw.returnData(True, f"表[{table_name}]已清空!")
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


# ==================== Character Sets (字符集) ====================

@blueprint.route("/charsets", methods=["POST"])
@panel_login_required
def list_charsets():
    """List available MySQL character sets"""
    try:
        conn = _get_mysql_connection()
        charsets = _exec_sql(conn, "SHOW CHARACTER SET")
        conn.close()
        return mw.returnData(True, {"charsets": charsets})
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


@blueprint.route("/variables", methods=["POST"])
@panel_login_required
def mysql_variables():
    """Get MySQL server variables"""
    search = request.form.get("search", "").strip()
    try:
        conn = _get_mysql_connection()
        if search:
            # Escape LIKE special characters to prevent injection
            safe_search = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            vars = _exec_sql(conn, f"SHOW VARIABLES LIKE '%{safe_search}%'")
        else:
            vars = _exec_sql(conn, "SHOW VARIABLES")
        conn.close()
        return mw.returnData(True, {"variables": vars[:100], "count": len(vars)})
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


@blueprint.route("/processlist", methods=["POST"])
@panel_login_required
def processlist():
    """Show MySQL process list"""
    try:
        conn = _get_mysql_connection()
        processes = _exec_sql(conn, "SHOW FULL PROCESSLIST")
        conn.close()
        return mw.returnData(True, {"processes": processes, "count": len(processes)})
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))


@blueprint.route("/kill_process", methods=["POST"])
@panel_login_required
def kill_mysql_process():
    """Kill a MySQL process"""
    pid = request.form.get("pid", "").strip()
    if not pid:
        return mw.returnData(False, "进程ID不能为空")

    try:
        conn = _get_mysql_connection()
        _exec_sql(conn, f"KILL {pid}")
        conn.close()
        return mw.returnData(True, f"进程{pid}已终止!")
    except Exception as e:
        return mw.returnData(False, _sanitize_error(e))
