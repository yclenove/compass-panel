# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import time
import base64
import json
import os
import sys

from flask import Blueprint, render_template, send_from_directory, make_response
from flask import redirect
from flask import Response
from flask import request

from admin.common import isLogined
from admin.user_login_check import panel_login_required
from admin import session

import core.mw as mw
import thisdb

# Vue SPA 静态文件目录
_vue_dist_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'static', 'dist'
)

# MIME 类型映射
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


def _serve_vue_file(file_path):
    """发送 Vue 静态文件，设置正确的 MIME 类型"""
    ext = os.path.splitext(file_path)[1].lower()
    mime_type = _vue_mime_types.get(ext, 'application/octet-stream')
    response = make_response(send_from_directory(_vue_dist_dir, file_path))
    response.headers['Content-Type'] = mime_type
    return response


def _serve_vue_spa(vue_sub_path):
    """服务 Vue SPA: 如果是静态文件则返回文件，否则返回 index.html"""
    if vue_sub_path and os.path.exists(os.path.join(_vue_dist_dir, vue_sub_path)):
        return _serve_vue_file(vue_sub_path)
    return send_from_directory(_vue_dist_dir, 'index.html')


blueprint = Blueprint(
    "dashboard", __name__, url_prefix="/", template_folder="../../templates"
)


@blueprint.route("/", endpoint="index", methods=["GET"])
@panel_login_required
def index():
    name = thisdb.getOption("template", default="default")
    return render_template("%s/index.html" % name)


# 安全路径
@blueprint.route("/<path>", endpoint="admin_safe_path", methods=["GET"])
def admin_safe_path(path):
    login = request.args.get("login", "")
    if login != "":
        try:
            # print(login)
            login_str = base64.b64decode(login)
            login_str = login_str.decode("utf-8")
            data = json.loads(login_str)

            time_now = time.time() * 1000
            time_diff = time_now - data["time"]

            if time_diff > 2000:
                return redirect("/")

            info = thisdb.getUserByName(data["username"])
            if info is None:
                return redirect("/")

            if info["password"] != mw.md5(data["password"]):
                return redirect("/")

            session["login"] = True
            session["username"] = info["name"]
            session["overdue"] = int(time.time()) + 7 * 24 * 60 * 60

            thisdb.updateUserLoginTime()
            return redirect("/")
        except Exception:
            pass

    db_path = thisdb.getOption("admin_path")
    name = thisdb.getOption("template", default="default")

    # 处理 Vue SPA 路径: /{admin_path}/vue/...
    vue_prefix = db_path + '/vue'
    if path == vue_prefix or path.startswith(vue_prefix + '/'):
        if not isLogined():
            # 未登录时重定向到登录页
            return redirect('/' + db_path)
        # 提取 Vue 子路径
        vue_sub = path[len(vue_prefix):].lstrip('/')
        return _serve_vue_spa(vue_sub)

    if isLogined():
        return redirect("/")
    if db_path == path:
        return render_template("%s/login.html" % name)

    unauthorized_status = thisdb.getOption("unauthorized_status")
    if unauthorized_status == "0":
        return render_template("%s/path.html" % name)
    return Response(status=int(unauthorized_status))


# 仅针对webhook插件
@blueprint.route("/hook", methods=["POST", "GET"])
def webhook():
    # 兼容获取关键数据
    access_key = request.args.get("access_key", "").strip()
    if access_key == "":
        access_key = request.form.get("access_key", "").strip()

    params = request.args.get("params", "").strip()
    if params == "":
        params = request.form.get("params", "").strip()

    input_args = {
        "access_key": access_key,
        "params": params,
    }

    wh_install_path = mw.getServerDir() + "/webhook"
    if not os.path.exists(wh_install_path):
        return mw.returnData(False, "请先安装WebHook插件!")

    package = mw.getPanelDir() + "/plugins/webhook"
    if package not in sys.path:
        sys.path.append(package)

    try:
        import webhook_index

        return webhook_index.runShellArgs(input_args)
    except Exception as e:
        return str(e)
