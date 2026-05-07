# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import sys
import time
import uuid
import logging

from datetime import timedelta

from flask import Flask
from flask import request
from flask import redirect
from flask import Response
from flask import session
from flask_compress import Compress

from flask_socketio import SocketIO, emit

from flask_caching import Cache


from admin.common import isLogined

import core.mw as mw
import config
import utils.config as utils_config
import thisdb

# 初始化db
from admin import setup

setup.init()

app = Flask(__name__, template_folder="templates/default")


# curl --compressed -I "http://127.0.0.1:44010/"
# -H "Accept-Encoding: br" --write-out "%{json}"
app.config["COMPRESS_ALGORITHM"] = ["br", "zstd", "gzip", "deflate"]
app.config["COMPRESS_LEVEL"] = 9  # 最高压缩级别
app.config["COMPRESS_MIN_SIZE"] = 500  # 最小压缩大小
Compress(app)

# 缓存配置
cache = Cache(config={"CACHE_TYPE": "simple"})
cache.init_app(app, config={"CACHE_TYPE": "simple"})

# 静态文件配置
app.static_folder = "../static"
app.static_url_path = "/static"
app.jinja_env.trim_blocks = True

# from whitenoise import WhiteNoise
# app.wsgi_app = WhiteNoise(
#     app.wsgi_app, root="../web/static/",
#     prefix="static/", max_age=604800
# )

# session配置
# app.secret_key = uuid.UUID(int=uuid.getnode()).hex[-12:]
app.config["SECRET_KEY"] = uuid.UUID(int=uuid.getnode()).hex[-12:]

# app.config['sessions'] = dict()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_KEY_PREFIX"] = "MW_:"
app.config["SESSION_COOKIE_NAME"] = "MW_VER_1"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=31)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 604800

# db的配置
# app.config['SQLALCHEMY_DATABASE_URI'] = (
#     mw.getSqitePrefix() + config.SQLITE_PATH
#     + "?timeout=20"  # 使用 SQLite 数据库
# )
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

# BASIC AUTH
app.config["BASIC_AUTH_OPEN"] = False
try:
    basic_auth = thisdb.getOptionByJson("basic_auth", default={"open": False})
    if basic_auth["open"]:
        app.config["BASIC_AUTH_OPEN"] = True
except Exception:
    pass

# 加载模块
from .submodules import get_submodules  # noqa: E402

for module in get_submodules():
    app.logger.info("Registering blueprint module: %s" % module)
    if app.blueprints.get(module.name) is None:
        app.register_blueprint(module)


# Vue SPA 静态文件目录和辅助函数（必须在 before_request 之前定义）
import os as _os
from flask import send_from_directory, make_response

_vue_dist_dir = _os.path.join(
    _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
    'static', 'dist'
)

_vue_mime_types = {
    '.js': 'application/javascript',
    '.css': 'text/css',
    '.html': 'text/html',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf',
}


def _send_vue_file(file_path):
    """发送 Vue 静态文件，设置正确的 MIME 类型"""
    ext = _os.path.splitext(file_path)[1].lower()
    mime_type = _vue_mime_types.get(ext, 'application/octet-stream')
    response = make_response(send_from_directory(_vue_dist_dir, file_path))
    response.headers['Content-Type'] = mime_type
    return response


def _serve_vue_spa(vue_sub_path):
    """服务 Vue SPA: 如果是静态文件则返回文件，否则返回 index.html"""
    if vue_sub_path and _os.path.exists(_os.path.join(_vue_dist_dir, vue_sub_path)):
        return _send_vue_file(vue_sub_path)
    return send_from_directory(_vue_dist_dir, 'index.html')


def sendAuthenticated():
    # 发送http认证信息
    request_host = mw.getHostAddr()
    result = Response(
        "", 401, {"WWW-Authenticate": 'Basic realm="%s"' % request_host.strip()}
    )
    if "login" not in session and "admin_auth" not in session:
        session.clear()
    return result


