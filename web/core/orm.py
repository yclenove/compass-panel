# coding: utf-8

import os

import pymysql.cursors


class ORM:
    __DB_PASS = None
    __DB_USER = "root"
    __DB_PORT = 3306
    __DB_NAME = ""
    __DB_HOST = "localhost"
    __DB_CONN = None
    __DB_CUR = None
    __DB_ERR = None
    __DB_CNF = "/etc/my.cnf"
    __DB_TIMEOUT = 1
    __DB_SOCKET = "/www/server/mysql/mysql.sock"

    __DB_CHARSET = "utf8"

    def _build_conn_kwargs(self, use_socket=False):
        """构建数据库连接参数"""
        kwargs = {
            "host": self.__DB_HOST,
            "user": self.__DB_USER,
            "passwd": self.__DB_PASS,
            "database": self.__DB_NAME,
            "port": int(self.__DB_PORT),
            "charset": self.__DB_CHARSET,
            "connect_timeout": self.__DB_TIMEOUT,
            "cursorclass": pymysql.cursors.DictCursor,
        }
        if use_socket:
            kwargs["unix_socket"] = self.__DB_SOCKET
        return kwargs

    def __Conn(self):
        """连接数据库，支持远程、socket 和本地三种方式"""
        try:
            use_socket = (
                self.__DB_HOST == "localhost"
                and os.path.exists(self.__DB_SOCKET)
            )

            kwargs = self._build_conn_kwargs(use_socket=use_socket)

            try:
                self.__DB_CONN = pymysql.connect(**kwargs)
            except Exception:
                # 回退到 127.0.0.1 重试
                self.__DB_HOST = "127.0.0.1"
                kwargs["host"] = self.__DB_HOST
                self.__DB_CONN = pymysql.connect(**kwargs)

            self.__DB_CUR = self.__DB_CONN.cursor()
            return True
        except Exception as e:
            self.__DB_ERR = e
            return False

    def setDbConf(self, conf):
        self.__DB_CNF = conf

    def setSocket(self, sock):
        self.__DB_SOCKET = sock

    def setCharset(self, charset):
        self.__DB_CHARSET = charset

    def setHost(self, host):
        self.__DB_HOST = host

    def setPort(self, port):
        self.__DB_PORT = port

    def setUser(self, user):
        self.__DB_USER = user

    def setPwd(self, pwd):
        self.__DB_PASS = pwd

    def getPwd(self):
        return self.__DB_PASS

    def setTimeout(self, timeout=1):
        self.__DB_TIMEOUT = timeout
        return True

    def setDbName(self, name):
        self.__DB_NAME = name

    def execute(self, sql):
        # 执行SQL语句返回受影响行
        if not self.__Conn():
            return self.__DB_ERR
        try:
            result = self.__DB_CUR.execute(sql)
            self.__DB_CONN.commit()
            self.__Close()
            return result
        except Exception as ex:
            return ex

    def ping(self):
        try:
            self.__DB_CONN.ping()
        except Exception as e:
            print(e)
        return True

    def find(self, sql):
        d = self.query(sql)
        if d is not None:
            if len(d) > 0:
                return d[0]
        return None

    def query(self, sql):
        # 执行SQL语句返回数据集
        if not self.__Conn():
            return self.__DB_ERR
        try:
            self.__DB_CUR.execute(sql)
            result = self.__DB_CUR.fetchall()
            # print(result)
            # 将元组转换成列表
            # data = map(list, result)
            self.__Close()
            return result
        except Exception as ex:
            return ex

    def __Close(self):
        # 关闭连接
        self.__DB_CUR.close()
        self.__DB_CONN.close()