@app.before_request
def requestCheck():
    request.start_time = time.time()

    # 处理 Vue 静态资源 - 这些路径不需要安全入口前缀
    # /vue/assets/... 和 /assets/... 都需要处理
    if request.path.startswith('/vue/assets/') or request.path.startswith('/assets/'):
        # 去掉 /vue/ 或 / 前缀，得到相对于 dist 目录的路径
        if request.path.startswith('/vue/'):
            file_path = request.path[len('/vue/'):]
        else:
            file_path = request.path[1:]
        if file_path and _os.path.exists(_os.path.join(_vue_dist_dir, file_path)):
            return _send_vue_file(file_path)
    # 处理 /static/favicon.ico 等 Vue 需要的静态资源
    if request.path.startswith('/static/favicon'):
        favicon_path = _os.path.join(_vue_dist_dir, 'favicon.ico')
        if _os.path.exists(favicon_path):
            return _send_vue_file('favicon.ico')

    # 处理 Vue SPA 路由 - 在路由匹配之前拦截
    try:
        db_path = thisdb.getOption("admin_path")
        if db_path:
            vue_prefix = '/' + db_path + '/vue'
            if request.path == vue_prefix or request.path == vue_prefix + '/' or request.path.startswith(vue_prefix + '/'):
                from admin.common import isLogined
                if not isLogined():
                    return redirect('/' + db_path)
                vue_sub = request.path[len(vue_prefix):].lstrip('/')
                return _serve_vue_spa(vue_sub)
    except Exception:
        pass

    admin_close = thisdb.getOption("admin_close")
    if admin_close == "yes":
        if not request.path.startswith("/close"):
            return redirect("/close")
    # 自定义basic auth认证
    if app.config["BASIC_AUTH_OPEN"]:
        basic_auth = thisdb.getOptionByJson("basic_auth", default={"open": False})
        if not basic_auth["open"]:
            return

        auth = request.authorization
        if request.path in ["/download", "/hook", "/down"]:
            return
        if not auth:
            return sendAuthenticated()

        salt = basic_auth["salt"]
        basic_user = mw.md5(auth.username.strip() + salt)
        basic_pwd = mw.md5(auth.password.strip() + salt)
        if (
            basic_user != basic_auth["basic_user"]
            or basic_pwd != basic_auth["basic_pwd"]
        ):
            return sendAuthenticated()

    # domain_check = mw.checkDomainPanel()
    # if domain_check:
    #     return domain_check


@app.after_request
def requestAfter(response):
    response.headers["soft"] = config.APP_NAME
    response.headers["mw-version"] = config.APP_VERSION
    response.headers["X-Response-Time"] = round(time.time() - request.start_time, 4)

    # 为 Vue 静态资源添加长期缓存头
    if request.path.startswith('/vue/assets/') or request.path.startswith('/assets/'):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"

    return response


@app.errorhandler(404)
def page_unauthorized(error):
    from flask import redirect

    return redirect("/", code=302)
    # return render_template_string('404 not found', error_info=error), 404


# 设置模板全局变量
@app.context_processor
def inject_global_variables():
    app_ver = config.APP_VERSION
    if mw.isDebugMode():
        app_ver = app_ver + str(time.time())

    data = utils_config.getGlobalVar()
    g_config = {"version": app_ver, "title": "MW面板", "ip": "127.0.0.1"}
    return dict(config=g_config, data=data)


# webssh
# socketio = SocketIO(manage_session=False, async_mode='threading',
#                     logger=False, engineio_logger=False, debug=False,
#                     ping_interval=25, ping_timeout=120)
socketio = SocketIO(
    logger=False,
    engineio_logger=False,
    cors_allowed_origins="*",
    async_mode="threading",
)
socketio.init_app(app)


@socketio.on("webssh_websocketio")
def webssh_websocketio(data):
    if not isLogined():
        emit("server_response", {"data": "会话丢失，请重新登陆面板!\r\n"})
        return
    import utils.ssh.ssh_terminal as ssh_terminal

    shell_client = ssh_terminal.ssh_terminal.instance()
    shell_client.run(request.sid, data)
    return


@socketio.on("webssh")
def webssh(data):
    if not isLogined():
        emit("server_response", {"data": "会话丢失，请重新登陆面板!\r\n"})
        return None

    import utils.ssh.ssh_local as ssh_local

    shell = ssh_local.ssh_local.instance()
    shell.run(data)
    return


# File logging
logger = logging.getLogger("werkzeug")
logger.setLevel(config.CONSOLE_LOG_LEVEL)

from utils.enhanced_log_rotation import EnhancedRotatingFileHandler  # noqa: E402

fh = EnhancedRotatingFileHandler(
    config.LOG_FILE,
    config.LOG_ROTATION_SIZE,
    config.LOG_ROTATION_AGE,
    config.LOG_ROTATION_MAX_LOG_FILES,
)
fh.setLevel(config.FILE_LOG_LEVEL)
app.logger.addHandler(fh)
logger.addHandler(fh)

# Console logging
ch = logging.StreamHandler()
ch.setLevel(config.CONSOLE_LOG_LEVEL)
ch.setFormatter(logging.Formatter(config.CONSOLE_LOG_FORMAT))

# Log the startup
app.logger.info("########################################################")
app.logger.info("Starting %s v%s...", config.APP_NAME, config.APP_VERSION)
app.logger.info("########################################################")
app.logger.debug("Python syspath: %s", sys.path)
